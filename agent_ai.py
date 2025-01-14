from phi.agent import Agent
# from phi.model.openai import OpenAIChat
from phi.model.groq import Groq
from phi.storage.agent.sqlite import SqlAgentStorage
from typing import List

from db_setup import setup_database, save_credentials_in_db, get_last_session_id_from_phone
from dotenv import load_dotenv

from datetime import datetime
# Get today's date
today_date = datetime.today().strftime('%d/%m/%Y')  # Format as dd/mm/yyyy

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
        description="Eva, asistente del concesionario de autos Connectia, especializada en programar citas y responder preguntas.",
        task="Gestionar citas y consultas sobre mantenimiento de autos.",
        instructions=[
            f"Hoy es {today_date}. Utiliza esta fecha como referencia para fechas relativas o validación.",
            "Inicia presentandote y pregunta amablemente el nombre del usuario.",
            "Ayuda a programar citas de mantenimiento y responder preguntas.",
            "Pregunta por fecha y hora futura. Si falta el año, usa el actual o pide confirmación.",
            "Valida que la fecha proporcionada sea válida (existe en el calendario). Si no es válida, pide una fecha diferente.",
            "Confirma la fecha de la cita de forma clara: '¿Te gustaría agendar la cita para el [Fecha (dd/yy/MMMM)]?'. Si la fecha no es válida o es una fecha pasada, pide otra fecha.",
            "Mantén las respuestas cortas, enfocándote en la fecha, hora y confirmación.",
            "Responde brevemente a preguntas sobre el taller, priorizando las citas."
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