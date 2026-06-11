"""
Telegram Crush Proposal Bot - Aiogram 3.x
All buttons use Reply Keyboards (no Inline Keyboards).
"""

import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import database as db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
BASE_URL = os.environ.get("RAILWAY_PUBLIC_DOMAIN", os.environ.get("BASE_URL", ""))

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)


# ========================
# FSM STATES
# ========================

class CreateLink(StatesGroup):
    crush_name = State()
    creator_name = State()
    message = State()


class SetEmoji(StatesGroup):
    waiting_link = State()
    waiting_emoji = State()


class SetMusic(StatesGroup):
    waiting_link = State()
    waiting_music = State()


class SetBg(StatesGroup):
    waiting_link = State()
    waiting_bg = State()


class SetMessage(StatesGroup):
    waiting_link = State()
    waiting_message = State()


class DeleteLink(StatesGroup):
    waiting_link = State()
    confirm = State()


class AdminBroadcast(StatesGroup):
    waiting_message = State()


class AdminBan(StatesGroup):
    waiting_user_id = State()


class AdminUnban(StatesGroup):
    waiting_user_id = State()


class AdminDeleteLink(StatesGroup):
    waiting_link_id = State()


class AdminUserStats(StatesGroup):
    waiting_user_id = State()


# ========================
# HELPER FUNCTIONS
# ========================

def get_base_url() -> str:
    """Get the base URL for crush page links."""
    if BASE_URL:
        domain = BASE_URL.replace("https://", "").replace("http://", "")
        return f"https://{domain}"
    return "https://your-app.railway.app"


def main_menu_keyboard():
    """Main menu Reply Keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💝 Create Link"), KeyboardButton(text="📋 My Links")],
            [KeyboardButton(text="📊 My Stats"), KeyboardButton(text="❓ Help")],
        ],
        resize_keyboard=True
    )


def cancel_keyboard():
    """Cancel Reply Keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Cancel")]],
        resize_keyboard=True
    )


def confirm_keyboard():
    """Confirm/Cancel Reply Keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Confirm"), KeyboardButton(text="❌ Cancel")]
        ],
        resize_keyboard=True
    )


def admin_keyboard():
    """Admin panel Reply Keyboard (compact)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Stats"), KeyboardButton(text="📢 Broadcast")],
            [KeyboardButton(text="🚫 Ban"), KeyboardButton(text="✅ Unban")],
            [KeyboardButton(text="🗑 Del Link"), KeyboardButton(text="👤 User Stats")],
            [KeyboardButton(text="🏠 Home")],
        ],
        resize_keyboard=True
    )


def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id == ADMIN_ID


# ========================
# COMMAND HANDLERS
# ========================

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command."""
    await state.clear()
    user = message.from_user
    db.register_user(user.id, user.username or "", user.first_name or "")

    if db.is_banned(user.id):
        await message.answer("🚫 You are banned from using this bot.")
        return

    welcome_text = (
        f"💕 **Welcome to Crush Proposal Bot!** 💕\n\n"
        f"Hey {user.first_name}! 👋\n\n"
        f"Create beautiful crush proposal pages and share them with your special someone! 🌹\n\n"
        f"✨ **Features:**\n"
        f"• Create unlimited proposal pages\n"
        f"• Custom messages & emojis\n"
        f"• Background music & images\n"
        f"• Get notified when they say YES! 🎉\n\n"
        f"Use the buttons below or type /help for commands."
    )

    await message.answer(welcome_text, parse_mode="Markdown",
                         reply_markup=main_menu_keyboard())


@router.message(Command("help"))
@router.message(F.text == "❓ Help")
async def cmd_help(message: Message, state: FSMContext):
    """Handle /help command."""
    await state.clear()
    help_text = (
        "💝 **Crush Proposal Bot - Help** 💝\n\n"
        "**Commands:**\n"
        "/create - Create a new crush page\n"
        "/setemoji - Set live emojis for a page\n"
        "/setmusic - Set background music\n"
        "/setbg - Set background image\n"
        "/setmessage - Change the message\n"
        "/mylinks - View your links\n"
        "/delete - Delete a link\n"
        "/stats - Your statistics\n\n"
        "**How it works:**\n"
        "1️⃣ Create a crush page with /create\n"
        "2️⃣ Customize it with emojis, music, etc.\n"
        "3️⃣ Share the link with your crush\n"
        "4️⃣ Get notified when they click YES! 🎉\n\n"
        "The **No** button runs away! 😂"
    )
    await message.answer(help_text, parse_mode="Markdown",
                         reply_markup=main_menu_keyboard())


# ========================
# CREATE LINK FLOW
# ========================

@router.message(Command("create"))
@router.message(F.text == "💝 Create Link")
async def cmd_create(message: Message, state: FSMContext):
    """Start create link flow."""
    if db.is_banned(message.from_user.id):
        await message.answer("🚫 You are banned from using this bot.")
        return

    await state.set_state(CreateLink.crush_name)
    await message.answer(
        "💕 **Create a Crush Page** 💕\n\n"
        "What is your crush's name?",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )


@router.message(CreateLink.crush_name)
async def process_crush_name(message: Message, state: FSMContext):
    """Process crush name input."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=main_menu_keyboard())
        return

    await state.update_data(crush_name=message.text)
    await state.set_state(CreateLink.creator_name)
    await message.answer(
        "👤 What is your name? (Creator name)",
        reply_markup=cancel_keyboard()
    )


