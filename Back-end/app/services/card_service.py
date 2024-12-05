from ..db import get_db_connection
from ..repositories.card_repository import (
    add_card_repository,
    remove_card_repository,
    update_card_repository,
    move_cards_in_column_repository,
    move_cards_between_different_columns_repository
)


def add_card_service(board_id, column_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        new_card = add_card_repository(board_id, column_id)
        conn.commit()
        return new_card
    except Exception as e:
        conn.rollback()  # Quay trở lại trạng thái ban đầu
        raise e
    finally:
        cursor.close()
        conn.close()


def remove_card_service(board_id, column_id, card_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        message = remove_card_repository(board_id, column_id, card_id)
        conn.commit()
        return message
    except Exception as e:
        conn.rollback()  # Quay trở lại trạng thái ban đầu
        raise e
    finally:
        cursor.close()
        conn.close()


def update_card_service(board_id, column_id, card_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        new_card = update_card_repository(board_id, column_id, card_id)
        conn.commit()
        return new_card
    except Exception as e:
        conn.rollback()  # Quay trở lại trạng thái ban đầu
        raise e
    finally:
        cursor.close()
        conn.close()


def move_cards_in_column_service(board_id, column_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        message = move_cards_in_column_repository(board_id, column_id)
        conn.commit()
        return message
    except Exception as e:
        conn.rollback()  # Quay trở lại trạng thái ban đầu
        raise e
    finally:
        cursor.close()
        conn.close()


def move_cards_between_different_columns_service(board_id, from_column_id, card_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        message = move_cards_between_different_columns_repository(board_id, from_column_id, card_id)
        conn.commit()
        return message
    except Exception as e:
        conn.rollback()  # Quay trở lại trạng thái ban đầu
        raise e
    finally:
        cursor.close()
        conn.close()