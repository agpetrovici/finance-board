import os

from flask import Blueprint, render_template

# from app.backend.models.db import db

# Get the absolute path to the static folder
current_dir = os.path.dirname(os.path.abspath(__file__))
static_folder = os.path.join(current_dir, "static")

bp = Blueprint(
    "imports",
    __name__,
    static_folder=static_folder,
    static_url_path="static",
    template_folder="templates",
    url_prefix="/imports",
)


@bp.route("/", methods=["GET"])
def index() -> str:
    return render_template("imports/index.html")
