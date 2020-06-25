"""Collection of models for flask-sqlalchemy ORM"""

from app import db, login
from datetime import datetime
import werkzeug.security
import flask_login
from typing import Optional
import uuid as uuid_lib
from sqlalchemy.orm import validates


@login.user_loader
def user_loader(user_id: str):
    """Get user from database by id for flask_login"""
    return User.query.get(int(user_id))


# ORM models are just classes with the db columns as member variables
class User(db.Model, flask_login.UserMixin):
    """User database model class"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(300), default='')
    # This is not an actual field but a high level view of all connected recipes.
    # Creates a recipe.author and a user.recipes
    recipes = db.relationship('Recipe', backref='author', lazy='dynamic')

    def __init__(self, username: str, email: str, password: Optional[str] = None, about_me: Optional[str] = ''):
        """ Create a user with a username and email address

        :param username: name of the user
        :param email: email of the user
        :param password: password of the user. Add with set_password if not set in init"""
        self.username = username
        self.email = email
        if password is not None:
            self.set_password(password)
        self.about_me = '' if about_me is None else about_me

    def set_password(self, password):
        """Set user's password hash to a hash of password"""
        self.password_hash = werkzeug.security.generate_password_hash(password)

    def check_password(self, password):
        """check whether the stored password hash is equal to the hash of password"""
        return werkzeug.security.check_password_hash(self.password_hash, password)

    @validates('about_me')
    def validate_about_me(self, key, about_me):
        if about_me and len(about_me) > 500:
            about_me = about_me[0:499]
        return about_me

    def __repr__(self):     # Tells python how to print objects of this class
        return '<User {}>'.format(self.username)


skill_levels = ['beginner', 'intermediate', 'advanced', 'pro']

# An association table for many-to-many relationships
recipe_tag = db.Table('recipe_tag',
                      db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
                      db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')))


class Recipe(db.Model):
    """Recipe database model class. Params: body: str, timestamp: Optional[str], user_id: int"""
    __tablename__ = 'recipe'
    __table_args__ = (db.UniqueConstraint('name', 'user_id'), )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    minutes = db.Column(db.Integer)
    skill_level = db.Column(db.String(10))
    calories = db.Column(db.Integer)
    thumbnail = db.Column(db.String(30))
    description = db.Column(db.String(100))
    body = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))   # user is not capital because it's that way in the db
    uuid = db.Column(db.String(36))
    images = db.relationship('RecipeImage', backref='recipe', lazy='dynamic')
    # Defines a many-to-many relationship. secondary is the association table used
    tags = db.relationship('Tag', secondary=recipe_tag, backref=db.backref('recipes', lazy='dynamic'), lazy='dynamic')

    def __init__(self, name: str, author_id: str, thumbnail: str = 'static/images/placeholder.png',
                 description: str = '', minutes: int = 10,
                 skill_level: str = 'beginner', calories: int = 0, body: str = ''):
        """Create a Recipe with the supplied name, body, author

        :param name: Recipe name
        :param author_id: database id of author
        :param thumbnail: name of file to add as thumbnail
        :param description: Short description of what the recipe is about for thumbnail display
        :param minutes: How many minutes the recipe takes to complete
        :param skill_level: 'beginner', 'intermediate', 'advanced', 'pro'
        :param calories: How many total calories the recipe contains
        :param body: Long-form notes for preparing the meal. The steps of the recipe are separate"""
        self.name = name
        self.user_id = author_id
        self.description = '' if description is None else description
        self.body = '' if body is None else body
        self.minutes = 0 if minutes is None else minutes
        self.thumbnail = 'static/images/placeholder.png' if thumbnail is None else thumbnail
        self.calories = 0 if calories is None else calories

        if skill_level in skill_levels:
            self.skill_level = skill_level
        else:
            self.skill_level = skill_levels[0]
        while True:
            provisional_uuid = str(uuid_lib.uuid4())
            if Recipe.query.filter_by(uuid=provisional_uuid).first() is None:
                self.uuid = provisional_uuid
                break

    def has_tag(self, tag):
        return self.tags.filter(Tag.id == tag.id).count() > 0

    def add_tag(self, tag):
        if not self.has_tag(tag):
            self.tags.append(tag)

    def remove_tag(self, tag):
        if self.has_tag(tag):
            self.tags.remove(tag)

    def __repr__(self):
        return '<Recipe name: {}, description: {}>'.format(self.name, self.description)


class RecipeImage(db.Model):
    """Images for recipe. Each recipe may have multiple images"""
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))

    def __init__(self, file_name: str, recipe_id: str):
        """Create an image for a recipe. Each recipe may have multiple images

        :param file_name: Name of file where the image is saved (just file name, no path)
        :param recipe_id: Database id of recipe that the image belongs to"""
        self.recipe_id = recipe_id
        self.file_name = 'placeholder.png' if len(file_name) > 150 else file_name

    def __repr__(self):
        recipe_name = self.recipe.name if self.recipe is not None else 'No Recipe'
        return '<Image name: {}, Recipe name: {}>'.format(self.file_name, recipe_name)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)

    def __init__(self, name: str, recipe: Optional[Recipe] = None):
        """ Create a tag with a name

        :param name: Name of the tag
        """
        self.name = name

    def __repr__(self):
        return '<Tag name: {} ID: {}>'.format(self.name, self.id)

