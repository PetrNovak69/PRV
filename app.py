
import os
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai


# ============================================================
# VDF Games Support Tool
# Backend: Flask + Render + Google Gemini API
# ============================================================

app = Flask(__name__)
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 32 * 1024


# ------------------------------------------------------------
# 1. Proměnné prostředí
# ------------------------------------------------------------

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

client = (
    genai.Client(api_key=GEMINI_API_KEY)
    if GEMINI_API_KEY
    else None
)


# ------------------------------------------------------------
# 2. Firemní dokumentace
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DOCUMENTATION_PATH = (
    BASE_DIR / "docs" / "podpora.md"
)

try:
    documentation = DOCUMENTATION_PATH.read_text(
        encoding="utf-8"
    )
except FileNotFoundError:
    documentation = ""

    print(
        "WARNING: Dokumentace docs/podpora.md nebyla nalezena."
    )


# ------------------------------------------------------------
# 3. Systémové instrukce
# ------------------------------------------------------------

SYSTEM_PROMPT = """
Jsi AI asistent technické podpory společnosti VDF Games.

Tvým úkolem je pomáhat zákazníkům s:
- Technickými problémy
- Hrami a jejich fungováním
- Řešením chyb
- Otázkami ohledně služeb VDF Games

Odpovídej česky, pokud zákazník nepoužije jiný jazyk.

Buď přátelský, profesionální a stručný.

Pokud odpověď najdeš v přiložené firemní dokumentaci,
použij ji jako hlavní zdroj informací.

Nevymýšlej si informace o společnosti ani jejích produktech.

Pokud odpověď neznáš, přiznej to.

------------------------------------------------------------

FIREMNÍ DOKUMENTACE:

""" + documentation


# ------------------------------------------------------------
# 4. Úvodní stránka
# ------------------------------------------------------------

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status": "online",
        "service": "VDF Games Support Tool",
        "ai": "Google Gemini",
        "model": GEMINI_MODEL
    })


# ------------------------------------------------------------
# 5. Health check
# ------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok"
    })


# ------------------------------------------------------------
# 6. AI CHAT ENDPOINT
# ------------------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def chat():

    # Kontrola API klíče
    if client is None:
        return jsonify({
            "error": "Chybí GEMINI_API_KEY na serveru."
        }), 500

    # Načtení požadavku
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Neplatný JSON požadavek."
        }), 400

    # Podpora různých názvů vstupního pole
    message = (
        data.get("message")
        or data.get("question")
        or data.get("prompt")
    )

    if not isinstance(message, str) or not message.strip():
        return jsonify({
            "error": "Zpráva nesmí být prázdná."
        }), 400

    message = message.strip()

    try:

        # Volání Google Gemini API
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                SYSTEM_PROMPT,
                "DOTAZ ZÁKAZNÍKA:\n" + message
            ]
        )

        answer = response.text

        if not answer:
            return jsonify({
                "error": "Gemini nevrátil žádnou odpověď."
            }), 502

        return jsonify({
            "success": True,
            "response": answer,
            "answer": answer
        })

    except Exception as e:

        print("Gemini API error:", str(e))

        return jsonify({
            "success": False,
            "error": "Při komunikaci s AI nastala chyba."
        }), 500


# ------------------------------------------------------------
# 7. Spuštění aplikace
# ------------------------------------------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
