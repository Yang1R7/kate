"""
REST API клиент для BeautyPro
"""
import requests
from typing import Optional, List, Dict, Any
from datetime import date, datetime


class BeautyProAPI:
    """Клиент для взаимодействия с BeautyPro API"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Базовый метод для HTTP запросов"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, params=params)
            elif method == "POST":
                response = self.session.post(url, json=data, params=params)
            elif method == "PUT":
                response = self.session.put(url, json=data)
            elif method == "DELETE":
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Неподдерживаемый метод: {method}")
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            elif response.status_code == 422:
                return {"success": False, "error": "Ошибка валидации данных"}
            else:
                error_detail = response.json().get("detail", "Неизвестная ошибка")
                return {"success": False, "error": error_detail}
                
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Не удалось подключиться к серверу"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== AUTH ====================
    
    def register(self, phone_number: str, password: str, full_name: str) -> Dict:
        """Регистрация нового клиента"""
        return self._request("POST", "/api/auth/register", {
            "phone_number": phone_number,
            "password": password,
            "full_name": full_name
        })
    
    def login(self, phone_number: str, password: str) -> Dict:
        """Авторизация пользователя"""
        return self._request("POST", "/api/auth/login", {
            "phone_number": phone_number,
            "password": password
        })
    
    # ==================== PROFESSIONS ====================
    
    def get_professions(self) -> Dict:
        """Получить список профессий"""
        return self._request("GET", "/api/professions")
    
    # ==================== SERVICES ====================
    
    def get_services(self, profession_id: Optional[int] = None) -> Dict:
        """Получить список услуг"""
        params = {}
        if profession_id:
            params["profession_id"] = profession_id
        return self._request("GET", "/api/services", params=params)
    
    def get_service(self, service_id: int) -> Dict:
        """Получить услугу по ID"""
        return self._request("GET", f"/api/services/{service_id}")
    
    def get_service_masters(self, service_id: int) -> Dict:
        """Получить мастеров для услуги"""
        return self._request("GET", f"/api/services/{service_id}/masters")
    
    def create_service(
        self,
        name: str,
        price: float,
        duration_minutes: int,
        profession_id: int
    ) -> Dict:
        """Создать новую услугу"""
        data = {
            "name": name,
            "price": price,
            "duration_minutes": duration_minutes,
            "profession_id": profession_id
        }
        return self._request("POST", "/api/services", data)
    
    def update_service(
        self,
        service_id: int,
        name: str = None,
        price: float = None,
        duration_minutes: int = None,
        profession_id: int = None
    ) -> Dict:
        """Обновить услугу"""
        data = {}
        if name is not None:
            data["name"] = name
        if price is not None:
            data["price"] = price
        if duration_minutes is not None:
            data["duration_minutes"] = duration_minutes
        if profession_id is not None:
            data["profession_id"] = profession_id
        return self._request("PUT", f"/api/services/{service_id}", data)
    
    def delete_service(self, service_id: int) -> Dict:
        """Удалить услугу"""
        return self._request("DELETE", f"/api/services/{service_id}")
    
    # ==================== MASTERS ====================
    
    def get_masters(self, active_only: bool = True) -> Dict:
        """Получить список мастеров"""
        return self._request("GET", "/api/masters", params={"active_only": active_only})
    
    def get_master(self, master_id: int) -> Dict:
        """Получить мастера по ID"""
        return self._request("GET", f"/api/masters/{master_id}")
    
    def get_master_services(self, master_id: int) -> Dict:
        """Получить услуги мастера"""
        return self._request("GET", f"/api/masters/{master_id}/services")
    
    def create_master(
        self, 
        full_name: str, 
        profession_id: int, 
        contact_info: str = "",
        service_ids: List[int] = None
    ) -> Dict:
        """Создать нового мастера"""
        data = {
            "full_name": full_name,
            "profession_id": profession_id,
            "contact_info": contact_info,
            "service_ids": service_ids or []
        }
        return self._request("POST", "/api/masters", data)
    
    def update_master(
        self, 
        master_id: int, 
        full_name: str = None, 
        profession_id: int = None,
        contact_info: str = None,
        service_ids: List[int] = None
    ) -> Dict:
        """Обновить данные мастера"""
        data = {}
        if full_name is not None:
            data["full_name"] = full_name
        if profession_id is not None:
            data["profession_id"] = profession_id
        if contact_info is not None:
            data["contact_info"] = contact_info
        if service_ids is not None:
            data["service_ids"] = service_ids
        return self._request("PUT", f"/api/masters/{master_id}", data)
    
    def delete_master(self, master_id: int) -> Dict:
        """Удалить мастера"""
        return self._request("DELETE", f"/api/masters/{master_id}")
    
    def assign_services_to_master(self, master_id: int, service_ids: List[int]) -> Dict:
        """Назначить услуги мастеру"""
        return self._request("POST", f"/api/masters/{master_id}/services", service_ids)
    
    # ==================== APPOINTMENTS ====================
    
    def get_appointments(
        self, 
        client_id: int, 
        status: str = None, 
        upcoming_only: bool = False
    ) -> Dict:
        """Получить записи клиента"""
        params = {"client_id": client_id, "upcoming_only": upcoming_only}
        if status:
            params["status"] = status
        return self._request("GET", "/api/appointments", params=params)
    
    def create_appointment(
        self,
        client_id: int,
        master_id: int,
        service_id: int,
        appointment_datetime: datetime
    ) -> Dict:
        """Создать новую запись"""
        data = {
            "master_id": master_id,
            "service_id": service_id,
            "appointment_datetime": appointment_datetime.isoformat()
        }
        return self._request("POST", "/api/appointments", data, params={"client_id": client_id})
    
    def cancel_appointment(self, appointment_id: int, client_id: int) -> Dict:
        """Отменить запись"""
        return self._request(
            "DELETE", 
            f"/api/appointments/{appointment_id}",
            params={"client_id": client_id}
        )
    
    def get_available_slots(
        self, 
        master_id: int, 
        service_id: int, 
        target_date: date
    ) -> Dict:
        """Получить доступные временные слоты"""
        params = {
            "master_id": master_id,
            "service_id": service_id,
            "target_date": target_date.isoformat()
        }
        return self._request("GET", "/api/available-slots", params=params)
    
    # ==================== HEALTH ====================
    
    def health_check(self) -> Dict:
        """Проверка работоспособности сервера"""
        return self._request("GET", "/api/health")
