import mysql.connector
from os import getenv
from dotenv import load_dotenv  
from datetime import datetime, timedelta
import json
from flask_mail import Message
from flask_login import UserMixin

load_dotenv() 

class DatabaseManager: 
    """Handles all database connections"""
    @staticmethod
    def get_db_connection():
        """Establish a connection to MySQL database."""
        conn = mysql.connector.connect(
            host=getenv('MYSQL_HOST'),
            user=getenv('MYSQL_USERNAME'),
            password=getenv('MYSQL_PASSWORD'),
            database=getenv('MYSQL_NAME')
        )
        DatabaseManager._ensure_staff_table_exists(conn)
        return conn
    
    @staticmethod
    def _ensure_staff_table_exists(conn):
        """Ensure the staff table exists, create it if not."""
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = 'staff'
        """, (getenv('MYSQL_NAME'),))
        
        if cursor.fetchone()[0] == 0:
            # Create the table if it doesn't exist
            cursor.execute("""
                CREATE TABLE staff (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    staff_id VARCHAR(50) NOT NULL UNIQUE,
                    full_name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    role VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX (staff_id),
                    INDEX (email)
                )
            """)
            conn.commit()
            print("Created staff table")
        
        cursor.close()

    
class User(UserMixin):
    def __init__(self, user_id=None, user_name=None, user_email=None):
        self.user_id = user_id
        self.user_name = user_name
        self.user_email = user_email
        self.db = DatabaseManager()
    
    # Required UserMixin methods
    def get_id(self):
        return str(self.user_id)
    
    # Custom methods
    def get_user_name(self):
        return str(self.user_name)
    
    def get_user_email(self):
        return str(self.user_email)    
    
    def get_user_data(self):
        """Get all user data from database"""
        if self.user_id:
            query = "SELECT * FROM users WHERE user_id = %s"
            result = self.db.execute_query(query, (self.user_id,))
        elif self.user_name:
            query = "SELECT * FROM users WHERE user_name = %s"
            result = self.db.execute_query(query, (self.user_name,))
        elif self.user_email:
            query = "SELECT * FROM users WHERE user_email = %s"
            result = self.db.execute_query(query, (self.user_email,))
        else:
            return None
        
        return result[0] if result else None
    
    @classmethod
    def get_user_data_by_user_id(cls, user_id):
        """Fetch user data using user ID"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return result
