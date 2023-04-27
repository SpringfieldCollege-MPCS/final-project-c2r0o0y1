import pathlib
from datetime import date
from typing import Optional, List  # 

from sqlmodel import Field, SQLModel, create_engine, Column, Integer, ForeignKey, Session
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlite3 import Connection as SQLite3Connection

TOP_DIR = pathlib.Path(__file__).parent

# Database connection goes here
sqlite_file_name =  TOP_DIR / 'database' / 'database.db'
sqlite_url = f"sqlite:///{sqlite_file_name}"  # 
engine = create_engine(sqlite_url, echo=False)  # 

# This is needed to enforce foreign key constraints
# You can ignore this

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

###############################
### Start Model Definitions ###
class Movie(SQLModel, table=True):  # 
    id: Optional[int] = Field(default=None, primary_key=True)  # this will autoincrement by default
    title: str
    director: str 


### End Model Definitions ####
##############################


##################################
### Begin Function Definitions ###
def create_movie(title:str, director:str, save=True):
    movie = Movie(title=title, director=director)
    if save:
        with Session(engine) as session:
            session.add(movie)
            session.commit()
            session.refresh(movie)
    return movie

def get_movies() -> List[Movie]:
    with Session(engine) as session:
        return list(session.query(Movie).all())

### End Function Definitions ###
################################

def update_entity(entity):
    with Session(engine) as session:
        session.add(entity)
        session.commit()
        session.refresh(entity)
    return entity

def get_entity(model:SQLModel, id):
    with Session(engine) as session:
        entity = session.get(model, id)
        return entity

def delete_entity(entity):
    with Session(engine) as session:
        session.delete(entity)
        session.commit()



def create_fake_data():
    """Insert your fake data in here"""
    create_movie("A tale of algorithms", "Jeremy Castagno", )
    create_movie("How I made my first million","Manish Bhusal")
    create_movie("Shrek", "Justin Manning")

def create_db_and_tables():  # 
    """This creates our tables and add some fake data"""
    SQLModel.metadata.drop_all(engine)  # 
    SQLModel.metadata.create_all(engine)  # 
    create_fake_data()

# Create tables and fake data by: python -m todolist.db
if __name__ == "__main__":  # 
    create_db_and_tables()  # 
