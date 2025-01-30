import mysql.connector
from os import getenv
from dotenv import load_dotenv

load_dotenv()


# Database configuration
db_config = {
    'host': getenv('MYSQL_HOST'),
    'user': getenv('MYSQL_USERNAME'),
    'password': getenv('MYSQL_PASSWORD'),
    'database': getenv('MYSQL_NAME')
}

def initialize_database():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

    # Create Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(15) NOT NULL
        )""")
        
        # Create Appointments Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            appointment_date DATETIME NOT NULL,
            purpose TEXT NOT NULL,
            status ENUM('scheduled', 'cancelled', 'completed') DEFAULT 'scheduled',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )""")
        
        connection.commit()
        cursor.close()

    except Exception as e:
        print(f"Error creating tables: {str(e)}")

if __name__ == "__main__":
    initialize_database()
