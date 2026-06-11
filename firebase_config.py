import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

_app = None
_db = None


def initialize_firebase():
    """Initialize Firebase from FIREBASE_CREDENTIALS environment variable."""
    global _app, _db

    if _app is not None:
        return _db

    creds_json = os.environ.get("FIREBASE_CREDENTIALS")
    if not creds_json:
        raise ValueError("FIREBASE_CREDENTIALS environment variable is not set")

    creds_dict = json.loads(creds_json)
    cred = credentials.Certificate(creds_dict)
    _app = firebase_admin.initialize_app(cred)
    _db = firestore.client()
    return _db


def get_db():
    """Get Firestore database client."""
    global _db
    if _db is None:
        _db = initialize_firebase()
    return _db