@router.message(CreateLink.creator_name)
async def process_creator_name(message: Message, state: FSMContext):
    """Process creator name input."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=main_menu_keyboard())
        return

    await state.update_data(creator_name=message.text)
    await state.set_state(CreateLink.message)
    await message.answer(
        "💌 Write a custom message for your crush:\n"
        "(or type 'skip' for default message)",
        reply_markup=cancel_keyboard()
    )


@router.message(CreateLink.message)
async def process_message(message: Message, state: FSMContext):
    """Process custom message and create the link."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=main_menu_keyboard())
        return

    data = await state.get_data()
    custom_message = message.text if message.text.lower() != "skip" else "I have a crush on you! 💕"

    link_id = db.create_link(
        user_id=message.from_user.id,
        crush_name=data["crush_name"],
        creator_name=data["creator_name"],
        message=custom_message
    )

    base_url = get_base_url()
    link = f"{base_url}/p/{link_id}"

    await state.clear()
    await message.answer(
        f"✅ **Crush Page Created!** 🎉\n\n"
        f"💕 Crush: {data['crush_name']}\n"
        f"👤 By: {data['creator_name']}\n"
        f"💌 Message: {custom_message}\n\n"
        f"🔗 **Your Link:**\n{link}\n\n"
        f"Share this with your crush! 💝\n\n"
        f"**Customize:**\n"
        f"/setemoji - Add live emojis\n"
        f"/setmusic - Add background music\n"
        f"/setbg - Add background image",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )


# ========================
# SET EMOJI
# ========================

