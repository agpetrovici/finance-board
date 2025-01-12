import os

from flask import Blueprint, Response, jsonify

# from app.backend.models.db import db

# Get the absolute path to the static folder
current_dir = os.path.dirname(os.path.abspath(__file__))
static_folder = os.path.join(current_dir, "static")

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/get-bank-statement", methods=["POST"])
def get_dashboard() -> Response:
    return jsonify({"message": "Hello, World!"})


@bp.route("/test-get-bank-statement", methods=["POST"])
def test_get_dashboard() -> Response:
    datasets = [
        {
            "label": "Income",
            "data": [1500, 2000, 1800, 2200, 2600, 2400],
            "borderColor": "rgb(75, 192, 192)",
            "tension": 0.1,
        },
        {
            "label": "Expenses",
            "data": [1200, 1800, 1600, 2000, 2200, 2100],
            "borderColor": "rgb(255, 99, 132)",
            "tension": 0.1,
        },
    ]

    labels = ["January", "February", "March", "April", "May", "June"]

    output = {
        "datasets": datasets,
        "labels": labels,
    }
    return jsonify(output)
