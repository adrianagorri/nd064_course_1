import sqlite3
import os
import sys
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

#Initialize variables
db_connection_count = 0
post_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    #Define db_connection_count
    global db_connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connection_count = db_connection_count + 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define healthz endpoint
@app.route('/healthz')
def healthz():
    response = app.response_class(
            response = json.dumps({"result":"OK - healthy"}),
            status = 200,
            mimetype = 'application/json'
    )
    app.logger.info('healthz endpoint successfull')
    return response

# Define metrics endpoint
@app.route('/metrics')
def metrics():
    #Define post_count
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    post_count = len(posts)
    connection.close()

    response = app.response_class(
            response = json.dumps({"status":"success","code":0,"data":{"db_connection_count": db_connection_count, "post_count": post_count}}),
            status = 200,
            mimetype = 'application/json'
    )
    app.logger.info('metrics endpoint successfull')
    return response

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    app.logger.info('Access main page successfull')
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.error('Access 404 page because non-existing articles')
      return render_template('404.html'), 404
    else:
      app.logger.info('Access an article: ' + post['title'])
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('Access About Us page successfull')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            app.logger.info('A new article is created: ' + title)
            return redirect(url_for('index'))
    
    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
    #Record the events to STDOUT & STDERR and Python logs at the DEBUG level
    #Define and set logging output
    log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
    log_level = (
	    getattr(logging, log_level)
	    if log_level in ["CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING"]
	    else logging.DEBUG
        )
    #Define and set stderr stdout handlers
    stderr_handler = logging.StreamHandler(sys.stderr)
    stdout_handler = logging.StreamHandler(sys.stdout)
    std_handlers = [stderr_handler, stdout_handler]
    # Define and set the format output of logs
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=log_level, handlers=std_handlers)

    app.run(host='0.0.0.0', port='3111')