@router.message(Command("setemoji"))
async def cmd_setemoji(message: Message, state: FSMContext):
    """Set emoji for a link."""
    if db.is_banned(message.from_user.id):
        await message.answer("🚫 You are banned.")
        return

    links = db.get_user_links(message.from_user.id)
    if not links:
        await message.answer("❌ You have no links. Create one with /create")
        return

    link_list = "\n".join([f"• `{l['id']}` - {l['crush_name']}" for l in links])
    await state.set_state(SetEmoji.waiting_link)
    await message.answer(
        f"🎭 **Set Live Emoji**\n\n"
        f"Your links:\n{link_list}\n\n"
        f"Send the link ID:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )


@router.message(SetEmoji.waiting_link)
async def process_emoji_link(message: Message, state: FSMContext):
    """Process link ID for emoji setting."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=main_menu_keyboard())
        return

    link = db.get_link(message.text.strip())
    if not link or link["user_id"] != message.from_user.id:
        await message.answer("❌ Invalid link ID. Try again:")
        return

    await state.update_data(link_id=message.text.strip())
    await state.set_state(SetEmoji.waiting_emoji)
    await message.answer(
        "🎭 Send the emoji you want floating on the page:\n"
        "Examples: 💕 🌹 ❤️ 💝 🦋 ✨",
        reply_markup=cancel_keyboard()
    )


@router.message(SetEmoji.waiting_emoji)
async def process_emoji_value(message: Message, state: FSMContext):
    """Save emoji setting."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=main_menu_keyboard())
        return

    data = await state.get_data()
    db.update_link_field(data["link_id"], "emoji", message.text.strip())
    await state.clear()
    await message.answer(
        f"✅ Emoji set to: {message.text.strip()}",
        reply_markup=main_menu_keyboard()
    )


# ========================
# SET MUSIC
# ========================

@router.message(Command("setmusic"))
async def cmd_setmusic(message: Message, state: FSMContext):
    """Set background music for a link."""
    if db.is_banned(message.from_user.id):
        await message.answer("🚫 You are banned.")
        return

    links = db.get_user_links(message.from_user.id)
    if not links:
        await message.answer("❌ You have no links. Create one with /create")
        return

    link_list = "\n".join([f"• `{l['id']}` - {l['crush_name']}" for l in links])
    await state.set_state(SetMusic.waiting_link)
    await message.answer(
        f"🎵 **Set Background Music**\n\n"
        f"Your links:\n{link_list}\n\n"
        f"Send the link ID:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )


@router.message(SetMusic.waiting_link)
async def process_music_link(message: Message, state: FSMContext):
    """Process link ID for music setting."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=main_menu_keyboard())
        return

    link = db.get_link(message.text.strip())
    if not link or link["user_id"] != message.from_user.id:
        await message.answer("❌ Invalid link ID. Try again:")
        return

    await state.update_data(link_id=message.text.strip())
    await state.set_state(SetMusic.waiting_music)
    await message.answer(
        "🎵 Send a direct URL to an MP3 file for background music:\n"
        "(e.g., https://example.com/song.mp3)",
        reply_markup=cancel_keyboard()
    )


@router.message(SetMusic.waiting_music)
async def process_music_value(message: Message, state: FSMContext):
    """Save music setting."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=main_menu_keyboard())
        return

    data = await state.get_data()
    db.update_link_field(data["link_id"], "bg_music", message.text.strip())
    await state.clear()
    await message.answer(
        "✅ Background music set!",
        reply_markup=main_menu_keyboard()
    )


# ========================
# SET BACKGROUND
# ========================

@router.message(Command("setbg"))
async def cmd_setbg(message: Message, state: FSMContext):
    """Set background image for a link."""
    if db.is_banned(message.from_user.id):
        await message.answer("🚫 You are banned.")
        return

    links = db.get_user_links(message.from_user.id)
    if not links:
        await message.answer("❌ You have no links. Create one with /create")
        return

    link_list = "\n".join([f"• `{l['id']}` - {l['crush_name']}" for l in links])
    await state.set_state(SetBg.waiting_link)
    await message.answer(
        f"🖼 **Set Background Image**\n\n"
        f"Your links:\n{link_list}\n\n"
        f"Send the link ID:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )


@router.message(SetBg.waiting_link)
async def process_bg_link(message: Message, state: FSMContext):
    """Process link ID for background setting."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=main_menu_keyboard())
        return

    link = db.get_link(message.text.strip())
    if not link or link["user_id"] != message.from_user.id:
        await message.answer("❌ Invalid link ID. Try again:")
        return

    await state.update_data(link_id=message.text.strip())
    await state.set_state(SetBg.waiting_bg)
    await message.answer(
        "🖼 Send a direct URL to an image for background:\n"
        "(e.g., https://example.com/image.jpg)",
        reply_markup=cancel_keyboard()
    )


@router.message(SetBg.waiting_bg)
async def process_bg_value(message: Message, state: FSMContext):
    """Save background image setting."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=main_menu_keyboard())
        return

    data = await state.get_data()
    db.update_link_field(data["link_id"], "bg_image", message.text.strip())
    await state.clear()
    await message.answer(
        "✅ Background image set!",
        reply_markup=main_menu_keyboard()
    )


# ========================
# SET MESSAGE
# ========================

@router.message(Command("setmessage"))
async def cmd_setmessage(message: Message, state: FSMContext):
    """Set custom message for a link."""
    if db.is_banned(message.from_user.id):
        await message.answer("🚫 You are banned.")
        return

    links = db.get_user_links(message.from_user.id)
    if not links:
        await message.answer("❌ You have no links. Create one with /create")
        return

    link_list = "\n".join([f"• `{l['id']}` - {l['crush_name']}" for l in links])
    await state.set_state(SetMessage.waiting_link)
    await message.answer(
        f"💌 **Set Custom Message**\n\n"
        f"Your links:\n{link_list}\n\n"
        f"Send the link ID:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )


@router.message(SetMessage.waiting_link)
async def process_setmsg_link(message: Message, state: FSMContext):
    """Process link ID for message setting."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=main_menu_keyboard())
        return

    link = db.get_link(message.text.strip())
    if not link or link["user_id"] != message.from_user.id:
        await message.answer("❌ Invalid link ID. Try again:")
        return

    await state.update_data(link_id=message.text.strip())
    await state.set_state(SetMessage.waiting_message)
    await message.answer(
        "💌 Write the new message for this crush page:",
        reply_markup=cancel_keyboard()
    )


@router.message(SetMessage.waiting_message)
async def process_setmsg_value(message: Message, state: FSMContext):
    """Save new message."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=main_menu_keyboard())
        return

    data = await state.get_data()
    db.update_link_field(data["link_id"], "message", message.text.strip())
    await state.clear()
    await message.answer(
        "✅ Message updated!",
        reply_markup=main_menu_keyboard()
    )


# ========================
# MY LINKS
# ========================

@router.message(Command("mylinks"))
@router.message(F.text == "📋 My Links")
async def cmd_mylinks(message: Message, state: FSMContext):
    """Show user's links."""
    await state.clear()
    links = db.get_user_links(message.from_user.id)

    if not links:
        await message.answer(
            "📋 You have no links yet.\nCreate one with /create!",
            reply_markup=main_menu_keyboard()
        )
        return

    base_url = get_base_url()
    text = "📋 **Your Crush Pages:**\n\n"
    for i, link in enumerate(links, 1):
        text += (
            f"{i}. 💕 {link['crush_name']}\n"
            f"   🔗 {base_url}/p/{link['id']}\n"
            f"   👁 Views: {link.get('views', 0)} | ❤️ Yes: {link.get('yes_count', 0)}\n"
            f"   🆔 ID: `{link['id']}`\n\n"
        )

    await message.answer(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())


# ========================
# DELETE LINK
# ========================

@router.message(Command("delete"))
async def cmd_delete(message: Message, state: FSMContext):
    """Delete a link."""
    links = db.get_user_links(message.from_user.id)
    if not links:
        await message.answer("❌ You have no links to delete.")
        return

    link_list = "\n".join([f"• `{l['id']}` - {l['crush_name']}" for l in links])
    await state.set_state(DeleteLink.waiting_link)
    await message.answer(
        f"🗑 **Delete a Link**\n\n"
        f"Your links:\n{link_list}\n\n"
        f"Send the link ID to delete:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )


@router.message(DeleteLink.waiting_link)
async def process_delete_link(message: Message, state: FSMContext):
    """Process link deletion."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=main_menu_keyboard())
        return

    link = db.get_link(message.text.strip())
    if not link or link["user_id"] != message.from_user.id:
        await message.answer("❌ Invalid link ID. Try again:")
        return

    await state.update_data(link_id=message.text.strip())
    await state.set_state(DeleteLink.confirm)
    await message.answer(
        f"⚠️ Delete page for **{link['crush_name']}**?\n"
        f"This cannot be undone!",
        parse_mode="Markdown",
        reply_markup=confirm_keyboard()
    )


@router.message(DeleteLink.confirm)
async def process_delete_confirm(message: Message, state: FSMContext):
    """Confirm deletion."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=main_menu_keyboard())
        return

    if message.text == "✅ Confirm":
        data = await state.get_data()
        db.delete_link(data["link_id"])
        await state.clear()
        await message.answer("✅ Link deleted!", reply_markup=main_menu_keyboard())
    else:
        await message.answer("Use ✅ Confirm or ❌ Cancel", reply_markup=confirm_keyboard())


# ========================
# STATS
# ========================

@router.message(Command("stats"))
@router.message(F.text == "📊 My Stats")
async def cmd_stats(message: Message, state: FSMContext):
    """Show user statistics."""
    await state.clear()
    stats = db.get_user_stats(message.from_user.id)

    if not stats:
        await message.answer("❌ No stats available yet.", reply_markup=main_menu_keyboard())
        return

    text = (
        f"📊 **Your Statistics**\n\n"
        f"📝 Links Created: {stats['links_created']}\n"
        f"👁 Total Views: {stats['total_views']}\n"
        f"❤️ Total Yes Clicks: {stats['total_yes']}\n"
    )

    await message.answer(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())


# ========================
# ADMIN PANEL
# ========================

@router.message(F.text == "🏠 Home")
async def admin_home(message: Message, state: FSMContext):
    """Return to main menu."""
    await state.clear()
    await message.answer("🏠 Main menu", reply_markup=main_menu_keyboard())


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    """Open admin panel."""
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Access denied.")
        return

    await state.clear()
    stats = db.get_admin_stats()
    text = (
        f"🔐 **Admin Panel**\n\n"
        f"👥 Users: {stats['total_users']}\n"
        f"🔗 Links: {stats['total_links']}\n"
        f"👁 Views: {stats['total_views']}\n"
        f"❤️ Yes Clicks: {stats['total_yes_clicks']}\n"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=admin_keyboard())


@router.message(F.text == "📊 Stats")
async def admin_stats(message: Message, state: FSMContext):
    """Admin stats button."""
    if not is_admin(message.from_user.id):
        return

    stats = db.get_admin_stats()
    text = (
        f"📊 **Bot Statistics**\n\n"
        f"👥 Total Users: {stats['total_users']}\n"
        f"🔗 Total Links: {stats['total_links']}\n"
        f"👁 Total Views: {stats['total_views']}\n"
        f"❤️ Total Yes: {stats['total_yes_clicks']}\n"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=admin_keyboard())


@router.message(F.text == "📢 Broadcast")
async def admin_broadcast_start(message: Message, state: FSMContext):
    """Start broadcast flow."""
    if not is_admin(message.from_user.id):
        return

    await state.set_state(AdminBroadcast.waiting_message)
    await message.answer(
        "📢 Send the message to broadcast to all users:",
        reply_markup=cancel_keyboard()
    )


@router.message(AdminBroadcast.waiting_message)
async def admin_broadcast_send(message: Message, state: FSMContext):
    """Send broadcast message."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=admin_keyboard())
        return

    users = db.get_all_users()
    sent = 0
    failed = 0

    for user in users:
        try:
            await bot.send_message(user["user_id"], message.text)
            sent += 1
        except Exception:
            failed += 1

    await state.clear()
    await message.answer(
        f"📢 Broadcast complete!\n✅ Sent: {sent}\n❌ Failed: {failed}",
        reply_markup=admin_keyboard()
    )


@router.message(F.text == "🚫 Ban")
async def admin_ban_start(message: Message, state: FSMContext):
    """Start ban flow."""
    if not is_admin(message.from_user.id):
        return

    await state.set_state(AdminBan.waiting_user_id)
    await message.answer("🚫 Send the User ID to ban:", reply_markup=cancel_keyboard())


@router.message(AdminBan.waiting_user_id)
async def admin_ban_process(message: Message, state: FSMContext):
    """Process ban."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=admin_keyboard())
        return

    try:
        user_id = int(message.text.strip())
        db.ban_user(user_id)
        await state.clear()
        await message.answer(f"🚫 User {user_id} banned!", reply_markup=admin_keyboard())
    except ValueError:
        await message.answer("❌ Invalid User ID. Send a number:")


@router.message(F.text == "✅ Unban")
async def admin_unban_start(message: Message, state: FSMContext):
    """Start unban flow."""
    if not is_admin(message.from_user.id):
        return

    banned = db.get_banned_users()
    if not banned:
        await message.answer("No banned users.", reply_markup=admin_keyboard())
        return

    text = "Banned users:\n" + "\n".join([f"• {u['user_id']}" for u in banned])
    await state.set_state(AdminUnban.waiting_user_id)
    await message.answer(f"{text}\n\nSend User ID to unban:", reply_markup=cancel_keyboard())


@router.message(AdminUnban.waiting_user_id)
async def admin_unban_process(message: Message, state: FSMContext):
    """Process unban."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=admin_keyboard())
        return

    try:
        user_id = int(message.text.strip())
        if db.unban_user(user_id):
            await state.clear()
            await message.answer(f"✅ User {user_id} unbanned!", reply_markup=admin_keyboard())
        else:
            await message.answer("❌ User not found in ban list.")
    except ValueError:
        await message.answer("❌ Invalid User ID. Send a number:")


@router.message(F.text == "🗑 Del Link")
async def admin_delete_link_start(message: Message, state: FSMContext):
    """Start admin link deletion."""
    if not is_admin(message.from_user.id):
        return

    await state.set_state(AdminDeleteLink.waiting_link_id)
    await message.answer("🗑 Send the Link ID to delete:", reply_markup=cancel_keyboard())


@router.message(AdminDeleteLink.waiting_link_id)
async def admin_delete_link_process(message: Message, state: FSMContext):
    """Process admin link deletion."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=admin_keyboard())
        return

    link_id = message.text.strip()
    if db.delete_link(link_id):
        await state.clear()
        await message.answer(f"✅ Link `{link_id}` deleted!", parse_mode="Markdown",
                             reply_markup=admin_keyboard())
    else:
        await message.answer("❌ Link not found. Try again:")


@router.message(F.text == "👤 User Stats")
async def admin_user_stats_start(message: Message, state: FSMContext):
    """Start user stats lookup."""
    if not is_admin(message.from_user.id):
        return

    await state.set_state(AdminUserStats.waiting_user_id)
    await message.answer("👤 Send the User ID:", reply_markup=cancel_keyboard())


@router.message(AdminUserStats.waiting_user_id)
async def admin_user_stats_process(message: Message, state: FSMContext):
    """Process user stats lookup."""
    if message.text == "❌ Cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=admin_keyboard())
        return

    try:
        user_id = int(message.text.strip())
        user = db.get_user(user_id)
        if not user:
            await message.answer("❌ User not found.")
            return

        stats = db.get_user_stats(user_id)
        text = (
            f"👤 **User Stats**\n\n"
            f"🆔 ID: {user_id}\n"
            f"📛 Name: {user.get('first_name', 'N/A')}\n"
            f"👤 Username: @{user.get('username', 'N/A')}\n"
            f"📝 Links: {stats.get('links_created', 0)}\n"
            f"👁 Views: {stats.get('total_views', 0)}\n"
            f"❤️ Yes: {stats.get('total_yes', 0)}\n"
            f"📅 Joined: {user.get('joined_at', 'N/A')}\n"
        )
        await state.clear()
        await message.answer(text, parse_mode="Markdown", reply_markup=admin_keyboard())
    except ValueError:
        await message.answer("❌ Invalid User ID. Send a number:")


# ========================
# NOTIFICATION SENDER
# ========================

async def send_yes_notification(user_id: int, crush_name: str, date: str, time: str):
    """Send notification to creator when crush says YES."""
    text = (
        f"🎉 SHE SAID YES ❤️\n\n"
        f"💕 Crush Name: {crush_name}\n"
        f"📅 Date: {date}\n"
        f"⏰ Time: {time}"
    )
    try:
        await bot.send_message(user_id, text)
        db.save_notification(user_id, crush_name, "yes")
    except Exception as e:
        logger.error(f"Failed to send notification to {user_id}: {e}")


# ========================
# BOT STARTUP
# ========================

async def start_bot():
    """Start the bot polling."""
    logger.info("Starting Crush Proposal Bot...")
    await dp.start_polling(bot)


async def stop_bot():
    """Stop the bot."""
    await bot.session.close()