class Admin(UserMixin):
    def __init__(self, user_id=None, username=None):
        self.id = user_id
        self.username = username
        self.db = DatabaseManager()

    def get_id(self):
        return str(self.id)
    
    def get_username(self):
        return str(self.username)

    def get_admin_data(self):
        """Get all user data from database"""
        if self.id:
            query = "SELECT * FROM users WHERE id = %s"
            result = self.db.execute_query(query, (self.id,))
        elif self.username:
            query = "SELECT * FROM users WHERE username = %s"
            result = self.db.execute_query(query, (self.username,))
        else:
            return None
        
        return result[0] if result else None  
    
    @classmethod
    def get_admin_data_by_username(cls, username):
        """Fetch admin user data using user ID"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin_account WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return result

    @classmethod
    def get_user_data_by_username(cls, username):
        """Fetch admin user data using user ID"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_name = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()       

        return result 
    
    @classmethod
    def get_user_data_by_user_id(cls, id):
        """Fetch user data using user ID"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()       

        return result   

    @classmethod
    def get_user_data_by_user_idNum(cls, id):
        """Fetch user data using user ID"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()       

        return result        

    def create_user_account(full_name, email, id_number):   
        """Create a new admin account"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            INSERT INTO users (user_id, user_name, user_email)
            VALUES (%s, %s, %s)
        """, (id_number, full_name, email))
        
        conn.commit()
        cursor.close()
        conn.close()     

    @classmethod
    def get_all_staff(cls):
        """Get all staff members"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM staff")
        staff = cursor.fetchall()
        cursor.close()
        conn.close()
        return staff

    @classmethod
    def get_staff_by_id(cls, staff_id):
        """Get staff member by ID number"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM staff WHERE staff_id = %s", (staff_id,))
        staff = cursor.fetchone()
        cursor.close()
        conn.close()
        return staff

    @classmethod
    def create_staff(cls, id_number, full_name, email, role):
        """Create new staff member"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO staff (staff_id, full_name, email, role)
            VALUES (%s, %s, %s, %s)
        """, (id_number, full_name, email, role))
        conn.commit()
        cursor.close()
        conn.close()

    @classmethod
    def update_staff(cls, staff_id, full_name, email, role):
        """Update staff member"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE staff 
            SET 
                full_name = %s, 
                email = %s, 
                role = %s 
            WHERE staff_id = %s
        """, (full_name, email, role, staff_id))
        conn.commit()
        cursor.close()
        conn.close()

    @classmethod
    def delete_staff(cls, staff_id):
        """Delete staff member"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM staff WHERE staff_id = %s", (staff_id,))
        conn.commit()
        cursor.close()
        conn.close()

class Appointment:
    def __init__(self, appointment_data=None):
        """Initialize with appointment data dictionary"""
        if appointment_data:
            self.__dict__.update(appointment_data)

    @classmethod
    def get_pending_appointments(cls):
        """Fetch all pending appointments for admin view"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM appointments 
            WHERE status = 'pending'   
            AND appointment_date >= CURDATE()
            ORDER BY appointment_date DESC
        """)
        
        appointments = [cls(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return appointments

    @classmethod
    def get_active_appointments(cls):
        """Fetch all approved appointments"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM appointments 
            WHERE status = 'approved'
            AND appointment_date >= CURDATE()
            ORDER BY appointment_date ASC
        """)
        
        appointments = [cls(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return appointments

    @classmethod
    def approve_appointment(cls, appointment_id, approved_by, notes):
        """Admin approves an appointment"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get appointment details before deletion for notification
        cursor.execute("SELECT * FROM appointments WHERE id = %s", (appointment_id,))
        appointment = cls(cursor.fetchone())
        
        try:
            # Update appointment status
            cursor.execute("""
                UPDATE appointments 
                SET status = 'approved', 
                    approved_by = %s,
                    notes = %s,
                    approved_at = NOW()
                WHERE id = %s
            """, (approved_by, notes, appointment_id))

            if cursor.rowcount == 0:  # Check if any row was updated
                raise ValueError("Appointment not found or already processed")
            
            conn.commit()
            
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def reject_appointment(cls, appointment_id, rejected_by, reason):
        """Admin rejects an appointment"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get appointment details before deletion for notification
        cursor.execute("SELECT * FROM appointments WHERE id = %s", (appointment_id,))
        appointment = cls(cursor.fetchone())        
        
        try:
            # Delete or mark as rejected based on your business logic
            cursor.execute("""
                UPDATE appointments 
                SET status = 'rejected',
                    approved_by = %s,
                    rejection_reason = %s,
                    approved_at = NOW()
                WHERE id = %s
            """, (rejected_by, reason, appointment_id))

            if cursor.rowcount == 0:  # Check if any row was updated
                raise ValueError("Appointment not found or already processed")
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def cancel_appointment(cls, appointment_id, cancelled_by, reason):
        """Admin rejects an appointment"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get appointment details before deletion for notification
        cursor.execute("SELECT * FROM appointments WHERE id = %s", (appointment_id,))
        appointment = cls(cursor.fetchone())        
        
        try:
            # Delete or mark as rejected based on your business logic
            cursor.execute("""
                UPDATE appointments 
                SET status = 'cancelled',
                    approved_by = %s,
                    rejection_reason = %s,
                    approved_at = NOW()
                WHERE id = %s
            """, (cancelled_by, reason, appointment_id))

            if cursor.rowcount == 0:  # Check if any row was updated
                raise ValueError("Appointment not found or already processed")
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()            

    @classmethod
    def reschedule_appointment(cls, appointment_id, new_date, new_time, reason):
        """Reschedule an existing appointment"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Get original appointment details
            cursor.execute("SELECT * FROM appointments WHERE id = %s", (appointment_id,))
            original = cls(cursor.fetchone())
            
            # Check for conflicts
            if cls.is_conflict(new_date, new_time):
                raise ValueError("The requested time slot is not available")
            
            # Update appointment
            cursor.execute("""
                UPDATE appointments 
                SET appointment_date = %s,
                    appointment_time = %s,
                    status = 'rescheduled',
                    notes = %s,
                WHERE id = %s
            """, (new_date, new_time, appointment_id))
            
            conn.commit()
            
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def is_conflict(date, time):
        """Check if time slot is already taken"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM appointments 
            WHERE appointment_date = %s 
            AND appointment_time = %s
            AND status IN ('approved')
        """, (date, time))
        
        conflict = cursor.fetchone()[0] > 0
        
        cursor.close()
        conn.close()
        return conflict

    @classmethod
    def get_available_slots(cls):
        """Get available time slots for scheduling"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get booked slots
        cursor.execute("""
            SELECT appointment_date, appointment_time 
            FROM appointments 
            WHERE status IN ('approved', 'scheduled')
            AND appointment_date >= CURDATE()
        """)
        
        booked_slots = {
            f"{row['appointment_date']} {row['appointment_time']}"
            for row in cursor.fetchall()
        }
        
        cursor.close()
        conn.close()

        today = datetime.today()
        available_slots = []

        # Generate slots for next 7 days
        for day in range(7):
            current_date = today + timedelta(days=day)
            if current_date.weekday() >= 5:  # Skip weekends
                continue

            date_str = current_date.strftime("%Y-%m-%d")
            
            # Generate time slots (9AM-4PM, skip lunch)
            for hour in [9, 10, 11, 13, 14, 15]:
                time_str = f"{hour:02d}:00"
                slot = f"{date_str} {time_str}"
                
                if slot not in booked_slots:
                    available_slots.append({
                        "date": date_str,
                        "time": time_str
                    })

        return available_slots