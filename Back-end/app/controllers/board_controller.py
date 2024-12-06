from flask import Blueprint, jsonify
from ..services.board_service import get_board_service

board_bp = Blueprint("board", __name__)


@board_bp.route("/boards/<board_id>", methods=["GET"])
def get_board(board_id):
    try:
        result = get_board_service(board_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404
