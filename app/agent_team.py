from phi.agent import Agent
from phi.model.ollama import Ollama
from knowledge_based import knowledge_base
from scheduler_agent import scheduler_agent
from clinic_agent import clinic_agent


agent_team = Agent(
    name="ClinicBot",
    team=[scheduler_agent, clinic_agent],
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
    knowledge=knowledge_base,
    search_knowledge=True,
    show_tool_calls=True,
)
clinic_agent.knowledge.load(recreate=False)


def handle_conversation():
    context = "" # store the history here
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        agent_team.print_response(user_input, stream=True)


if __name__=="__main__":
    handle_conversation()