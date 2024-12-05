import mysql.connector

db_config = {
    "user": "root",
    "password": "",
    "host": "localhost",
    "port": "3308",
    "database": "trello_demo",
}

def get_db_connection():
    return mysql.connector.connect(**db_config)
