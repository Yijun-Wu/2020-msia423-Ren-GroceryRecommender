import os
import sys
import logging.config
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String
import pandas as pd
import argparse
import yaml

logger = logging.getLogger(__name__)
Base = declarative_base()


class Recommendation(Base):
    """
    Create a data model for the database to be set up for association rules data

    A Recommendation object will include an item name and its top 5 recommendations
    """
    __tablename__ = 'Recommendation'

    item_name = Column(String(100), primary_key = True)
    recommendation1 = Column(String(100), unique = False, nullable = False)
    recommendation2 = Column(String(100), unique = False, nullable = False)
    recommendation3 = Column(String(100), unique = False, nullable = False)
    recommendation4 = Column(String(100), unique = False, nullable = False)
    recommendation5 = Column(String(100), unique = False, nullable = False)

    def __repr__(self):
        rec_repr = "<Recommendation(item_name='%s', recommendation1='%s', recommendation2='%s', recommendation3='%s', recommendation4='%s', recommendation5='%s')>"
        return rec_repr % (self.item_name, self.recommendation1, self.recommendation2, self.recommendation3, self.recommendation4, self.recommendation5)


def _truncate_rec(session):
    """Deletes recommendations if rerunning and run into unique key error."""
    session.execute('''DELETE FROM Recommendation''')
    session.execute('''DROP TABLE Recommendation''')


def create_engine_string(SQLALCHEMY_DATABASE_URI, RDS_FLAG):
    """ Creates the path to the RDS or local SQLITE database
        Inputs:
            SQLALCHEMY_DATABASE_URI: database location path
            RDS_FLAG: whether user chooses to create RDS database or not
        Returns:
            engine string
    """
    if (SQLALCHEMY_DATABASE_URI is None) or (SQLALCHEMY_DATABASE_URI is ""):
        # RDS connection set up
        conn_type = "mysql+pymysql"
        user = os.environ.get("MYSQL_USER")
        password = os.environ.get("MYSQL_PASSWORD")
        host = os.environ.get("MYSQL_HOST")
        port = os.environ.get("MYSQL_PORT")
        database = os.environ.get("DATABASE_NAME")
        if RDS_FLAG is True:
            engine_string = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, database)
        else:
            engine_string = 'sqlite:////data/Recommendation.db'
    else:
        engine_string = os.environ.get("SQLALCHEMY_DATABASE_URI")

    return engine_string



def create_db(engine_string):
    """Creates a database with the data models inherited from `Base` (Recommendation).
    Args:
        engine_string (`str`, default None): String defining SQLAlchemy connection URI in the form of
            `dialect+driver://username:password@host:port/database`.
    Returns:
        None or Exception error if there's invalid value
    """
    try:
        engine = sql.create_engine(engine_string)
        Base.metadata.create_all(engine)
        logger.info("Database created.")
    except Exception as e:
        logger.error("Please enter correct credentials to access database.")
        sys.exit(1)


def get_session(engine_string):
    """Get session from SQLAlchemy connection string
    Args:
        engine_string: SQLAlchemy connection string
    Returns:
        SQLAlchemy session
    """
    engine = sql.create_engine(engine_string)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def add_rows(input_path, session):
    """Insert data records into created RDS database
    Args:
        input_path: local recommendation table to be written into database
        session: get session from SQLAlchemy connection string
    Returns:
        None
    """
    # import data from csv
    logger.info("read in data")
    df = pd.read_csv(input_path)
    df = df.drop(['Unnamed: 0'], axis=1)

    rows = []

    for i in range(len(df)):
        each_row = Recommendation(item_name=str(df['item_name'][i]),
                             recommendation1=str(df['recommendation1'][i]),
                             recommendation2=str(df['recommendation2'][i]),
                             recommendation3=str(df['recommendation3'][i]),
                             recommendation4=str(df['recommendation4'][i]),
                             recommendation5=str(df['recommendation5'][i]))

        rows.append(each_row)
    session.add_all(rows)
    session.commit()
    logger.info("Session commit complete")


def create_rec_db(args):
    """ Create database in RDS or local with recommendation table as input records
    Args:
        args that contain input file path, truncate flag, rds flag
    Returns:
        None
    """

    # Get SQLALCHEMY_DATABASE_URI from environment and generate engine string
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    engine_string = create_engine_string(SQLALCHEMY_DATABASE_URI, args.rds)

    # If "truncate" is given as an argument (i.e. python models.py --truncate), then empty the recommendation table)
    if args.truncate is True:
        session = get_session(engine_string)
        try:
            logger.info("Attempting to truncate Recommendation table.")
            _truncate_rec(session)
            session.commit()
            logger.info("Recommendation truncated.")
        except Exception as e:
            logger.error("Error occurred while attempting to truncate Recommendation table.")
            logger.error(e)
        finally:
            session.close()

    # create database
    create_db(engine_string)
    try:
        # write records into table
        session = get_session(engine_string)
        add_rows(args.input, session)
        logger.info("Database created successfully with all rows added")
    except Exception as e:
        logger.error(e)
    finally:
        session.close()
