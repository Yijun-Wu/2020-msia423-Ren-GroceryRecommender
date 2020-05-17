import os
import sys
import logging
import logging.config

import sqlalchemy as sql
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# sys.path.append('./config')
import config
from helpers import create_connection, get_session, engine_string_generator
import argparse

# RDS/SQL connection set up
conn_type = "mysql+pymysql"
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
host = os.environ.get("MYSQL_HOST")
port = os.environ.get("MYSQL_PORT")
database = os.environ.get("DATABASE_NAME")

# logging
logging_config = 'config/logging/local.conf'
logging.config.fileConfig(logging_config)
logger = logging.getLogger('msia423_db')

Base = declarative_base()


class Food(Base):
    """
    Create a data model for the database to be set up for food data
    """
    __tablename__ = 'food'
    id = Column(Integer, primary_key=True)
    product_name = Column(String(100), unique=False, nullable=False)
    portion = Column(Integer, unique=False, nullable=False)
    portion_amount = Column(Float(), unique=False, nullable=False)
    portion_name = Column(String(100), unique=False, nullable=False)
    factor = Column(Float(), unique=False, nullable=False)
    increment = Column(Float(), unique=False, nullable=False)
    multiplier = Column(Float(), unique=False, nullable=False)
    grains = Column(Float(), unique=False, nullable=False)
    whole_grains = Column(Float(), unique=False, nullable=False)
    vegetables = Column(Float(), unique=False, nullable=False)
    orange_vegetables = Column(Float(), unique=False, nullable=False)
    drkgreen_vegetables = Column(Float(), unique=False, nullable=False)
    starchy_vegetables = Column(Float(), unique=False, nullable=False)
    other_vegetables = Column(Float(), unique=False, nullable=False)
    fruits = Column(Float(), unique=False, nullable=False)
    milk = Column(Float(), unique=False, nullable=False)
    meats = Column(Float(), unique=False, nullable=False)
    soy = Column(Float(), unique=False, nullable=False)
    drybeans_peas = Column(Float(), unique=False, nullable=False)
    oils = Column(Float(), unique=False, nullable=False)
    solid_fats = Column(Float(), unique=False, nullable=False)
    added_sugars = Column(Float(), unique=False, nullable=False)
    alcohol = Column(Float(), unique=False, nullable=False)
    calories = Column(Float(), unique=False, nullable=False)
    saturated_fats = Column(Float(), unique=False, nullable=False)

    def __repr__(self):
        food_repr = "<Food(id='%d', product_name='%s', portion='%d', portion_amount='%f', portion_name='%s', factor='%f', increment='%f', multiplier='%f', grains='%f', whole_grains='%f', vegetables='%f', orange_vegetables='%f', drkgreen_vegetables='%f', starchy_vegetables='%f', other_vegetables='%f', fruits='%f', milk='%f', meats='%f', soy='%f', drybeans_peas='%f', oils='%f', solid_fats='%f', added_sugars='%f', alcohol='%f', calories='%f', saturated_fats='%f')>"
        return food_fact % (
        self.id, self.product_name, self.portion, self.portion_amount, self.portion_name, self.factor, self.increment,
        self.multiplier, self.grains, self.whole_grains, self.vegetables, self.orange_vegetables,
        self.drkgreen_vegetables, self.starchy_vegetables, self.other_vegetables, self.fruits, self.milk, self.meats,
        self.soy, self.drybeans_peas, self.solid_fats, self.added_sugars, self.alcohol, self.calories,
        self.saturated_fats)


def _truncate_food(session):
    """Deletes foods if rerunning and run into unique key error."""
    session.execute('''DELETE FROM food''')


def create_db(engine_string):
    """Creates a database with the data models inherited from `Base` (food).
    Args:
        engine_string (`str`, default None): String defining SQLAlchemy connection URI in the form of
            `dialect+driver://username:password@host:port/database`.
    Returns:
        None
    """
    try:
        engine = sql.create_engine(engine_string)
        Base.metadata.create_all(engine)
        logger.info("Database: msia423_db.db created successfully")
    except Exception as e:
        logger.error(e)
        sys.exit(1)


if __name__ == "__main__":
    engine_string = engine_string_generator(config.DB_FLAG, host, user, password, port, database, conn_type)
    parser = argparse.ArgumentParser(description="Create defined tables in database")
    parser.add_argument("--truncate", "-t", default=False, action="store_true",
                        help="If given, delete current records from food table before create_all "
                             "so that table can be recreated without unique id issues ")
    args = parser.parse_args()

    # If "truncate" is given as an argument (i.e. python models.py --truncate), then empty the food table)
    if args.truncate:
        session = get_session(engine_string=config.SQLALCHEMY_DATABASE_URI)
        try:
            logger.info("Attempting to truncate food table.")
            _truncate_food(session)
            session.commit()
            logger.info("food truncated.")
        except Exception as e:
            logger.error("Error occurred while attempting to truncate food table.")
            logger.error(e)
        finally:
            session.close()

    create_db(engine_string)