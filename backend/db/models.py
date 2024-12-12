from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.types import JSON
from sqlalchemy import create_engine
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy import Index
from sqlalchemy.schema import Table
from .base import Base
from .types import JSONField


class School(Base):
    __tablename__ = "schools"

    id: Mapped[UUID] = mapped_column(PgUUID, primary_key=True, server_default=func.uuid_generate_v4())
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)  # Índice en teléfono
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    students: Mapped[List["Student"]] = relationship(back_populates="school")
    conversations: Mapped[List["Conversation"]] = relationship(back_populates="school")


class Tutor(Base):
    __tablename__ = "tutors"

    id: Mapped[UUID] = mapped_column(PgUUID, primary_key=True, server_default=func.uuid_generate_v4())
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)  # Índice en teléfono
    email: Mapped[Optional[str]] = mapped_column(String(255),index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    students: Mapped[List["Student"]] = relationship("Student", secondary="tutor_student", back_populates="tutors")


class Student(Base):
    __tablename__ = "students"

    id: Mapped[UUID] = mapped_column(PgUUID, primary_key=True, server_default=func.uuid_generate_v4())
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[datetime] = mapped_column(Date, nullable=False)
    school_id: Mapped[UUID] = mapped_column(PgUUID, ForeignKey("schools.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    school: Mapped["School"] = relationship(back_populates="students")
    tutors: Mapped[List["Tutor"]] = relationship("Tutor", secondary="tutor_student", back_populates="students")
    conversations: Mapped[List["Conversation"]] = relationship(back_populates="student")


class TutorStudent(Base):
    __tablename__ = "tutor_student"

    tutor_id: Mapped[UUID] = mapped_column(PgUUID, ForeignKey("tutors.id"), primary_key=True)
    student_id: Mapped[UUID] = mapped_column(PgUUID, ForeignKey("students.id"), primary_key=True)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_tutor_student_compound', 'tutor_id', 'student_id'),
        Index('idx_tutor_student_active', 'is_active')  # Útil para filtrar tutores activos
    )

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[UUID] = mapped_column(PgUUID, primary_key=True, server_default=func.uuid_generate_v4())
    student_id: Mapped[UUID] = mapped_column(PgUUID, ForeignKey("students.id"), nullable=False)
    school_id: Mapped[UUID] = mapped_column(PgUUID, ForeignKey("schools.id"), nullable=False)
    claude_conversation_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="INITIATED")
    reason: Mapped[Optional[str]] = mapped_column(Text)
    last_interaction_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    __table_args__ = (
        CheckConstraint(
            status.in_([
                'INITIATED',
                'PENDING_TUTOR',
                'ACTIVE_TUTOR_DIALOG',
                'PENDING_SCHOOL_CONFIRMATION',
                'SCHOOL_CONFIRMED',
                'CLOSED',
                'CANCELLED'
            ]),
            name='valid_status'
        ),
        # Añadimos el índice
        Index('idx_conversations_claude_id', 'claude_conversation_id'),
    )

    student: Mapped["Student"] = relationship(back_populates="conversations")
    school: Mapped["School"] = relationship(back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"


    id: Mapped[UUID] = mapped_column(PgUUID, primary_key=True, server_default=func.uuid_generate_v4())
    conversation_id: Mapped[UUID] = mapped_column(PgUUID, ForeignKey("conversations.id"), nullable=False, index=True)  # Índice usando mapped_column
    sender_type: Mapped[str] = mapped_column(String(50), nullable=False)
    sender_id: Mapped[UUID] = mapped_column(PgUUID, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    JSONField
    claude_response_metadata: Mapped[Optional[dict]] = mapped_column(JSONField)
    #claude_response_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            sender_type.in_(['SCHOOL', 'TUTOR', 'CLAUDE']),
            name='valid_sender_type'
        ),
        Index('idx_messages_created_at', 'created_at'),
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

class ServiceStatus(Base):
    __tablename__ = "service_status"

    id : Mapped[UUID]= mapped_column(PgUUID, primary_key=True, server_default=func.uuid_generate_v4())
    service_name : Mapped[str] = mapped_column(String(50), nullable=False)
    status : Mapped[bool] = mapped_column(Boolean, default=False)
    last_check : Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    error_message : Mapped[str] = mapped_column(String(50), nullable=False)