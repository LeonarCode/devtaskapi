from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import settings

Base = declarative_base()

engine = create_engine(settings.DB_CONNECTION, pool_pre_ping=True)

LocalSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    session = LocalSession()
    try:
        yield session
    finally:
        session.close()