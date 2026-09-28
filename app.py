import os
import base64
from io import BytesIO

from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

# =========================================================
# GEMINI
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None


# =========================================================
# FRONTEND
# =========================================================

HTML = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>AI Studio</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background:
                radial-gradient(circle at top left, #263b80, transparent 35%),
                radial-gradient(circle at bottom right, #63258c, transparent 35%),
                #080b16;
            color: white;
            min-height: 100vh;
        }

        .header {
            padding: 22px;
            text-align: center;
        }

        .logo {
            font-size: 32px;
            font-weight: 900;
            letter-spacing: 1px;
        }

        .subtitle {
            color: #aeb6d4;
            margin-top: 7px;
        }

        .container {
            width: min(1000px, 94%);
            margin: auto;
            padding-bottom: 50px;
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            flex-wrap: wrap;
        }

        button {
            border: 0;
            border-radius: 14px;
            padding: 13px 18px;
            cursor: pointer;
            font-weight: 700;
            color: white;
            background: #202844;
        }

        button.active {
            background: linear-gradient(135deg, #6d5dfc, #a64cff);
        }

        .card {
            background: rgba(17, 23, 43, .88);
            border: 1px solid rgba(255,255,255,.08);
            border-radius: 24px;
            padding: 25px;
            box-shadow: 0 20px 60px rgba(0,0,0,.25);
            margin-bottom: 20px;
        }

        h2 {
            margin-top: 0;
        }

        textarea {
            width: 100%;
            min-height: 150px;
            resize: vertical;
            border: 1px solid #303955;
            border-radius: 16px;
            background: #0d1223;
            color: white;
            padding: 17px;
            outline: none;
            font-size: 16px;
        }

        textarea:focus {
            border-color: #795cff;
        }

        .generate {
            margin-top: 14px;
            width: 100%;
            background: linear-gradient(135deg, #715cff, #b044ff);
            font-size: 17px;
            padding: 16px;
        }

        .result {
            margin-top: 20px;
            padding: 18px;
            background: #0b1020;
            border-radius: 16px;
            white-space: pre-wrap;
            line-height: 1.6;
            min-height: 60px;
        }

        .result img {
            width: 100%;
            max-width: 900px;
            border-radius: 18px;
            display: block;
            margin: auto;
        }

        .hidden {
            display: none;
        }

        .status {
            font-size: 14px;
            color: #aeb6d4;
            margin-top: 10px;
        }

        .error {
            color: #ff7777;
        }

        .success {
            color: #73e6a0;
        }
    </style>
</head>

<body>

<div class="header">
    <div class="logo">✨ AI Studio</div>
    <div class="subtitle">
        Chat • Image • AI
    </div>
</div>

<div class="container">

    <div class="tabs">
        <button class="tab active" onclick="showTab('chat', this)">
            💬 AI Chat
        </button>

        <button class="tab" onclick="showTab('image', this)">
            🖼️ Rasm yaratish
        </button>
    </div>


    <!-- CHAT -->

    <div id="chat" class="card">

        <h2>💬 AI Chat</h2>

        <textarea
            id="chatPrompt"
            placeholder="Savolingizni yozing..."
        ></textarea>

        <button class="generate" onclick="chat()">
            🚀 AI'ga yuborish
        </button>

        <div id="chatStatus" class="status"></div>

        <div id="chatResult" class="result">
            Javob shu yerda chiqadi.
        </div>

    </div>


    <!-- IMAGE -->

    <div id="image" class="card hidden">

        <h2>🖼️ AI Rasm Generator</h2>

        <textarea
            id="imagePrompt"
            placeholder="Masalan: Futuristik Toshkent shahri, kechasi, neon chiroqlar, cinematic, ultra detailed..."
        ></textarea>

        <button class="generate" onclick="generateImage()">
            🎨 Rasm yaratish
        </button>

        <div id="imageStatus" class="status"></div>

        <div id="imageResult" class="result">
            Rasm shu yerda chiqadi.
        </div>

    </div>

</div>


<script>

function showTab(name, button) {

    document.getElementById("chat").classList.add("hidden");
    document.getElementById("image").classList.add("hidden");

    document.getElementById(name).classList.remove("hidden");

    document.querySelectorAll(".tab").forEach(
        x => x.classList.remove("active")
    );

    button.classList.add("active");
}


// =========================================================
// CHAT
// =========================================================

async function chat() {

    const prompt =
        document.getElementById("chatPrompt").value.trim();

    const status =
        document.getElementById("chatStatus");

    const result =
        document.getElementById("chatResult");

    if (!prompt) {
        status.innerHTML =
            '<span class="error">Savol yozing.</span>';
        return;
    }

    status.innerHTML = "⏳ AI javob tayyorlamoqda...";
    result.innerText = "";

    try {

        const response = await fetch("/api/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                prompt: prompt
            })

        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Xatolik yuz berdi"
            );
        }

        result.innerText = data.answer;

        status.innerHTML =
            '<span class="success">✅ Tayyor</span>';

    } catch (error) {

        status.innerHTML =
            '<span class="error">' +
            error.message +
            '</span>';

    }
}


