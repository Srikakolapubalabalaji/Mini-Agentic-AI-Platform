import json

from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from agentops.application.config import settings

Base = declarative_base()


class EventLog(Base):
    """
    Append-only event log for auditing and replay.
    """

    __tablename__ = "event_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, index=True)
    trace_id = Column(String)
    message_type = Column(String)
    created_at = Column(String)
    payload = Column(Text)  # JSON serialized A2A envelope


engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def append_event(
    run_id: str, trace_id: str, message_type: str, created_at: str, payload_dict: dict
):
    with SessionLocal() as session:
        event = EventLog(
            run_id=run_id,
            trace_id=trace_id,
            message_type=message_type,
            created_at=created_at,
            payload=json.dumps(payload_dict),
        )
        session.add(event)
        session.commit()
