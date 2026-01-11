"""
BeautyPro REST API Server
FastAPI приложение для салона красоты
"""
from typing import Annotated, List, Optional
from datetime import date
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from server.database import engine, get_db, Base
from server import crud, schemas, models

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BeautyPro API",
    description="REST API для салона красоты BeautyPro",
    version="1.0.0"
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency для получения сессии БД
SessionDep = Annotated[Session, Depends(get_db)]


# ==================== STARTUP EVENT ====================

@app.on_event("startup")
def startup_event():
    """Инициализация при запуске"""
    db = next(get_db())
    crud.init_database(db)
    db.close()


# ==================== AUTH ENDPOINTS ====================

@app.post("/api/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: SessionDep):
    """Регистрация нового клиента"""
    # Проверяем, существует ли пользователь
    existing = crud.get_user_by_phone(db, user.phone_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким номером телефона уже существует"
        )
    
    db_user = crud.create_user(db, user)
    return db_user


@app.post("/api/auth/login", response_model=schemas.UserResponse)
def login(credentials: schemas.UserLogin, db: SessionDep):
    """Авторизация пользователя"""
    user = crud.authenticate_user(db, credentials.phone_number, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный номер телефона или пароль"
        )
    return user


# ==================== PROFESSION ENDPOINTS ====================

@app.get("/api/professions", response_model=List[schemas.ProfessionResponse])
def get_professions(db: SessionDep):
    """Получить список всех профессий"""
    return crud.get_professions(db)


# ==================== SERVICE ENDPOINTS ====================

@app.get("/api/services", response_model=List[schemas.ServiceResponse])
def get_services(db: SessionDep, profession_id: Optional[int] = None):
    """Получить список услуг (можно фильтровать по профессии)"""
    if profession_id:
        return crud.get_services_by_profession(db, profession_id)
    return crud.get_services(db)


@app.get("/api/services/{service_id}", response_model=schemas.ServiceResponse)
def get_service(service_id: int, db: SessionDep):
    """Получить услугу по ID"""
    service = crud.get_service_by_id(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    return service


@app.get("/api/services/{service_id}/masters", response_model=List[schemas.MasterResponse])
def get_service_masters(service_id: int, db: SessionDep):
    """Получить мастеров, оказывающих услугу"""
    masters = crud.get_masters_by_service(db, service_id)
    return masters


@app.post("/api/services", response_model=schemas.ServiceResponse)
def create_service(service: schemas.ServiceCreate, db: SessionDep):
    """Создать новую услугу (только для админа)"""
    return crud.create_service(db, service)


@app.put("/api/services/{service_id}", response_model=schemas.ServiceResponse)
def update_service(service_id: int, service: schemas.ServiceUpdate, db: SessionDep):
    """Обновить услугу (только для админа)"""
    db_service = crud.update_service(db, service_id, service)
    if not db_service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    return db_service


@app.delete("/api/services/{service_id}", response_model=schemas.MessageResponse)
def delete_service(service_id: int, db: SessionDep):
    """Удалить услугу (только для админа)"""
    success = crud.delete_service(db, service_id)
    if not success:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    return schemas.MessageResponse(message="Услуга успешно удалена")


# ==================== MASTER ENDPOINTS ====================

@app.get("/api/masters", response_model=List[schemas.MasterResponse])
def get_masters(db: SessionDep, active_only: bool = True):
    """Получить список всех мастеров"""
    return crud.get_masters(db, active_only)


@app.get("/api/masters/{master_id}", response_model=schemas.MasterResponse)
def get_master(master_id: int, db: SessionDep):
    """Получить мастера по ID"""
    master = crud.get_master_by_id(db, master_id)
    if not master:
        raise HTTPException(status_code=404, detail="Мастер не найден")
    return master


@app.get("/api/masters/{master_id}/services", response_model=List[schemas.ServiceBrief])
def get_master_services(master_id: int, db: SessionDep):
    """Получить услуги мастера"""
    master = crud.get_master_by_id(db, master_id)
    if not master:
        raise HTTPException(status_code=404, detail="Мастер не найден")
    return master.services


@app.post("/api/masters", response_model=schemas.MasterResponse)
def create_master(master: schemas.MasterCreate, db: SessionDep):
    """Создать нового мастера (только для админа)"""
    return crud.create_master(db, master)


@app.put("/api/masters/{master_id}", response_model=schemas.MasterResponse)
def update_master(master_id: int, master: schemas.MasterUpdate, db: SessionDep):
    """Обновить данные мастера (только для админа)"""
    db_master = crud.update_master(db, master_id, master)
    if not db_master:
        raise HTTPException(status_code=404, detail="Мастер не найден")
    return db_master


@app.delete("/api/masters/{master_id}", response_model=schemas.MessageResponse)
def delete_master(master_id: int, db: SessionDep):
    """Удалить мастера (только для админа)"""
    success = crud.delete_master(db, master_id)
    if not success:
        raise HTTPException(status_code=404, detail="Мастер не найден")
    return schemas.MessageResponse(message="Мастер успешно удален")


@app.post("/api/masters/{master_id}/services", response_model=schemas.MasterResponse)
def assign_services(master_id: int, service_ids: List[int], db: SessionDep):
    """Назначить услуги мастеру (только для админа)"""
    master = crud.assign_services_to_master(db, master_id, service_ids)
    if not master:
        raise HTTPException(status_code=404, detail="Мастер не найден")
    return master


# ==================== APPOINTMENT ENDPOINTS ====================

@app.get("/api/appointments", response_model=List[schemas.AppointmentResponse])
def get_appointments(
    client_id: int,
    db: SessionDep,
    status: Optional[str] = None,
    upcoming_only: bool = False
):
    """Получить записи клиента"""
    return crud.get_appointments_by_client(db, client_id, status, upcoming_only)


@app.post("/api/appointments", response_model=schemas.AppointmentResponse)
def create_appointment(
    client_id: int,
    appointment: schemas.AppointmentCreate,
    db: SessionDep
):
    """Создать новую запись"""
    # Проверяем, что клиент существует
    client = crud.get_user_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    
    # Проверяем, что мастер существует и активен
    master = crud.get_master_by_id(db, appointment.master_id)
    if not master or not master.is_active:
        raise HTTPException(status_code=404, detail="Мастер не найден или неактивен")
    
    # Проверяем, что услуга существует
    service = crud.get_service_by_id(db, appointment.service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    
    # Проверяем, что мастер оказывает эту услугу
    if service not in master.services:
        raise HTTPException(
            status_code=400, 
            detail="Выбранный мастер не оказывает данную услугу"
        )
    
    return crud.create_appointment(db, client_id, appointment)


@app.delete("/api/appointments/{appointment_id}", response_model=schemas.MessageResponse)
def cancel_appointment(appointment_id: int, client_id: int, db: SessionDep):
    """Отменить запись"""
    success = crud.cancel_appointment(db, appointment_id, client_id)
    if not success:
        raise HTTPException(
            status_code=404, 
            detail="Запись не найдена или уже отменена"
        )
    return schemas.MessageResponse(message="Запись успешно отменена")


@app.get("/api/available-slots", response_model=schemas.AvailableSlotsResponse)
def get_available_slots(
    master_id: int,
    service_id: int,
    target_date: date,
    db: SessionDep
):
    """Получить доступные временные слоты"""
    slots = crud.get_available_time_slots(db, master_id, service_id, target_date)
    return schemas.AvailableSlotsResponse(
        date=target_date.isoformat(),
        slots=slots
    )


# ==================== HEALTH CHECK ====================

@app.get("/api/health")
def health_check():
    """Проверка работоспособности сервера"""
    return {"status": "ok", "message": "BeautyPro API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
