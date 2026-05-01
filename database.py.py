import os
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()

usuarios = Table(
    "usuarios",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("nome", String, nullable=False),
    Column("telegram_id", String, unique=True, nullable=False),
)

def init_db():
    metadata.create_all(bind=engine)
