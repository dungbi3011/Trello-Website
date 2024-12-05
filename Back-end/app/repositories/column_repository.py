from ..db import get_db_connection
from flask import request
import uuid


def add_column_repository(board_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Parse the incoming JSON data
    data = request.get_json()
    new_column_id = "column-id-" + str(uuid.uuid4())  # Generate random column ID
    title = data.get("title")

    # Find the maximum position of existing columns in the board
    cursor.execute(
        "SELECT MAX(position) AS max_position FROM columns WHERE board_id = %s",
        (board_id,),
    )
    result = cursor.fetchone()
    max_position = (
        result["max_position"] if result and result["max_position"] is not None else 0
    )

    # Assign the new column position (next available position)
    new_position = max_position + 1

    # Insert the new column into the 'columns' table
    insert_column_query = """
        INSERT INTO columns (id, board_id, title, position)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(insert_column_query, (new_column_id, board_id, title, new_position))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    # Return the new column data to the front-end
    new_column = {
        "_id": new_column_id,
        "boardId": board_id,
        "title": title,
        "cardOrderIds": [],  # No cards yet in the new column
        "cards": [],  # No cards yet in the new column
    }
    return new_column


def remove_column_repository(board_id, column_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Delete the column from the 'columns' table
    delete_column_query = "DELETE FROM columns WHERE id = %s AND board_id = %s"
    cursor.execute(delete_column_query, (column_id, board_id))
    #

    conn.commit()
    conn.close()
    return f"Column {column_id} removed successfully"


def update_column_repository(board_id, column_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Parse the incoming JSON data
    data = request.get_json()
    title = data.get("title")
    card_order_ids = data.get("cardOrderIds", [])

    # Update the column's title in the 'columns' table
    update_column_query = """
        UPDATE columns 
        SET title = %s 
        WHERE id = %s AND board_id = %s
    """
    cursor.execute(update_column_query, (title, column_id, board_id))

    # Update the positions of cards if cardOrderIds are provided
    if card_order_ids:
        for index, card_id in enumerate(card_order_ids):
            update_card_position_query = """
                UPDATE cards 
                SET position = %s 
                WHERE id = %s AND column_id = %s
            """
            cursor.execute(update_card_position_query, (index + 1, card_id, column_id))

    # Fetch the updated cards for the column
    fetch_cards_query = """
        SELECT id as _id, column_id, title, description, cover, position 
        FROM cards 
        WHERE column_id = %s 
        ORDER BY position
    """
    cursor.execute(fetch_cards_query, (column_id,))
    cards = cursor.fetchall()

    conn.commit()
    conn.close()

    # Return the updated column data, including the cards
    updated_column = {
        "_id": column_id,
        "boardId": board_id,
        "title": title,
        "cardOrderIds": [card["_id"] for card in cards],  # Reconstruct from database
        "cards": cards,  # Include updated cards
    }
    return updated_column


def update_column_order_repository(board_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Parse the incoming JSON data
    data = request.get_json()
    column_order_ids = data.get("columnOrderIds", [])
    if not column_order_ids:
        return {"error": "No column order provided"}

    # Assign new positions to the columns based on their order
    for index, column_id in enumerate(column_order_ids):
        # Assign a new position as a float
        new_position = index + 1.0
        update_position_query = """
            UPDATE columns 
            SET position = %s 
            WHERE id = %s AND board_id = %s
        """
        cursor.execute(update_position_query, (new_position, column_id, board_id))
    #
    conn.commit()
    conn.close()

    return {"message": "Column order updated successfully"}
