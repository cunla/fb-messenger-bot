import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import logging

# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite')
logging.info(f'Using for db: {DATABASE_URL}')
engine = create_engine(DATABASE_URL)
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)

Base = declarative_base()
