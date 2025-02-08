from phi.agent import Agent
from phi.model.ollama import Ollama
# from knowledge_based import knowledge_base


clinic_agent = Agent(
    name="ClinicBot",
    model=Ollama(id="clinic_llama32"),
    role="Help students, faculty, and staff interact with the university’s health services online.",
    instructions=[
        f"""
            "Do not provide medical diagnoses",
            "For emergencies, direct to campus emergency services",
            "Refer to clinic hours and services from knowledge base",
            "Maintain calm and supportive tone"
        """
        ],
)

