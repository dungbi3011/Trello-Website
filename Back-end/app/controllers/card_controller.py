from flask import Blueprint, jsonify, request
from ..services.card_service import (
    add_card_service,
    remove_card_service,
    update_card_service,
    move_cards_in_column_service,
    move_cards_between_different_columns_service,
)

card_bp = Blueprint("card", __name__)


@card_bp.route("/boards/<board_id>/columns/<column_id>/cards", methods=["POST"])
def add_card(board_id, column_id):
    data = request.get_json()
    try:
        new_card = add_card_service(board_id, column_id, data)
        return jsonify(new_card), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@card_bp.route(
    "/boards/<board_id>/columns/<column_id>/cards/<card_id>", methods=["DELETE"]
)
def remove_card(board_id, column_id, card_id):
    try:
        message = remove_card_service(board_id, column_id, card_id)
        return jsonify(message), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@card_bp.route(
    "/boards/<board_id>/columns/<column_id>/cards/<card_id>", methods=["PUT"]
)
def update_card(board_id, column_id, card_id):
    data = request.get_json()
    try:
        new_card = update_card_service(board_id, column_id, card_id, data)
        return jsonify(new_card), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@card_bp.route("/boards/<board_id>/columns/<column_id>/cards/move", methods=["PATCH"])
def move_cards_in_column(board_id, column_id):
    data = request.get_json()
    try:
        message = move_cards_in_column_service(board_id, column_id, data)
        return jsonify(message), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@card_bp.route(
    "/boards/<board_id>/columns/<from_column_id>/cards/<card_id>/move",
    methods=["PATCH"],
)
def move_cards_between_different_columns(board_id, from_column_id, card_id):
    data = request.get_json()
    try:
        message = move_cards_between_different_columns_service(board_id, from_column_id, card_id, data)
        return jsonify(message), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
