from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "name": "AI Studio",
        "message": "AI Studio server ishlayapti!"
    })


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
