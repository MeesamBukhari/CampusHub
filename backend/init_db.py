import mysql.connector
from mysql.connector import Error
from config import Config
import os

def init_db():
    conn = None
    cursor = None
    try:
        # Try connecting with configured password
        try:
            conn = mysql.connector.connect(
                host=Config.DB_CONFIG['host'],
                user=Config.DB_CONFIG['user'],
                password=Config.DB_CONFIG['password']
            )
        except Error:
            # Fallback to configured password (if it was empty, try 'password', if it was 'password', try empty)
            print("Connection failed, retrying with alternative password...")
            alt_password = 'password' if Config.DB_CONFIG['password'] == '' else ''
            conn = mysql.connector.connect(
                host=Config.DB_CONFIG['host'],
                user=Config.DB_CONFIG['user'],
                password=alt_password
            )
            
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        db_name = Config.DB_CONFIG['database']
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' checked/created.")
        
        # Connect to the specific database
        conn.database = db_name
        
        # Read schema.sql
        schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            
        # Execute schema commands
        # Split by semicolon to handle multiple statements
        commands = schema_sql.split(';')
        for command in commands:
            if command.strip():
                cursor.execute(command)
        print("Schema initialized.")
        
        # Check if users table is empty to decide on seeding
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            print("Seeding database...")
            seed_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'seed.sql')
            with open(seed_path, 'r') as f:
                seed_sql = f.read()
                
            # Execute seed commands
            seed_commands = seed_sql.split(';')
            for command in seed_commands:
                if command.strip():
                    try:
                        cursor.execute(command)
                    except Error as e:
                        print(f"Error executing seed command: {e}")
            conn.commit()
            print("Database seeded.")
        else:
            print("Database already contains data, skipping seed.")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()
