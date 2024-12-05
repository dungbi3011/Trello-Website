from ..repositories.board_repository import get_board_repository

def get_board_service(board_id):
    result = get_board_repository(board_id)
    return result
