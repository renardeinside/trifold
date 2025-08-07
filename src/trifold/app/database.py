from sqlmodel import SQLModel

from trifold.app.config import rt
from trifold.app.notify import notify_function, notify_trigger


def create_db_and_tables():
    rt.logger.info("Creating database and tables...")
    SQLModel.metadata.create_all(rt.engine)
    rt.logger.info("Database and tables created successfully.")

    rt.logger.info("Creating notify function and trigger...")

    with rt.engine.connect() as conn:
        conn.execute(notify_function)
        conn.execute(notify_trigger)
        conn.commit()

    rt.logger.info("Notify function and trigger created successfully.")

    rt.logger.info("Database initialized successfully.")
