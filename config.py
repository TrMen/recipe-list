"""Configurations for flask application"""
import os
import logging
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.dirname(__file__)
load_dotenv(os.path.join(basedir, '.env'))  # Load environment variables from a ".env" file

_defaults = {
    'SECRET_KEY': 'Super_secret_key_here',
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + os.path.join(basedir, 'app.db'),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'REMEMBER_COOKIE_DURATION': timedelta(minutes=120),
    'STATIC_FOLDER': os.path.join(basedir, 'app', 'static'),
    'VAR_FOLDER': os.path.join(basedir, 'app', 'var'),
    'SEND_FILE_MAX_AGE_DEFAULT': 0,
    'MAX_SEARCH_RESULTS': 50,
    'LOG_TO_STDOUT': False
}


def _warn_default(variable_name: str):
    """Get default value for variable name with logging a warning"""
    logging.warning('No {} supplied in environment variable, using default'.format(variable_name))
    return _defaults[variable_name]


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or _warn_default('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or _warn_default('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = _defaults['SQLALCHEMY_TRACK_MODIFICATIONS']
    REMEMBER_COOKIE_DURATION = os.environ.get('REMEMBER_COOKIE_DURATION') or _warn_default('REMEMBER_COOKIE_DURATION')
    STATIC_FOLDER = os.environ.get('STATIC_FOLDER') or _defaults['STATIC_FOLDER']
    VAR_FOLDER = os.environ.get('VAR_FOLDER') or _defaults['VAR_FOLDER']
    SEND_FILE_MAX_AGE_DEFAULT = os.environ.get('SEND_FILE_MAX_AGE_DEFAULT') or _warn_default(
        'SEND_FILE_MAX_AGE_DEFAULT')
    MAX_SEARCH_RESULTS = os.environ.get('MAX_SEARCH_RESULTS') or _defaults['MAX_SEARCH_RESULTS']
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT') or _defaults['LOG_TO_STDOUT']     # Required for heroku logging
