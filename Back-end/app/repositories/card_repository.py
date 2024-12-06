def fetch_card_max_position(column_id, cursor):
    # Find the maximum position of existing columns in the board
    cursor.execute(
        "SELECT MAX(position) AS max_position FROM cards WHERE column_id = %s",
        (column_id,),
    )
    return cursor.fetchone()


def insert_card(
    new_card_id, column_id, title, description, cover, new_position, cursor
):
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


def remove_card(board_id, column_id, card_id, cursor):
    # Delete the card from the 'cards' table
    delete_card_query = "DELETE FROM cards WHERE id = %s AND column_id = %s"
    cursor.execute(delete_card_query, (card_id, column_id))


def update_card(title, card_id, column_id, cursor):
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


def update_card_position_in_one_column(new_position, card_id, column_id, cursor):
    update_position_query = """
            UPDATE cards 
            SET position = %s 
            WHERE id = %s AND column_id = %s
        """
    cursor.execute(update_position_query, (new_position, card_id, column_id))


def update_columnID_for_moved_card(to_column_id, card_id, cursor):
    # Update the column ID for the moved card
    cursor.execute(
        """
        UPDATE cards 
        SET column_id = %s 
        WHERE id = %s
        """,
        (to_column_id, card_id),
    )


def update_positions_in_old_column(
    current_position, card_id_in_order, from_column_id, cursor
):
    cursor.execute(
        """
            UPDATE cards 
            SET position = %s 
            WHERE id = %s AND column_id = %s
            """,
        (current_position, card_id_in_order, from_column_id),
    )


def update_positions_in_new_column(
    current_position, card_id_in_order, to_column_id, cursor
):
    cursor.execute(
        """
            UPDATE cards 
            SET position = %s 
            WHERE id = %s AND column_id = %s
            """,
        (current_position, card_id_in_order, to_column_id),
    )
