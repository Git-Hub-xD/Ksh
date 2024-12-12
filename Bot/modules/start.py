import random
from time import time
from config import app
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from Bot.modules.flood_control import check_flood
from Bot.modules.leveling import level_up
from Bot.modules.shop import get_shop_page, handle_purchase
from Bot.modules.guess import start_game, join_game, force_start_game, cancel_game, start_guessing_game
from database.db_manager import create_db, add_user, ensure_user_exists, get_user, update_points, update_level, update_health, connect_db

create_db()  # Ensure the table is created if it doesn't exist

@app.on_message(filters.command("start"))
def start_handler(client, message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name  # Use first name for the link
    username = message.from_user.username or first_name

    # Ensure user exists in the database
    ensure_user_exists(user_id, username)

    # Fetch user data from the database
    user_data = get_user(user_id)
    if user_data:
        user_id, username, points, level, exp, health, last_activity_time, last_claimed, xp_booster_expiry = user_data

        # Create a user link using the user's first name
        user_link = f'<a href="tg://user?id={user_id}">{first_name}</a>'

        # Inline keyboard with a button to your chat group
        chat_group_url = "https://t.me/KaisenWorld"  # Replace with your group link
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Join Chat Group", url=chat_group_url)]
            ]
        )

        # Send a welcome message with user data and the user link
        message.reply_photo(
            photo="https://imgur.com/a/EvmGYI7",
            caption=(
                f"Hey {user_link}, 𝖶𝖾𝗅𝖼𝗈𝗆𝖾 𝗍𝗈 𝗍𝗁𝖾 𝖯𝗒𝗑𝗇 𝖡𝗈𝗍 ! 🎉\n\n"
                f"<b>📜 ʜᴏᴡ ᴛᴏ ᴇᴀʀɴ ᴛᴏᴋᴇɴs ?</b>\n"
                f"- ᴊᴜsᴛ ᴄʜᴀᴛ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ ! ᴇᴠᴇʀʏ ᴍᴇssᴀɢᴇ ʏᴏᴜ sᴇɴᴅ ɢᴇᴛs ʏᴏᴜ ᴄʟᴏsᴇʀ ᴛᴏ ᴇᴀʀɴɪɴɢ ᴄᴏɪɴs.\n\n"
                f"𝖦𝖾𝗍 𝗌𝗍𝖺𝗋𝗍𝖾𝖽 𝗇𝗈𝗐 ! 𝗍𝗒𝗉𝖾 /help 𝖿𝗈𝗋 𝗆𝗈𝗋𝖾 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌.\n\n"
                f"🎯 **ʏᴏᴜʀ sᴛᴀᴛs :**\n• ᴄᴏɪɴs : {points:,} | ʟᴇᴠᴇʟ : {level}"
            ),
            reply_markup=keyboard,  # Attach the keyboard to the message
        )

    # If user data doesn't exist, add the user and fetch data again
    if user_data is None:
        add_user(user_id, username)
        user_data = get_user(user_id)

@app.on_message(filters.command("shop"))
def shop_handler(client, message):
    """Handle the /shop command to display the shop."""
    page_number = 1  # Default to the first page
    shop_text, reply_markup = get_shop_page(page_number)
    message.reply_text(shop_text, reply_markup=reply_markup)

@app.on_callback_query(filters.regex(r"shop_page_\d+"))
def shop_page_handler(client, callback_query):
    """Handle navigation between shop pages."""
    page_number = int(callback_query.data.split("_")[-1])
    shop_text, reply_markup = get_shop_page(page_number)
    callback_query.message.edit_text(shop_text, reply_markup=reply_markup)

@app.on_callback_query(filters.regex(r"buy_\d+"))
def shop_purchase_handler(client, callback_query):
    """Handle purchases from the shop."""
    user_id = callback_query.from_user.id
    item_id = int(callback_query.data.split("_")[-1])
    response = handle_purchase(user_id, item_id)
    callback_query.answer(response, show_alert=True)

@app.on_message(filters.command("profile"))
async def profile_handler(client, message):
    """Handle the /profile command."""
    # Check if the command is replied to a message or tagged with @username
    if message.reply_to_message:
        # If the command is used by replying to another user's message
        target_user = message.reply_to_message.from_user
    elif message.entities and message.entities[0].type == "mention":
        # If the command is used by tagging a user (e.g., @username)
        target_user = message.entities[0].user
    else:
        # If no reply or mention, show the profile of the user who sent the command
        target_user = message.from_user

    # Check if the target is a bot
    if target_user.is_bot:
        await message.reply("You can't get the profile of a bot.")
        return

    # Fetch user data from the database for the target user
    user_data = get_user(target_user.id)
    if user_data:
        user_id, username, points, level, exp, health, last_activity_time, last_claimed, xp_booster_expiry = user_data

        # Create a user link using the user's first name
        user_link = f'<a href="tg://user?id={target_user.id}">{target_user.first_name}</a>'

        # Format the last activity time
        time_diff = int(time()) - last_activity_time
        last_activity = format_time_diff(time_diff)

        # Prepare the profile text
        profile_text = f"""
        **{user_link}'s Profile:**
💎 **Level** : {level}
🎮 **Exp** : {exp}/{level * 100}
💰 **Coins** : {points:,}
❤️ **Health** : {health}%
        
🕛 **Last Checkin** : {last_activity}

- **You're doing great! Keep chatting to level up!**
        """

        # Send the profile details
        await message.reply_text(profile_text)
    else:
        # If user data doesn't exist
        await message.reply_text(f"Error fetching {target_user.first_name}'s profile. Please try again later or use /start!")


def format_time_diff(seconds):
    """Convert seconds into a readable time format."""
    if seconds < 60:
        return f"{seconds} seconds ago"
    elif seconds < 3600:
        return f"{seconds // 60} minutes ago"
    elif seconds < 86400:
        return f"{seconds // 3600} hours ago"
    else:
        return f"{seconds // 86400} days ago"

@app.on_message(filters.text)
async def handle_message(client, message):
    """Handle the flood control and leveling up based on chat activity."""
    # List of allowed group chat IDs (replace with your actual group IDs)
    ALLOWED_GROUPS = [-1002135192853, -1002324159284]  # Add your group IDs here

    # Ensure the message is from an allowed group
    if message.chat.id not in ALLOWED_GROUPS:
        return  # Ignore messages outside allowed groups

    user_id = message.from_user.id
  
    # Flood control logic
    if check_flood(user_id):
        await message.reply("You are sending messages too quickly. Please wait a few seconds!")
    else:
        # Increment experience and level based on the message content
        level_up(user_id, message.text)

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
