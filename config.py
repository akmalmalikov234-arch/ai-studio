import os

APP_NAME = os.getenv("APP_NAME", "AI Studio")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")

SECRET_KEY = os.getenv("SECRET_KEY", "")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///ai_studio.db"
)

MAX_LOGIN_ATTEMPTS = 5
SESSION_TIMEOUT_MINUTES = 60

FREE_PLAN = {
    "name": "Free",
    "videos": 0,
    "images": 0
}

PLANS = {
    "small": {
        "name": "Kichik",
        "videos": 5,
        "period_days": 4,
        "price": 0
    },
    "medium": {
        "name": "O‘rta",
        "videos": 20,
        "period_days": 30,
        "price": 0
    },
    "large": {
        "name": "Katta",
        "videos": 100,
        "period_days": 30,
        "price": 0
    }
}
