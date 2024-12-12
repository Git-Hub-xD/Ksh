from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import app
from Bot.modules.guess import start_game, join_game, force_start_game, cancel_game, start_guessing_game

@app.on_message(filters.command("help"))
def help_handler(client, message):
    # List of available commands and their descriptions
    help_text = (
        "Here are the commands you can use with the Kaisen Ranking Bot:\n\n"
        "💬 : General Commands\n"
        "/start - ɪɴɪᴛᴀʟɪᴢᴇ ʏᴏᴜʀ ᴘʀᴏғɪʟᴇ\n"
        "/profile - ᴠɪᴇᴡ ᴘʀᴏғɪʟᴇ\n"
        "/help - ᴅɪsᴘʟᴀʏ ᴛʜɪs ʜᴇʟᴘ ᴍᴇɴᴜ\n\n"
        "👇 Join this temporary channel for updates !"
    )
    
    # Inline button linking to a Telegram channel
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Temporary Channel", url="https://t.me/+uoS9m1WPN71mOGRl")
            ]
        ]
    )
    
    # Send the help message to the user with the inline button
    message.reply_text(help_text, reply_markup=buttons)

# Guess The Number - Game

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
