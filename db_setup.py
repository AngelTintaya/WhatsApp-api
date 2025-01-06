from sqlalchemy import Column, String, create_engine, insert, DateTime, select, desc
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from datetime import datetime
from pytz import timezone

Base = declarative_base()

# Define the GMT-5 timezone
LOCAL_TIMEZONE = timezone("America/Lima")

class AgentSession(Base):
    __tablename__ = "md_agent"
    session_id = Column(String, primary_key=True)
    phone_id = Column(String, primary_key=True)
    inserted_at = Column(DateTime, default=lambda: datetime.now(LOCAL_TIMEZONE))  # Timestamp in GMT-5

# Internal engine setup
DATABASE_URL = "sqlite:///tmp/agent_storage.db"

# Ensure directory exists
db_path = DATABASE_URL.split("sqlite:///")[-1]
os.makedirs(os.path.dirname(db_path), exist_ok=True)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Database setup
def setup_database():
    """
    Create the database and table if they do not exist.
    """
    Base.metadata.create_all(engine)

# Function to save credentials
def save_credentials_in_db(session_id: str, phone_id: str) -> None:
    """
    Save session_id and phone_id into the md_agent table.
    Skip insertion if the record already exists.
    """
    session = Session()

    stmt = insert(AgentSession).values(
        session_id=session_id,
        phone_id=phone_id,
        inserted_at=datetime.now(LOCAL_TIMEZONE)  # Use the current GMT-5 time
    ).prefix_with("OR IGNORE")  # Add ON CONFLICT DO NOTHING

    try:
        session.execute(stmt)
        session.commit()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        session.close()

# Function to get the last session_id from phone_id
def get_last_session_id_from_phone(phone_number: str) -> str:
    """
    Retrieve the last session_id associated with the given phone_number.
    Returns the session_id if found, otherwise None.
    """
    session = Session()

    try:
        stmt = (
            select(AgentSession.session_id)
            .where(AgentSession.phone_id == phone_number)
            .order_by(desc(AgentSession.inserted_at))  # Order by the timestamp
            .limit(1)
        )
        result = session.execute(stmt).scalar()  # Get the first scalar result
        return result  # Returns None if no record is found
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        session.close()
