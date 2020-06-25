"""This file defines the flask application instance"""
from app import app, db
from app.models import User, Recipe, RecipeImage, Tag


@app.shell_context_processor
def make_shell_context():
    """flask shell (the terminal command) registers the contents returned by this function when run"""
    return {'db': db, 'User': User, 'Recipe': Recipe, 'RecipeImage': RecipeImage, 'Tag': Tag}
