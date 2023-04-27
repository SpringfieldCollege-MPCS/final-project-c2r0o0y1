
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Input, Button, Static
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive
from typing import List

from ..db import get_movies, Movie, create_movie, get_entity, delete_entity
from .helper import get_ordered_values

class MovieApp(App):
    CSS_PATH = "style.css"
    movies: List[Movie] = reactive([], always_update=True)
    selected_row = None
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