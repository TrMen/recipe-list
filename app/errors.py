from flask import render_template, request
from app import app, db


@app.errorhandler(404)
def not_found_error(error):
    app.logger.warning('A user reached a 404 error')
    return render_template('404.html', referer=request.args.get('Referer')), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error('A user reached a 500 error')
    return render_template('500.html', referer=request.args.get('Referer')), 500
