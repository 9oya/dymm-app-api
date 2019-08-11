from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from dymm_api import config

engine = create_engine(config.DevelopmentConfig.DATABASE_URI,
                       pool_size=20, max_overflow=0)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import dymm_api.models
    Base.metadata.create_all(bind=engine)
