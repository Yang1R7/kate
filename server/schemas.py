"""
Pydantic схемы для валидации данных API
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    phone_number: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Схема для регистрации"""
    password: str


class UserLogin(BaseModel):
    """Схема для авторизации"""
    phone_number: str
    password: str


class UserResponse(UserBase):
    """Схема ответа пользователя"""
    id: int
    role: str

    model_config = ConfigDict(from_attributes=True)


# ==================== PROFESSION SCHEMAS ====================

class ProfessionBase(BaseModel):
    name: str


class ProfessionResponse(ProfessionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ==================== SERVICE SCHEMAS ====================

class ServiceBase(BaseModel):
    name: str
    price: float
    duration_minutes: int
    profession_id: int


class ServiceCreate(ServiceBase):
    """Схема создания услуги"""
    pass


class ServiceUpdate(BaseModel):
    """Схема обновления услуги"""
    name: Optional[str] = None
    price: Optional[float] = None
    duration_minutes: Optional[int] = None
    profession_id: Optional[int] = None


class ServiceResponse(ServiceBase):
    id: int
    profession: Optional[ProfessionResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ServiceBrief(BaseModel):
    """Краткая информация об услуге"""
    id: int
    name: str
    price: float
    duration_minutes: int

    model_config = ConfigDict(from_attributes=True)


# ==================== MASTER SCHEMAS ====================

class MasterBase(BaseModel):
    full_name: str
    profession_id: int
    contact_info: Optional[str] = None


class MasterCreate(MasterBase):
    """Схема создания мастера"""
    service_ids: Optional[List[int]] = []


class MasterUpdate(BaseModel):
    """Схема обновления мастера"""
    full_name: Optional[str] = None
    profession_id: Optional[int] = None
    contact_info: Optional[str] = None
    service_ids: Optional[List[int]] = None


class MasterResponse(MasterBase):
    """Схема ответа мастера"""
    id: int
    is_active: bool
    profession: Optional[ProfessionResponse] = None
    services: List[ServiceBrief] = []

    model_config = ConfigDict(from_attributes=True)


class MasterBrief(BaseModel):
    """Краткая информация о мастере"""
    id: int
    full_name: str
    profession: Optional[ProfessionResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== APPOINTMENT SCHEMAS ====================

class AppointmentBase(BaseModel):
    master_id: int
    service_id: int
    appointment_datetime: datetime


class AppointmentCreate(AppointmentBase):
    """Схема создания записи"""
    pass


class AppointmentResponse(BaseModel):
    """Схема ответа записи"""
    id: int
    appointment_datetime: datetime
    status: str
    master: MasterBrief
    service: ServiceBrief

    model_config = ConfigDict(from_attributes=True)


class AppointmentWithClient(AppointmentResponse):
    """Схема записи с информацией о клиенте (для админа)"""
    client: UserResponse

    model_config = ConfigDict(from_attributes=True)


# ==================== TIME SLOT SCHEMAS ====================

class TimeSlot(BaseModel):
    """Доступный временной слот"""
    time: str  # Формат "HH:MM"
    datetime: datetime


class AvailableSlotsResponse(BaseModel):
    """Ответ с доступными слотами"""
    date: str
    slots: List[TimeSlot]


# ==================== GENERIC RESPONSES ====================

class MessageResponse(BaseModel):
    """Общий ответ с сообщением"""
    message: str
    success: bool = True
