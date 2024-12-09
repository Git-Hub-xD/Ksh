from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import get_user, update_points, update_health, connect_db
import time

# Admin user ID (replace this with the actual admin ID)
BOT_ADMIN_ID = 6329058409

# Example shop items
SHOP_ITEMS = {
    1: {
        "name": "XP Booster",
        "price": 300,
        "description": "Boost your XP gain for 24 hours !",
        "condition": "no_active_booster",
    },
    2: {
        "name": "Health Refill",
        "price": 20,
        "description": "Instantly restore health to 100%.",
        "condition": "not_full_health",
    }
}

ITEMS_PER_PAGE = 6

def get_shop_page(page_number):
    """Generate the shop text and inline buttons for a given page."""
    start_index = (page_number - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    items = list(SHOP_ITEMS.items())[start_index:end_index]

    if not items:
        return "No items available on this page.", InlineKeyboardMarkup([])

    # Generate shop text
    shop_text = "🛒 **Welcome to the Shop!** 🛒\n\n"
    for item_id, item in items:
        shop_text += f"{item_id}. **{item['name']}** - {item['price']} coins\n"
        shop_text += f"   {item['description']}\n\n"

    # Generate inline buttons, grouping 2 buttons per row
    buttons = []
    for i in range(0, len(items), 2):
        row = [
            InlineKeyboardButton(item["name"], callback_data=f"buy_{item_id}")
            for item_id, item in items[i:i + 2]
        ]
        buttons.append(row)

    # Add navigation buttons
    if len(SHOP_ITEMS) > ITEMS_PER_PAGE:
        nav_buttons = []
        if start_index > 0:
            nav_buttons.append(InlineKeyboardButton("Previous", callback_data=f"shop_page_{page_number - 1}"))
        if end_index < len(SHOP_ITEMS):
            nav_buttons.append(InlineKeyboardButton("Next", callback_data=f"shop_page_{page_number + 1}"))
        buttons.append(nav_buttons)

    return shop_text, InlineKeyboardMarkup(buttons)

def handle_purchase(user_id, item_id):
    """Handle the purchase of a shop item."""
    # Fetch user data from the database
    user_data = get_user(user_id)
    if not user_data:
        return "User not found. Please register using /start."

    points = user_data[2]  # Assuming points are at index 2
    health = user_data[5]  # Assuming health is at index 5
    xp_booster_expiry = user_data[8]  # Assuming xp_booster_expiry is at index 8

    item = SHOP_ITEMS.get(item_id)
    if not item:
        return "Item not found."

    # Check conditions for XP Booster
    if item["condition"] == "no_active_booster":
        if xp_booster_expiry > time.time():
            return "You already have an active XP Booster. Wait for it to expire before purchasing another."
    
    if item["condition"] == "not_full_health" and health == 100:
        return "Your health is already full. You don't need a Health Refill."

    # Check coins
    if points < item["price"]:
        return "You don't have enough coins to buy this item."

    # Deduct coins and apply the effect
    update_points(user_id, -item["price"])  # Deduct points from the user
    
    if item["condition"] == "no_active_booster":
        # Set XP booster expiry (24 hours from now)
        xp_booster_expiry = time.time() + 86400  # 24 hours in seconds
        update_xp_booster_expiry(user_id, xp_booster_expiry)  # Update the database with the new expiry time

    if item["condition"] == "not_full_health":
        # Update health to 100% in the database
        update_health(user_id, 100)

    return f"You successfully purchased: {item['name']}!"

def update_xp_booster_expiry(user_id, expiry_time):
    """Update the user's XP booster expiry time in the database."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET xp_booster_expiry = ?
            WHERE user_id = ?
            """,
            (expiry_time, user_id),
        )
        conn.commit()
