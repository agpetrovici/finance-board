from flask import Blueprint, render_template

# from app.backend.models.db import db

bp = Blueprint("dashboard", __name__, static_folder="static", template_folder="templates", url_prefix="/")


@bp.route("/", methods=["GET"])
def get_dashboard():
    return render_template("dashboard/index.html")
