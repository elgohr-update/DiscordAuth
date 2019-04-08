import random
import string
import os

from flask import Flask, redirect, url_for, abort
from flask_dance.contrib.google import make_google_blueprint, google

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]
app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.environ["GOOGLE_CLIENT_ID"]
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.environ["GOOGLE_CLIENT_SECRET"]
google_bp = make_google_blueprint(scope=["profile", "email"])
app.register_blueprint(google_bp, url_prefix="/login")

TOKENS = {}


@app.route("/")
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v1/userinfo")
    email = resp.json()["email"]
    if not email.endswith("@mun.ca"):
        return "You must use a MUN email address to sign in."
    else:
        prefix = email.split("@")[0]
        if prefix not in TOKENS:
            TOKENS[prefix] = "".join([random.choice(string.ascii_letters) for _ in range(20)])
        return f"Identity verified. Please return to the Discord and run the command: !identity verify {TOKENS[prefix]}"


@app.route("/identity/<token>")
def identity(token):
    for ident, t in TOKENS.items():
        if t == token:
            return ident
    abort(404)