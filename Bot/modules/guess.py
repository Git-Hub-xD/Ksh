import random
from threading import Timer
from pyrogram import filters
from config import app  # Import the shared app instance

# Game data storage
current_game = {}  # Stores game data for each chat
join_timers = {}  # Timers for the join phase


def reset_game(chat_id):
    """Reset the game data for a chat."""
    if chat_id in current_game:
        del current_game[chat_id]
    if chat_id in join_timers:
        join_timers[chat_id].cancel()
        del join_timers[chat_id]


@app.on_message(filters.command("newguess"))
def newguess_handler(client, message):
    """Handle /newguess command to start a game."""
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id in current_game:
        message.reply("A game is already active in this chat. Use /cancelguess to cancel it first.")
        return

    current_game[chat_id] = {
        "host": user_id,
        "players": {user_id: message.from_user.first_name},
        "difficulty": None,
        "target_number": None,
        "turn_order": [],
        "current_turn": 0,
        "attempts": {},
        "game_active": False,
    }

    message.reply(
        f"🎮 **Guess the Number Game Started by {message.from_user.first_name}!**\n"
        "Players, join the game using /joinguess.\n"
        "The game will start in 60 seconds or use /forceguess to start immediately.\n\n"
        "Minimum players: 2 | Maximum players: No limit."
    )

    join_timers[chat_id] = Timer(60.0, start_game_automatically, args=(client, chat_id, message))
    join_timers[chat_id].start()


@app.on_message(filters.command("joinguess"))
def joinguess_handler(client, message):
    """Handle /joinguess command to join a game."""
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in current_game:
        message.reply("No active game to join. Start a new game with /newguess.")
        return

    if user_id in current_game[chat_id]["players"]:
        message.reply("You are already in the game.")
        return

    current_game[chat_id]["players"][user_id] = message.from_user.first_name
    message.reply(f"{message.from_user.first_name} has joined the game!")


def start_game_automatically(client, chat_id, message):
    """Automatically start the game after the join phase."""
    if chat_id not in current_game or current_game[chat_id]["game_active"]:
        return

    if len(current_game[chat_id]["players"]) < 2:
        message.reply("Not enough players joined. The game has been canceled.")
        reset_game(chat_id)
        return

    start_guessing_game(client, chat_id, message)


@app.on_message(filters.command("forceguess"))
def forceguess_handler(client, message):
    """Handle /forceguess command to start the game manually."""
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in current_game:
        message.reply("No active game to force start. Start a new game with /newguess.")
        return

    if current_game[chat_id]["host"] != user_id:
        message.reply("Only the game host can force start the game.")
        return

    if len(current_game[chat_id]["players"]) < 2:
        message.reply("Not enough players to start the game. Minimum players required: 2.")
        return

    start_guessing_game(client, chat_id, message)


@app.on_message(filters.command("cancelguess"))
def cancelguess_handler(client, message):
    """Handle /cancelguess command to cancel a game."""
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in current_game:
        message.reply("No active game to cancel.")
        return

    if current_game[chat_id]["host"] != user_id:
        message.reply("Only the game host can cancel the game.")
        return

    reset_game(chat_id)
    message.reply("The game has been canceled.")


@app.on_message(filters.text & filters.group)
def guess_number_handler(client, message):
    """Handle guesses from players."""
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in current_game:
        message.reply("No active game. Start one with /newguess.")
        return

    game = current_game[chat_id]
    if not game["game_active"]:
        message.reply("The game hasn't started yet. Wait for it to begin.")
        return

    if user_id != game["turn_order"][game["current_turn"]]:
        message.reply("It's not your turn!")
        return

    try:
        guess = int(message.text.split()[1])
    except (IndexError, ValueError):
        message.reply("Please provide a valid number.")
        return

    if guess == game["target_number"]:
        message.reply(f"🎉 {game['players'][user_id]} guessed the number {guess} correctly!")
        reset_game(chat_id)
    elif guess < game["target_number"]:
        message.reply(f"The number is higher than {guess}.")
    else:
        message.reply(f"The number is lower than {guess}.")

    game["current_turn"] = (game["current_turn"] + 1) % len(game["turn_order"])
