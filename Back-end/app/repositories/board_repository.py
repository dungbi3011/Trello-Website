def fetch_board_data(board_id, cursor):
    query = """
    SELECT b.id as _id, b.title, b.description, b.type, 
           co.id as column_id, co.title as column_title, co.position as column_position, 
           ca.id as card_id, ca.title as card_title, ca.description as card_description, 
           ca.cover as card_cover, ca.position as card_position
    FROM boards b
    LEFT JOIN columns co ON b.id = co.board_id
    LEFT JOIN cards ca ON co.id = ca.column_id
    WHERE b.id = %s
    ORDER BY co.position ASC, ca.position ASC;
    """
    cursor.execute(query, (board_id,))
    return cursor.fetchall()


def update_column_positions(position, column_id, cursor):
    cursor.execute(
        "UPDATE columns SET position = %s WHERE id = %s", (position, column_id)
    )


def update_card_positions(position, card_id, cursor):
    cursor.execute("UPDATE cards SET position = %s WHERE id = %s", (position, card_id))
