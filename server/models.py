"""
SQLAlchemy ORM модели для BeautyPro
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from server.database import Base


# Таблица связи многие-ко-многим: мастера <-> услуги
master_services = Table(
    "master_services",
    Base.metadata,
    Column("master_id", Integer, ForeignKey("masters.id"), primary_key=True),
    Column("service_id", Integer, ForeignKey("services.id"), primary_key=True),
)


class User(Base):
    """Модель пользователя (клиент или администратор)"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="client")  # 'client' или 'admin'

    # Связь с записями
    appointments: Mapped[List["Appointment"]] = relationship(back_populates="client")

    def __repr__(self) -> str:
        return f"User(id={self.id}, phone={self.phone_number}, role={self.role})"


class Profession(Base):
    """Модель профессии"""
    __tablename__ = "professions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    # Связи
    masters: Mapped[List["Master"]] = relationship(back_populates="profession")
    services: Mapped[List["Service"]] = relationship(back_populates="profession")

    def __repr__(self) -> str:
        return f"Profession(id={self.id}, name={self.name})"


class Master(Base):
    """Модель мастера"""
    __tablename__ = "masters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100))
    profession_id: Mapped[int] = mapped_column(ForeignKey("professions.id"))
    contact_info: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)  # Для "мягкого" удаления

    # Связи
    profession: Mapped["Profession"] = relationship(back_populates="masters")
    services: Mapped[List["Service"]] = relationship(
        secondary=master_services,
        back_populates="masters"
    )
    appointments: Mapped[List["Appointment"]] = relationship(back_populates="master")

    def __repr__(self) -> str:
        return f"Master(id={self.id}, name={self.full_name})"


class Service(Base):
    """Модель услуги"""
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    profession_id: Mapped[int] = mapped_column(ForeignKey("professions.id"))

    # Связи
    profession: Mapped["Profession"] = relationship(back_populates="services")
    masters: Mapped[List["Master"]] = relationship(
        secondary=master_services,
        back_populates="services"
    )
    appointments: Mapped[List["Appointment"]] = relationship(back_populates="service")

    def __repr__(self) -> str:
        return f"Service(id={self.id}, name={self.name}, price={self.price})"


class Appointment(Base):
    """Модель записи на процедуру"""
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id"))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    appointment_datetime: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")  # scheduled, completed, canceled

    # Связи
    client: Mapped["User"] = relationship(back_populates="appointments")
    master: Mapped["Master"] = relationship(back_populates="appointments")
    service: Mapped["Service"] = relationship(back_populates="appointments")

    def __repr__(self) -> str:
        return f"Appointment(id={self.id}, datetime={self.appointment_datetime}, status={self.status})"
