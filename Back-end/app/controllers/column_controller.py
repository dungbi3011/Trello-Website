from flask import Blueprint, jsonify, request
from ..services.column_service import (
    add_column_service,
    remove_column_service,
    update_column_service,
    update_column_order_service
)

column_bp = Blueprint("column", __name__)


@column_bp.route("/boards/<board_id>/columns", methods=["POST"])
def add_column(board_id):
    data = request.get_json()
    try:
        new_column = add_column_service(board_id, data)
        return jsonify(new_column), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@column_bp.route("/boards/<board_id>/columns/<column_id>", methods=["DELETE"])
def remove_column(board_id, column_id):
    try:
        message = remove_column_service(board_id, column_id)
        return jsonify(message), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@column_bp.route("/boards/<board_id>/columns/<column_id>", methods=["PUT"])
def update_column(board_id, column_id):
    data = request.get_json()
    try:
        new_column = update_column_service(board_id, column_id, data)
        return jsonify(new_column), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@column_bp.route("/boards/<board_id>/columns/move", methods=["PATCH"])
def update_column_order(board_id):
    data = request.get_json()
    try:
        message = update_column_order_service(board_id, data)
        return jsonify(message), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500