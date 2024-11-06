import uuid, json
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# MySQL database configuration
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'port': '3306',
    'database': 'trello_website'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

app = Flask(__name__)
CORS(app)

@app.route('/boards/<board_id>', methods=['GET'])
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
                board = {key: row[key] for key in row if key not in ('column_id', 'card_id', 'column_title', 'card_order_ids')}
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
                        "cardOrderIds": json.loads(row["card_order_ids"]) if row["card_order_ids"] else [],
                        "cards": []
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
                        "memberIds": json.loads(row["card_member_ids"]) if row["card_member_ids"] else [],
                        "comments": json.loads(row["card_comments"]) if row["card_comments"] else [],
                        "attachments": json.loads(row["card_attachments"]) if row["card_attachments"] else []
                    }
                    columns[column_id]["cards"].append(card)

        return jsonify(board), 200

    return jsonify({'error': 'Board not found'}), 404

# @app.route('/boards/<board_id>/columns', methods=['POST'])
# def add_column(board_id):
#     new_column_data = request.get_json()

#     # Check if the board exists
#     for board in board_data:
#         if board["_id"] == board_id:
#             # Generate a new unique ID for the column
#             new_column_id = len(board['columns']) + 1  # Incremental ID based on existing columns
#             new_column_id_str = f"column-id-{uuid.uuid4()}"  # Format ID as "column-id-XX"
            
#             # Prepare the new column
#             new_column = {
#                 "_id": new_column_id_str,
#                 "boardId": board_id,
#                 "title": new_column_data["title"],
#                 "cardOrderIds": [],
#                 "cards": [],
#             }

#             # Create a placeholder card
#             placeholder_card = {
#                 "_id": f"{new_column_id_str}-placeholder-card",  # Corrected placeholder ID
#                 "boardId": board_id,
#                 "columnId": new_column_id_str,
#                 "FE_PlaceholderCard": True,
#             }

#             # Add the placeholder card to the new column
#             new_column["cards"].append(placeholder_card)
#             new_column["cardOrderIds"].append(placeholder_card["_id"])

#             # Add the new column to the board's columns and columnOrderIds
#             board["columns"].append(new_column)
#             board["columnOrderIds"].append(new_column["_id"])

#             return jsonify(new_column), 201  # Respond with the newly created column

#     return jsonify({'error': f'Board not found with ID: {board_id}'}), 404

# @app.route('/boards/<board_id>/columns/<column_id>/cards', methods=['POST'])
# def add_card(board_id, column_id):
#     new_card_data = request.get_json()
#     new_card_id = f"card-id-{uuid.uuid4()}"

#     new_card = {
#         "_id": new_card_id,
#         "columnId": column_id,
#         **new_card_data  # This will unpack the other card data (title, description, etc.)
#     }

#     # Validate and process card data
#     for board in board_data:
#         if board["_id"] == board_id:
#             for column in board["columns"]:
#                 if column["_id"] == column_id:
#                     # Add the new card to the column's cards list
#                     column["cards"].append(new_card)
#                     # Update cardOrderIds to reflect the new card
#                     column["cardOrderIds"].append(new_card["_id"])
#                     return jsonify(new_card), 201  # Return the new card and a 201 status
#             break
#     return jsonify({'error': 'Board not found with ID: ' + board_id}), 404

# @app.route('/boards/<board_id>/columns/<column_id>', methods=['DELETE'])
# def remove_column(board_id, column_id):
#     # Find the board by ID
#     for board in board_data:
#         if board["_id"] == board_id:
#             # Find and remove the column by ID
#             board["columns"] = [col for col in board["columns"] if col["_id"] != column_id]
#             # Update columnOrderIds to remove the column ID
#             board["columnOrderIds"] = [col_id for col_id in board["columnOrderIds"] if col_id != column_id]
#             return jsonify({"message": f"Column {column_id} deleted successfully"}), 201
    
#     return jsonify({"error": f"Board or Column not found with IDs: {board_id}, {column_id}"}), 404

# @app.route('/boards/<board_id>/columns/<column_id>/cards/<card_id>', methods=['DELETE'])
# def remove_card(board_id, column_id, card_id):
#     # Find the board by ID
#     for board in board_data:
#         if board["_id"] == board_id:
#             # Find the column by ID within the board
#             for column in board["columns"]:
#                 if column["_id"] == column_id:
#                     # Find the card by ID within the column
#                     column["cards"] = [card for card in column["cards"] if card["_id"] != card_id]
#                     column["cardOrderIds"] = [cid for cid in column["cardOrderIds"] if cid != card_id]
#                     return jsonify({"message": f"Card {card_id} removed successfully"}), 201
#             return jsonify({'error': f'Column not found with ID: {column_id}'}), 404
#     return jsonify({'error': f'Board not found with ID: {board_id}'}), 404


# @app.route('/boards/<board_id>/columns/<column_id>', methods=['PUT'])
# def update_column(board_id, column_id):
#     updated_column_data = request.get_json()

#     # Find the board by ID
#     for board in board_data:
#         if board["_id"] == board_id:
#             # Find the column and update its details
#             for col in board["columns"]:
#                 if col["_id"] == column_id:
#                     col.update(updated_column_data)
#                     return jsonify(col), 201
    
#     return jsonify({"error": f"Board or Column not found with IDs: {board_id}, {column_id}"}), 404

# @app.route('/boards/<board_id>/columns/<column_id>/cards/<card_id>', methods=['PUT'])
# def update_card(board_id, column_id, card_id):
#     updated_card_data = request.get_json()

#     # Find the board by ID
#     for board in board_data:
#         if board["_id"] == board_id:
#             # Find the column by ID within the board
#             for column in board["columns"]:
#                 if column["_id"] == column_id:
#                     # Find the card by ID within the column and update it
#                     for idx, card in enumerate(column["cards"]):
#                         if card["_id"] == card_id:
#                             column["cards"][idx] = updated_card_data
#                             return jsonify(updated_card_data), 201
#                     return jsonify({'error': f'Card not found with ID: {card_id}'}), 404
#             return jsonify({'error': f'Column not found with ID: {column_id}'}), 404
#     return jsonify({'error': f'Board not found with ID: {board_id}'}), 404


# @app.route('/boards/<board_id>/columns/<column_id>/cards/<card_id>/move', methods=['PUT'])
# def move_card(board_id, column_id, card_id, target_column_id):
#     board = get_board(board_id)
#     if board:
#         for column in board['columns']:
#             if column['_id'] == column_id:
#                 for card in column['cards']:
#                     if card['_id'] == card_id:
#                         column['cards'].remove(card)
#                         break
#                 break
#         for column in board['columns']:
#             if column['_id'] == target_column_id:
#                 column['cards'].append(card)
#                 break
#         update_board(board)
#         return jsonify({'message': 'Card moved successfully'}), 200
#     else:
#         return jsonify({'error': 'Board not found with ID: ' + board_id}), 404

# def update_board(board):
#     # Replace this with your actual board update logic (e.g., saving to a database)
#     global board_data  # Assuming board_data is a global variable
#     board_data = board

if __name__ == '__main__':
    app.run(debug=True)