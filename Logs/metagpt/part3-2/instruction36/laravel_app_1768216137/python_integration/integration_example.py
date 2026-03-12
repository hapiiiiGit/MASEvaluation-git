"""
integration_example.py

This script demonstrates integration with a Laravel project.
It prints a message and connects to a MySQL database to fetch sample data.
You can extend this script to interact with the Laravel backend via HTTP or other means.

Requirements:
- Python 3.x
- mysql-connector-python (install via pip if needed)

Usage:
$ python integration_example.py
"""

import mysql.connector
from mysql.connector import Error

def fetch_sample_data():
    """
    Connects to the MySQL database and fetches sample data from the 'users' table.
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password',  # Change as needed
            database='laravel_app_db'
        )
        if connection.is_connected():
            print("Connected to MySQL database.")
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, email FROM users LIMIT 5;")
            rows = cursor.fetchall()
            print("Sample users from database:")
            for row in rows:
                print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}")
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

def main():
    print("Python integration script running.")
    fetch_sample_data()

if __name__ == "__main__":
    main()