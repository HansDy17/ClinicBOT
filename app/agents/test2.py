from datetime import datetime, timedelta
from os import getenv
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

# Database configuration
db_config = {
    'host': getenv('MYSQL_HOST'),
    'user': getenv('MYSQL_USERNAME'),
    'password': getenv('MYSQL_PASSWORD'),
    'database': getenv('MYSQL_NAME')
}

def set_clinic_appointment(date: str, time: str, patient_name: str) -> str:
    """
    Set an appointment at the clinic.

    Args:
        date (str): Date of the appointment (YYYY-MM-DD)
        time (str): Time of the appointment (HH:MM)
        patient_name (str): Name of the patient

    Returns:
        str: Confirmation message
    """
    # In a real scenario, you would integrate with your clinic's scheduling system
    # For this example, we'll just return a confirmation message
    appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    end_time = appointment_datetime + timedelta(minutes=30)

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
                    INSERT INTO appointments (user_id, appointment_date, purpose)
                    VALUES (%s, %s, %s)
                """, (1,date, patient_name))
        conn.commit()
    except mysql.connector.Error as e:
        return f"Database error: {str(e)}"
    finally:
        cursor.close()
        conn.close()
    
    return f"Appointment set for {patient_name} on {appointment_datetime.strftime('%B %d, %Y at %I:%M %p')} to {end_time.strftime('%I:%M %p')}."

from phi.agent import Agent
from phi.model.ollama import Ollama
 
agent = Agent(
    name="Clinic Appointment Assistant",
    instructions=[
        f"You're a clinic appointment assistant. Today is {datetime.now().strftime('%B %d, %Y')}.",
        "You can help users by setting appointments at the clinic.",
        "Clinic hours are from 9:00 AM to 5:00 PM, Monday to Friday.",
        "Appointments are 30 minutes long.",
    ],
    model=Ollama(id="llama3.2"),
    tools=[set_clinic_appointment],
    # show_tool_calls=True,
    # markdown=True,
)


def handle_conversation():
    print("ClinicBOT: Welcome to University Health Services. How can I help you today?")
    conversation_state = {}
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break
                
            response = agent.run(user_input)
            print(f"\nClinicBOT: {response}")

        except KeyboardInterrupt:
            print("\nSession ended.")
            break
        except Exception as e:
            print(f"\nClinicBOT: I encountered an error. Please try again. {str(e)}")

if __name__ == "__main__":
    handle_conversation()