
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database.db import Base


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    exam_name = Column(String(200), nullable=False)
    total_questions = Column(Integer, nullable=False)
    options_per_question = Column(Integer, default=4)
    marks_per_correct = Column(Float, default=1.0)
    negative_marking = Column(Float, default=0.0)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    answer_key = relationship(
        "AnswerKey",
        back_populates="exam",
        uselist=False,
        cascade="all, delete-orphan"
    )

    results = relationship(
        "OMRResult",
        back_populates="exam",
        cascade="all, delete-orphan"
    )


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(200), nullable=False)
    roll_number = Column(String(50), unique=True, nullable=False)
    email = Column(String(200), nullable=True)

    results = relationship(
        "OMRResult",
        back_populates="student"
    )


class AnswerKey(Base):
    __tablename__ = "answer_keys"

    id = Column(Integer, primary_key=True, index=True)

    exam_id = Column(
        Integer,
        ForeignKey("exams.id"),
        unique=True,
        nullable=False
    )

    answers = Column(JSON, nullable=False)

    exam = relationship(
        "Exam",
        back_populates="answer_key"
    )


class OMRResult(Base):
    __tablename__ = "omr_results"

    __table_args__ = (
        UniqueConstraint(
            "exam_id",
            "student_id",
            name="uq_exam_student_result"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    exam_id = Column(
        Integer,
        ForeignKey("exams.id"),
        nullable=False
    )

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    detected_answers = Column(JSON, nullable=False)

    correct = Column(Integer, default=0)
    incorrect = Column(Integer, default=0)
    unanswered = Column(Integer, default=0)
    review_required = Column(Integer, default=0)

    score = Column(Float, default=0.0)
    maximum_marks = Column(Float, default=0.0)
    percentage = Column(Float, default=0.0)

    evaluated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    exam = relationship(
        "Exam",
        back_populates="results"
    )

    student = relationship(
        "Student",
        back_populates="results"
    )
