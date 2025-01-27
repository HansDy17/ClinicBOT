import mysql.connector
from os import getenv
from dotenv import load_dotenv  

load_dotenv()

db = mysql.connector.connect(
    host = getenv('MYSQL_HOST'),
    user = getenv('MYSQL_USERNAME'),
    password = getenv('MYSQL_PASSWORD'),
    database = getenv('MYSQL_NAME')
)
cursor = db.cursor()

class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def get_id(self):
        return str(self.id)

    # Existing user methods
    @classmethod
    def userList(cls):
        cursor = db.cursor()
        sql = "SELECT * from users"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    # Add, delete, and fetch users

    @classmethod
    def userData(self, username):
        cursor = db.cursor()
        sql = "SELECT * FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        result = cursor.fetchall()
        cursor.close()
        return result
    
    # Existing methods for user data

    # **Appointment Management Methods**

    @classmethod
    def bookAppointment(cls, user_id, appointment_date, appointment_type, doctor_name, notes=""):
        """Books a new appointment for a user."""
        cursor = db.cursor()
        sql = """
            INSERT INTO appointments (user_id, appointment_date, appointment_type, doctor_name, status, notes)
            VALUES (%s, %s, %s, %s, 'Scheduled', %s)
        """
        cursor.execute(sql, (user_id, appointment_date, appointment_type, doctor_name, notes))
        db.commit()
        cursor.close()

    @classmethod
    def getAppointments(cls, user_id):
        """Fetch all appointments for a specific user."""
        cursor = db.cursor()
        sql = "SELECT * FROM appointments WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
        cursor.close()
        return result
    
    @classmethod
    def cancelAppointment(cls, appointment_id):
        """Cancel an existing appointment."""
        cursor = db.cursor()
        sql = "UPDATE appointments SET status = 'Canceled' WHERE appointment_id = %s"
        cursor.execute(sql, (appointment_id,))
        db.commit()
        cursor.close()

    @classmethod
    def rescheduleAppointment(cls, appointment_id, new_date):
        """Reschedule an existing appointment."""
        cursor = db.cursor()
        sql = "UPDATE appointments SET appointment_date = %s WHERE appointment_id = %s"
        cursor.execute(sql, (new_date, appointment_id))
        db.commit()
        cursor.close()

    @classmethod
    def getAppointmentById(cls, appointment_id):
        """Fetch details of a specific appointment."""
        cursor = db.cursor()
        sql = "SELECT * FROM appointments WHERE appointment_id = %s"
        cursor.execute(sql, (appointment_id,))
        result = cursor.fetchone()
        cursor.close()
        return result
    
    @classmethod
    def updateAppointmentNotes(cls, appointment_id, new_notes):
        """Update notes for a specific appointment."""
        cursor = db.cursor()
        sql = "UPDATE appointments SET notes = %s WHERE appointment_id = %s"
        cursor.execute(sql, (new_notes, appointment_id))
        db.commit()
        cursor.close()

    @classmethod
    def check_conflicts(date, time, dentist):
        cursor.execute("""
            SELECT * FROM appointments
            WHERE date=? AND time=? AND dentist=?;
        """, (date, time, dentist))
        return cursor.fetchone() is not None

class User_Verification_Data(UserMixin):
    # Existing verification methods

    # Additional functionality for clinic-related data (e.g., health records)
    @classmethod
    def addHealthRecord(cls, user_id, record_type, record_data):
        """Add a health record to a user's profile."""
        cursor = db.cursor()
        sql = """
            INSERT INTO health_records (user_id, record_type, record_data)
            VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (user_id, record_type, record_data))
        db.commit()
        cursor.close()

    @classmethod
    def getHealthRecords(cls, user_id):
        """Fetch all health records for a user."""
        cursor = db.cursor()
        sql = "SELECT * FROM health_records WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
        cursor.close()
        return result
