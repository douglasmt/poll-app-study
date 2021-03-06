import random
from typing import List

import database
from models.poll import Poll
from models.option import Option
from connections import create_connection

DATABASE_PROMPT = "Enter the DATABASE_URI value or leave empty to load from .env file: "

MENU_PROMPT = """-- Menu --

1) Create new poll
2) List open polls
3) Vote on a poll
4) Show poll votes
5) Select a random winner from a poll option
6) Exit

Enter your choice: """

NEW_OPTION_PROMPT = "Enter new option text (or leave empty to stop adding options): "


def prompt_create_poll():
    poll_title = input("Enter poll title: ")
    poll_owner = input("Enter poll owner: ")
    poll = Poll(poll_title, poll_owner)
    poll.save()

    while new_option := input(NEW_OPTION_PROMPT):
        poll.add_option(new_option)


def list_open_polls():
    for poll in Poll.all():  # fetch all the polls
        print(f"{poll.id}: {poll.title} (created by {poll.owner})")
        # I can put this inside the __str__ method of the Poll object


def prompt_vote_poll():
    poll_id = int(input("Enter poll would you like to vote on: "))
    _print_poll_options(Poll.get(poll_id).options)  # .options gets polls along with the options

    option_id = int(input("Enter option you'd like to vote for: "))
    username = input("Enter the username you'd like to vote as: ")

    Option.get(option_id).vote(username)  # get the options and the username


def _print_poll_options(poll_with_options: List[Option]):  # Option class we import
    for option in poll_with_options:
        print(f"{option.id}: {option.option_text}")  # can be used in the __str__ method


def show_poll_votes():
    poll_id = int(input("Enter poll you would like to see votes for: "))
    poll = Poll.get(poll_id)
    options = poll.options
    # the list of options
    votes_per_options = [len(option.votes) for option in options]  # list comprehension
    # all the votes from the database directly
    total_votes = sum(votes_per_options)
    # the sum of the votes

    try:
        for option, votes in zip(options, votes_per_options):
            percentage = votes / total_votes * 100
            print(f"{option.option_text} got {votes} votes ({percentage:.2f}% of total)")
    except ZeroDivisionError:
        print("No votes cast for this poll yet.")


def randomize_poll_winner():
    poll_id = int(input("Enter poll you'd like to pick a winner for: "))
    _print_poll_options(Poll.get(poll_id).options)

    option_id = int(input("Enter which is the winning option, we'll pick a random winner from voters: "))
    votes = Option.get(option_id).votes
    winner = random.choice(votes)
    print(f"The randomly selected winner is {winner[0]}.")


MENU_OPTIONS = {
    "1": prompt_create_poll,
    "2": list_open_polls,
    "3": prompt_vote_poll,
    "4": show_poll_votes,
    "5": randomize_poll_winner
}


def menu():

    connection = create_connection()
    database.create_tables(connection)

    while (selection := input(MENU_PROMPT)) != "6":
        try:
            MENU_OPTIONS[selection]()
        except KeyError:
            print("Invalid input selected. Please try again.")


menu()
