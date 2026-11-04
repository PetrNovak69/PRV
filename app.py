import os
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI


# ============================================================
# VDF Games Support Tool
# Backend: Flask + Render + OpenAI Responses API
# ============================================================

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024


# ------------------------------------------------------------
# 1. Proměnné prostředí
# ------------------------------------------------------------

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


# ------------------------------------------------------------
# 2. Firemní dokumentace
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DOCUMENTATION_PATH = BASE_DIR / "docs" / "podpora.md"

try:
    documentation = DOCUMENTATION_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    documentation = ""
