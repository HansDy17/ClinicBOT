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

def create_tables():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Create Patient table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Patient (
                patient_id VARCHAR(500),
                patient_name VARCHAR(100) NOT NULL,
                patient_email VARCHAR(500) NOT NULL UNIQUE,
                patient_gender VARCHAR(6) NOT NULL,
                patient_contact INT(10) NOT NULL,
                PRIMARY KEY (patient_id)
            )
        """)

        # Create Doctor table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Doctor (
                doctor_id VARCHAR(500) NOT NULL,
                doctor_name VARCHAR(100) NOT NULL,
                doctor_email VARCHAR(500) NOT NULL UNIQUE,
                doctor_specialization VARCHAR(100) NOT NULL,
                doctor_contact INT(10) NOT NULL,
                doctor_avail_days VARCHAR(100) NOT NULL,
                PRIMARY KEY (doctor_id)
            )
        """)

        # Create Appointment table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Appointment (
                appointment_id VARCHAR(500),
                appointment_date DATETIME NOT NULL,
                appointment_time DATETIME NOT NULL,
                appointment_status VARCHAR(50) NOT NULL,
                appointment_start DATETIME NOT NULL,
                appointment_end DATETIME NOT NULL,
                patient_id VARCHAR(500),
                doctor_id VARCHAR(500),
                PRIMARY KEY (appointment_id),
                FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id),
            )
        """)

        # Create Health Records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_records (
                record_id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT,
                record_type VARCHAR(255),
                record_data TEXT,
                FOREIGN KEY (patient_id) REFERENCES Patient(patient_id)
            )
        """)

        connection.close()
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {str(e)}")

if __name__ == "__main__":
    create_tables()
