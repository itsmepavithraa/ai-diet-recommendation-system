# Handles the MySQL connection used to look up patients by ID.

import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",   # <-- change this to your MySQL password
    "database": "diet_recommendation_db",
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
