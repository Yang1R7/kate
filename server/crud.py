"""
CRUD операции для работы с базой данных
"""
from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from passlib.hash import bcrypt

from server import models, schemas


# ==================== PASSWORD UTILS ====================

def hash_password(password: str) -> str:
    """Хеширование пароля"""
    return bcrypt.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Проверка пароля"""
    return bcrypt.verify(password, hashed)


# ==================== USER CRUD ====================

def get_user_by_phone(db: Session, phone_number: str) -> Optional[models.User]:
    """Получить пользователя по номеру телефона"""
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Получить пользователя по ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Создать нового пользователя (клиента)"""
    db_user = models.User(
        phone_number=user.phone_number,
        password_hash=hash_password(user.password),
        full_name=user.full_name,
        role="client"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, phone_number: str, password: str) -> Optional[models.User]:
    """Аутентификация пользователя"""
    user = get_user_by_phone(db, phone_number)
    if user and verify_password(password, user.password_hash):
        return user
    return None


# ==================== PROFESSION CRUD ====================

def get_professions(db: Session) -> List[models.Profession]:
    """Получить все профессии"""
    return db.query(models.Profession).all()


def get_profession_by_id(db: Session, profession_id: int) -> Optional[models.Profession]:
    """Получить профессию по ID"""
    return db.query(models.Profession).filter(models.Profession.id == profession_id).first()


# ==================== SERVICE CRUD ====================

def get_services(db: Session) -> List[models.Service]:
    """Получить все услуги"""
    return db.query(models.Service).all()


def get_services_by_profession(db: Session, profession_id: int) -> List[models.Service]:
    """Получить услуги по профессии"""
    return db.query(models.Service).filter(models.Service.profession_id == profession_id).all()


def get_service_by_id(db: Session, service_id: int) -> Optional[models.Service]:
    """Получить услугу по ID"""
    return db.query(models.Service).filter(models.Service.id == service_id).first()


def get_master_services(db: Session, master_id: int) -> List[models.Service]:
    """Получить услуги конкретного мастера"""
    master = db.query(models.Master).filter(models.Master.id == master_id).first()
    if master:
        return master.services
    return []


