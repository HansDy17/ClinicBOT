from phi.agent import Agent
from phi.model.ollama import Ollama
from datetime import datetime, timedelta
import dateparser

appointments = []  # Replace this with a proper database in production

def process_appointment_request(user_input):
    # Parse date and time from user input using Llama3.2 and `dateparser`
    parsed_response = clinic_agent.model.chat(input=f"Extract date and time from: {user_input}", context="")
    date_time = parse_date_time(parsed_response)
    
    if not date_time:
        print("ClinicBOT: I couldn't determine a date and time from your input. Can you provide a specific day and time?")
        return

    # Ensure the date is valid and in the future
    if date_time <= datetime.now():
        print("ClinicBOT: The date and time you provided are in the past. Can you provide a future date?")
        return

    # Check for conflicts
    conflict = check_appointment_conflict(date_time)
    if conflict:
        print(f"ClinicBOT: The selected time ({date_time.strftime('%Y-%m-%d %I:%M %p')}) is already booked.")
        suggest_alternatives(date_time)
        return

    # Gather additional details
    name = input("ClinicBOT: Can I have your name? ").strip()
    reason = input("ClinicBOT: Can you tell me the reason for your visit? ").strip()

    # Confirm details
    print(f"ClinicBOT: Here's the information I gathered:")
    print(f"    Name: {name}") 
    print(f"    Date: {date_time.strftime('%Y-%m-%d')}")
    print(f"    Time: {date_time.strftime('%I:%M %p')}")
    print(f"    Reason: {reason}")

    confirm = input("ClinicBOT: Does this look correct? (yes/no) ").strip().lower()
    if confirm == "yes":
        # Save the appointment
        appointments.append({
            "name": name,
            "date": date_time.date(),
            "time": date_time.time(),
            "reason": reason
        })
        print("ClinicBOT: Your appointment has been scheduled. Thank you!")
    else:
        print("ClinicBOT: Let's try again.")
        process_appointment_request("I want to make an appointment")  # Restart the process

def parse_date_time(response):
    """
    Use `dateparser` to extract and parse a date and time from the agent's response.
    """
    date_time = dateparser.parse(response, settings={"PREFER_DATES_FROM": "future"})
    return date_time

def check_appointment_conflict(date_time):
    """
    Check if the selected date and time conflicts with existing appointments.
    """
    for appointment in appointments:
        if appointment["date"] == date_time.date() and appointment["time"] == date_time.time():
            return True
    return False

def suggest_alternatives(date_time):
    """
    Suggest alternative times if there's a conflict.
    """
    print("ClinicBOT: Let me suggest some alternatives.")
    alternative_times = []
    for i in range(1, 6):  # Suggest up to 5 alternative times
        new_time = date_time + timedelta(minutes=30 * i)  # Suggest 30-minute intervals
        if not check_appointment_conflict(new_time):
            alternative_times.append(new_time)

    if alternative_times:
        print("ClinicBOT: Here are some available options:")
        for alt_time in alternative_times:
            print(f"    {alt_time.strftime('%Y-%m-%d %I:%M %p')}")
    else:
        print("ClinicBOT: Sorry, I couldn't find any nearby free slots. Try a different day.")


scheduler_agent = Agent(
    name="ClinicBot",
    description="Book and manage appointments",
    model=Ollama(id="clinic_llama32"),
    role="Handle appointment scheduling and availability checks for the university clinic.",
    tools=[process_appointment_request()],
    instructions=[
        f"""
        "Always verify time slot availability before confirming appointments",
        "Handle rescheduling requests by first canceling existing appointments",
        "Provide alternative time slots in case of conflicts",
        "Maintain a log of all appointments for reference"
        """
        ],
    debug_mode=True,
    # knowledge=knowledge_base,
    # search_knowledge=True,
)
# clinic_agent.knowledge.load(recreate=False)

