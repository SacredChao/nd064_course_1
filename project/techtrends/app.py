import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from prometheus_client import Counter # Used for counting db connections

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

db_connection_counter = Counter('db_connection_count', 'Total number of database connections') # Counter to track the number of database connections

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connection_counter.inc()  # Increment the counter for each database connection
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

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logger.info(f"No Article with ID {post_id}. Returning 404.")
      return render_template('404.html'), 404
    else:
      logger.info(f"Article \"{post['title']}\" retrieved!")
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logger.info("The 'About Us' page was retrieved.")
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
            logger.info(f"New article with title \"{title}\" created!")
            return redirect(url_for('index'))

    return render_template('create.html')

# Define the healthcheck endpoint
@app.route('/healthz')
def healthz():
    response = {
        "result": "OK - healthy"
    }
    return jsonify(response), 200

# Define the metrics endpoint
@app.route('/metrics')
def metrics():
    # Get the total number of posts in the database
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    connection.close()
    
    # Get the current value of the database connection counter
    db_connection_count = db_connection_counter._value.get()

    # Return the metrics as a JSON response
    response = {
        "db_connection_count": db_connection_count,
        "post_count": post_count
    }
    return jsonify(response), 200

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
