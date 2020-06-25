"""Collection of webforms for Flask-WTF"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, TextAreaField, \
    MultipleFileField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email, Length, NumberRange
from flask_wtf.file import FileField, FileAllowed
from app.models import User, skill_levels
from app import thumbnails, images
import flask_login


# A form is a class, their members are the fields
class LoginForm(FlaskForm):
    """Webform for logging in. Asks for a username, password and whether to remember the user"""
    # DataRequired() specifies that this must not be empty
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Registration webform. Asks for username, email and password"""
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=1, max=100)])
    about_me = TextAreaField('About me', render_kw={"rows": 6, "cols": 50}, validators=[Length(max=500)])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # Will get called as a validator, because it has the form validate_<attr>
    def validate_username(self, username: StringField):
        """Custom validator to check if the username is already registered"""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email: StringField):
        """Custom validator to check if the email is already registered"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditUserForm(FlaskForm):
    username = StringField('User name', validators=[Length(min=1, max=100)])
    email = StringField('Email', validators=[Email(), Length(min=1, max=100)])
    about_me = TextAreaField('About me', render_kw={"rows": 6, "cols": 50}, validators=[Length(max=500)])
    old_password = PasswordField('Old password', default=None)
    new_password = PasswordField('New password', default=None)
    new_password_confirm = PasswordField('Repeat new password', default=None, validators=[EqualTo('new_password')])
    submit = SubmitField('Save Changes')

    def validate_username(self, username: StringField):
        """Custom validator to check if the username is already registered"""
        user = User.query.filter_by(username=username.data).first()
        if user is not None and username.data != flask_login.current_user.username:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email: StringField):
        """Custom validator to check if the email is already registered"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None and email.data != flask_login.current_user.email:
            raise ValidationError('Please use a different email address.')


class CreateRecipeForm(FlaskForm):
    """Webform for creating a recipe. Asks user for various information"""
    name = StringField('Recipe name', validators=[DataRequired(), Length(min=1, max=100)])
    minutes = IntegerField('Required Minutes', validators=[NumberRange(min=0, max=600)], default=0)
    skill_level = SelectField('Skill level', choices=list(zip(range(len(skill_levels)), skill_levels)), coerce=int)
    calories = IntegerField('Total Calories', validators=[NumberRange(min=0, max=10000)], default=0)
    thumbnail = FileField(validators=[FileAllowed(thumbnails, u'Image only!')])
    description = TextAreaField('Short description', render_kw={"rows": 6, "cols": 50},
                                validators=[Length(max=500)])
    recipe_images = MultipleFileField('Some images of your recipe', validators=[FileAllowed(images, u'Image only!')])
    body = TextAreaField('How do you prepare this recipe?', render_kw={"rows": 20, "cols": 200},
                         validators=[Length(max=10000)])
    submit = SubmitField('Create Recipe')

    def validate_name(self, name: StringField):
        """Custom validator to check whether the new recipe name is unique for this user"""
        if flask_login.current_user.recipes.filter_by(name=name.data).first() is not None:
            raise ValidationError('You can only have one recipe with that name')

    def validate_thumbnail(self, thumbnail: FileField):
        """Custom validator to check whether a placeholder image was submitted"""
        if thumbnail.data is not None:
            if thumbnail.data.filename == 'placeholder.png':
                raise ValidationError('File name must not be "placeholder.png"')

    def validate_recipe_images(self, recipe_images: MultipleFileField):
        """Custom validator to check whether too many images or a placeholder image was submitted"""
        if recipe_images.data:
            for recipe_image in recipe_images.data:
                if recipe_image.filename == 'placeholder.png':
                    raise ValidationError('File name must not be "placeholder.png"')

            if len(recipe_images.data) > 25:
                raise ValidationError('Too many filed. Max. 25')


class EditRecipeForm(FlaskForm):
    """Webform for editing a recipe. Asks user for various information"""
    name = StringField('Recipe name', validators=[DataRequired(), Length(min=1, max=100)])
    minutes = IntegerField('Required Minutes', validators=[NumberRange(min=0, max=600)], default=0)
    skill_level = SelectField('Skill level', choices=list(zip(range(len(skill_levels)), skill_levels)), coerce=int)
    calories = IntegerField('Total Calories', validators=[NumberRange(min=0, max=10000)], default=0)
    description = TextAreaField('Short description', render_kw={"rows": 6, "cols": 50},
                                validators=[Length(max=500)])
    body = TextAreaField('How do you prepare this recipe?', render_kw={"rows": 20, "cols": 200},
                         validators=[Length(max=10000)])
    submit = SubmitField('Create Recipe')


class AddTagForm(FlaskForm):
    tag_name = StringField('Tag name', validators=[Length(min=1, max=100)])
    submit = SubmitField('Add Tag')


class SearchForm(FlaskForm):
    term = StringField('Term', validators=[Length(min=1, max=100)])
    kind = SelectField('Type', choices=[('recipe', 'Recipe'), ('tag', 'Tag')], default='recipe')
    go = SubmitField('Search')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')
