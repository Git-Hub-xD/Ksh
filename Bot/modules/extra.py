from config import app
from pyrogram import Client, filters
from pyrogram.types import Message
from Bot.modules.guess import start_game, join_game, force_start_game, cancel_game, start_guessing_game

@app.on_message(filters.command("newguess"))
def newguess_handler(client, message):
    """Handle the /newguess command to start a new game."""
    start_game(client, message)

@app.on_message(filters.command("joinguess"))
def joinguess_handler(client, message):
    """Handle the /joinguess command to join a game."""
    join_game(client, message)

@app.on_message(filters.command("forceguess"))
def forceguess_handler(client, message):
    """Handle the /forceguess command to force start a game."""
    force_start_game(client, message)

@app.on_message(filters.command("cancelguess"))
def cancelguess_handler(client, message):
    """Handle the /cancelguess command to cancel a game."""
    cancel_game(client, message)

@app.on_message(filters.text & filters.group)
def guess_number_handler(client, message):
    """Handle guesses from players."""
    if message.text.startswith("/guess"):
        process_guess(client, message)