def create_service(db: Session, service: schemas.ServiceCreate) -> models.Service:
    """Создать новую услугу"""
    db_service = models.Service(
        name=service.name,
        price=service.price,
        duration_minutes=service.duration_minutes,
        profession_id=service.profession_id
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


def update_service(db: Session, service_id: int, service: schemas.ServiceUpdate) -> Optional[models.Service]:
    """Обновить услугу"""
    db_service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not db_service:
        return None
    
    if service.name is not None:
        db_service.name = service.name
    if service.price is not None:
        db_service.price = service.price
    if service.duration_minutes is not None:
        db_service.duration_minutes = service.duration_minutes
    if service.profession_id is not None:
        db_service.profession_id = service.profession_id
    
    db.commit()
    db.refresh(db_service)
    return db_service


def delete_service(db: Session, service_id: int) -> bool:
    """Удалить услугу"""
    db_service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not db_service:
        return False
    
    db.delete(db_service)
    db.commit()
    return True


# ==================== MASTER CRUD ====================

def get_masters(db: Session, active_only: bool = True) -> List[models.Master]:
    """Получить всех мастеров"""
    query = db.query(models.Master)
    if active_only:
        query = query.filter(models.Master.is_active == True)
    return query.all()


def get_master_by_id(db: Session, master_id: int) -> Optional[models.Master]:
    """Получить мастера по ID"""
    return db.query(models.Master).filter(models.Master.id == master_id).first()


def get_masters_by_service(db: Session, service_id: int) -> List[models.Master]:
    """Получить мастеров, оказывающих определенную услугу"""
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if service:
        return [m for m in service.masters if m.is_active]
    return []


def create_master(db: Session, master: schemas.MasterCreate) -> models.Master:
    """Создать нового мастера"""
    db_master = models.Master(
        full_name=master.full_name,
        profession_id=master.profession_id,
        contact_info=master.contact_info
    )
    
    # Привязываем услуги
    if master.service_ids:
        services = db.query(models.Service).filter(models.Service.id.in_(master.service_ids)).all()
        db_master.services = services
    
    db.add(db_master)
    db.commit()
    db.refresh(db_master)
    return db_master


def update_master(db: Session, master_id: int, master_update: schemas.MasterUpdate) -> Optional[models.Master]:
    """Обновить данные мастера"""
    db_master = get_master_by_id(db, master_id)
    if not db_master:
        return None
    
    if master_update.full_name is not None:
        db_master.full_name = master_update.full_name
    if master_update.profession_id is not None:
        db_master.profession_id = master_update.profession_id
    if master_update.contact_info is not None:
        db_master.contact_info = master_update.contact_info
    if master_update.service_ids is not None:
        services = db.query(models.Service).filter(models.Service.id.in_(master_update.service_ids)).all()
        db_master.services = services
    
    db.commit()
    db.refresh(db_master)
    return db_master


def delete_master(db: Session, master_id: int) -> bool:
    """Удалить мастера из базы данных"""
    db_master = get_master_by_id(db, master_id)
    if db_master:
        # Удаляем связи с услугами
        db_master.services = []
        db.commit()
        # Удаляем мастера
        db.delete(db_master)
        db.commit()
        return True
    return False


def assign_services_to_master(db: Session, master_id: int, service_ids: List[int]) -> Optional[models.Master]:
    """Назначить услуги мастеру"""
    db_master = get_master_by_id(db, master_id)
    if not db_master:
        return None
    
    services = db.query(models.Service).filter(models.Service.id.in_(service_ids)).all()
    db_master.services = services
    db.commit()
    db.refresh(db_master)
    return db_master


# ==================== APPOINTMENT CRUD ====================

def get_appointments_by_client(
    db: Session, 
    client_id: int, 
    status: Optional[str] = None,
    upcoming_only: bool = False
) -> List[models.Appointment]:
    """Получить записи клиента"""
    query = db.query(models.Appointment).filter(models.Appointment.client_id == client_id)
    
    if status:
        query = query.filter(models.Appointment.status == status)
    
    if upcoming_only:
        query = query.filter(
            models.Appointment.appointment_datetime >= datetime.now(),
            models.Appointment.status == "scheduled"
        )
    
    return query.order_by(models.Appointment.appointment_datetime.desc()).all()


def get_appointment_by_id(db: Session, appointment_id: int) -> Optional[models.Appointment]:
    """Получить запись по ID"""
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()


def create_appointment(
    db: Session, 
    client_id: int, 
    appointment: schemas.AppointmentCreate
) -> models.Appointment:
    """Создать новую запись"""
    db_appointment = models.Appointment(
        client_id=client_id,
        master_id=appointment.master_id,
        service_id=appointment.service_id,
        appointment_datetime=appointment.appointment_datetime,
        status="scheduled"
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


def cancel_appointment(db: Session, appointment_id: int, client_id: int) -> bool:
    """Отменить запись"""
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.client_id == client_id
    ).first()
    
    if appointment and appointment.status == "scheduled":
        appointment.status = "canceled"
        db.commit()
        return True
    return False


def get_available_time_slots(
    db: Session, 
    master_id: int, 
    service_id: int, 
    target_date: date
) -> List[schemas.TimeSlot]:
    """Получить доступные временные слоты для записи"""
    # Рабочие часы салона (9:00 - 20:00)
    work_start = 9
    work_end = 20
    
    # Получаем услугу для определения длительности
    service = get_service_by_id(db, service_id)
    if not service:
        return []
    
    duration_minutes = service.duration_minutes
    
    # Получаем все записи мастера на эту дату
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())
    
    existing_appointments = db.query(models.Appointment).filter(
        models.Appointment.master_id == master_id,
        models.Appointment.appointment_datetime >= start_datetime,
        models.Appointment.appointment_datetime <= end_datetime,
        models.Appointment.status == "scheduled"
    ).all()
    
    # Собираем занятые периоды
    busy_periods = []
    for apt in existing_appointments:
        apt_service = get_service_by_id(db, apt.service_id)
        if apt_service:
            end_time = apt.appointment_datetime + timedelta(minutes=apt_service.duration_minutes)
            busy_periods.append((apt.appointment_datetime, end_time))
    
    # Генерируем доступные слоты (каждые 30 минут)
    available_slots = []
    current_time = datetime.combine(target_date, datetime.min.time().replace(hour=work_start))
    end_work_time = datetime.combine(target_date, datetime.min.time().replace(hour=work_end))
    
    while current_time + timedelta(minutes=duration_minutes) <= end_work_time:
        slot_end = current_time + timedelta(minutes=duration_minutes)
        
        # Проверяем, не пересекается ли слот с занятыми периодами
        is_available = True
        for busy_start, busy_end in busy_periods:
            if not (slot_end <= busy_start or current_time >= busy_end):
                is_available = False
                break
        
        # Проверяем, что слот не в прошлом
        if current_time <= datetime.now():
            is_available = False
        
        if is_available:
            available_slots.append(schemas.TimeSlot(
                time=current_time.strftime("%H:%M"),
                datetime=current_time
            ))
        
        current_time += timedelta(minutes=30)
    
    return available_slots


