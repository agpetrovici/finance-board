import os

from flask import Blueprint, render_template

# from app.backend.models.db import db

# Get the absolute path to the static folder
current_dir = os.path.dirname(os.path.abspath(__file__))
static_folder = os.path.join(current_dir, "static")

bp = Blueprint("dashboard", __name__, static_folder=static_folder, static_url_path="/dashboard/static", template_folder="templates", url_prefix="/")


@bp.route("/", methods=["GET"])
def get_dashboard() -> str:
    return render_template("dashboard/dashboard.html")


@bp.route("/test-dashboard", methods=["GET"])
def test_get_dashboard() -> str:
    return render_template("dashboard/test_dashboard.html")
