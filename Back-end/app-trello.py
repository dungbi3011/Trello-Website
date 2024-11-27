import uuid, json
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector


app = Flask(__name__)
CORS(app)

# MySQL database configuration
db_config = {
    "user": "root",
    "password": "",
    "host": "localhost",
    "port": "3308",
    "database": "trello_demo",
}


def get_db_connection():
    return mysql.connector.connect(**db_config)


app = Flask(__name__)
CORS(app)


@app.route("/boards/<board_id>", methods=["GET"])
def get_board(board_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Updated SQL query to fetch board, columns, and cards with positions
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
        # Initialize board structure
        board = {}
        columns = {}
        column_order_ids = []  # To store column IDs in order
        card_order_ids_map = {}  # To store cardOrderIds for each column

        for row in rows:
            if not board:
                # Initialize board details (first row will always contain board details)
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
                    # Add column to the dictionary if not already added
                    columns[column_id] = {
                        "_id": column_id,
                        "boardId": board_id,
                        "title": row["column_title"],
                        "cardOrderIds": [],  # Will populate this after iterating
                        "cards": [],
                    }
                    # Append the column ID to the column_order_ids list
                    column_order_ids.append(column_id)
                    # Initialize cardOrderIds list for this column
                    card_order_ids_map[column_id] = []

                if row["card_id"]:
                    # Add card to the appropriate column
                    card = {
                        "_id": row["card_id"],
                        "columnId": column_id,
                        "title": row["card_title"],
                        "description": row["card_description"],
                        "cover": row["card_cover"],
                    }
                    columns[column_id]["cards"].append(card)
                    # Append the card ID to the cardOrderIds for this column
                    card_order_ids_map[column_id].append(row["card_id"])

        # After processing all rows, populate cardOrderIds for each column
        for column_id, column in columns.items():
            column["cardOrderIds"] = card_order_ids_map[column_id]
            board["columns"].append(column)

        # Add columnOrderIds to the board
        board["columnOrderIds"] = column_order_ids

        return jsonify(board), 200

    return jsonify({"error": "Board not found"}), 404



@app.route("/boards/<board_id>/columns", methods=["POST"])
def add_column(board_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Parse the incoming JSON data
    data = request.get_json()
    new_column_id = "column-id-" + str(uuid.uuid4())  # Generate random column ID
    title = data.get("title")

    # Find the maximum position of existing columns in the board
    cursor.execute("SELECT MAX(position) AS max_position FROM columns WHERE board_id = %s", (board_id,))
    result = cursor.fetchone()
    max_position = result["max_position"] if result and result["max_position"] is not None else 0

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
        "cards": [],         # No cards yet in the new column
    }
    return jsonify(new_column), 201



@app.route("/boards/<board_id>/columns/<column_id>/cards", methods=["POST"])
def add_card(board_id, column_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Parse the incoming JSON data
    data = request.get_json()
    new_card_id = f"card-id-{uuid.uuid4()}"  # random cardID
    title = data.get("title", "Untitled Card")
    description = data.get("description", "")
    cover = data.get("cover", None)
    member_ids = data.get("memberIds", [])
    comments = data.get("comments", [])
    attachments = data.get("attachments", [])

    # Insert the new card into the 'cards' table
    insert_card_query = """
        INSERT INTO cards (id, column_id, title, description, cover, member_ids, comments, attachments)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(
        insert_card_query,
        (
            new_card_id,
            column_id,
            title,
            description,
            cover,
            json.dumps(member_ids),
            json.dumps(comments),
            json.dumps(attachments),
        ),
    )

   # Select card_order_ids from database 
    cursor.execute("SELECT card_order_ids FROM columns WHERE id = %s", (column_id,))
    result = cursor.fetchone()

    # Initialize card_order_ids as an empty list if result is None or card_order_ids is None
    card_order_ids = (
        json.loads(result["card_order_ids"] or "[]")
        if result and result["card_order_ids"]
        else []
    )
    card_order_ids.append(new_card_id)

    # Update card_order_ids
    update_column_query = "UPDATE columns SET card_order_ids = %s WHERE id = %s"
    cursor.execute(update_column_query, (json.dumps(card_order_ids), column_id))

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
        "memberIds": member_ids,
        "comments": comments,
        "attachments": attachments,
    }
    return jsonify(new_card), 201


@app.route("/boards/<board_id>/columns/<column_id>", methods=["DELETE"])
def remove_column(board_id, column_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Delete the column from the 'columns' table
    delete_column_query = "DELETE FROM columns WHERE id = %s AND board_id = %s"
    cursor.execute(delete_column_query, (column_id, board_id))
    #
    conn.commit()
    conn.close()

    return jsonify({"message": f"Column {column_id} removed successfully"}), 200


@app.route("/boards/<board_id>/columns/<column_id>/cards/<card_id>", methods=["DELETE"])
def remove_card(board_id, column_id, card_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Delete the card from the 'cards' table
    delete_card_query = "DELETE FROM cards WHERE id = %s AND column_id = %s"
    cursor.execute(delete_card_query, (card_id, column_id))

    # Select card_order_ids from database & update it
    cursor.execute("SELECT card_order_ids FROM columns WHERE id = %s", (column_id,))
    result = cursor.fetchone()
    if result:
        card_order_ids = json.loads(result["card_order_ids"])
        if card_id in card_order_ids:
            card_order_ids.remove(card_id)
            update_column_query = "UPDATE columns SET card_order_ids = %s WHERE id = %s"
            cursor.execute(update_column_query, (json.dumps(card_order_ids), column_id))

    #
    conn.commit()
    conn.close()
    return jsonify({"message": f"Card {card_id} removed successfully"}), 200


@app.route("/boards/<board_id>/columns/<column_id>", methods=["PUT"])
def update_column(board_id, column_id):
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
    return jsonify(updated_column), 200


@app.route("/boards/<board_id>/columns/<column_id>/cards/<card_id>", methods=["PUT"])
def update_card(board_id, column_id, card_id):
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
        SET title = %s, description = %s, cover = %s, member_ids = %s, comments = %s, attachments = %s
        WHERE id = %s AND column_id = %s
    """
    cursor.execute(
        update_card_query,
        (
            title,
            description,
            cover,
            json.dumps(member_ids),
            json.dumps(comments),
            json.dumps(attachments),
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
    return jsonify(updated_card), 200


@app.route("/boards/<board_id>/columns/move", methods=["PATCH"])
def update_column_order(board_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Parse the incoming JSON data
    data = request.get_json()
    column_order_ids = data.get("columnOrderIds", [])
    if not column_order_ids:
        return jsonify({"error": "No column order provided"}), 400

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

    conn.commit()
    conn.close()

    return jsonify({"message": "Column order updated successfully"}), 200



@app.route("/boards/<board_id>/columns/<column_id>/cards/move", methods=["PATCH"])
def move_cards_in_column(board_id, column_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    data = request.get_json()
    card_order_ids = data.get("cardOrderIds", [])

    if not card_order_ids:
        return jsonify({"error": "cardOrderIds is required"}), 400

    # Update the card_order_ids in the column
    update_column_query = (
        "UPDATE columns SET card_order_ids = %s WHERE id = %s AND board_id = %s"
    )
    cursor.execute(
        update_column_query, (json.dumps(card_order_ids), column_id, board_id)
    )

    #
    conn.commit()
    conn.close()
    return jsonify({"message": "Card order updated successfully"}), 200


@app.route(
    "/boards/<board_id>/columns/<from_column_id>/cards/<card_id>/move",
    methods=["PATCH"],
)
def move_card_between_diferent_columns(board_id, from_column_id, card_id):
    data = request.get_json()
    to_column_id = data.get("toColumnId")
    new_card_index = data.get("newCardIndex")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Remove card from the old column
    cursor.execute(
        "SELECT card_order_ids FROM columns WHERE id = %s", (from_column_id,)
    )
    from_column_data = cursor.fetchone()
    if from_column_data and from_column_data["card_order_ids"]:
        from_card_order_ids = json.loads(from_column_data["card_order_ids"])
        from_card_order_ids.remove(card_id)
        cursor.execute(
            "UPDATE columns SET card_order_ids = %s WHERE id = %s",
            (json.dumps(from_card_order_ids), from_column_id),
        )

    # Add card to the new column
    cursor.execute("SELECT card_order_ids FROM columns WHERE id = %s", (to_column_id,))
    to_column_data = cursor.fetchone()
    if to_column_data and to_column_data["card_order_ids"]:
        to_card_order_ids = json.loads(to_column_data["card_order_ids"])
        to_card_order_ids.insert(new_card_index, card_id)
        cursor.execute(
            "UPDATE columns SET card_order_ids = %s WHERE id = %s",
            (json.dumps(to_card_order_ids), to_column_id),
        )

    # Update the card's columnId to the new column
    cursor.execute(
        "UPDATE cards SET column_id = %s WHERE id = %s", (to_column_id, card_id)
    )

    # 
    conn.commit()
    conn.close()

    return jsonify({"message": "Card moved successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)