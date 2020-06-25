"""Specifies which URLS the application implements and what behavior those URLS have in view functions"""
import os
import shutil
from app import app, db, thumbnails, images, upload_sets
from flask import render_template, flash, redirect, url_for, request, send_from_directory, session, g
import flask_login
from app.forms import LoginForm, RegistrationForm, CreateRecipeForm, \
    EditUserForm, AddTagForm, SearchForm, EmptyForm, EditRecipeForm
from app.models import User, Recipe, RecipeImage, Tag
import werkzeug.urls
import random
from sqlalchemy import exc


@app.before_first_request
def before_first():
    """Initialize session last_url"""
    session['last_url'] = url_for('index')


@app.before_request
def before_request():
    g.search_form = SearchForm()  # This is a global variable accessible in the request, so we can use forms in base


# These decorators specify for which requested URLS this function is to be executed
@app.route('/')
@app.route('/index')
def index():
    """Index view function. Renders an index site"""
    session['last_url'] = url_for('index')
    # TODO: Choose these by hand (also make this query use a database random function if database grows)
    favorite_recipes = [] if Recipe.query.count() < 9 else random.sample(Recipe.query.all(), 9)
    favorite_tags = [] if Tag.query.count() < 6 else random.sample(Tag.query.all(), 6)
    return render_template('index.html', title='Home', favorite_recipes=favorite_recipes,
                           favorite_tags=favorite_tags)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login view function. Presents the user with a login page and logs them in if login was successful"""
    if flask_login.current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        target_user = User.query.filter_by(username=form.username.data).first()
        if target_user is None or not target_user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        flask_login.login_user(target_user, remember=form.remember_me.data)

        next_page = request.args.get('next')    # Where the user is supposed to redirect after login
        # netloc !='' means it redirects to another page, not a relative URL
        if not next_page or werkzeug.urls.url_parse(next_page).netloc != '':
            next_page = session['last_url']
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    """Logout view function. Logs the current user out"""
    flask_login.logout_user()
    return redirect(session['last_url'])


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register view function. Renders a registration form and registers the user if successful"""
    if flask_login.current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        target_user = User(username=form.username.data, email=form.email.data,
                           password=form.password.data, about_me=form.about_me.data)
        db.session.add(target_user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/search', methods=['POST'])
def search():
    """View function for handling search POST requests.
    Separate from search results view function to allow reloading without form resubmission"""
    if g.search_form.validate_on_submit():
        return redirect(url_for('search_results', kind=g.search_form.kind.data, term=g.search_form.term.data))
    return redirect(session['last_url'])


@app.route('/search/results/<kind>/<term>')
def search_results(kind: str, term: str):
    """Display search results. Separate request handling to allow reloading without form resubmission."""
    if kind == 'tag':
        target_tag = Tag.query.filter(Tag.name == term).first()
        relevant_recipes = [] if target_tag is None else target_tag.recipes[:app.config.get('MAX_SEARCH_RESULTS')]
        title = 'Tag {}'.format('' if target_tag is None else target_tag.name)
        full_term = 'Recipes in the Tag Named: ' + term
    elif kind == 'recipe':
        relevant_recipes = Recipe.query.filter(Recipe.name.contains(term))[:app.config.get('MAX_SEARCH_RESULTS')]
        title = 'Search results'
        full_term = 'Recipe Names Including: ' + term
    else:
        flash('Not a valid search kind')
        return redirect(url_for('index'))
    session['last_url'] = url_for('search_results', kind=kind, term=term)
    return render_template('search_results.html', recipes=relevant_recipes, title=title, search_term=full_term,
                           display_author=True)


@app.route('/recipe/<uuid>/add-tag', methods=['POST'])
@flask_login.login_required
def add_tag(uuid):
    """Add a Tag to a recipe. Does not display anything, but just processes data from a form elsewhere."""
    form = AddTagForm()
    if not form.tag_name.data:
        return redirect(session['last_url'])
    if form.validate_on_submit():
        target_recipe = Recipe.query.filter_by(uuid=uuid).first()
        target_tag = Tag.query.filter_by(name=form.tag_name.data).first()
        if target_tag is None:
            target_tag = Tag(form.tag_name.data)
            db.session.add(target_tag)
        if target_recipe is None:
            flash('That recipe does not exist')
            return redirect(url_for('index'))
        if flask_login.current_user != target_recipe.author:
            flash("You're not authorized to add a tag to this recipe")
            return redirect(url_for('recipe', uuid=uuid))

        target_recipe.add_tag(target_tag)
        db.session.commit()
        return redirect(url_for('recipe', uuid=uuid))
    else:
        return redirect(url_for('index'))


@app.route('/recipe/<uuid>')
def recipe(uuid: str):
    """Recipe view function. Displays the recipe with uuid."""
    target_recipe = Recipe.query.filter_by(uuid=uuid).first_or_404()

    session['last_url'] = url_for('recipe', uuid=uuid)  # To jump back after login and logout

    tag_names = [t.name for t in target_recipe.tags]

    edit_priv = flask_login.current_user == target_recipe.author if flask_login.current_user.is_authenticated else False

    recipe_images = [i.file_name for i in target_recipe.images]
    image_urls = [url_for('image', image_set='images', image_name=i) for i in recipe_images]

    add_tag_form = AddTagForm()

    delete_form = EmptyForm()

    return render_template('recipe.html', title='Recipe', recipe=target_recipe, image_urls=image_urls,
                           tag_names=tag_names, edit_priv=edit_priv, add_tag_form=add_tag_form, delete_form=delete_form)


@app.route('/recipe/<uuid>/delete', methods=['POST'])
@flask_login.login_required
def delete_recipe(uuid: str):
    form = EmptyForm()
    if form.validate_on_submit():
        target_recipe = Recipe.query.filter_by(uuid=uuid).first()
        if target_recipe is None:
            flash('That recipe does not exist')
            return redirect(url_for('index'))
        if target_recipe.author != flask_login.current_user:
            flash('Only the author may delete a recipe')
            return redirect(url_for('index'))
        db.session.delete(target_recipe)
        db.session.commit()
        flash('Recipe deleted')
        return redirect(url_for('user', username=flask_login.current_user.username))


@app.route('/tag/<tag_name>')
def tag(tag_name: str):
    """View function for getting a tag by it's name. Tag names are globally unique. Displays recipes in that tag"""
    target_tag = Tag.query.filter_by(name=tag_name).first()
    if target_tag is None:
        flash('Tag {} does not exist').format(tag_name)
        return redirect(url_for('index'))

    session['last_url'] = url_for('tag', tag_name=tag_name)
    relevant_recipes = target_tag.recipes[:app.config.get('MAX_SEARCH_RESULTS')]
    return render_template('search_results.html', title="Tag {}".format(tag_name), search_term=target_tag.name,
                           recipes=relevant_recipes)


@app.route('/user/<username>')
def user(username: str):
    """User view function. Displays a personal page for <username>, with their recipes."""
    target_user = User.query.filter_by(username=username).first()
    if target_user is None:
        flash('User {} does not exist'.format(username))
        return redirect(url_for('index'))

    session['last_url'] = url_for('user', username=username)  # To jump back after login and logout

    edit_priv = flask_login.current_user == target_user if flask_login.current_user.is_authenticated else False

    recipes = list(target_user.recipes)
    col_count = 3
    recipes_matrix = [recipes[row:row+col_count] for row in range(0, len(recipes), col_count)]

    return render_template('user.html', title='User Profile', user=target_user,
                           edit_privilege=edit_priv, recipes=recipes_matrix)


@app.route('/random_recipe')
def random_recipe():
    """Random recipe view function. Selects a random recipe and redirects to that recipe's URL"""
    try:
        recipe_uuid = random.choice(db.session.query(Recipe.uuid).all())[0]
    except IndexError:
        flash('There are no recipes')
        return redirect(url_for('index'))
    return redirect(url_for('recipe', uuid=recipe_uuid))


def _appropriate_thumbnail_file_name(recipe_images):
    """Helper function to locate a file_name for thumbnail. Use first image if it exists, otherwise use placeholder

    :param recipe_images: data from MultipleFileField with images. The first image will be selected if not None"""
    first_filename = recipe_images[0].filename if recipe_images else None
    if not first_filename:
        return 'placeholder.png'
    else:
        try:
            shutil.copy2(os.path.join(app.config['VAR_FOLDER'], 'images', first_filename),
                         os.path.join(app.config['VAR_FOLDER'], 'thumbnails'))
            return first_filename
        except (FileNotFoundError, IOError):
            app.logger.error(
                'Could not open file {} for storing as a thumbnail, using placeholder'.format(first_filename))
            return 'placeholder.png'


@app.route('/create_recipe', methods=['GET', 'POST'])
@flask_login.login_required
def create_recipe():
    """View function to create recipe. Renders an input form for various information and saves it to database"""
    form = CreateRecipeForm()
    if form.validate_on_submit():

        r = Recipe(form.name.data, flask_login.current_user.id, 'placeholder.png', form.description.data,
                   form.minutes.data, form.skill_level.data, form.calories.data, form.body.data)
        try:
            db.session.add(r)
            db.session.commit()     # Needs to be done here so id gets generated for adding the thumbnail
        except exc.IntegrityError:
            db.session.rollback()
            flash('Each of your recipe names must be unique')
            app.logger.warning('Had to rollback because of duplicate recipe names')
            return render_template('create_recipe.html', title='Create Recipe', form=form)

        for recipe_image in form.recipe_images.data:
            recipe_image_name = images.save(recipe_image) if recipe_image else 'placeholder.png'
            i = RecipeImage(recipe_image_name, r.id)
            db.session.add(i)

        # Needs to be back here because the files need to be saved on disk already
        r.thumbnail = _appropriate_thumbnail_file_name(form.recipe_images.data) if not form.thumbnail.data\
            else thumbnails.save(form.thumbnail.data)

        db.session.commit()

        flash('Recipe {} created successfully'.format(r.name))
        return redirect(url_for('recipe', uuid=r.uuid))
    return render_template('create_recipe.html', title='Create Recipe', form=form)


@app.route('/image/<image_set>/<image_name>')
def image(image_set: str, image_name: str):
    """View function to retrieve an image in a given image set"""
    if image_set in upload_sets:
        return send_from_directory(os.path.join(app.config['VAR_FOLDER'], image_set), image_name)
    else:
        app.logger.warning('Invalid upload set for image view function, using placeholder')
        return send_from_directory(os.path.join(app.config['STATIC_FOLDER'], 'images'), 'placeholder.png')


@flask_login.login_required
@app.route('/user/<username>/edit', methods=['GET', 'POST'])
def edit(username: str):
    """Edit the information of the user with the given username. Will redirect to index if user does not exist"""
    target_user = User.query.filter_by(username=username).first()
    if not target_user or target_user != flask_login.current_user:
        flash('You can not access this page')
        app.logger.warning('The wrong user gained access to the edit user profile page')
        return redirect(url_for('index'))

    form = EditUserForm()
    if request.method == 'GET':     # This is so values don't get overwritten on POST
        form.username.default = target_user.username
        form.about_me.default = target_user.about_me
        form.email.default = target_user.email
        form.process()

    elif form.validate_on_submit():
        if form.old_password.data and form.new_password.data:
            if target_user.check_password(form.old_password.data):
                target_user.set_password(form.new_password.data)
            else:
                flash('Your old password was incorrect')
                return render_template('edit_user.html', title='Edit User', form=form, username=target_user.username)

        target_user.username = form.username.data
        target_user.email = form.email.data
        target_user.about_me = form.about_me.data

        db.session.commit()
        return redirect(url_for('user', username=target_user.username))

    return render_template('edit_user.html', title='Edit User', form=form, username=target_user.username)


@flask_login.login_required
@app.route('/recipe/<uuid>/edit', methods=['GET', 'POST'])
def edit_recipe(uuid: str):
    """Edit the information of the recipe with the given uuid. Will redirect to index if recipe does not exist"""
    target_recipe = Recipe.query.filter_by(uuid=uuid).first()
    if not target_recipe or target_recipe.author != flask_login.current_user:
        flash('You can not access this page')
        app.logger.warning('The wrong user gained access to the edit recipe page')
        return redirect(url_for('index'))

    form = EditRecipeForm()
    if request.method == 'GET':     # This is so values don't get overwritten on POST
        form.name.default = target_recipe.name
        form.minutes.default = target_recipe.minutes
        form.skill_level.default = target_recipe.skill_level
        form.calories.default = target_recipe.calories
        form.description.default = target_recipe.description
        form.body.default = target_recipe.body
        form.process()

    elif form.validate_on_submit():
        # Can't be a validator because form doesn't know the exact recipe
        if flask_login.current_user.recipes.filter_by(name=form.name.data).first() is not None \
                and target_recipe.name != form.name.data:
            flash('You can only have one recipe with that name')
            return render_template('edit_recipe.html', title='Edit Recipe', form=form, recipe_name=target_recipe.name)

        target_recipe.name = form.name.data
        target_recipe.minutes = form.minutes.data
        target_recipe.skill_level = form.skill_level.data
        target_recipe.calories = form.calories.data
        target_recipe.description = form.description.data
        target_recipe.body = form.body.data

        db.session.commit()
        flash('Changes saved successfully!')
        return redirect(url_for('recipe', uuid=target_recipe.uuid))

    return render_template('edit_recipe.html', title='Edit Recipe', form=form, recipe_name=target_recipe.name)
