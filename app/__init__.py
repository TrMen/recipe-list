"""Startup file. Initializes application"""
import os
import logging
import shutil
from logging.handlers import RotatingFileHandler

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)
csrf = CSRFProtect(app)

# Error handling
if not os.path.exists('logs'):
    os.mkdir('logs')

if app.config['LOG_TO_STDOUT']: # Log to STDOUT for Heroku apps
    # Make sure to do heroku config:set LOG_TO_STDOUT=1 in the project root directory to log to files on Heroku
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    app.logger.addHandler(stream_handler)
else:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/recipe_list.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))

    file_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    app.logger.addHandler(file_handler)

app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
app.logger.info('Recipe List startup')


# For image uploads with Flask-Upload. Do not use that garbage module again, it's full of bugs
# Apparently we need to provide a lambda here because the config variable of app isn't getting recognized...
thumbnails = UploadSet('thumbnails', IMAGES,
                       default_dest=lambda p_app: os.path.join(p_app.config.get('VAR_FOLDER'), 'thumbnails'))
images = UploadSet('images', IMAGES,
                   default_dest=lambda p_app: os.path.join(p_app.config.get('VAR_FOLDER'), 'images'))

# Set up image storage locations and placeholders
upload_sets = ('thumbnails', 'images')
for u_set in upload_sets:
    path = os.path.join(app.config['VAR_FOLDER'], u_set)
    if not os.path.isdir(path):
        app.logger.info('Creating folder and placeholder for upload_set {}'.format(u_set))
        os.mkdir(path)
    try:
        shutil.copy2(os.path.join(app.config['STATIC_FOLDER'], 'images', 'placeholder.png'), path)
    except FileNotFoundError:
        with open(os.path.join(path, 'placeholder.png'), 'a') as f:
            app.logger.warning('Could not find static placeholder image, using empty file')

configure_uploads(app, (thumbnails, images))
patch_request_class(app)  # set maximum file size, default is 16MB

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
# Specifies which view function handles login so flask_login can automatically redirect to that URL
login.login_view = 'login'

# Import at the bottom to work around circular imports. route module needs to import app as well
from app import routes, models, errors
