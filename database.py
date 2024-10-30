#!/usr/bin/env python3
import sqlite3

def reset_database():
    try:
        connection = sqlite3.connect('hospital.db')
        cursor = connection.cursor()
        print("connected")

        # Clear the resources table
        cursor.execute('DELETE FROM resources')
        print("resources cleared")

        # Repopulate the table
        resources = [
            ('ER personnel', 9),
            ('Intake personnel', 4),
            ('Operating rooms', 5),
            ('Nursing beds A', 30),
            ('Nursing beds B', 40)
        ]

        cursor.executemany('''
            INSERT INTO resources (resource, count) VALUES (?, ?)
        ''', resources)
        print("data inserted")
        connection.commit()
        connection.close()
    except sqlite3.Error as e: 
        print(f"SQLite error: {e}")
    except Exception as e: 
        print(f"Unexpected error: {e}")
