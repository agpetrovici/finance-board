import json

from flask import Blueprint, Response
from flask import render_template, jsonify
from flask import request

from app.backend.models.account import Account
from app.backend.models.db import db
from app.backend.routes.imports.utils.get_last_movement import get_last_movement
from app.backend.routes.imports.utils.process_bbva import get_new_movements

bp = Blueprint(
    "imports",
    __name__,
    static_folder="static",
    template_folder="templates",
    url_prefix="/imports",
)


@bp.route("/", methods=["GET"])
def index() -> str:
    return render_template("imports/index.html")


@bp.route("/bbva", methods=["GET"])
def import_bbva() -> str:
    accounts = Account.query.all()
    return render_template("imports/tpl_bbva.html", accounts=accounts)


@bp.route("/from-bbva", methods=["POST"])
def import_bbva_process() -> tuple[Response, int]:
    data = request.json
    if data is None:
        return jsonify({"status": "error", "message": "No data received."}), 400

    account_pk = data.get("accountPk")
    text = data.get("text")

    if account_pk == "" or text == "":
        return jsonify({"status": "error", "message": "No account pk or text provided."}), 400

    try:
        account_pk = int(account_pk)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid account pk."}), 400

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid JSON format."}), 400

    # First get the last movement in the database so I know from where to get the data from the dict
    last_movement = get_last_movement(account_pk)
    if last_movement is None:
        return jsonify({"status": "error", "message": "No last bank id."}), 400

    # Then get the new movements from the dict
    new_movements = get_new_movements(data, last_movement, account_pk)
    if not new_movements:
        return jsonify({"status": "error", "message": "No new movements."}), 400

    # Then save the new movements to the database
    db.session.add_all(new_movements)
    db.session.commit()
    return jsonify({"status": "success", "message": f"Added {len(new_movements)} movements."}), 200


@bp.route("/test-from-bbva", methods=["POST"])
def test_import_bbva_process() -> tuple[Response, int]:
    data = request.json
    if data is None:
        return jsonify({"status": "error", "message": "No data received."}), 400

    account_pk = data.get("accountPk")
    text = data.get("text")

    if account_pk == "" or text == "":
        return jsonify({"status": "error", "message": "No account pk or text provided."}), 400

    try:
        account_pk = int(account_pk)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid account pk."}), 400

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid JSON format."}), 400

    # First get the last movement in the database so I know from where to get the data from the dict
    last_bank_id = get_last_movement(account_pk)
    if last_bank_id is None:
        return jsonify({"status": "error", "message": "No last bank id."}), 400

    # Then get the new movements from the dict
    new_movements = get_new_movements(data, last_bank_id, account_pk)
    if not new_movements:
        return jsonify({"status": "error", "message": "No new movements."}), 400

    return jsonify({"status": "success", "message": f"Added {len(new_movements)} movements."}), 200

