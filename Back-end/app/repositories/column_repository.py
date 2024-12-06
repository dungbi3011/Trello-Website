def fetch_max_column_position(board_id, cursor):
    query = "SELECT MAX(position) AS max_position FROM columns WHERE board_id = %s"
    cursor.execute(query, (board_id,))
    return cursor.fetchone()


def insert_column(cursor, new_column_id, board_id, title, new_position):
    query = """
        INSERT INTO columns (id, board_id, title, position)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (new_column_id, board_id, title, new_position))


def delete_column(board_id, column_id, cursor):
    query = "DELETE FROM columns WHERE id = %s AND board_id = %s"
    cursor.execute(query, (column_id, board_id))


def update_column(title, column_id, board_id, cursor):
    # Update the column's title in the 'columns' table
    update_column_query = """
        UPDATE columns 
        SET title = %s 
        WHERE id = %s AND board_id = %s
    """
    cursor.execute(update_column_query, (title, column_id, board_id))


def update_card_position(index, card_id, column_id, cursor):
    update_card_position_query = """
        UPDATE cards 
        SET position = %s 
        WHERE id = %s AND column_id = %s
    """
    cursor.execute(update_card_position_query, (index + 1, card_id, column_id))


def fetch_card_query(column_id, cursor):
    # Fetch the updated cards for the column
    fetch_cards_query = """
        SELECT id as _id, column_id, title, description, cover, position 
        FROM cards 
        WHERE column_id = %s 
        ORDER BY position
    """
    cursor.execute(fetch_cards_query, (column_id,))


def update_position_query(new_position, column_id, board_id, cursor):
    update_position_query = """
            UPDATE columns 
            SET position = %s 
            WHERE id = %s AND board_id = %s
        """
    cursor.execute(update_position_query, (new_position, column_id, board_id))
