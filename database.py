"""
Firebase Firestore database operations for Crush Proposal Bot.
Collections: users, links, views, yes_clicks, settings, banned_users, notifications
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from firebase_config import get_db
from google.cloud.firestore_v1 import FieldFilter


def get_timestamp():
    """Get current UTC timestamp."""
    now = datetime.now(timezone.utc)
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "timestamp": now.isoformat()
    }


# ========================
# USER OPERATIONS
# ========================

def register_user(user_id: int, username: str = "", first_name: str = ""):
    """Register a new user or update existing user info."""
    db = get_db()
    user_ref = db.collection("users").document(str(user_id))
    user_doc = user_ref.get()

    if not user_doc.exists:
        user_ref.set({
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "joined_at": get_timestamp()["timestamp"],
            "links_created": 0,
            "total_views": 0,
            "total_yes": 0
        })
        return True
    else:
        user_ref.update({
            "username": username,
            "first_name": first_name
        })
        return False


def get_user(user_id: int) -> Optional[dict]:
    """Get user data by user_id."""
    db = get_db()
    doc = db.collection("users").document(str(user_id)).get()
    if doc.exists:
        return doc.to_dict()
    return None


def get_all_users() -> list:
    """Get all registered users."""
    db = get_db()
    docs = db.collection("users").stream()
    return [doc.to_dict() for doc in docs]


def get_total_users() -> int:
    """Get total number of registered users."""
    db = get_db()
    docs = db.collection("users").stream()
    return sum(1 for _ in docs)


# ========================
# LINK OPERATIONS
# ========================

def create_link(user_id: int, crush_name: str, creator_name: str,
                message: str = "I have a crush on you! 💕",
                bg_image: str = "", bg_music: str = "",
                emoji: str = "💕") -> str:
    """Create a new crush page link. Returns the unique ID."""
    db = get_db()
    unique_id = uuid.uuid4().hex[:10]

    link_data = {
        "id": unique_id,
        "user_id": user_id,
        "crush_name": crush_name,
        "creator_name": creator_name,
        "message": message,
        "bg_image": bg_image,
        "bg_music": bg_music,
        "emoji": emoji,
        "views": 0,
        "yes_count": 0,
        "no_count": 0,
        "created_at": get_timestamp()["timestamp"]
    }

    db.collection("links").document(unique_id).set(link_data)

    # Update user's link count
    user_ref = db.collection("users").document(str(user_id))
    user_doc = user_ref.get()
    if user_doc.exists:
        current_count = user_doc.to_dict().get("links_created", 0)
        user_ref.update({"links_created": current_count + 1})

    return unique_id


def get_link(link_id: str) -> Optional[dict]:
    """Get link data by unique ID."""
    db = get_db()
    doc = db.collection("links").document(link_id).get()
    if doc.exists:
        return doc.to_dict()
    return None


def get_user_links(user_id: int) -> list:
    """Get all links created by a user."""
    db = get_db()
    docs = db.collection("links").where(
        filter=FieldFilter("user_id", "==", user_id)
    ).stream()
    return [doc.to_dict() for doc in docs]


def delete_link(link_id: str) -> bool:
    """Delete a link by ID."""
    db = get_db()
    doc_ref = db.collection("links").document(link_id)
    doc = doc_ref.get()
    if doc.exists:
        link_data = doc.to_dict()
        # Decrease user's link count
        user_ref = db.collection("users").document(str(link_data["user_id"]))
        user_doc = user_ref.get()
        if user_doc.exists:
            current_count = user_doc.to_dict().get("links_created", 0)
            user_ref.update({"links_created": max(0, current_count - 1)})
        doc_ref.delete()
        return True
    return False


def update_link_field(link_id: str, field: str, value) -> bool:
    """Update a specific field of a link."""
    db = get_db()
    doc_ref = db.collection("links").document(link_id)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({field: value})
        return True
    return False


def get_total_links() -> int:
    """Get total number of links."""
    db = get_db()
    docs = db.collection("links").stream()
    return sum(1 for _ in docs)


# ========================
# VIEW OPERATIONS
# ========================

def record_view(link_id: str, ip_address: str = ""):
    """Record a page view."""
    db = get_db()
    ts = get_timestamp()

    # Add view record
    db.collection("views").add({
        "link_id": link_id,
        "ip_address": ip_address,
        "date": ts["date"],
        "time": ts["time"],
        "timestamp": ts["timestamp"]
    })

    # Increment view count on link
    link_ref = db.collection("links").document(link_id)
    link_doc = link_ref.get()
    if link_doc.exists:
        current_views = link_doc.to_dict().get("views", 0)
        link_ref.update({"views": current_views + 1})

        # Update user's total views
        user_id = link_doc.to_dict().get("user_id")
        if user_id:
            user_ref = db.collection("users").document(str(user_id))
            user_doc = user_ref.get()
            if user_doc.exists:
                total_views = user_doc.to_dict().get("total_views", 0)
                user_ref.update({"total_views": total_views + 1})


def get_total_views() -> int:
    """Get total number of views across all links."""
    db = get_db()
    docs = db.collection("views").stream()
    return sum(1 for _ in docs)


# ========================
# YES CLICK OPERATIONS
# ========================

def record_yes_click(link_id: str, ip_address: str = "") -> dict:
    """Record a 'Yes' click and return click data."""
    db = get_db()
    ts = get_timestamp()

    link_ref = db.collection("links").document(link_id)
    link_doc = link_ref.get()

    if not link_doc.exists:
        return {}

    link_data = link_doc.to_dict()

    click_data = {
        "link_id": link_id,
        "user_id": link_data.get("user_id"),
        "crush_name": link_data.get("crush_name"),
        "creator_name": link_data.get("creator_name"),
        "ip_address": ip_address,
        "date": ts["date"],
        "time": ts["time"],
        "timestamp": ts["timestamp"]
    }

    # Save yes click
    db.collection("yes_clicks").add(click_data)

    # Increment yes count on link
    current_yes = link_data.get("yes_count", 0)
    link_ref.update({"yes_count": current_yes + 1})

    # Update user's total yes count
    user_id = link_data.get("user_id")
    if user_id:
        user_ref = db.collection("users").document(str(user_id))
        user_doc = user_ref.get()
        if user_doc.exists:
            total_yes = user_doc.to_dict().get("total_yes", 0)
            user_ref.update({"total_yes": total_yes + 1})

    return click_data


def get_total_yes_clicks() -> int:
    """Get total number of yes clicks."""
    db = get_db()
    docs = db.collection("yes_clicks").stream()
    return sum(1 for _ in docs)


# ========================
# BAN OPERATIONS
# ========================

def ban_user(user_id: int, reason: str = ""):
    """Ban a user."""
    db = get_db()
    db.collection("banned_users").document(str(user_id)).set({
        "user_id": user_id,
        "reason": reason,
        "banned_at": get_timestamp()["timestamp"]
    })


def unban_user(user_id: int) -> bool:
    """Unban a user."""
    db = get_db()
    doc_ref = db.collection("banned_users").document(str(user_id))
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.delete()
        return True
    return False


def is_banned(user_id: int) -> bool:
    """Check if a user is banned."""
    db = get_db()
    doc = db.collection("banned_users").document(str(user_id)).get()
    return doc.exists


def get_banned_users() -> list:
    """Get all banned users."""
    db = get_db()
    docs = db.collection("banned_users").stream()
    return [doc.to_dict() for doc in docs]


# ========================
# NOTIFICATION OPERATIONS
# ========================

def save_notification(user_id: int, crush_name: str, notification_type: str = "yes"):
    """Save a notification record."""
    db = get_db()
    ts = get_timestamp()
    db.collection("notifications").add({
        "user_id": user_id,
        "crush_name": crush_name,
        "type": notification_type,
        "date": ts["date"],
        "time": ts["time"],
        "timestamp": ts["timestamp"]
    })


def get_user_notifications(user_id: int) -> list:
    """Get notifications for a user."""
    db = get_db()
    docs = db.collection("notifications").where(
        filter=FieldFilter("user_id", "==", user_id)
    ).stream()
    return [doc.to_dict() for doc in docs]


# ========================
# SETTINGS OPERATIONS
# ========================

def get_setting(key: str, default=None):
    """Get a bot setting."""
    db = get_db()
    doc = db.collection("settings").document(key).get()
    if doc.exists:
        return doc.to_dict().get("value", default)
    return default


def set_setting(key: str, value):
    """Set a bot setting."""
    db = get_db()
    db.collection("settings").document(key).set({"value": value})


# ========================
# STATS
# ========================

def get_admin_stats() -> dict:
    """Get admin dashboard statistics."""
    return {
        "total_users": get_total_users(),
        "total_links": get_total_links(),
        "total_views": get_total_views(),
        "total_yes_clicks": get_total_yes_clicks()
    }


def get_user_stats(user_id: int) -> dict:
    """Get statistics for a specific user."""
    user = get_user(user_id)
    if not user:
        return {}
    links = get_user_links(user_id)
    return {
        "links_created": len(links),
        "total_views": sum(link.get("views", 0) for link in links),
        "total_yes": sum(link.get("yes_count", 0) for link in links),
        "links": links
    }
