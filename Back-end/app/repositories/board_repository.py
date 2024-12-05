from ..db import get_db_connection

def get_board_repository(board_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

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
    rows = cursor.fetchall()

    if rows:
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
                    updated_cards.append((len(card_order_ids_map[column_id]), row["card_id"]))

        for column_id, column in columns.items():
            column["cardOrderIds"] = card_order_ids_map[column_id]
            board["columns"].append(column)

        board["columnOrderIds"] = column_order_ids

        for position, column_id in updated_columns:
            cursor.execute("UPDATE columns SET position = %s WHERE id = %s", (position, column_id))

        for position, card_id in updated_cards:
            cursor.execute("UPDATE cards SET position = %s WHERE id = %s", (position, card_id))

        conn.commit()
        conn.close()
        return board 

    conn.close()
    raise Exception("Board not found")
