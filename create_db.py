import mysql.connector

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'clinic_bot'
}

def create_tables():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Create Customer table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Customer (
                customer_id VARCHAR(500),
                customer_name VARCHAR(20) NOT NULL,
                customer_email VARCHAR(500) NOT NULL UNIQUE,
                customer_password VARCHAR(500) NOT NULL,
                customer_gender VARCHAR(6) NOT NULL,
                customer_contact INT(10) NOT NULL,
                PRIMARY KEY (customer_id)
            )
        """)

        # Create Restaurant table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Restaurant (
                resto_id VARCHAR(500) NOT NULL,
                resto_name VARCHAR(55) NOT NULL,
                resto_email VARCHAR(500) NOT NULL,
                resto_pass VARCHAR(500) NOT NULL,
                resto_address VARCHAR(500) NOT NULL,
                opening_time TIME NOT NULL,
                closing_time TIME NOT NULL,
                resto_availseats INT(10) NOT NULL DEFAULT '0',
                resto_category VARCHAR(50) NOT NULL ,
                resto_contact INT(10) NULL DEFAULT '0',
                insertion_time TIMESTAMP NOT NULL DEFAULT (now()),
                PRIMARY KEY (resto_id),
                UNIQUE INDEX resto_email (`resto_email`)
            )
        """)

        # Create Menu table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Menu (
                menu_id VARCHAR(500),
                menu_food VARCHAR(5000) NOT NULL,
                PRIMARY KEY (menu_id)
            )
        """)

        # Create Reservation table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Reservation (
                reserv_id VARCHAR(500),
                reserv_date DATETIME NOT NULL,
                reserv_time DATETIME NOT NULL,
                reserv_status VARCHAR(255) NOT NULL,
                reserv_start DATETIME NOT NULL,
                reserv_end DATETIME NOT NULL,
                customer_id VARCHAR(500),
                resto_id VARCHAR(50),
                PRIMARY KEY (reserv_id),
                FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
                FOREIGN KEY (resto_id) REFERENCES Restaurant(resto_id)
            )
        """)

        # Create Rating table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Rating (
                rating_id VARCHAR(600),
                rating_resto VARCHAR(50),
                rating_comment TEXT,
                rating_date DATETIME,
                rating_time DATETIME,
                customer_id VARCHAR(500),
                PRIMARY KEY (rating_id),
                FOREIGN KEY (rating_resto) REFERENCES Restaurant(resto_id),
                FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
            )
        """)

        connection.close()
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {str(e)}")

if __name__ == "__main__":
    create_tables()
