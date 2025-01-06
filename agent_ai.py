from phi.agent import Agent
# from phi.model.openai import OpenAIChat
from phi.model.groq import Groq
from phi.storage.agent.sqlite import SqlAgentStorage
from typing import List

from db_setup import setup_database, save_credentials_in_db, get_last_session_id_from_phone
from dotenv import load_dotenv

load_dotenv()
setup_database()

def ask_eva(query: str, phone_number:int, rules: List[str] = None) -> str:
    if rules is None:
        rules = []  # Initialize an empty list if none provided
    
    session_id = get_last_session_id_from_phone(phone_number)
    instructions = ["The answer should be in spanish"]
    instructions.extend(rules)

    agent=Agent(
        session_id=session_id,
        # model=OpenAIChat(id="gpt-4o"),
        model=Groq(id="llama-3.3-70b-Versatile"),
        storage=SqlAgentStorage(table_name="agent_sessions", db_file="tmp/agent_storage.db"),
        description="You are a Car Shop Dialer Agent in Connectia",
        task="You should help customer to schedule car maintenance or answer doubts related to the carshop",
        instructions=[
            "Respond in Spanish for all questions and prompts.",
            "If asked to schedule an appointment, always request a specific date.",
            "If the provided date is missing a year, assume it is in the year of the next week.",
            "When a date is given, return it in the format 'dd/mm/YYYY' and ask the user to confirm if the date is correct.",
            "Only proceed with confirming the maintenance appointment once the date has been explicitly confirmed by the user.",
            "After confirming the appointment, always ensure the user knows that their car maintenance is scheduled, and end by expressing that you hope to see them there.",
        ],
        add_history_to_messages=True,
        num_history_responses=5,
        add_datetime_to_instructions=True,
        read_chat_history=True
    )

    if session_id is None:
        session_id = agent.session_id
        save_credentials_in_db(session_id, phone_number)
        print(f"Started Session: {session_id}\n")
    else:
        print(f"Continuing Session: {session_id}\n")

    response = agent.run(query)
    # print("Pregunta: ",query)
    # print(response.content)
    return response.content, session_id

"""
rpta, session_id = ask_eva(
    'Hola',
    123456
    )
print(rpta)


rpta, session_id = ask_eva(
    'Quisiera agendar una cita',
    123456,
    rules=[
        "When asked to schedule, request for a date"
        ]
    )
print(rpta)

rpta, session_id = ask_eva(
    'Claro, el 5 de Febrero',
    123456,
    rules=[
        "If year is missing, consider the year of the next week",
        "If a date is given, return it back in the formad dd/mm/YYYY, and ask to confirm if the date is correct",
        ]
    )
print(rpta)

rpta, session_id = ask_eva(
    'Si, es correcto',
    123456,
    rules=[
        "Only when date was confirmed or correct, always confirmcthat the car maintenance was done, and always end to hope to see them there",
        ]
    )
print(rpta)
"""