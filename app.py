import traceback
from flask import render_template, request, redirect, url_for
import logging.config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
from sqlalchemy.util import OrderedSet
from src.recommender_db import Recommendation


# Initialize the Flask application
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug('Test log')

# Initialize the database
db = SQLAlchemy(app)
basket = OrderedSet()

# Connect to RDS or local database and query all data
logger.info('Connecting to '+ app.config['SQLALCHEMY_DATABASE_URI'])
recommendations = db.session.query(Recommendation).all()

# Generate list of items in database so that we can fetch corresponding recommendations later
item_ls = []
for i in range(len(recommendations)):
    # Make sure recommendations show up no matter user input's in lower or upper case
    item_ls.append(recommendations[i].item_name.lower())


@app.route('/')
def index():
    """  Create view into index page that collects user input data

    Returns: rendered html template

    """
    logger.debug("Index page accessed")
    return render_template('index.html', basket = basket)


@app.route('/add_thing', methods=['GET', 'POST'])
def add_thing():
    """ Display top 5 recommendations with a new item input, no matter from textbox or checkbox.

    If an item only has less than 5 recommendations, only display those available;

    If an item is not found in database or there's invalid input, return error page.

    Returns: rendered html template.

    """
    try:
        rec5 = OrderedSet()
        # Store user input data
        fetch_items = request.form['items'].lower()
        # Take the newly added item, search through list, and fetch corresponding recommendations
        # Make sure recommendations show up no matter user input's in lower or upper case by matching with item list
        idx = item_ls.index(fetch_items)
        basket.add(fetch_items.title())
        rec5 = [recommendations[idx].recommendation1, recommendations[idx].recommendation2, recommendations[idx].recommendation3, recommendations[idx].recommendation4, recommendations[idx].recommendation5]
        # If an item only has less than 5 recommendations, only display those available
        for i in range(len(rec5)):
            if rec5[i] == "nan":
                rec5 = rec5[:i]
                return render_template('index.html', basket = basket, recommendations = rec5)
        # if it does have top 5 recommendations, display them all
        return render_template('index.html', basket = basket, recommendations = rec5)
    except:
        # If an item is not found in database or there's invalid input, return error page
        logger.warning("Not able to display recommendations, error page returned")
        return render_template('error.html')


@app.route('/reset-basket/', methods=['POST'])
def reset_basket():
    """ Empty the basket whenever user hit reset button, so that they can create a new grocery list.

        The basket and recommendations keep updating until reset.

        Returns: rendered html template.
    """
    global basket
    basket = OrderedSet()
    return redirect('/')


if __name__ == '__main__':
    # Running the app
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])