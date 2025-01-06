from agent_ai import ask_eva
from db_setup import setup_database, save_credentials_in_db, get_last_session_id_from_phone

setup_database()

test_get_session = False
test_eva = True
test_db = False
phone_id="989898989" # 989898989 121122121

if test_get_session:
    session_id = get_last_session_id_from_phone(phone_id)
    print(session_id)

if test_eva:
    rpta, session_id = ask_eva(
        'Si, es correcta!',
        phone_id
        )
    print(rpta)

    """
    rpta, session_id = ask_eva(
        'Quisiera agendar una cita',
        123456,
        rules=[
            "When asked to schedule, request for a date"
            ]
        )
    print(rpta)
    """

if test_db:
    save_credentials_in_db(session_id=session_id, phone_id=phone_id)