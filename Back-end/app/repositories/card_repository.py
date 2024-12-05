from ..db import get_db_connection
from flask import request
import uuid


def add_card_repository(board_id, column_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Parse the incoming JSON data
    data = request.get_json()
    new_card_id = f"card-id-{uuid.uuid4()}"  # random cardID
    title = data.get("title", "Untitled Card")
    description = data.get("description", "")
    cover = data.get("cover", "")

    # Find the maximum position of existing columns in the board
    cursor.execute(
        "SELECT MAX(position) AS max_position FROM cards WHERE column_id = %s",
        (column_id,),
    )
    result = cursor.fetchone()
    max_position = (
        result["max_position"] if result and result["max_position"] is not None else 0
    )

    # Assign the new column position (next available position)
    new_position = max_position + 1

    # Insert the new card into the 'cards' table
    insert_card_query = """
        INSERT INTO cards (id, column_id, title, description, cover, position)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(
        insert_card_query,
        (
            new_card_id,
            column_id,
            title,
            description,
            cover,
            new_position,
        ),
    )
    #
    conn.commit()
    conn.close()

    # Return the new card data
    new_card = {
        "_id": new_card_id,
        "columnId": column_id,
        "title": title,
        "description": description,
        "cover": cover,
        "memberIds": [],
        "comments": [],
        "attachments": [],
    }
    return new_card


def remove_card_repository(board_id, column_id, card_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Delete the card from the 'cards' table
    delete_card_query = "DELETE FROM cards WHERE id = %s AND column_id = %s"
    cursor.execute(delete_card_query, (card_id, column_id))
    #

    conn.commit()
    conn.close()
    return f"Card {card_id} removed successfully"


def update_card_repository(board_id, column_id, card_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Parse the incoming JSON data
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    cover = data.get("cover")
    member_ids = data.get("memberIds", [])
    comments = data.get("comments", [])
    attachments = data.get("attachments", [])

    # Update the card in the 'cards' table
    update_card_query = """
        UPDATE cards 
        SET title = %s
        WHERE id = %s AND column_id = %s
    """
    cursor.execute(
        update_card_query,
        (
            title,
            card_id,
            column_id,
        ),
    )
    #
    conn.commit()
    conn.close()

    # Return the updated card data
    updated_card = {
        "_id": card_id,
        "columnId": column_id,
        "title": title,
        "description": description,
        "cover": cover,
        "memberIds": member_ids,
        "comments": comments,
        "attachments": attachments,
    }
    return updated_card


def move_cards_in_column_repository(board_id, column_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    data = request.get_json()
    card_order_ids = data.get("cardOrderIds", [])

    if not card_order_ids:
        return {"error": "cardOrderIds is required"}
    
    # Assign new positions to the columns based on their order
    for index, card_id in enumerate(card_order_ids):
        # Assign a new position as a float
        new_position = index + 1.0
        update_position_query = """
            UPDATE cards 
            SET position = %s 
            WHERE id = %s AND column_id = %s
        """
        cursor.execute(update_position_query, (new_position, card_id, column_id))
    #
    conn.commit()
    conn.close()
    return {"message": "Card order updated successfully"}


def move_cards_between_different_columns_repository(board_id, from_column_id, card_id):
    data = request.get_json()
    to_column_id = data.get("toColumnId")
    active_card_order_ids = data.get("activeCardOrderIds", [])  # Updated card order from the front-end
    over_card_order_ids = data.get("overCardOrderIds", [])  # Updated card order from the front-end
    new_card_index = data.get("newCardIndex")

    # Validate input
    if not to_column_id:
        return {"error": "Target column ID is missing"}

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Update the column ID for the moved card
    cursor.execute(
        """
        UPDATE cards 
        SET column_id = %s 
        WHERE id = %s
        """,
        (to_column_id, card_id),
    )

    # Update positions of cards in the old column based on the provided order
    current_position = 1.0
    for card_id_in_order in active_card_order_ids:
        cursor.execute(
            """
            UPDATE cards 
            SET position = %s 
            WHERE id = %s AND column_id = %s
            """,
            (current_position, card_id_in_order, from_column_id),
        )
        current_position += 1.0

    # Insert the dragged card into the target column's order
    over_card_order_ids.insert(new_card_index, card_id)

    # Update positions of cards in the new column based on the new order
    current_position = 1.0
    for card_id_in_order in over_card_order_ids:
        cursor.execute(
            """
            UPDATE cards 
            SET position = %s 
            WHERE id = %s AND column_id = %s
            """,
            (current_position, card_id_in_order, to_column_id),
        )
        current_position += 1.0

    conn.commit()
    conn.close()

    return {"message": "Card moved successfully"}