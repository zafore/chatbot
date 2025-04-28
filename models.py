# models.py
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    user_message = Column(String)
    bot_response = Column(String)

engine = create_engine('sqlite:///chatbot.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
