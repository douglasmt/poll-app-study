from typing import List, Tuple

import psycopg2
from psycopg2.extras import execute_values  # used in create_poll()


Poll = Tuple[int, str, str]                             # my custom type, sequence for CREATE_POLLS input
Option = Tuple[int, str, int]
Vote = Tuple[str, int]                                  # my custom type, sequence for CREATE_VOTES


# PollResults = Tuple[int, str, int, float]
# my custom type, sequence for SELECT_POLL_VOTE_DETAILS
# id int, option_text text, vote_count(int), vote_percentage float
# no longer used PollWithOption = Tuple[int, str, str, int, str, int]
# my custom type,   polls(id,title,owner_username)      - int, str, str
# and               options(id, option_text, poll_id)   - int, str, int


CREATE_POLLS = """CREATE TABLE IF NOT EXISTS polls 
(id SERIAL PRIMARY KEY, title TEXT, owner_username TEXT);"""
CREATE_OPTIONS = """CREATE TABLE IF NOT EXISTS options 
(id SERIAL PRIMARY KEY, option_text TEXT, poll_id INTEGER, FOREIGN KEY(poll_id) REFERENCES polls(id));"""
CREATE_VOTES = """CREATE TABLE IF NOT EXISTS votes 
(username TEXT, option_id INTEGER, FOREIGN KEY(option_id) REFERENCES options (id));"""

SELECT_POLL = "SELECT * FROM POLLS WHERE id = %s;"
SELECT_ALL_POLLS = "SELECT * FROM polls;"

SELECT_POLL_OPTIONS = """SELECT * FROM options
WHERE poll_id = %s;"""
SELECT_LATEST_POLL = """SELECT * FROM polls
WHERE polls.id = (
    SELECT id FROM polls ORDER BY id DESC LIMIT 1
);"""

SELECT_OPTION = "SELECT * FROM options WHERE id = %s;"
SELECT_VOTES_FOR_OPTION = "SELECT * FROM votes WHERE option_id = %s;"

INSERT_POLL_RETURN_ID = "INSERT INTO polls (title, owner_username) VALUES (%s, %s) RETURNING id;"
INSERT_OPTION_RETURNING_ID = "INSERT INTO options (option_text, poll_id) VALUES (%s, %s) RETURNING id;"
INSERT_VOTE = "INSERT INTO votes (username, option_id) VALUES (%s, %s);"    # used in create_poll()


def create_tables(connection):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_POLLS)
            cursor.execute(CREATE_OPTIONS)
            cursor.execute(CREATE_VOTES)


# -- polls --
def create_poll(connection, title: str, owner: str):
    # options: List[str] - it will be a list of items
    # 3.8 python or above can use it
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_POLL_RETURN_ID, (title, owner))  # returns ID on cursor

            poll_id = cursor.fetchone()[0]  # result from RETURNING id
            return poll_id


def get_polls(connection) -> List[Poll]:  # the list of Poll fields will be returned to the caller
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_POLLS)
            return cursor.fetchall()


def get_poll(connection, poll_id: int) -> Poll:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_POLL, (poll_id,))
            return cursor.fetchone()


def get_latest_poll(connection) -> Poll:
    # the list of PollWithOption fields will be returned to the caller
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_LATEST_POLL)
            return cursor.fetchone()


def get_poll_options(connection, poll_id: int) -> List[Option]:
    # poll_id takes only integers
    # the list of PollWithOption fields will be returned to the caller
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_POLL_OPTIONS, (poll_id,))
            return cursor.fetchall()


# -- options --

def get_option(connection, option_id: int) -> Option:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_OPTION, (option_id,))
            return cursor.fetchone()


def add_option(connection, option_text, poll_id: int):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_OPTION_RETURNING_ID, (option_text, poll_id))
            option_id = cursor.fetchone()[0]
            return option_id


# -- votes --

def get_votes_for_option(connection, option_id: int) -> List[Vote]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_VOTES_FOR_OPTION, (option_id,))
            return cursor.fetchall()


def add_poll_vote(connection, username: str, option_id: int):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_VOTE, (username, option_id))
