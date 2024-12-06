from ..db import get_db_connection
from ..repositories.board_repository import (
    fetch_board_data,
    update_column_positions,
    update_card_positions,
)


def get_board_service(board_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        rows = fetch_board_data(board_id, cursor)
        if rows:
            board, updated_columns, updated_cards = process_board_data(rows, board_id)
            for position, column_id in updated_columns:
                update_column_positions(position, column_id, cursor)
            for position, card_id in updated_cards:
                update_card_positions(position, card_id, cursor)
            conn.commit()
            return board
        raise Exception("Board not found")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def process_board_data(rows, board_id):
    board = {}
    columns = {}
    column_order_ids = []
    card_order_ids_map = {}
    updated_columns = []
    updated_cards = []

    for row in rows:
        if not board:
            board = {
                "_id": row["_id"],
                "title": row["title"],
                "description": row["description"],
                "type": row["type"],
                "columns": [],
            }
        if row["column_id"]:
            column_id = row["column_id"]
            if column_id not in columns:
                columns[column_id] = {
                    "_id": column_id,
                    "boardId": board_id,
                    "title": row["column_title"],
                    "cardOrderIds": [],
                    "cards": [],
                }
                column_order_ids.append(column_id)
                updated_columns.append((len(column_order_ids), column_id))
                card_order_ids_map[column_id] = []
            if row["card_id"]:
                card = {
                    "_id": row["card_id"],
                    "columnId": column_id,
                    "title": row["card_title"],
                    "description": row["card_description"],
                    "cover": row["card_cover"],
                }
                columns[column_id]["cards"].append(card)
                card_order_ids_map[column_id].append(row["card_id"])
                updated_cards.append(
                    (len(card_order_ids_map[column_id]), row["card_id"])
                )
    for column_id, column in columns.items():
        column["cardOrderIds"] = card_order_ids_map[column_id]
        board["columns"].append(column)

    board["columnOrderIds"] = column_order_ids

    return board, updated_columns, updated_cards
