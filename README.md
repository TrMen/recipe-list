# recipe-list
A Website for cooking recipes using a Flask backend.

**Available online at:** https://recipe-listaw.herokuapp.com/index  
The Heroku deployment is currently incomplete. You can create an account, and create/view recipes as usual. 
However, image uploads will not be persistent over multiple days. 
Uploading many images may also result in a timeout, as image uploads are currently not asynchronous. I plan to fix this soon by using Amazon S3 for image storage.

**Local Setup:** 
* Supply environment variables to customize app execution (Optional).   
This can be done through a `.env` file, or through manual setting with `export <ENV_VAR>=<value>` (set on Windows).  
It is recommended to supply at least `SECRET_KEY` because a hard-coded default will be used otherwise.  
 A database should also be specified through `DATABASE_URL`, otherwise an SQLite database will be created  
 * Create a database with the correct schema using `flask db upgrade`
 * Set `FLASK_DEBUG=development` if you want to run the application in debug mode (Optional). This cannot be done in `.env` 
 * Run with `flask run`
 * View at localhost:5000
