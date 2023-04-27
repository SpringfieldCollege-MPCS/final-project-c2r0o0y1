
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum, auto
from prompt_toolkit import PromptSession
from sqlmodel import SQLModel

from ..db import Movie, get_movies, delete_entity, get_entity, create_movie
from .console import console
from .helper import show_table_and_ask_for_command, Command, EntityNotFound

class Step(Enum):
    show_movies = auto()

@dataclass
class AppState():
    app_step:Step = Step.show_movies
    movie_list = []
    def __init__(self):
        self.refresh_movies()
    
    def refresh_movies(self):
        self.movie_list = get_movies()

def execute_command(session:PromptSession, state:AppState, state_key:str, model:SQLModel):
    
    response = show_table_and_ask_for_command(session, state, state_key, model)
    if ' ' in response:
        command, value = response.split(' ', 1)
    else:
        command = response
        value = ""
    command = command.lower()
    if command == Command.remove:
        if model == Movie:
            delete_entity(get_entity(Movie, int(value)))
            state.refresh_movies()
    elif command == Command.add:
        if model == Movie:
            title = session.prompt("Title: ")
            director = session.prompt("Director: ")
            create_movie(title=title, director=director)
            state.refresh_movies()
        else:
            console.print("[danger]Not supported")
    elif command == Command.quit:
        return False
    else:
        console.print("[danger]Unknown command")
    return True

def cli():
    state = AppState() # contains our app sate
    session = PromptSession() # allows us to prompt the user

    console.print("You can exit the program by pressing [success]CTRL+D[/success] at anytime")
    console.print("You must type in a command and a value: Eg. 'select 1', 'complete 1'")
    console.print()
    loop = True
    while loop:
        try:
            if state.app_step == Step.show_movies:
                loop = execute_command(session, state, 'movie_list', model=Movie)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except EntityNotFound as e:
            console.print(f"{e}\n")
        except Exception:
            console.print_exception()
            
    console.print('GoodBye!')


if __name__ == '__main__':
    cli()