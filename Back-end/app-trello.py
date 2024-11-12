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
    "port": "3306",
    "database": "trello_website",
}


def get_db_connection():
    return mysql.connector.connect(**db_config)


app = Flask(__name__)
CORS(app)


@app.route("/boards/<board_id>", methods=["GET"])
def get_board(board_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Query to fetch the board and its related columns and cards using JOINs
    query = """
    SELECT b.id as _id, b.title, b.description, b.type, 
           b.owner_ids, b.member_ids, b.column_order_ids as columnOrderIds, 
           c.id as column_id, c.title as column_title, c.card_order_ids, 
           ca.id as card_id, ca.title as card_title, ca.description as card_description, 
           ca.cover as card_cover, ca.member_ids as card_member_ids, 
           ca.comments as card_comments, ca.attachments as card_attachments
    FROM boards b
    LEFT JOIN columns c ON b.id = c.board_id
    LEFT JOIN cards ca ON c.id = ca.column_id
    WHERE b.id = %s
    """

    cursor.execute(query, (board_id,))
    rows = cursor.fetchall()

    if rows:
        # Group data to reconstruct the board structure
        board = {}
        columns = {}
        for row in rows:
            if not board:
                # Initialize board information (first row will have board details)
                board = {
                    key: row[key]
                    for key in row
                    if key
                    not in ("column_id", "card_id", "column_title", "card_order_ids")
                }
                board["columns"] = []
                board["columnOrderIds"] = row["columnOrderIds"]  # Use the correct key

            if row["column_id"]:
                column_id = row["column_id"]
                if column_id not in columns:
                    # Add column to columns dictionary if not already added
                    columns[column_id] = {
                        "_id": column_id,
                        "boardId": board_id,
                        "title": row["column_title"],
                        "cardOrderIds": (
                            json.loads(row["card_order_ids"])
                            if row["card_order_ids"]
                            else []
                        ),
                        "cards": [],
                    }
                    # Add column to the board's columns
                    board["columns"].append(columns[column_id])

                if row["card_id"]:
                    # Add card to the appropriate column
                    card = {
                        "_id": row["card_id"],
                        "columnId": column_id,
                        "title": row["card_title"],
                        "description": row["card_description"],
                        "cover": row["card_cover"],
                        "memberIds": (
                            json.loads(row["card_member_ids"])
                            if row["card_member_ids"]
                            else []
                        ),
                        "comments": (
                            json.loads(row["card_comments"])
                            if row["card_comments"]
                            else []
                        ),
                        "attachments": (
                            json.loads(row["card_attachments"])
                            if row["card_attachments"]
                            else []
                        ),
                    }
                    columns[column_id]["cards"].append(card)

        return jsonify(board), 200

    return jsonify({"error": "Board not found"}), 404


@app.route("/boards/<board_id>/columns", methods=["POST"])
def add_column(board_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Parse the incoming JSON data
    data = request.get_json()
    new_column_id = "column-id-" + str(uuid.uuid4()) # random columnID
    title = data.get("title")

    # Insert the new column into the 'columns' table
    insert_column_query = """
        INSERT INTO columns (id, board_id, title, card_order_ids)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(
        insert_column_query, (new_column_id, board_id, title, json.dumps([]))
    )

    # Select column_order_ids from database & update it
    cursor.execute("SELECT column_order_ids FROM boards WHERE id = %s", (board_id,))
    result = cursor.fetchone()
    if result:
        column_order_ids = json.loads(result["column_order_ids"])
        column_order_ids.append(new_column_id)
        update_board_query = "UPDATE boards SET column_order_ids = %s WHERE id = %s"
        cursor.execute(update_board_query, (json.dumps(column_order_ids), board_id))

    # 
    conn.commit()
    conn.close()

    # Return the new column data to the front-end
    new_column = {
        "_id": new_column_id,
        "boardId": board_id,
        "title": title,
        "cardOrderIds": [],
        "cards": [],
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

    # Select column_order_ids from database & update it
    cursor.execute("SELECT column_order_ids FROM boards WHERE id = %s", (board_id,))
    result = cursor.fetchone()
    if result:
        column_order_ids = json.loads(result["column_order_ids"])
        if column_id in column_order_ids:
            column_order_ids.remove(column_id)

            # Update the board with the new column order
            update_board_query = "UPDATE boards SET column_order_ids = %s WHERE id = %s"
            cursor.execute(update_board_query, (json.dumps(column_order_ids), board_id))

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

    # Update the column in the 'columns' table
    update_column_query = """
        UPDATE columns 
        SET title = %s, card_order_ids = %s 
        WHERE id = %s AND board_id = %s
    """
    cursor.execute(
        update_column_query, (title, json.dumps(card_order_ids), column_id, board_id)
    )

    #
    conn.commit()
    conn.close()

    # Return the updated column data
    updated_column = {
        "_id": column_id,
        "boardId": board_id,
        "title": title,
        "cardOrderIds": card_order_ids,
        "cards": [],  # cards will be populated on the front-end based on card order
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

    data = request.get_json()
    column_order_ids = data.get("columnOrderIds", [])
    if not column_order_ids:
        return jsonify({"error": "No column order provided"}), 400
    cursor.execute(
        "UPDATE boards SET column_order_ids = %s WHERE id = %s",
        (json.dumps(column_order_ids), board_id),
    )
    conn.commit()
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