# ==================== INIT DATA ====================

def init_database(db: Session):
    """Инициализация базы данных начальными данными"""
    
    # Проверяем, есть ли уже данные
    if db.query(models.Profession).first():
        return  # Данные уже есть
    
    # Создаем профессии
    professions_data = [
        {"name": "Парикмахер"},
        {"name": "Визажист"},
        {"name": "Мастер маникюра"}
    ]
    
    professions = {}
    for p_data in professions_data:
        profession = models.Profession(**p_data)
        db.add(profession)
        db.flush()
        professions[p_data["name"]] = profession.id
    
    # Создаем услуги по профессиям
    services_data = [
        # Парикмахер (5 услуг)
        {"name": "Женская стрижка", "price": 2000, "duration_minutes": 60, "profession_id": professions["Парикмахер"]},
        {"name": "Стрижка чёлки", "price": 800, "duration_minutes": 30, "profession_id": professions["Парикмахер"]},
        {"name": "Укладка", "price": 2000, "duration_minutes": 40, "profession_id": professions["Парикмахер"]},
        {"name": "Окрашивание в один тон", "price": 5000, "duration_minutes": 120, "profession_id": professions["Парикмахер"]},
        {"name": "Тонирование волос", "price": 3500, "duration_minutes": 90, "profession_id": professions["Парикмахер"]},
        # Визажист (5 услуг)
        {"name": "Вечерний макияж", "price": 3000, "duration_minutes": 60, "profession_id": professions["Визажист"]},
        {"name": "Экспресс-макияж", "price": 1500, "duration_minutes": 30, "profession_id": professions["Визажист"]},
        {"name": "Свадебный макияж", "price": 6000, "duration_minutes": 90, "profession_id": professions["Визажист"]},
        {"name": "Коррекция бровей", "price": 400, "duration_minutes": 15, "profession_id": professions["Визажист"]},
        {"name": "Окрашивание бровей", "price": 500, "duration_minutes": 15, "profession_id": professions["Визажист"]},
        # Мастер маникюра (6 услуг)
        {"name": "Маникюр без покрытия", "price": 1200, "duration_minutes": 60, "profession_id": professions["Мастер маникюра"]},
        {"name": "Маникюр с покрытием гель-лака", "price": 1800, "duration_minutes": 90, "profession_id": professions["Мастер маникюра"]},
        {"name": "Педикюр (пальчики и стопы без покрытия)", "price": 2000, "duration_minutes": 90, "profession_id": professions["Мастер маникюра"]},
        {"name": "Педикюр (пальчики без покрытия)", "price": 1500, "duration_minutes": 60, "profession_id": professions["Мастер маникюра"]},
        {"name": "Педикюр (пальчики с гель-лаком)", "price": 1800, "duration_minutes": 90, "profession_id": professions["Мастер маникюра"]},
        {"name": "Педикюр полный с гель-лаком", "price": 2500, "duration_minutes": 120, "profession_id": professions["Мастер маникюра"]},
    ]
    
    for s_data in services_data:
        service = models.Service(**s_data)
        db.add(service)
    
    db.flush()  # Чтобы получить ID услуг
    
    # Получаем ID услуг по профессиям для назначения мастерам
    hairdresser_services = db.query(models.Service).filter(
        models.Service.profession_id == professions["Парикмахер"]
    ).all()
    
    makeup_services = db.query(models.Service).filter(
        models.Service.profession_id == professions["Визажист"]
    ).all()
    
    nail_services = db.query(models.Service).filter(
        models.Service.profession_id == professions["Мастер маникюра"]
    ).all()
    
    # Создаем 15 мастеров
    masters_data = [
        # Парикмахеры (5 человек)
        # Услуги: 0-Женская стрижка, 1-Стрижка чёлки, 2-Укладка, 3-Окрашивание, 4-Тонирование
        {
            "full_name": "Анна Петрова",
            "profession_id": professions["Парикмахер"],
            "contact_info": "+7 (999) 111-22-33",
            "services": hairdresser_services  # Все услуги
        },
        {
            "full_name": "Мария Иванова",
            "profession_id": professions["Парикмахер"],
            "contact_info": "+7 (999) 222-33-44",
            "services": [hairdresser_services[0], hairdresser_services[1], hairdresser_services[2]]  # Стрижки и укладка
        },
        {
            "full_name": "Елена Сидорова",
            "profession_id": professions["Парикмахер"],
            "contact_info": "+7 (999) 333-44-55",
            "services": [hairdresser_services[0], hairdresser_services[3], hairdresser_services[4]]  # Стрижка, окрашивание, тонирование
        },
        {
            "full_name": "Сергей Козлов",
            "profession_id": professions["Парикмахер"],
            "contact_info": "+7 (999) 444-55-66",
            "services": [hairdresser_services[0], hairdresser_services[1]]  # Только стрижки
        },
        {
            "full_name": "Дмитрий Волков",
            "profession_id": professions["Парикмахер"],
            "contact_info": "+7 (999) 555-66-77",
            "services": [hairdresser_services[0], hairdresser_services[2], hairdresser_services[3]]  # Стрижка, укладка, окрашивание
        },
        
        # Визажисты (5 человек)
        # Услуги: 0-Вечерний, 1-Экспресс, 2-Свадебный, 3-Коррекция бровей, 4-Окрашивание бровей
        {
            "full_name": "Ольга Смирнова",
            "profession_id": professions["Визажист"],
            "contact_info": "+7 (999) 666-77-88",
            "services": makeup_services  # Все услуги
        },
        {
            "full_name": "Наталья Кузнецова",
            "profession_id": professions["Визажист"],
            "contact_info": "+7 (999) 777-88-99",
            "services": [makeup_services[0], makeup_services[1], makeup_services[2]]  # Все макияжи
        },
        {
            "full_name": "Татьяна Попова",
            "profession_id": professions["Визажист"],
            "contact_info": "+7 (999) 888-99-00",
            "services": [makeup_services[0], makeup_services[2], makeup_services[3]]  # Вечерний, свадебный, брови
        },
        {
            "full_name": "Ирина Соколова",
            "profession_id": professions["Визажист"],
            "contact_info": "+7 (999) 999-00-11",
            "services": [makeup_services[1], makeup_services[3], makeup_services[4]]  # Экспресс и брови
        },
        {
            "full_name": "Алина Новикова",
            "profession_id": professions["Визажист"],
            "contact_info": "+7 (999) 100-20-30",
            "services": [makeup_services[0], makeup_services[2]]  # Вечерний и свадебный
        },
        
        # Мастера маникюра (5 человек)
        # Услуги: 0-Маникюр без покрытия, 1-Маникюр гель-лак, 2-Педикюр полный без покр,
        #         3-Педикюр пальчики без покр, 4-Педикюр пальчики с гель-лак, 5-Педикюр полный с гель-лак
        {
            "full_name": "Екатерина Морозова",
            "profession_id": professions["Мастер маникюра"],
            "contact_info": "+7 (999) 200-30-40",
            "services": nail_services  # Все услуги
        },
        {
            "full_name": "Виктория Лебедева",
            "profession_id": professions["Мастер маникюра"],
            "contact_info": "+7 (999) 300-40-50",
            "services": [nail_services[0], nail_services[1]]  # Только маникюр
        },
        {
            "full_name": "Юлия Федорова",
            "profession_id": professions["Мастер маникюра"],
            "contact_info": "+7 (999) 400-50-60",
            "services": [nail_services[0], nail_services[1], nail_services[4], nail_services[5]]  # Маникюр и педикюр с гель-лаком
        },
        {
            "full_name": "Светлана Михайлова",
            "profession_id": professions["Мастер маникюра"],
            "contact_info": "+7 (999) 500-60-70",
            "services": [nail_services[2], nail_services[3], nail_services[4], nail_services[5]]  # Только педикюр
        },
        {
            "full_name": "Кристина Белова",
            "profession_id": professions["Мастер маникюра"],
            "contact_info": "+7 (999) 600-70-80",
            "services": [nail_services[1], nail_services[5]]  # Гель-лак маникюр и полный педикюр
        },
    ]
    
    for m_data in masters_data:
        master = models.Master(
            full_name=m_data["full_name"],
            profession_id=m_data["profession_id"],
            contact_info=m_data["contact_info"]
        )
        master.services = m_data["services"]
        db.add(master)
    
    # Создаем администратора
    admin = models.User(
        phone_number="admin",
        password_hash=hash_password("admin"),
        full_name="Администратор",
        role="admin"
    )
    db.add(admin)
    
    # Создаем тестового клиента
    client = models.User(
        phone_number="+79991234567",
        password_hash=hash_password("123456"),
        full_name="Тестовый Клиент",
        role="client"
    )
    db.add(client)
    
    db.commit()
    print("База данных инициализирована начальными данными!")
    print("Добавлено 15 мастеров с услугами!")
