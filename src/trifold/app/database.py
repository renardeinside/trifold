from sqlmodel import SQLModel

from trifold.app.config import rt


def create_db_and_tables():
    rt.logger.info("Creating database and tables...")
    SQLModel.metadata.create_all(rt.engine)
    rt.logger.info("Database and tables created successfully.")
