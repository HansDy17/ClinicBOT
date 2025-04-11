import mysql.connector
from os import getenv
from dotenv import load_dotenv  
from datetime import datetime, timedelta
import json
from flask_mail import Message
from ..import mail

load_dotenv() 

class DatabaseManager: 
    """Handles all database connections"""
    @staticmethod
    def get_db_connection():
        """Establish a connection to MySQL database."""
        return mysql.connector.connect(
            host=getenv('MYSQL_HOST'),
            user=getenv('MYSQL_USERNAME'),
            password=getenv('MYSQL_PASSWORD'),
            database=getenv('MYSQL_NAME')
        )

class Appointment:
    def __init__(self, appointment_data=None):
        """Initialize with appointment data dictionary"""
        if appointment_data:
            self.__dict__.update(appointment_data)

    @staticmethod
    def send_notification(email, subject, message):
        """Send email notification using Flask-Mail"""
        msg = Message(
            subject,
            sender=getenv('MAIL_USERNAME'),
            recipients=[email]
        )
        msg.body = message
        mail.send(msg)

    @classmethod
    def get_pending_appointments(cls):
        """Fetch all pending appointments for admin view"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM appointments 
            WHERE status = 'pending'
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
    def approve_appointment(cls, appointment_id, approved_by):
        """Admin approves an appointment"""
        conn = DatabaseManager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Update appointment status
            cursor.execute("""
                UPDATE appointments 
                SET status = 'approved', 
                    approved_by = %s,
                    approved_date = NOW()
                WHERE id = %s
            """, (approved_by, appointment_id))
            
            # Get appointment details for notification
            cursor.execute("SELECT * FROM appointments WHERE id = %s", (appointment_id,))
            appointment = cls(cursor.fetchone())
            
            conn.commit()
            
            # Send approval notification
            cls.send_notification(
                appointment.user_email,
                "Appointment Approved",
                f"Your appointment on {appointment.appointment_date} at {appointment.appointment_time} has been approved."
            )
            
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
        
        try:
            # Get appointment details before deletion for notification
            cursor.execute("SELECT * FROM appointments WHERE id = %s", (appointment_id,))
            appointment = cls(cursor.fetchone())
            
            # Delete or mark as rejected based on your business logic
            cursor.execute("""
                UPDATE appointments 
                SET status = 'rejected',
                    rejected_by = %s,
                    rejected_reason = %s,
                    rejected_date = NOW()
                WHERE id = %s
            """, (rejected_by, reason, appointment_id))
            
            conn.commit()
            
            # Send rejection notification
            cls.send_notification(
                appointment.user_email,
                "Appointment Rejected",
                f"Your appointment request has been rejected. Reason: {reason}"
            )
            
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def reschedule_appointment(cls, appointment_id, new_date, new_time):
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
                    status = 'rescheduled'
                WHERE id = %s
            """, (new_date, new_time, appointment_id))
            
            conn.commit()
            
            # Send reschedule notification
            cls.send_notification(
                original.user_email,
                "Appointment Rescheduled",
                f"Your appointment has been rescheduled to {new_date} at {new_time}"
            )
            
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
            AND status IN ('approved', 'scheduled')
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