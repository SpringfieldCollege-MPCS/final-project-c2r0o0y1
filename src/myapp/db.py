
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
# class Movie(SQLModel, table=True):  # 
#     id: Optional[int] = Field(default=None, primary_key=True)  # this will autoincrement by default
#     title: str
#     director: str 

class Company(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class User(SQLModel, table=True):  # 
    id: Optional[int] = Field(default=None, primary_key=True) 
    first_name: str
    last_name: str
    email: str
    company_id: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey("company.id", ondelete="CASCADE"))
    )

class Password(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    website: str
    username: str
    salted: str
    created: str
    updated: str
    user_id: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    )


### End Model Definitions ####
##############################


##################################
### Begin Function Definitions ###
def create_company(name:str=None, save=True):
    company = Company(name=name)
    if save:
        with Session(engine) as session:
            session.add(company)
            session.commit()
            session.refresh(company)
    return company

def create_user(first_name:str, last_name:str=None, email:str=None, company_id:Optional[int]=None , save=True):
    user = User(first_name=first_name, last_name=last_name, email=email, company_id=company_id)
    if save:
        with Session(engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
    return user

def create_password(url:str=None, username:str=None, password:str=None, create:str=None, update:str=None, user_id:Optional[int]=None, save=True):
    if create is None:
        create = str(date.today())
    if update is None:
        update = str(date.today())
    password = Password(website=url, username=username, salted=password, created=create, updated=update, user_id=user_id)
    if save:
        with Session(engine) as session:
            session.add(password)
            session.commit()
            session.refresh(password)
    return password


def get_companies()->List[Company]:
    with Session(engine) as session:
        return list(session.query(Company).all())

def get_users(company_id=1) -> List[User]:
    with Session(engine) as session:
        return list(session.query(User).where(User.company_id == company_id))
    
def get_passwords(user_id=1) -> List[Password]:
    with Session(engine) as session:
        return list(session.query(Password).where(Password.user_id == user_id))

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
    # create_movie("A tale of algorithms", "Jeremy Castagno", )
    # create_movie("How I made my first million","Manish Bhusal")
    # create_movie("Shrek", "Justin Manning")
    company_1 = create_company('Zomato')
    company_2 = create_company('Flipkart')
    user_1 = create_user('Chhandak', 'Roy','roychhandak2001@gmail.com',company_id=company_2.id)
    user_2 = create_user('Akriti','Kaur','kaurakriti@gamil.com',company_id=company_1.id)
    create_password("facebook.com",'cRoy','xxxxxxx','23-12-2012','26-12-2015',user_id=user_1.id)
    create_password("github.com",'aKaur','yyyyyyyyy','23-12-2012','26-12-2015',user_id=user_2.id)

def create_db_and_tables():  # 
    """This creates our tables and add some fake data"""
    SQLModel.metadata.drop_all(engine)  # 
    SQLModel.metadata.create_all(engine)  # 
    create_fake_data()

# Create tables and fake data by: python -m todolist.db
if __name__ == "__main__":  # 
    create_db_and_tables()  # 
