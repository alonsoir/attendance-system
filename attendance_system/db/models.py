from sqlalchemy import Boolean, Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    interactions = relationship("Interaction", back_populates="created_by")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    student_name = Column(String, index=True)
    tutor_phone = Column(String)
    tutor_name = Column(String, nullable=True)
    status = Column(String)  # active, resolved, closed
    claude_response = Column(JSON)
    sensitivity_score = Column(Integer)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime, nullable=True)

    # Relaciones
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("User", back_populates="interactions")

    # Historial de mensajes
    messages = relationship("InteractionMessage", back_populates="interaction")


class InteractionMessage(Base):
    __tablename__ = "interaction_messages"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    sender_type = Column(String)  # system, tutor, claude
    content = Column(String)
    metadata = Column(JSON, nullable=True)

    interaction = relationship("Interaction", back_populates="messages")


class ServiceStatus(Base):
    __tablename__ = "service_status"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, unique=True)
    status = Column(Boolean)
    last_check = Column(DateTime, default=datetime.utcnow)
    error_message = Column(String, nullable=True)
