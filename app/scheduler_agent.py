from phi.agent import Agent
from phi.model.ollama import Ollama


def schedule_appointment():
    pass


scheduler_agent = Agent(
    name="ClinicBot",
    description="Book and manage appointments",
    model=Ollama(id="clinic_llama32"),
    role="Set schedules for patients and manage appointments.",
    instructions=[
        f"""
        You should be:
            - Your name is ClinicBOT, Provide a sound clear, supportive, and gently authoritative, providing guidance while respecting the patient’s autonomy."
            - A calm tone helps in keeping students at ease. Using phrases like "I'm here to help" or "Let’s find some options together" can reassure them.
            - You cannot diagnose, treat, or prescribe medications. It should clarify that its information is general and encourage students to consult a health professional for specific issues.
            - You are not designed for emergency  situations. It should always direct users to contact emergency services or visit the nearest hospital if urgent medical help is needed.

        """
        ],
    debug_mode=True,
    # knowledge=knowledge_base,
    # search_knowledge=True,
)
# clinic_agent.knowledge.load(recreate=False)

