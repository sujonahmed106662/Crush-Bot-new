"""
FastAPI web application for Crush Proposal Bot.
Serves crush pages, handles yes/no clicks, admin panel, and bot webhook.
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import database as db
from firebase_config import initialize_firebase
from image_generator import generate_yes_image
from bot import bot, dp, send_yes_notification, start_bot, stop_bot, BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase on startup
initialize_firebase()

# Ensure directories exist
os.makedirs("static", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/images", exist_ok=True)
os.makedirs("static/music", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("generated", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage bot lifecycle with FastAPI."""
    # Start bot polling in background
    bot_task = asyncio.create_task(start_bot())
    logger.info("Bot polling started")
    yield
    # Cleanup
    await stop_bot()
    bot_task.cancel()
    logger.info("Bot stopped")


app = FastAPI(title="Crush Proposal Bot", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/generated", StaticFiles(directory="generated"), name="generated")

# Templates
templates = Jinja2Templates(directory="templates")


# ========================
# CRUSH PAGE ROUTES
# ========================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page."""
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/p/{link_id}", response_class=HTMLResponse)
async def crush_page(request: Request, link_id: str):
    """Serve a crush proposal page."""
    link = db.get_link(link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Page not found")

    # Record view
    client_ip = request.client.host if request.client else ""
    db.record_view(link_id, client_ip)

    return templates.TemplateResponse("crush_page.html", {
        "request": request,
        "link": link,
        "crush_name": link.get("crush_name", ""),
        "creator_name": link.get("creator_name", ""),
        "message": link.get("message", "I have a crush on you! 💕"),
        "bg_image": link.get("bg_image", ""),
        "bg_music": link.get("bg_music", ""),
        "emoji": link.get("emoji", "💕"),
        "link_id": link_id
    })


@app.post("/api/yes/{link_id}")
async def handle_yes_click(request: Request, link_id: str):
    """Handle YES button click."""
    link = db.get_link(link_id)
    if not link:
        return JSONResponse({"error": "Link not found"}, status_code=404)

    client_ip = request.client.host if request.client else ""
    click_data = db.record_yes_click(link_id, client_ip)

    if click_data:
        # Send notification to creator
        asyncio.create_task(
            send_yes_notification(
                user_id=click_data["user_id"],
                crush_name=click_data["crush_name"],
                date=click_data["date"],
                time=click_data["time"]
            )
        )

        # Generate and send image
        asyncio.create_task(
            send_yes_image_to_user(
                user_id=click_data["user_id"],
                crush_name=click_data["crush_name"],
                creator_name=click_data["creator_name"],
                date=click_data["date"],
                time=click_data["time"]
            )
        )

    return JSONResponse({
        "success": True,
        "message": "🎉 SHE SAID YES ❤️",
        "crush_name": link.get("crush_name", "")
    })


@app.post("/api/no/{link_id}")
async def handle_no_click(request: Request, link_id: str):
    """Handle NO button click (just for tracking)."""
    link = db.get_link(link_id)
    if not link:
        return JSONResponse({"error": "Link not found"}, status_code=404)

    # Increment no count
    current_no = link.get("no_count", 0)
    db.update_link_field(link_id, "no_count", current_no + 1)

    return JSONResponse({"success": True})


async def send_yes_image_to_user(user_id: int, crush_name: str, creator_name: str,
                                  date: str, time: str):
    """Generate and send the congratulations image to the user via Telegram."""
    try:
        from aiogram.types import BufferedInputFile

        image_buffer = generate_yes_image(crush_name, creator_name, date, time)
        image_data = image_buffer.read()

        photo = BufferedInputFile(image_data, filename="congratulations.png")
        caption = (
            f"🎉 **SHE SAID YES** ❤️\n\n"
            f"💕 Crush: {crush_name}\n"
            f"👤 By: {creator_name}\n"
            f"📅 {date} ⏰ {time}\n\n"
            f"🥰 Congratulations!"
        )
        await bot.send_photo(user_id, photo=photo, caption=caption, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to send image to {user_id}: {e}")


# ========================
# ADMIN WEB PANEL
# ========================

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Admin web dashboard."""
    stats = db.get_admin_stats()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "stats": stats
    })


@app.get("/api/admin/stats")
async def api_admin_stats():
    """API endpoint for admin stats."""
    stats = db.get_admin_stats()
    return JSONResponse(stats)


# ========================
# HEALTH CHECK
# ========================

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway."""
    return JSONResponse({"status": "ok", "bot": "running"})
