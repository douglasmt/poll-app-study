import database
from typing import List
from models.option import Option
from connections import create_connection


class Poll:  # definition of the class for polls objecs with its options
    def __init__(self, title: str, owner: str,  _id: int = None):  # constructor
        self.id = _id
        self.title = title
        self.owner = owner

    def __repr__(self) -> str:  # returns what is this object
        return f"Poll ({self.title!r}, {self.owner!r}, {self.id!r})"

    def save(self):  # creating a new poll object
        connection = create_connection()
        new_poll_id = database.create_poll(connection, self.title, self.owner)
        # just affects the poll table
        connection.close()
        self.id = new_poll_id

    def add_option(self, option_text: str):
        Option(option_text, self.id).save()
        # adds a choice(option object) for the poll

    @property  # to be able to access poll.options instead of poll.options()
    def options(self) -> List[Option]:  # get the options created for that poll object
        connection = create_connection()
        options = database.get_poll_options(connection, self.id)
        # just get options from the options table
        connection.close()
        return [Option(option[1], option[2], option[0]) for option in options]
        # option_text, poll_id and id from option object

    @classmethod
    def get(cls, poll_id: int) -> "Poll":
        connection = create_connection()
        poll = database.get_poll(connection, poll_id)
        # just uses the polls table
        connection.close()
        return cls(poll[1], poll[2], poll[0])

    @classmethod
    def all(cls) -> List["Poll"]:
        connection = create_connection()
        polls = database.get_polls(connection)
        connection.close()
        return [Poll(poll[1], poll[2], poll[0]) for poll in polls]
        # title,  owner_username, and id from the poll object

    @classmethod
    def latest(cls) -> "Poll":
        connection = create_connection()
        poll = database.get_latest_poll(connection)
        connection.close()
        return cls(poll[1], poll[2], poll[0])
        # my custom type,   polls(id,title,owner_username)      - int, str, str
        # and               options(id, option_text, poll_id)   - int, str, int
