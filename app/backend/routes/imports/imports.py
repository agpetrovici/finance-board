import json
import base64
from datetime import date
from decimal import Decimal

from flask import Blueprint, Response
from flask import render_template, jsonify
from flask import request
from flask import current_app
from mindee import Client

from app.backend.models.db import db
from app.backend.models.m_account import Account
from app.backend.routes.imports.utils.bbva.process_bbva import get_new_movements_bbva
from app.backend.routes.imports.utils.binance.get_account_balance import get_account_balance
from app.backend.routes.imports.utils.csb43.get_csb43_movements import get_new_movements_from_BankStatement
from app.backend.routes.imports.utils.csb43.process_csb43 import parse_aes43
from app.backend.routes.imports.utils.get_last_movement import get_last_movement
from app.backend.routes.imports.utils.revolut.process_revolut import get_new_movements_revolut
from app.backend.utils.receipts.prediction import make_receipt_prediction

bp = Blueprint(
    "imports",
    __name__,
    static_folder="static",
    template_folder="templates",
    url_prefix="/imports",
)


@bp.route("/", methods=["GET"])
def index() -> str:
    return render_template("imports/tpl_import_index.html")


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
    new_movements = get_new_movements_bbva(data, last_movement, account_pk)
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
    new_movements = get_new_movements_bbva(data, last_bank_id, account_pk)
    if not new_movements:
        return jsonify({"status": "error", "message": "No new movements."}), 400

    return jsonify({"status": "success", "message": f"Added {len(new_movements)} movements."}), 200


@bp.route("/norma43", methods=["GET"])
def import_norma43() -> str:
    return render_template("imports/tpl_norma43.html")


@bp.route("/from-norma43", methods=["POST"])
def import_norma43_process() -> tuple[Response, int]:
    try:
        files = request.files
        file = files["file"]
        file_content: bytes = file.read()
        bank_statement = parse_aes43(file_content)
    except Exception:
        return jsonify({"status": "error", "message": "Invalid file format."}), 400

    status, messages, new_movements = get_new_movements_from_BankStatement(bank_statement)

    if status:
        # Then save the new movements to the database
        db.session.add_all(new_movements)
        db.session.commit()
        messages.append(f"Added {len(new_movements)} movements in the db.")
        return jsonify({"status": "success", "messages": messages}), 200
    else:
        return jsonify({"status": "error", "messages": messages}), 400


@bp.route("/binance")
def import_binance() -> str:
    return render_template("imports/tpl_binance.html")


@bp.route("/from-binance", methods=["POST"])
def import_from_binance() -> tuple[Response, int]:
    try:
        get_account_balance()
        return jsonify({"status": "success", "message": "Account balance imported successfully."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Account balance import failed: {e}."}), 400


@bp.route("/revolut")
def import_revolut() -> str:
    return render_template("imports/tpl_revolut.html")


@bp.route("/from-revolut", methods=["POST"])
def import_from_revolut() -> tuple[Response, int]:
    data = request.json
    if data is None:
        return jsonify({"status": "error", "message": "No data received."}), 400

    text = data.get("text")

    if text == "":
        return jsonify({"status": "error", "message": "No account pk or text provided."}), 400

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid JSON format."}), 400

    accounts = Account.query.all()

    # Then get the new movements from the dict
    new_movements = get_new_movements_revolut(data, accounts)
    if not new_movements:
        return jsonify({"status": "error", "message": "No new movements."}), 400

    # Then save the new movements to the database
    db.session.add_all(new_movements)
    db.session.commit()
    return jsonify({"status": "success", "message": f"Added {len(new_movements)} movements."}), 200


@bp.route("/receipts")
def import_receipts() -> str:
    return render_template("imports/tpl_receipts.html")


@bp.route("/get-receipt-data", methods=["POST"])
def import_from_receipts() -> tuple[Response, int]:
    file = request.files["receipt"]
    data_input: bytes = file.read()
    file_name = file.filename

    mindee_client = Client(api_key=current_app.config["MINDEE_API_KEY"])
    result = make_receipt_prediction(mindee_client, data_input, file_name)

    # Return the image file encoded in base64 within a JSON response
    data = {}
    if file_name and data_input:
        data["transaction"] = {
            "date": str(_date),
            "amount": str(_amount),
        }

    return jsonify(
        {
            "status": "success",
            "message": "Image processed successfully",
            "data": data,
        }
    ), 200
