from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import app

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
