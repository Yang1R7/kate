import socket
import threading
import json
import sqlite3
from datetime import datetime
from hashlib import sha256


class BeautySalonServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.setup_database()

    def setup_database(self):
        """Создание и настройка базы данных"""
        self.conn = sqlite3.connect('beauty_salon.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

        # Таблица пользователей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT
            )
        ''')

        # Таблица услуг
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                duration_minutes INTEGER
            )
        ''')

        # Таблица мастеров
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS masters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                specialization TEXT,
                phone TEXT,
                email TEXT
            )
        ''')

        # Таблица связей мастеров и услуг
        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS master_services (
                    master_id INTEGER,
                    service_id INTEGER,
                    PRIMARY KEY (master_id, service_id),
                    FOREIGN KEY (master_id) REFERENCES masters (id),
                    FOREIGN KEY (service_id) REFERENCES services (id)
                )
            ''')

        # Таблица записей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                master_id INTEGER,
                service_id INTEGER,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                FOREIGN KEY (client_id) REFERENCES users (id),
                FOREIGN KEY (master_id) REFERENCES masters (id),
                FOREIGN KEY (service_id) REFERENCES services (id)
            )
        ''')

        self.conn.commit()

        # Добавляем тестовые данные, если таблицы пусты
        self.add_sample_data()

    def add_sample_data(self):
        """Добавление тестовых данных"""
        # Проверяем, есть ли уже пользователи
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] == 0:
            # Добавляем администратора
            admin_pass = sha256("123".encode()).hexdigest()
            self.cursor.execute(
                "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                ("123", admin_pass, "123", "Администратор")
            )

            # Добавляем тестовые услуги
            services = [
                ("Стрижка женская", "Модная женская стрижка", 1500.00, 60),
                ("Стрижка мужская", "Классическая мужская стрижка", 800.00, 30),
                ("Окрашивание волос", "Окрашивание в один тон", 3000.00, 120),
                ("Маникюр", "Аппаратный маникюр", 1200.00, 90),
                ("Педикюр", "Комбинированный педикюр", 1800.00, 120)
            ]

            self.cursor.executemany(
                "INSERT INTO services (name, description, price, duration_minutes) VALUES (?, ?, ?, ?)",
                services
            )

            # Добавляем мастеров
            masters = [
                ("Анна Петрова", "Парикмахер", "+79101234567", "anna@salon.ru"),
                ("Мария Иванова", "Мастер маникюра", "+79107654321", "maria@salon.ru"),
                ("Сергей Смирнов", "Барбер", "+79051234567", "sergey@salon.ru")
            ]

            self.cursor.executemany(
                "INSERT INTO masters (full_name, specialization, phone, email) VALUES (?, ?, ?, ?)",
                masters
            )

            # Добавляем связи мастеров и услуг
            master_services = [
                (1, 1), (1, 2), (1, 3),  # Анна - все парикмахерские услуги
                (2, 4), (2, 5),  # Мария - маникюр и педикюр
                (3, 1), (3, 2)  # Сергей - мужские стрижки
            ]

            self.cursor.executemany(
                "INSERT INTO master_services (master_id, service_id) VALUES (?, ?)",
                master_services
            )

            self.conn.commit()

    def hash_password(self, password):
        """Хеширование пароля"""
        return sha256(password.encode()).hexdigest()

    def handle_client(self, client_socket, address):
        """Обработка клиентских подключений"""
        print(f"[+] Новое подключение от {address}")

        try:
            while True:
                # Получаем данные от клиента
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break

                try:
                    request = json.loads(data)
                    response = self.process_request(request)
                    client_socket.send(json.dumps(response).encode('utf-8'))
                except json.JSONDecodeError:
                    response = {"status": "error", "message": "Неверный формат данных"}
                    client_socket.send(json.dumps(response).encode('utf-8'))

        except ConnectionResetError:
            print(f"[-] Соединение с {address} разорвано")
        finally:
            client_socket.close()
            if address in self.clients:
                del self.clients[address]

    def get_master_services(self, request):
        """Получение услуг конкретного мастера"""
        master_id = request.get('master_id')

        self.cursor.execute('''
                SELECT DISTINCT s.id, s.name, s.description, s.price, s.duration_minutes
                FROM services s
                JOIN master_services ms ON s.id = ms.service_id
                WHERE ms.master_id = ?
            ''', (master_id,))

        services = self.cursor.fetchall()

        result = []
        for service in services:
            result.append({
                "id": service[0],
                "name": service[1],
                "description": service[2],
                "price": service[3],
                "duration": service[4]
            })

        return {"status": "success", "services": result}

    def get_service_masters(self, request):
        """Получение мастеров для конкретной услуги"""
        service_id = request.get('service_id')

        self.cursor.execute('''
            SELECT m.id, m.full_name, m.specialization, m.phone, m.email
            FROM masters m
            JOIN master_services ms ON m.id = ms.master_id
            WHERE ms.service_id = ?
        ''', (service_id,))

        masters = self.cursor.fetchall()

        result = []
        for master in masters:
            result.append({
                "id": master[0],
                "full_name": master[1],
                "specialization": master[2],
                "phone": master[3],
                "email": master[4]
            })

        return {"status": "success", "masters": result}

    def process_request(self, request):
        """Обработка запросов от клиента"""
        action = request.get('action')

        if action == 'login':
            return self.handle_login(request)
        elif action == 'register':
            return self.handle_register(request)
        elif action == 'get_services':
            return self.get_services()
        elif action == 'get_masters':
            return self.get_masters()
        elif action == 'get_master_services':  # Новый метод
            return self.get_master_services(request)
        elif action == 'get_service_masters':  # Новый метод
            return self.get_service_masters(request)
        elif action == 'create_appointment':
            return self.create_appointment(request)
        elif action == 'get_appointments':
            return self.get_appointments(request)
        elif action == 'cancel_appointment':
            return self.cancel_appointment(request)
        elif action == 'get_available_times':
            return self.get_available_times(request)
        else:
            return {"status": "error", "message": "Неизвестное действие"}

    def handle_login(self, request):
        """Авторизация пользователя"""
        username = request.get('username')
        password = request.get('password')

        hashed_password = self.hash_password(password)

        self.cursor.execute(
            "SELECT id, username, role, full_name FROM users WHERE username = ? AND password = ?",
            (username, hashed_password)
        )
        user = self.cursor.fetchone()

        if user:
            return {
                "status": "success",
                "message": "Вход выполнен успешно",
                "user": {
                    "id": user[0],
                    "username": user[1],
                    "role": user[2],
                    "full_name": user[3]
                }
            }
        else:
            return {"status": "error", "message": "Неверные учетные данные"}

    def handle_register(self, request):
        """Регистрация нового пользователя"""
        username = request.get('username')
        password = request.get('password')
        full_name = request.get('full_name', '')

        try:
            hashed_password = self.hash_password(password)
            self.cursor.execute(
                "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                (username, hashed_password, "client", full_name)
            )
            self.conn.commit()
            return {"status": "success", "message": "Регистрация успешна"}
        except sqlite3.IntegrityError:
            return {"status": "error", "message": "Пользователь уже существует"}

    def get_services(self):
        """Получение списка услуг"""
        self.cursor.execute("SELECT id, name, description, price, duration_minutes FROM services")
        services = self.cursor.fetchall()

        result = []
        for service in services:
            result.append({
                "id": service[0],
                "name": service[1],
                "description": service[2],
                "price": service[3],
                "duration": service[4]
            })

        return {"status": "success", "services": result}

    def get_masters(self):
        """Получение списка мастеров"""
        self.cursor.execute("SELECT id, full_name, specialization, phone, email FROM masters")
        masters = self.cursor.fetchall()

        result = []
        for master in masters:
            result.append({
                "id": master[0],
                "full_name": master[1],
                "specialization": master[2],
                "phone": master[3],
                "email": master[4]
            })

        return {"status": "success", "masters": result}

    def get_available_times(self, request):
        """Получение доступного времени для записи"""
        master_id = request.get('master_id')
        date = request.get('date')

        # Стандартные рабочие часы
        work_hours = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00",
                      "15:00", "16:00", "17:00", "18:00", "19:00"]

        # Получаем занятое время
        self.cursor.execute(
            "SELECT appointment_time FROM appointments WHERE master_id = ? AND appointment_date = ? AND status != 'cancelled'",
            (master_id, date)
        )
        booked_times = [time[0] for time in self.cursor.fetchall()]

        # Фильтруем доступное время
        available_times = [time for time in work_hours if time not in booked_times]

        return {"status": "success", "available_times": available_times}

    def create_appointment(self, request):
        """Создание новой записи"""
        client_id = request.get('client_id')
        master_id = request.get('master_id')
        service_id = request.get('service_id')
        date = request.get('date')
        time = request.get('time')
        notes = request.get('notes', '')

        try:
            self.cursor.execute(
                """INSERT INTO appointments 
                (client_id, master_id, service_id, appointment_date, appointment_time, notes) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (client_id, master_id, service_id, date, time, notes)
            )
            self.conn.commit()
            return {"status": "success", "message": "Запись создана успешно", "appointment_id": self.cursor.lastrowid}
        except Exception as e:
            return {"status": "error", "message": f"Ошибка при создании записи: {str(e)}"}

    def get_appointments(self, request):
        """Получение записей пользователя"""
        client_id = request.get('client_id')

        self.cursor.execute('''
            SELECT a.id, a.appointment_date, a.appointment_time, a.status, a.notes,
                   s.name as service_name, s.price,
                   m.full_name as master_name
            FROM appointments a
            JOIN services s ON a.service_id = s.id
            JOIN masters m ON a.master_id = m.id
            WHERE a.client_id = ?
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        ''', (client_id,))

        appointments = self.cursor.fetchall()

        result = []
        for app in appointments:
            result.append({
                "id": app[0],
                "date": app[1],
                "time": app[2],
                "status": app[3],
                "notes": app[4],
                "service_name": app[5],
                "price": app[6],
                "master_name": app[7]
            })

        return {"status": "success", "appointments": result}

    def cancel_appointment(self, request):
        """Отмена записи"""
        appointment_id = request.get('appointment_id')

        self.cursor.execute(
            "UPDATE appointments SET status = 'cancelled' WHERE id = ?",
            (appointment_id,)
        )
        self.conn.commit()

        if self.cursor.rowcount > 0:
            return {"status": "success", "message": "Запись отменена"}
        else:
            return {"status": "error", "message": "Запись не найдена"}

    def start(self):
        """Запуск сервера"""
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"[*] Сервер запущен на {self.host}:{self.port}")

        try:
            while True:
                client_socket, address = self.server.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.start()
                print(f"[*] Активных подключений: {threading.active_count() - 1}")
        except KeyboardInterrupt:
            print("\n[*] Остановка сервера...")
        finally:
            self.server.close()
            self.conn.close()


if __name__ == "__main__":
    server = BeautySalonServer()
    server.start()