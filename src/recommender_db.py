import os
import sys
import logging.config
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String
import pandas as pd
import argparse

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


def create_db(RDS_FLAG):
    """Creates a database with the data models inherited from `Base` (Recommendation).
    Args:
        engine_string (`str`, default None): String defining SQLAlchemy connection URI in the form of
            `dialect+driver://username:password@host:port/database`.
    Returns:
        None or Exception error if there's invalid value
    """
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
    logger = logging.getLogger('create_rds_DB')

    # connect to rds if true, otherwise connect to local database
    if RDS_FLAG is True:
        engine_string = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, database)
    else:
        engine_string = 'sqlite:////data/Recommendation.db'

    try:
        engine = sql.create_engine(engine_string)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        add_rows()
        logger.info("Database created successfully with all rows added")
    except Exception as e:
        logger.error(e)
        sys.exit(1)

def add_rows():
# def add_rows(session, item_name, rec1, rec2, rec3, rec4, rec5):
    """Insert data into a local RDS instance
    Args:
        None
    Returns:
        None
    """
    # import data from csv
    df = pd.read_csv('data/external/recommendations.csv')
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create defined tables in database")
    parser.add_argument("--truncate", "-t", default=False, action="store_true",
                        help="If given, delete current records from food table before create_all "
                             "so that table can be recreated without unique id issues ")
    args = parser.parse_args()

    # If "truncate" is given as an argument (i.e. python models.py --truncate), then empty the recommendation table)
    if args.truncate:
        engine = sql.create_engine(engine_string)
        Session = sessionmaker(bind=engine)
        session = Session()
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
        # add rows to create database
        engine = sql.create_engine(engine_string)
        Session = sessionmaker(bind=engine)
        session = Session()
        add_rows()
        # add_rows(session, 'a', '1', '2', '3', '4', '5')

        logger.info("Database created successfully with all rows added")
    except Exception as e:
        logger.error(e)
    finally:
        session.close()
