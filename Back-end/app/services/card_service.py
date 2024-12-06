import uuid
from ..db import get_db_connection
from ..repositories.card_repository import (
    fetch_card_max_position,
    insert_card,
    remove_card,
    update_card,
    update_card_position_in_one_column,
    update_columnID_for_moved_card,
    update_positions_in_old_column,
    update_positions_in_new_column
)


def add_card_service(board_id, column_id, data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:    
        new_card_id = f"card-id-{uuid.uuid4()}"  # random cardID
        title = data.get("title", "Untitled Card")
        description = data.get("description", "")
        cover = data.get("cover", "")

        # Find the maximum position of existing columns in the board
        result = fetch_card_max_position(column_id, cursor)
        max_position = (
            result["max_position"] if result and result["max_position"] is not None else 0
        )
        # Assign the new column position (next available position)
        new_position = max_position + 1
        # Insert the new card into the 'cards' table
        insert_card(new_card_id, column_id, title, description, cover, new_position, cursor)
        #
        conn.commit()
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
    except Exception as e:
        conn.rollback()
        raise e
    finally: 
        conn.close()


def remove_card_service(board_id, column_id, card_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        remove_card(board_id, column_id, card_id, cursor)       
        conn.commit()
        return f"Card {card_id} removed successfully"
    except Exception as e:
        conn.rollback()  # Quay trở lại trạng thái ban đầu
        raise e
    finally:
        conn.close()


def update_card_service(board_id, column_id, card_id, data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        title = data.get("title")
        description = data.get("description")
        cover = data.get("cover")
        member_ids = data.get("memberIds", [])
        comments = data.get("comments", [])
        attachments = data.get("attachments", [])
        # Update the card in the 'cards' table
        update_card(title, card_id, column_id, cursor)
        #
        conn.commit()
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
    except Exception as e:
        conn.rollback()
        raise e
    finally: 
        conn.close()


def move_cards_in_column_service(board_id, column_id, data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        card_order_ids = data.get("cardOrderIds", [])
        if not card_order_ids:
            return {"error": "cardOrderIds is required"}
        # Assign new positions to the columns based on their order
        for index, card_id in enumerate(card_order_ids):
            # Assign a new position as a float
            new_position = index + 1.0
            update_card_position_in_one_column(new_position, card_id, column_id, cursor)
        #
        conn.commit()
        return {"message": "Card order updated successfully"}
    except Exception as e:
        conn.rollback()
        raise e
    finally: 
        conn.close()


def move_cards_between_different_columns_service(board_id, from_column_id, card_id, data):
    to_column_id = data.get("toColumnId")
    active_card_order_ids = data.get("activeCardOrderIds", [])  # Updated card order from the front-end
    over_card_order_ids = data.get("overCardOrderIds", [])  # Updated card order from the front-end
    new_card_index = data.get("newCardIndex")

    # Validate input
    if not to_column_id:
        return {"error": "Target column ID is missing"}
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:   
        # Update the column ID for the moved card
        update_columnID_for_moved_card(to_column_id, card_id, cursor)
        # Update positions of cards in the old column based on the provided order
        current_position = 1.0
        for card_id_in_order in active_card_order_ids:
            update_positions_in_old_column(current_position, card_id_in_order, from_column_id, cursor)
            current_position += 1.0
        # Insert the dragged card into the target column's order
        over_card_order_ids.insert(new_card_index, card_id)
        # Update positions of cards in the new column based on the new order
        current_position = 1.0
        for card_id_in_order in over_card_order_ids:
            update_positions_in_new_column(current_position, card_id_in_order, to_column_id, cursor)
            current_position += 1.0
        conn.commit()
        return {"message": "Card moved successfully"}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