// =========================================================
// IMAGE
// =========================================================

async function generateImage() {

    const prompt =
        document.getElementById("imagePrompt").value.trim();

    const status =
        document.getElementById("imageStatus");

    const result =
        document.getElementById("imageResult");

    if (!prompt) {
        status.innerHTML =
            '<span class="error">Prompt yozing.</span>';
        return;
    }

    status.innerHTML =
        "⏳ Rasm yaratilmoqda... Bu biroz vaqt olishi mumkin.";

    result.innerHTML = "";

    try {

        const response = await fetch(
            "/api/image",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    prompt: prompt
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Rasm yaratilmadi"
            );
        }

        if (!data.image) {
            throw new Error(
                "Gemini rasm qaytarmadi."
            );
        }

        const img = document.createElement("img");

        img.src =
            "data:" +
            data.mime_type +
            ";base64," +
            data.image;

        result.appendChild(img);

        status.innerHTML =
            '<span class="success">✅ Rasm tayyor</span>';

    } catch (error) {

        status.innerHTML =
            '<span class="error">' +
            error.message +
            '</span>';

    }
}

</script>

</body>
</html>
"""


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template_string(HTML)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "gemini_configured": bool(GEMINI_API_KEY)
    })


# =========================================================
# CHAT API
# =========================================================

@app.route("/api/chat", methods=["POST"])
def api_chat():

    if not client:

        return jsonify({
            "error":
                "GEMINI_API_KEY Render Environment Variables "
                "ichida sozlanmagan."
        }), 500

    data = request.get_json(silent=True) or {}

    prompt = str(
        data.get("prompt", "")
    ).strip()

    if not prompt:

        return jsonify({
            "error": "Prompt bo'sh."
        }), 400

    if len(prompt) > 12000:

        return jsonify({
            "error":
                "Prompt juda uzun. 12000 belgidan oshirmang."
        }), 400

    try:

        response = client.models.generate_content(

            model="gemini-3.8-flash",

            contents=prompt,

            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=4096
            )
        )

        answer = response.text

        if not answer:
            answer = "AI javob qaytarmadi."

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        return jsonify({
            "error":
                "Gemini API xatosi: " + str(e)
        }), 500


# =========================================================
# IMAGE API
# =========================================================

@app.route("/api/image", methods=["POST"])
def api_image():

    if not client:

        return jsonify({
            "error":
                "GEMINI_API_KEY sozlanmagan."
        }), 500

    data = request.get_json(silent=True) or {}

    prompt = str(
        data.get("prompt", "")
    ).strip()

    if not prompt:

        return jsonify({
            "error": "Rasm promptini yozing."
        }), 400

    if len(prompt) > 8000:

        return jsonify({
            "error":
                "Prompt juda uzun."
        }), 400

    try:

        response = client.models.generate_content(

            model="gemini-2.5-flash-image",

            contents=prompt,

            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"]
            )
        )

        if not response.candidates:

            return jsonify({
                "error":
                    "Gemini hech qanday natija qaytarmadi."
            }), 500

        for candidate in response.candidates:

            if not candidate.content:
                continue

            for part in candidate.content.parts:

                if getattr(part, "inline_data", None):

                    image_data = part.inline_data.data

                    if isinstance(
                        image_data,
                        str
                    ):
                        image_data = base64.b64decode(
                            image_data
                        )

                    return jsonify({

                        "image":
                            base64.b64encode(
                                image_data
                            ).decode("utf-8"),

                        "mime_type":
                            part.inline_data.mime_type
                            or "image/png"
                    })

        return jsonify({
            "error":
                "Gemini rasm yaratmadi."
        }), 500

    except Exception as e:

        return jsonify({
            "error":
                "Gemini Image API xatosi: " + str(e)
        }), 500


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "error": "Sahifa topilmadi."
    }), 404


@app.errorhandler(500)
def server_error(error):

    return jsonify({
        "error": "Server xatosi."
    }), 500


# =========================================================
# LOCAL RUN
# =========================================================

if __name__ == "__main__":

    port = int(
        os.getenv("PORT", "5000")
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
