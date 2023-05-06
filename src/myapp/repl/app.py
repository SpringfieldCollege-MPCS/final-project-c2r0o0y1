
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum, auto
from prompt_toolkit import PromptSession
from sqlmodel import SQLModel

from ..db import Company,User,Password, get_companies, get_users,get_passwords,delete_entity, get_entity, create_company,create_user,create_password
from .console import console
from .helper import show_table_and_ask_for_command, Command, EntityNotFound, get_item

class Step(Enum):
    show_companies = auto()
    show_users = auto()
    show_passwords = auto()

@dataclass
class AppState():
    app_step:Step = Step.show_companies
    all_company_list: List[Company] = field(default_factory=list)
    all_user_list: List[User] = field(default_factory=list)
    all_password_list: List[Password] = field(default_factory=list)
    active_company: Optional[Company] = None
    active_user: Optional[User] = None

    def __init__(self):
        self.refresh_companies()
    
    def refresh_companies(self):
        self.all_company_list = get_companies()
    
    def refresh_users(self):
        # self.all_user_list = get_users()
        if self.active_company is not None:
            self.all_user_list = get_users(self.active_company.id)
        else:
            self.all_user_list = []

    def refresh_passwords(self):
        # self.all_password_list = get_passwords()
        if self.active_user is not None:
            self.all_password_list = get_passwords(self.active_user.id)
        else:
            self.all_password_list = []
    
    def set_active_company(self, id:int):
        self.active_company = get_item(id, self.all_company_list, model=Company)
        self.refresh_users()

    def set_active_user(self, id:int):
        self.active_user = get_item(id, self.all_user_list, model=User)
        self.refresh_passwords()

def execute_command(session:PromptSession, state:AppState, state_key:str, model:SQLModel):
    
    response = show_table_and_ask_for_command(session, state, state_key, model)
    if len(response.split(' ')) < 2:
        # user wants to quit
        if response == Command.quit:
            return False # return false to make the program exit
        # user just entered a bad command
        # warn them and then loop again
        console.print("[danger]You must type in a command and a value: Eg. 'select 1'")
        return True
    if ' ' in response:
        command, value = response.split(' ', 1)
    else:
        command = response
        value = ""
    command = command.lower()
    if command == Command.select:
        if model == Company:
            state.set_active_company(value)
            state.app_step = Step.show_users
        elif model == User:
            state.set_active_user(value)
            state.app_step = Step.show_passwords

    elif command == Command.remove:
        if model == Company:
            console.print("[warning]Not supported currently")
        elif model == User:
            if state.active_user is not None and state.active_user.id == int(value):
                state.active_user = None
                state.app_step = Step.show_users
            delete_entity(get_entity(User, int(value)))
        else:
            delete_entity(get_entity(Password, int(value)))
    elif command == Command.quit:
        return False
    else:
        console.print("[danger]Unknown command")
    return True

def cli():
    state = AppState() # contains our app sate
    session = PromptSession() # allows us to prompt the user

    console.print("You can exit the program by pressing [success]CTRL+D[/success] at anytime")
    console.print("You must type in a command and a value: Eg. 'select _', 'remove _'")
    console.print()
    loop = True
    while loop:
        try:
            if state.app_step == Step.show_companies:
                loop = execute_command(session, state,'all_company_list', model=Company)
            elif state.app_step == Step.show_users:
                loop = execute_command(session, state, 'all_user_list', model=User)
            elif state.app_step == Step.show_passwords:
                loop = execute_command(session, state, 'all_password_list', model=Password)
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