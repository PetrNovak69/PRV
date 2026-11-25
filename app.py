
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
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


# ------------------------------------------------------------
# 2. Firemní dokumentace
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DOCUMENTATION_PATH = BASE_DIR / "docs" / "podpora.md"

try:
    documentation = DOCUMENTATION_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    documentation = ""
