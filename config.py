"""Configurations for flask application"""
import os
import logging
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

_defaults = {
    'SECRET_KEY': 'Super_secret_key_here',
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + os.path.join(basedir, 'app.db'),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'REMEMBER_COOKIE_DURATION': timedelta(minutes=120),
    'STATIC_FOLDER': os.path.join(basedir, 'app', 'static'),
    'VAR_FOLDER': os.path.join(basedir, 'app', 'var'),
    'SEND_FILE_MAX_AGE_DEFAULT': 0
}


def _default(variable_name: str):
    """Get default value for variable name with logging a warning"""
    logging.warning('No {} supplied in environment variable, using default'.format(variable_name))
    return _defaults[variable_name]


class Config(object):
    SECRET_KEY = os.environ.get('RECIPES_SECRET_KEY') or _default('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('RECIPES_DATABASE_URL') or _default('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = _defaults['SQLALCHEMY_TRACK_MODIFICATIONS']
    REMEMBER_COOKIE_DURATION = _defaults['REMEMBER_COOKIE_DURATION']
    STATIC_FOLDER = _defaults['STATIC_FOLDER']
    VAR_FOLDER = _defaults['VAR_FOLDER']
    SEND_FILE_MAX_AGE_DEFAULT = _default('SEND_FILE_MAX_AGE_DEFAULT')
    MAX_SEARCH_RESULTS = 50
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT') # Required for heroku logging
