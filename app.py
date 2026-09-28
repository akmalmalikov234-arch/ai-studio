from flask import Flask, jsonify
from database import init_database

app = Flask(__name__)

init_database()


@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "app": "AI Studio",
        "message": "AI Studio server ishlayapti!"
    })


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "database": "connected"
    })


@app.route("/api/plans")
def plans():
    return jsonify({
        "plans": [
            {
                "id": "small",
                "name": "Kichik",
                "price": 0,
                "videos": 5,
                "days": 4
            },
            {
                "id": "medium",
                "name": "O‘rta",
                "price": 0,
                "videos": 20,
                "days": 30
            },
            {
                "id": "large",
                "name": "Katta",
                "price": 0,
                "videos": 100,
                "days": 30
            }
        ]
    })


@app.route("/api/features")
def features():
    return jsonify({
        "chat": True,
        "image_generation": True,
        "video_generation": True,
        "subscriptions": True,
        "admin_panel": True
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
