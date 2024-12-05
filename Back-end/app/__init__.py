from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    from .controllers.board_controller import board_bp
    from .controllers.column_controller import column_bp
    from .controllers.card_controller import card_bp

    app.register_blueprint(board_bp)
    app.register_blueprint(column_bp)
    app.register_blueprint(card_bp)

    return app
