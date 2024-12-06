import uuid
from ..db import get_db_connection
from ..repositories.column_repository import (
    fetch_max_column_position,
    insert_column,
    delete_column,
    update_column,
    update_card_position,
    fetch_card_query,
    update_position_query,
)


def add_column_service(board_id, data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        result = fetch_max_column_position(board_id, cursor)
        max_position = (
            result["max_position"]
            if result and result["max_position"] is not None
            else 0
        )
        new_position = max_position + 1

        new_column_id = "column-id-" + str(uuid.uuid4())
        title = data.get("title")

        insert_column(cursor, new_column_id, board_id, title, new_position)

        new_column = {
            "_id": new_column_id,
            "boardId": board_id,
            "title": title,
            "cardOrderIds": [],
            "cards": [],
        }
        conn.commit()
        return new_column
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def remove_column_service(board_id, column_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        delete_column(board_id, column_id, cursor)
        conn.commit()
        return {"message": f"Column {column_id} removed successfully"}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def update_column_service(board_id, column_id, data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        title = data.get("title")
        card_order_ids = data.get("cardOrderIds", [])
        # Update the column's title in the 'columns' table
        update_column(title, column_id, board_id, cursor)
        # Update the positions of cards if cardOrderIds are provided
        if card_order_ids:
            for index, card_id in enumerate(card_order_ids):
                update_card_position(index, card_id, column_id, cursor)
        # Fetch the updated cards for the column
        fetch_card_query(column_id, cursor)
        cards = cursor.fetchall()
        conn.commit()
        # Return the updated column data, including the cards
        updated_column = {
            "_id": column_id,
            "boardId": board_id,
            "title": title,
            "cardOrderIds": [
                card["_id"] for card in cards
            ],  # Reconstruct from database
            "cards": cards,  # Include updated cards
        }
        return updated_column
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def update_column_order_service(board_id, data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Parse the incoming JSON data
        column_order_ids = data.get("columnOrderIds", [])
        if not column_order_ids:
            return {"error": "No column order provided"}

        # Assign new positions to the columns based on their order
        for index, column_id in enumerate(column_order_ids):
            # Assign a new position as a float
            new_position = index + 1.0
            update_position_query(new_position, column_id, board_id, cursor)
        #
        conn.commit()
        return {"message": "Column order updated successfully"}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
