
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Input, Button, Static
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive
from typing import List
from textual.widgets import (
    Button,
    Header,
    Footer,
    Static,
    Switch,
    Label,
    ListItem,
    ListView,
    Input,
)
from ..db import Company,User,Password, get_companies, get_users,get_passwords,delete_entity, get_entity, create_company,create_user,create_password
from .helper import get_ordered_values

class Password(Static):
    """A Password Widget. Holds a task text, date, completed, and remove button"""

    def __init__(self, password:Password) -> None:
        super().__init__()
        self.my_password: Password = password

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Label(self.my_password.salted, classes="")
        yield Label(self.my_task.date_created, classes="task-date")
        yield Switch(classes="task-checkbox", value=self.my_task.completed, name=self.my_task.id)
        yield Button.error("Remove", name=self.my_task.id)

    def on_switch_changed(self, message):
        self.my_task.completed = message.value
        self.my_task = update_entity(self.my_task)

    def on_button_pressed(self, message:Button.Pressed):
        old_tasks:List = self.parent.tasks # get the tasks from the parent
        old_tasks.remove(self.my_task) # remove the old task
        self.parent.tasks = old_tasks # this causes an update on the parent
        delete_entity(self.my_task) # delete from database

class TaskItems(Vertical):
    tasks: List[Task] = reactive([], always_update=True)
    async def watch_tasks(self):
        try:
            await self.query("TaskItem").remove()
        except:
            pass
        for task in self.tasks:
            self.mount(TaskItem(task))

class Worklists(ListView):
    """This holds the names of the worklists on the left sidebar"""
    worklists = reactive([], always_update=True)
    async def watch_worklists(self):
        return await self.reload_list(self.worklists)
    
    async def reload_list(self, worklists: List[Worklist]):
        cache_index = self.index
        await self.query(".worklist-item-container").remove()
        for worklist in worklists:
            self.mount(
                ListItem(
                    Horizontal(
                    Label(worklist.name, name=worklist.id, classes="worklist-item"),
                    Button.error("X", classes="worklist-item-button", name=worklist)), 
                classes="worklist-item-container", name=worklist.id)
            )
        self.refresh(layout=True)
        self.index = cache_index if cache_index is not None else 0
    
    def on_button_pressed(self, message:Button.Pressed):
        """Called when the delete button is pressed on a worklist"""
        worklist = message.button.name
        self.worklists.remove(worklist) # remove the old task
        self.worklists = self.worklists # this causes an update on the parent
        if len(self.worklists) == 0:
            tasklist_widget: TaskItems = self.parent.parent.parent.parent.parent.query_one("#task-items")
            tasklist_widget.tasks =  [] # change to zero
        delete_entity(worklist) # delete from database
        self.refresh(layout=True)

class MovieApp(App):
    CSS_PATH = "style.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    user_id = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.companies = get_companies()
        self.company_list = [
            dict(value=i, text=f"{company.first_name}")
            for i, user in enumerate(self.companies)
        ]
        self.user = None
    def compose(self) -> ComposeResult:
        with Container(id='app-grid'):
            yield DataTable(id='left')
            with Vertical(id='right'):
                yield Input(id="title",placeholder="Title")
                yield Input(id="director", placeholder="Director")
                with Horizontal(id='buttons'):
                    yield Button.success("Add", id="add")
                    yield Button.error("Remove", id="remove")


    def on_mount(self) -> None:
        self.refresh_movies()
        self.init_datatable()

    def refresh_movies(self):
        self.movies = get_movies()

    def refresh_table(self):
        table = self.query_one(DataTable)
        table.clear()
        row_values = [get_ordered_values(Movie, movie) for movie in self.movies]
        table.add_rows(row_values)

    def init_datatable(self):
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        schema = Movie.schema()
        fields = schema['properties']
        field_ids = list(fields.keys())
        table.add_columns(*field_ids)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add":
            # add item
            title_widget = self.query_one("#title")
            director_widget = self.query_one("#director")

            create_movie(title=title_widget.value, director=director_widget.value)

            self.refresh_movies()
            self.refresh_table()

            title_widget.value = ""
            director_widget.value = ""
        else:
            # remove item
            if self.selected_row is not None:
                id = self.selected_row[0]
                delete_entity(get_entity(Movie, id))
                self.refresh_movies()
                self.refresh_table()

    def on_data_table_row_highlighted(self, message):
        self.selected_row = message.control.get_row(message.row_key)

def main():
    app = MovieApp()
    app.run()


if __name__ == "__main__":
    main()