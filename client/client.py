# client.py
import socket
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
from tkinter import font as tkfont


class BeautySalonClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Салон красоты - Клиент")
        self.root.geometry("1000x750")  # Увеличиваем размер окна

        self.current_user = None
        self.socket = None
        self.connect_to_server()

        self.setup_ui()

    def connect_to_server(self):
        """Подключение к серверу"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(('127.0.0.1', 5555))
            print("[*] Подключено к серверу")
        except ConnectionRefusedError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу")
            self.root.quit()

    def send_request(self, request):
        """Отправка запроса на сервер"""
        try:
            self.socket.send(json.dumps(request).encode('utf-8'))
            response = self.socket.recv(4096).decode('utf-8')
            return json.loads(response)
        except Exception as e:
            print(f"Ошибка при отправке запроса: {e}")
            return {"status": "error", "message": "Ошибка соединения"}

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Главный фрейм
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настраиваем расширение колонок
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

        # Фрейм авторизации
        self.login_frame = ttk.LabelFrame(self.main_frame, text="Авторизация", padding="10")
        self.login_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(self.login_frame, text="Логин:").grid(row=0, column=0, sticky=tk.W)
        self.login_entry = ttk.Entry(self.login_frame, width=20)
        self.login_entry.grid(row=0, column=1, padx=5)

        ttk.Label(self.login_frame, text="Пароль:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.password_entry = ttk.Entry(self.login_frame, width=20, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=(5, 0))

        self.login_button = ttk.Button(self.login_frame, text="Войти", command=self.login)
        self.login_button.grid(row=0, column=2, rowspan=2, padx=10)

        ttk.Label(self.login_frame, text="Нет аккаунта?").grid(row=2, column=0, pady=(10, 0))
        self.register_button = ttk.Button(self.login_frame, text="Зарегистрироваться",
                                          command=self.show_register_dialog)
        self.register_button.grid(row=2, column=1, columnspan=2, pady=(10, 0))

        # Основные вкладки (появятся после входа)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        # Скрываем до входа
        self.notebook.grid_remove()

    def show_register_dialog(self):
        """Диалог регистрации"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Регистрация")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Регистрация нового пользователя",
                  font=("Arial", 12, "bold")).pack(pady=(0, 20))

        ttk.Label(frame, text="Имя пользователя:").pack(anchor=tk.W)
        username_entry = ttk.Entry(frame, width=30)
        username_entry.pack(pady=(0, 10))

        ttk.Label(frame, text="Пароль:").pack(anchor=tk.W)
        password_entry = ttk.Entry(frame, width=30, show="*")
        password_entry.pack(pady=(0, 10))

        ttk.Label(frame, text="ФИО:").pack(anchor=tk.W)
        fullname_entry = ttk.Entry(frame, width=30)
        fullname_entry.pack(pady=(0, 20))

        def register():
            username = username_entry.get()
            password = password_entry.get()
            fullname = fullname_entry.get()

            if not username or not password:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            request = {
                "action": "register",
                "username": username,
                "password": password,
                "full_name": fullname
            }

            response = self.send_request(request)

            if response["status"] == "success":
                messagebox.showinfo("Успех", response["message"])
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", response["message"])

        ttk.Button(frame, text="Зарегистрироваться", command=register).pack()

    def login(self):
        """Авторизация пользователя"""
        username = self.login_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Предупреждение", "Введите логин и пароль")
            return

        request = {
            "action": "login",
            "username": username,
            "password": password
        }

        response = self.send_request(request)

        if response["status"] == "success":
            self.current_user = response["user"]
            messagebox.showinfo("Успех", f"Добро пожаловать, {self.current_user['full_name']}!")
            self.show_main_interface()
        else:
            messagebox.showerror("Ошибка", response["message"])

    def show_main_interface(self):
        """Показать основной интерфейс после входа"""
        self.login_frame.grid_remove()
        self.notebook.grid()

        # Создаем вкладки
        self.create_services_tab()
        self.create_appointments_tab()
        self.create_new_appointment_tab()  # Новая версия с выбором пути

        # Загружаем данные
        self.load_services()
        self.load_appointments()

    def create_services_tab(self):
        """Вкладка с услугами"""
        self.services_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.services_tab, text="Услуги")

        # Дерево для отображения услуг
        columns = ("name", "description", "price", "duration")
        self.services_tree = ttk.Treeview(self.services_tab, columns=columns, show="headings")

        self.services_tree.heading("name", text="Услуга")
        self.services_tree.heading("description", text="Описание")
        self.services_tree.heading("price", text="Цена (руб)")
        self.services_tree.heading("duration", text="Длительность (мин)")

        self.services_tree.column("name", width=200)
        self.services_tree.column("description", width=300)
        self.services_tree.column("price", width=100)
        self.services_tree.column("duration", width=150)

        scrollbar = ttk.Scrollbar(self.services_tab, orient=tk.VERTICAL,
                                  command=self.services_tree.yview)
        self.services_tree.configure(yscrollcommand=scrollbar.set)

        self.services_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_appointments_tab(self):
        """Вкладка с записями"""
        self.appointments_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.appointments_tab, text="Мои записи")

        # Дерево для отображения записей
        columns = ("date", "time", "service", "master", "price", "status")
        self.appointments_tree = ttk.Treeview(self.appointments_tab, columns=columns, show="headings")

        self.appointments_tree.heading("date", text="Дата")
        self.appointments_tree.heading("time", text="Время")
        self.appointments_tree.heading("service", text="Услуга")
        self.appointments_tree.heading("master", text="Мастер")
        self.appointments_tree.heading("price", text="Цена")
        self.appointments_tree.heading("status", text="Статус")

        self.appointments_tree.column("date", width=100)
        self.appointments_tree.column("time", width=80)
        self.appointments_tree.column("service", width=200)
        self.appointments_tree.column("master", width=150)
        self.appointments_tree.column("price", width=100)
        self.appointments_tree.column("status", width=100)

        scrollbar = ttk.Scrollbar(self.appointments_tab, orient=tk.VERTICAL,
                                  command=self.appointments_tree.yview)
        self.appointments_tree.configure(yscrollcommand=scrollbar.set)

        # Кнопки управления
        button_frame = ttk.Frame(self.appointments_tab)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(button_frame, text="Обновить",
                   command=self.load_appointments).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отменить запись",
                   command=self.cancel_selected_appointment).pack(side=tk.LEFT, padx=5)

        self.appointments_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_new_appointment_tab(self):
        """Вкладка для создания новой записи с выбором пути"""
        self.new_appointment_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.new_appointment_tab, text="Новая запись")

        # Основной контейнер (БЕЗ Canvas и скролла!)
        self.new_appointment_container = ttk.Frame(self.new_appointment_tab)
        self.new_appointment_container.pack(fill=tk.BOTH, expand=True)

        # Текущий выбранный мастер и услуга
        self.selected_master = None
        self.selected_service = None
        self.selected_master_id = None
        self.selected_service_id = None

        # Создаем все фреймы
        self.create_choice_frame()
        self.create_master_selection_frame()
        self.create_master_services_frame()
        self.create_service_selection_frame()
        self.create_service_masters_frame()
        self.create_appointment_details_frame()

        # Показываем только choice_frame изначально
        self.choice_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def create_choice_frame(self):
        """Создание фрейма выбора пути (БЕЗ скролла)"""
        self.choice_frame = ttk.LabelFrame(
            self.new_appointment_container,
            text="Выберите способ записи",
            padding="20"
        )

        # Заголовок
        title_label = ttk.Label(
            self.choice_frame,
            text="Выберите способ записи",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 30))

        # Фрейм для двух блоков
        blocks_frame = ttk.Frame(self.choice_frame)
        blocks_frame.pack(fill=tk.BOTH, expand=True)

        # Блок "Мастера"
        master_block = ttk.LabelFrame(
            blocks_frame,
            text="Запись через мастера",
            padding="20"
        )
        master_block.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10), pady=10)
        blocks_frame.columnconfigure(0, weight=1)
        blocks_frame.rowconfigure(0, weight=1)

        # Иконка для мастера
        master_icon = tk.Label(
            master_block,
            text="👨‍🎨",
            font=("Arial", 48)
        )
        master_icon.pack(pady=(10, 20))

        # Описание
        master_desc = tk.Label(
            master_block,
            text="Выберите сначала мастера, а затем услуги,\nкоторые он оказывает",
            font=("Arial", 10),
            justify="center"
        )
        master_desc.pack(pady=(0, 20))

        # Кнопка выбора мастера
        self.choose_master_btn = ttk.Button(
            master_block,
            text="Выбрать мастера",
            command=self.choose_master_path,
            width=20
        )
        self.choose_master_btn.pack(pady=(0, 10))

        # Блок "Услуги"
        service_block = ttk.LabelFrame(
            blocks_frame,
            text="Запись через услугу",
            padding="20"
        )
        service_block.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0), pady=10)
        blocks_frame.columnconfigure(1, weight=1)

        # Иконка для услуги
        service_icon = tk.Label(
            service_block,
            text="💇",
            font=("Arial", 48)
        )
        service_icon.pack(pady=(10, 20))

        # Описание
        service_desc = tk.Label(
            service_block,
            text="Выберите сначала услугу, а затем мастера,\nкоторый её оказывает",
            font=("Arial", 10),
            justify="center"
        )
        service_desc.pack(pady=(0, 20))

        # Кнопка выбора услуги
        self.choose_service_btn = ttk.Button(
            service_block,
            text="Выбрать услугу",
            command=self.choose_service_path,
            width=20
        )
        self.choose_service_btn.pack(pady=(0, 10))

    def create_master_selection_frame(self):
        """Создание фрейма выбора мастера со скроллом"""
        self.master_selection_frame = ttk.LabelFrame(
            self.new_appointment_container,
            text="Выбор мастера",
            padding="10"
        )

        # Canvas и скролл ТОЛЬКО для этого фрейма
        self.master_selection_canvas = tk.Canvas(self.master_selection_frame)
        self.master_selection_scrollbar = ttk.Scrollbar(self.master_selection_frame, orient="vertical",
                                                        command=self.master_selection_canvas.yview)

        # Фрейм для контента внутри Canvas
        self.master_selection_content = ttk.Frame(self.master_selection_canvas)

        # Привязка размера
        self.master_selection_content.bind(
            "<Configure>",
            lambda e: self.master_selection_canvas.configure(scrollregion=self.master_selection_canvas.bbox("all"))
        )

        self.master_selection_canvas.create_window((0, 0), window=self.master_selection_content, anchor="nw")
        self.master_selection_canvas.configure(yscrollcommand=self.master_selection_scrollbar.set)

        # Упаковка
        self.master_selection_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.master_selection_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопка "Назад" - добавляем ВНЕ скроллируемой области
        self.master_selection_btn_frame = ttk.Frame(self.master_selection_frame)
        self.master_selection_btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            self.master_selection_btn_frame,
            text="← Назад",
            command=self.back_to_choice
        ).pack()

    def create_master_services_frame(self):
        """Создание фрейма услуг мастера со скроллом"""
        self.master_services_frame = ttk.LabelFrame(
            self.new_appointment_container,
            text="Выбор услуг у мастера",
            padding="10"
        )

        # Canvas и скролл
        self.master_services_canvas = tk.Canvas(self.master_services_frame)
        self.master_services_scrollbar = ttk.Scrollbar(self.master_services_frame, orient="vertical",
                                                       command=self.master_services_canvas.yview)

        # Фрейм для контента
        self.master_services_content = ttk.Frame(self.master_services_canvas)

        # Привязка размера
        self.master_services_content.bind(
            "<Configure>",
            lambda e: self.master_services_canvas.configure(scrollregion=self.master_services_canvas.bbox("all"))
        )

        self.master_services_canvas.create_window((0, 0), window=self.master_services_content, anchor="nw")
        self.master_services_canvas.configure(yscrollcommand=self.master_services_scrollbar.set)

        # Упаковка
        self.master_services_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.master_services_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки управления
        self.master_services_btn_frame = ttk.Frame(self.master_services_frame)
        self.master_services_btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            self.master_services_btn_frame,
            text="← Назад к выбору мастера",
            command=self.back_to_master_selection
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self.master_services_btn_frame,
            text="↶ Начало",
            command=self.back_to_choice
        ).pack(side=tk.LEFT, padx=5)

    def create_service_selection_frame(self):
        """Создание фрейма выбора услуги со скроллом"""
        self.service_selection_frame = ttk.LabelFrame(
            self.new_appointment_container,
            text="Выбор услуги",
            padding="10"
        )

        # Canvas и скролл
        self.service_selection_canvas = tk.Canvas(self.service_selection_frame)
        self.service_selection_scrollbar = ttk.Scrollbar(self.service_selection_frame, orient="vertical",
                                                         command=self.service_selection_canvas.yview)

        # Фрейм для контента
        self.service_selection_content = ttk.Frame(self.service_selection_canvas)

        # Привязка размера
        self.service_selection_content.bind(
            "<Configure>",
            lambda e: self.service_selection_canvas.configure(scrollregion=self.service_selection_canvas.bbox("all"))
        )

        self.service_selection_canvas.create_window((0, 0), window=self.service_selection_content, anchor="nw")
        self.service_selection_canvas.configure(yscrollcommand=self.service_selection_scrollbar.set)

        # Упаковка
        self.service_selection_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.service_selection_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопка "Назад"
        self.service_selection_btn_frame = ttk.Frame(self.service_selection_frame)
        self.service_selection_btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            self.service_selection_btn_frame,
            text="← Назад",
            command=self.back_to_choice
        ).pack()

    def create_service_masters_frame(self):
        """Создание фрейма мастеров для услуги со скроллом"""
        self.service_masters_frame = ttk.LabelFrame(
            self.new_appointment_container,
            text="Выбор мастера для услуги",
            padding="10"
        )

        # Canvas и скролл
        self.service_masters_canvas = tk.Canvas(self.service_masters_frame)
        self.service_masters_scrollbar = ttk.Scrollbar(self.service_masters_frame, orient="vertical",
                                                       command=self.service_masters_canvas.yview)

        # Фрейм для контента
        self.service_masters_content = ttk.Frame(self.service_masters_canvas)

        # Привязка размера
        self.service_masters_content.bind(
            "<Configure>",
            lambda e: self.service_masters_canvas.configure(scrollregion=self.service_masters_canvas.bbox("all"))
        )

        self.service_masters_canvas.create_window((0, 0), window=self.service_masters_content, anchor="nw")
        self.service_masters_canvas.configure(yscrollcommand=self.service_masters_scrollbar.set)

        # Упаковка
        self.service_masters_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.service_masters_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки управления
        self.service_masters_btn_frame = ttk.Frame(self.service_masters_frame)
        self.service_masters_btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            self.service_masters_btn_frame,
            text="← Назад к выбору услуги",
            command=self.back_to_service_selection
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self.service_masters_btn_frame,
            text="↶ Начало",
            command=self.back_to_choice
        ).pack(side=tk.LEFT, padx=5)

    def create_appointment_details_frame(self):
        """Создание фрейма оформления записи (БЕЗ скролла)"""
        self.appointment_details_frame = ttk.LabelFrame(
            self.new_appointment_container,
            text="Оформление записи",
            padding="20"
        )

        # Заголовок
        ttk.Label(
            self.appointment_details_frame,
            text="Оформление записи",
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 20))

        # Информация о выборе
        self.appointment_info_frame = ttk.Frame(self.appointment_details_frame)
        self.appointment_info_frame.pack(fill=tk.X, pady=(0, 20))

        self.master_label = ttk.Label(
            self.appointment_info_frame,
            text="",
            font=("Arial", 11, "bold")
        )
        self.master_label.pack(anchor=tk.W)

        self.service_label = ttk.Label(
            self.appointment_info_frame,
            text="",
            font=("Arial", 11, "bold")
        )
        self.service_label.pack(anchor=tk.W)

        self.price_label = ttk.Label(
            self.appointment_info_frame,
            text="",
            font=("Arial", 10)
        )
        self.price_label.pack(anchor=tk.W)

        self.duration_label = ttk.Label(
            self.appointment_info_frame,
            text="",
            font=("Arial", 10)
        )
        self.duration_label.pack(anchor=tk.W)

        # Выбор даты
        date_frame = ttk.Frame(self.appointment_details_frame)
        date_frame.pack(fill=tk.X, pady=(10, 5))

        ttk.Label(date_frame, text="Дата (ГГГГ-ММ-ДД):").pack(side=tk.LEFT, padx=(0, 10))
        self.date_entry = ttk.Entry(date_frame, width=15)
        self.date_entry.pack(side=tk.LEFT)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Кнопка проверки доступного времени
        ttk.Button(
            date_frame,
            text="Проверить доступное время",
            command=self.check_available_time_final
        ).pack(side=tk.LEFT, padx=10)

        # Выбор времени
        time_frame = ttk.Frame(self.appointment_details_frame)
        time_frame.pack(fill=tk.X, pady=(5, 10))

        ttk.Label(time_frame, text="Время:").pack(side=tk.LEFT, padx=(0, 10))
        self.time_var = tk.StringVar()
        self.time_combo = ttk.Combobox(time_frame, textvariable=self.time_var, state="readonly", width=10)
        self.time_combo.pack(side=tk.LEFT)

        # Примечания
        notes_frame = ttk.Frame(self.appointment_details_frame)
        notes_frame.pack(fill=tk.X, pady=(10, 20))

        ttk.Label(notes_frame, text="Примечания:").pack(anchor=tk.W)
        self.notes_text = tk.Text(notes_frame, height=4, width=50)
        self.notes_text.pack(fill=tk.X, pady=(5, 0))

        # Кнопки управления
        button_frame = ttk.Frame(self.appointment_details_frame)
        button_frame.pack(pady=(10, 0))

        ttk.Button(
            button_frame,
            text="← Назад",
            command=self.back_to_previous_selection
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Создать запись",
            command=self.create_appointment_final,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)

        # Стиль для акцентной кнопки
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="#4CAF50")
        style.map("Accent.TButton",
                  background=[('active', '#45a049')])

    def choose_master_path(self):
        """Выбор пути через мастера"""
        self.choice_frame.pack_forget()
        self.show_master_selection()

    def choose_service_path(self):
        """Выбор пути через услугу"""
        self.choice_frame.pack_forget()
        self.show_service_selection()

    def show_master_selection(self):
        """Показать выбор мастера"""
        # Очищаем старые данные
        for widget in self.master_selection_content.winfo_children():
            widget.destroy()

        # Заголовок
        title_label = ttk.Label(
            self.master_selection_content,
            text="Выберите мастера",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Загружаем мастеров
        request = {"action": "get_masters"}
        response = self.send_request(request)

        if response["status"] == "success":
            masters = response["masters"]

            for master in masters:
                master_frame = ttk.Frame(self.master_selection_content, relief="solid", borderwidth=1)
                master_frame.pack(fill=tk.X, padx=5, pady=5)

                # Информация о мастере
                info_frame = ttk.Frame(master_frame)
                info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

                ttk.Label(
                    info_frame,
                    text=master['full_name'],
                    font=("Arial", 11, "bold")
                ).pack(anchor=tk.W)

                ttk.Label(
                    info_frame,
                    text=f"Специализация: {master['specialization']}",
                    font=("Arial", 9)
                ).pack(anchor=tk.W)

                ttk.Label(
                    info_frame,
                    text=f"Телефон: {master['phone']}",
                    font=("Arial", 9)
                ).pack(anchor=tk.W)

                # Кнопка выбора
                select_btn = ttk.Button(
                    master_frame,
                    text="Выбрать",
                    command=lambda m=master: self.select_master(m)
                )
                select_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        else:
            error_label = ttk.Label(
                self.master_selection_content,
                text="Не удалось загрузить список мастеров",
                font=("Arial", 11, "bold")
            )
            error_label.pack(pady=20)

        # Показываем фрейм
        self.master_selection_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def select_master(self, master):
        """Выбор мастера"""
        self.selected_master = master
        self.selected_master_id = master['id']

        # Скрываем выбор мастера, показываем выбор услуг
        self.master_selection_frame.pack_forget()
        self.show_master_services()

    def show_master_services(self):
        """Показать услуги выбранного мастера"""
        # Очищаем старые данные
        for widget in self.master_services_content.winfo_children():
            widget.destroy()

        # Заголовок
        title_label = ttk.Label(
            self.master_services_content,
            text=f"Услуги мастера: {self.selected_master['full_name']}",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Загружаем услуги мастера
        request = {
            "action": "get_master_services",
            "master_id": self.selected_master_id
        }
        response = self.send_request(request)

        if response["status"] == "success":
            services = response["services"]

            if not services:
                empty_label = ttk.Label(
                    self.master_services_content,
                    text="У этого мастера пока нет доступных услуг",
                    font=("Arial", 11)
                )
                empty_label.pack(pady=20)
            else:
                for service in services:
                    service_frame = ttk.Frame(self.master_services_content, relief="solid", borderwidth=1)
                    service_frame.pack(fill=tk.X, padx=5, pady=5)

                    # Информация об услуге
                    info_frame = ttk.Frame(service_frame)
                    info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

                    ttk.Label(
                        info_frame,
                        text=service['name'],
                        font=("Arial", 11, "bold")
                    ).pack(anchor=tk.W)

                    ttk.Label(
                        info_frame,
                        text=service['description'],
                        font=("Arial", 9)
                    ).pack(anchor=tk.W)

                    ttk.Label(
                        info_frame,
                        text=f"Цена: {service['price']} руб. | Длительность: {service['duration']} мин.",
                        font=("Arial", 9)
                    ).pack(anchor=tk.W)

                    # Кнопка выбора
                    select_btn = ttk.Button(
                        service_frame,
                        text="Выбрать",
                        command=lambda s=service: self.select_service_from_master(s)
                    )
                    select_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        # Показываем фрейм
        self.master_services_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def select_service_from_master(self, service):
        """Выбор услуги у мастера"""
        self.selected_service = service
        self.selected_service_id = service['id']

        # Обновляем информацию в фрейме оформления
        self.master_label.config(text=f"Мастер: {self.selected_master['full_name']}")
        self.service_label.config(text=f"Услуга: {self.selected_service['name']}")
        self.price_label.config(text=f"Цена: {self.selected_service['price']} руб.")
        self.duration_label.config(text=f"Длительность: {self.selected_service['duration']} мин.")

        # Скрываем выбор услуг, показываем оформление записи
        self.master_services_frame.pack_forget()
        self.show_appointment_details()

    def show_service_selection(self):
        """Показать выбор услуги"""
        # Очищаем старые данные
        for widget in self.service_selection_content.winfo_children():
            widget.destroy()

        # Заголовок
        title_label = ttk.Label(
            self.service_selection_content,
            text="Выберите услугу",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Загружаем услуги
        request = {"action": "get_services"}
        response = self.send_request(request)

        if response["status"] == "success":
            services = response["services"]

            for service in services:
                service_frame = ttk.Frame(self.service_selection_content, relief="solid", borderwidth=1)
                service_frame.pack(fill=tk.X, padx=5, pady=5)

                # Информация об услуге
                info_frame = ttk.Frame(service_frame)
                info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

                ttk.Label(
                    info_frame,
                    text=service['name'],
                    font=("Arial", 11, "bold")
                ).pack(anchor=tk.W)

                ttk.Label(
                    info_frame,
                    text=service['description'],
                    font=("Arial", 9)
                ).pack(anchor=tk.W)

                ttk.Label(
                    info_frame,
                    text=f"Цена: {service['price']} руб. | Длительность: {service['duration']} мин.",
                    font=("Arial", 9)
                ).pack(anchor=tk.W)

                # Кнопка выбора
                select_btn = ttk.Button(
                    service_frame,
                    text="Выбрать",
                    command=lambda s=service: self.select_service(s)
                )
                select_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        else:
            error_label = ttk.Label(
                self.service_selection_content,
                text="Не удалось загрузить список услуг",
                font=("Arial", 11, "bold")
            )
            error_label.pack(pady=20)

        # Показываем фрейм
        self.service_selection_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def select_service(self, service):
        """Выбор услуги"""
        self.selected_service = service
        self.selected_service_id = service['id']

        # Скрываем выбор услуги, показываем выбор мастера
        self.service_selection_frame.pack_forget()
        self.show_service_masters()

    def show_service_masters(self):
        """Показать мастеров для выбранной услуги"""
        # Очищаем старые данные
        for widget in self.service_masters_content.winfo_children():
            widget.destroy()

        # Заголовок
        title_label = ttk.Label(
            self.service_masters_content,
            text=f"Мастера для услуги: {self.selected_service['name']}",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Загружаем мастеров для услуги
        request = {
            "action": "get_service_masters",
            "service_id": self.selected_service_id
        }
        response = self.send_request(request)

        if response["status"] == "success":
            masters = response["masters"]

            if not masters:
                empty_label = ttk.Label(
                    self.service_masters_content,
                    text="Для этой услуги пока нет доступных мастеров",
                    font=("Arial", 11)
                )
                empty_label.pack(pady=20)
            else:
                for master in masters:
                    master_frame = ttk.Frame(self.service_masters_content, relief="solid", borderwidth=1)
                    master_frame.pack(fill=tk.X, padx=5, pady=5)

                    # Информация о мастере
                    info_frame = ttk.Frame(master_frame)
                    info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

                    ttk.Label(
                        info_frame,
                        text=master['full_name'],
                        font=("Arial", 11, "bold")
                    ).pack(anchor=tk.W)

                    ttk.Label(
                        info_frame,
                        text=f"Специализация: {master['specialization']}",
                        font=("Arial", 9)
                    ).pack(anchor=tk.W)

                    ttk.Label(
                        info_frame,
                        text=f"Телефон: {master['phone']}",
                        font=("Arial", 9)
                    ).pack(anchor=tk.W)

                    # Кнопка выбора
                    select_btn = ttk.Button(
                        master_frame,
                        text="Выбрать",
                        command=lambda m=master: self.select_master_from_service(m)
                    )
                    select_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        # Показываем фрейм
        self.service_masters_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def select_master_from_service(self, master):
        """Выбор мастера для услуги"""
        self.selected_master = master
        self.selected_master_id = master['id']

        # Обновляем информацию в фрейме оформления
        self.master_label.config(text=f"Мастер: {self.selected_master['full_name']}")
        self.service_label.config(text=f"Услуга: {self.selected_service['name']}")
        self.price_label.config(text=f"Цена: {self.selected_service['price']} руб.")
        self.duration_label.config(text=f"Длительность: {self.selected_service['duration']} мин.")

        # Скрываем выбор мастера, показываем оформление записи
        self.service_masters_frame.pack_forget()
        self.show_appointment_details()

    def show_appointment_details(self):
        """Показать оформление записи"""
        self.appointment_details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def check_available_time_final(self):
        """Проверка доступного времени для окончательной записи"""
        date = self.date_entry.get()

        if not date:
            messagebox.showwarning("Предупреждение", "Введите дату")
            return

        # Проверка формата даты
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        request = {
            "action": "get_available_times",
            "master_id": self.selected_master_id,
            "date": date
        }

        response = self.send_request(request)

        if response["status"] == "success":
            self.time_combo['values'] = response["available_times"]
            if response["available_times"]:
                messagebox.showinfo("Успех", f"Найдено {len(response['available_times'])} доступных времени")
            else:
                messagebox.showwarning("Предупреждение", "На эту дату нет доступного времени")
        else:
            messagebox.showerror("Ошибка", "Не удалось получить доступное время")

    def create_appointment_final(self):
        """Создание окончательной записи"""
        if not self.current_user:
            return

        date = self.date_entry.get()
        time = self.time_var.get()
        notes = self.notes_text.get("1.0", tk.END).strip()

        # Проверка заполненности полей
        if not all([date, time]):
            messagebox.showwarning("Предупреждение", "Заполните дату и время")
            return

        # Проверка формата даты
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        request = {
            "action": "create_appointment",
            "client_id": self.current_user["id"],
            "master_id": self.selected_master_id,
            "service_id": self.selected_service_id,
            "date": date,
            "time": time,
            "notes": notes
        }

        response = self.send_request(request)

        if response["status"] == "success":
            messagebox.showinfo("Успех", response["message"])

            # Возвращаемся к выбору пути
            self.appointment_details_frame.pack_forget()
            self.choice_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # Обновляем список записей
            self.load_appointments()
            self.notebook.select(1)  # Переключаемся на вкладку с записями

            # Сбрасываем выбор
            self.selected_master = None
            self.selected_service = None
            self.selected_master_id = None
            self.selected_service_id = None

        else:
            messagebox.showerror("Ошибка", response["message"])

    def back_to_choice(self):
        """Вернуться к выбору пути"""
        # Скрываем все фреймы
        self.master_selection_frame.pack_forget()
        self.master_services_frame.pack_forget()
        self.service_selection_frame.pack_forget()
        self.service_masters_frame.pack_forget()
        self.appointment_details_frame.pack_forget()

        # Показываем выбор пути
        self.choice_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Сбрасываем выбор
        self.selected_master = None
        self.selected_service = None
        self.selected_master_id = None
        self.selected_service_id = None

    def back_to_master_selection(self):
        """Вернуться к выбору мастера"""
        self.master_services_frame.pack_forget()
        self.master_selection_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def back_to_service_selection(self):
        """Вернуться к выбору услуги"""
        self.service_masters_frame.pack_forget()
        self.service_selection_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def back_to_previous_selection(self):
        """Вернуться к предыдущему шагу в зависимости от пути"""
        if self.selected_master and not self.selected_service:
            # Если выбран мастер, но не услуга
            self.appointment_details_frame.pack_forget()
            self.master_services_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        elif self.selected_service and not self.selected_master:
            # Если выбрана услуга, но не мастер
            self.appointment_details_frame.pack_forget()
            self.service_masters_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        else:
            # Иначе возвращаемся к выбору пути
            self.back_to_choice()

    def load_services(self):
        """Загрузка списка услуг"""
        request = {"action": "get_services"}
        response = self.send_request(request)

        if response["status"] == "success":
            self.services = response["services"]

    def load_appointments(self):
        """Загрузка записей пользователя"""
        if not self.current_user:
            return

        # Очищаем дерево
        for item in self.appointments_tree.get_children():
            self.appointments_tree.delete(item)

        request = {
            "action": "get_appointments",
            "client_id": self.current_user["id"]
        }

        response = self.send_request(request)

        if response["status"] == "success":
            for appointment in response["appointments"]:
                self.appointments_tree.insert('', 'end', values=(
                    appointment["date"],
                    appointment["time"],
                    appointment["service_name"],
                    appointment["master_name"],
                    f"{appointment['price']} руб.",
                    appointment["status"]
                ))

    def cancel_selected_appointment(self):
        """Отмена выбранной записи"""
        selection = self.appointments_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите запись для отмены")
            return

        item = self.appointments_tree.item(selection[0])
        values = item['values']

        confirmation = messagebox.askyesno("Подтверждение",
                                           f"Вы уверены, что хотите отменить запись на {values[0]} {values[1]}?")

        if confirmation:
            messagebox.showinfo("Информация", "Функция отмены записи будет реализована в полной версии")

    def run(self):
        """Запуск клиентского приложения"""
        self.root.mainloop()


def main():
    root = tk.Tk()
    app = BeautySalonClient(root)
    app.run()


if __name__ == "__main__":
    main()