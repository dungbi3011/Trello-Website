from ..db import get_db_connection
from ..repositories.column_repository import (
    add_column_repository,
    remove_column_repository,
    update_column_repository,
    update_column_order_repository,
)


def add_column_service(board_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        new_column = add_column_repository(board_id)
        conn.commit()
        return new_column
    except Exception as e:
        conn.rollback()  # Quay trở lại trạng thái ban đầu
        raise e
    finally:
        cursor.close()
        conn.close()


def remove_column_service(board_id, column_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        message = remove_column_repository(board_id, column_id)
        conn.commit()
        return message
    except Exception as e:
        conn.rollback()  # Quay trở lại trạng thái ban đầu
        raise e
    finally:
        cursor.close()
        conn.close()


def update_column_service(board_id, column_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        new_column = update_column_repository(board_id, column_id)
        conn.commit()
        return new_column
    except Exception as e:
        conn.rollback()  # Quay trở lại trạng thái ban đầu
        raise e
    finally:
        cursor.close()
        conn.close()


def update_column_order_service(board_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        message = update_column_order_repository(board_id)
        conn.commit()
        return message
    except Exception as e:
        conn.rollback()  # Quay trở lại trạng thái ban đầu
        raise e
    finally:
        cursor.close()
        conn.close()

