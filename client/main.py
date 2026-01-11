"""
BeautyPro Desktop Application
Главное приложение с GUI на Tkinter
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from tkcalendar import Calendar
from api_client import BeautyProAPI


class HoverButton(tk.Button):
    """Кнопка с hover-эффектом"""
    def __init__(self, master, hover_bg='#0052CC', hover_fg='white', **kwargs):
        self.default_bg = kwargs.get('bg', '#0066FF')
        self.default_fg = kwargs.get('fg', 'white')
        self.hover_bg = hover_bg
        self.hover_fg = hover_fg
        super().__init__(master, **kwargs)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, e):
        self.config(bg=self.hover_bg, fg=self.hover_fg)
    
    def _on_leave(self, e):
        self.config(bg=self.default_bg, fg=self.default_fg)


class HoverCard(tk.Frame):
    """Карточка с hover-эффектом"""
    def __init__(self, master, hover_bg='#F0F7FF', **kwargs):
        self.default_bg = kwargs.get('bg', 'white')
        self.hover_bg = hover_bg
        super().__init__(master, **kwargs)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, e):
        self.config(bg=self.hover_bg)
        for child in self.winfo_children():
            try:
                child.config(bg=self.hover_bg)
                for subchild in child.winfo_children():
                    try:
                        subchild.config(bg=self.hover_bg)
                    except:
                        pass
            except:
                pass
    
    def _on_leave(self, e):
        self.config(bg=self.default_bg)
        for child in self.winfo_children():
            try:
                child.config(bg=self.default_bg)
                for subchild in child.winfo_children():
                    try:
                        subchild.config(bg=self.default_bg)
                    except:
                        pass
            except:
                pass


class BeautyProApp:
    """Главное приложение BeautyPro"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("BeautyPro - Салон красоты")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        
        self.api = BeautyProAPI()
        self.current_user = None
        self.selected_master = None
        self.selected_service = None
        self.loading_overlay = None
        
        self.setup_styles()
        self.show_login_screen()
    
    def create_styled_button(self, parent, text, command, style='primary', width=None):
        """Создать стилизованную кнопку (работает на macOS)"""
        styles = {
            'primary': {'bg': '#0066FF', 'fg': 'white', 
                       'hover_bg': '#0052CC', 'hover_fg': 'white'},
            'success': {'bg': '#0066FF', 'fg': 'white', 
                       'hover_bg': '#0052CC', 'hover_fg': 'white'},
            'danger': {'bg': '#CC0000', 'fg': 'white', 
                      'hover_bg': '#990000', 'hover_fg': 'white'},
            'accent': {'bg': '#0066FF', 'fg': 'white', 
                      'hover_bg': '#0052CC', 'hover_fg': 'white'},
            'secondary': {'bg': '#0066FF', 'fg': 'white', 
                         'hover_bg': '#0052CC', 'hover_fg': 'white'},
        }
        s = styles.get(style, styles['primary'])
        
        # Используем Frame + Label для корректного отображения на macOS
        frame = tk.Frame(parent, bg=s['bg'], cursor="hand2")
        
        label = tk.Label(frame, text=text, font=("Arial", 11, "bold"),
                        bg=s['bg'], fg=s['fg'], padx=15, pady=8, cursor="hand2")
        label.pack()
        
        def on_click(e):
            command()
        
        def on_enter(e):
            frame.config(bg=s['hover_bg'])
            label.config(bg=s['hover_bg'], fg=s['hover_fg'])
        
        def on_leave(e):
            frame.config(bg=s['bg'])
            label.config(bg=s['bg'], fg=s['fg'])
        
        frame.bind('<Button-1>', on_click)
        label.bind('<Button-1>', on_click)
        frame.bind('<Enter>', on_enter)
        frame.bind('<Leave>', on_leave)
        label.bind('<Enter>', on_enter)
        label.bind('<Leave>', on_leave)
        
        return frame
    
    def create_button(self, parent, text, command, bg=None, fg=None, font=None, 
                     width=None, padx=15, pady=8, relief="flat"):
        """Создать кнопку с полной кликабельностью (работает на macOS)"""
        if bg is None:
            bg = '#0066FF'
        if fg is None:
            fg = 'white'
        if font is None:
            font = ("Arial", 11, "bold")
        
        # Определяем цвет при наведении
        hover_bg = '#0052CC' if bg == '#0066FF' else ('#990000' if bg == self.colors['danger'] else bg)
        
        # Используем Frame + Label для корректного отображения на macOS
        frame = tk.Frame(parent, bg=bg, cursor="hand2")
        
        label = tk.Label(frame, text=text, font=font, bg=bg, fg=fg,
                        padx=padx, pady=pady, cursor="hand2")
        label.pack()
        
        def on_click(e):
            command()
        
        def on_enter(e):
            frame.config(bg=hover_bg)
            label.config(bg=hover_bg)
        
        def on_leave(e):
            frame.config(bg=bg)
            label.config(bg=bg)
        
        frame.bind('<Button-1>', on_click)
        label.bind('<Button-1>', on_click)
        frame.bind('<Enter>', on_enter)
        frame.bind('<Leave>', on_leave)
        label.bind('<Enter>', on_enter)
        label.bind('<Leave>', on_leave)
        
        return frame
    
    def create_card(self, parent, hover=True):
        """Создать карточку с белым фоном и синей рамкой"""
        if hover:
            card = HoverCard(parent, bg=self.colors['white'], hover_bg=self.colors['light'], 
                           padx=15, pady=15, relief="flat", bd=0,
                           highlightbackground=self.colors['primary'], highlightthickness=1)
            return card
        return tk.Frame(parent, bg=self.colors['white'], padx=15, pady=15, relief="flat", bd=0,
                       highlightbackground=self.colors['primary'], highlightthickness=1)
    
    def show_loading(self, message="Загрузка..."):
        """Показать индикатор загрузки"""
        if self.loading_overlay:
            return
        self.loading_overlay = tk.Frame(self.root, bg='#00000080')
        self.loading_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        box = tk.Frame(self.loading_overlay, bg=self.colors['white'], padx=30, pady=20)
        box.place(relx=0.5, rely=0.5, anchor='center')
        
        self.spinner_label = tk.Label(box, text="⏳", font=("Arial", 30), bg=self.colors['white'],
                                     fg=self.colors['primary'])
        self.spinner_label.pack()
        
        tk.Label(box, text=message, font=("Arial", 12), bg=self.colors['white'], 
                fg=self.colors['text']).pack(pady=(10, 0))
        
        self.root.update()
    
    def hide_loading(self):
        """Скрыть индикатор загрузки"""
        if self.loading_overlay:
            self.loading_overlay.destroy()
            self.loading_overlay = None
    
    def setup_styles(self):
        """Настройка стилей приложения"""
        style = ttk.Style()
        
        # Используем тему 'clam' для светлого фона
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Сине-белая цветовая схема с чёрным текстом
        self.colors = {
            'primary': '#0066FF',        # Основной синий
            'primary_dark': '#0052CC',   # Тёмно-синий для hover
            'secondary': '#0066FF',
            'accent': '#0066FF',
            'success': '#0066FF',
            'warning': '#0066FF',
            'danger': '#CC0000',          # Красный для удаления
            'info': '#0066FF',
            'light': '#F0F7FF',           # Очень светлый синий для hover
            'dark': '#0066FF',
            'white': '#FFFFFF',           # Белый фон
            'gray': '#555555',            # Серый для второстепенного текста
            'bg': '#FFFFFF',
            'btn_bg': '#FFFFFF',
            'btn_hover': '#E8F2FF',
            'border': '#0066FF',
            'card_bg': '#FFFFFF',
            'text': '#000000',            # Чёрный текст
            'text_dark': '#000000',       # Чёрный текст
        }
        
        self.root.configure(bg=self.colors['white'])
        
        # Настройка выпадающего списка Combobox
        self.root.option_add('*TCombobox*Listbox.background', 'white')
        self.root.option_add('*TCombobox*Listbox.foreground', self.colors['text'])
        self.root.option_add('*TCombobox*Listbox.selectBackground', self.colors['primary'])
        self.root.option_add('*TCombobox*Listbox.selectForeground', 'white')
        
        style.configure("TFrame", background=self.colors['white'], borderwidth=0)
        style.configure("Card.TFrame", background=self.colors['white'], relief="flat", borderwidth=0)
        style.configure("TLabelframe", background=self.colors['white'], borderwidth=0)
        style.configure("TLabelframe.Label", background=self.colors['white'], 
                       foreground=self.colors['primary'], font=("Arial", 11, "bold"))
        style.configure("TScrollbar", background=self.colors['white'], troughcolor=self.colors['white'])
        
        # Белый фон для всех элементов
        style.configure(".", background=self.colors['white'])
        
        style.configure("Title.TLabel", font=("Arial", 24, "bold"), 
                       foreground=self.colors['primary'], background=self.colors['white'])
        style.configure("Subtitle.TLabel", font=("Arial", 12), 
                       foreground=self.colors['text'], background=self.colors['white'])
        style.configure("TLabel", background=self.colors['white'], foreground=self.colors['text'])
        
        style.configure("TButton", font=("Arial", 10), foreground=self.colors['white'],
                       background=self.colors['primary'], padding=(15, 8))
        style.map("TButton", background=[('active', self.colors['primary_dark'])])
        
        # Notebook без серого фона - полностью белый
        style.configure("TNotebook", background=self.colors['white'], borderwidth=0, padding=0,
                       tabmargins=[0, 0, 0, 0])
        style.configure("TNotebook.Tab", font=("Arial", 11, "bold"), padding=(20, 10),
                       foreground=self.colors['white'], background=self.colors['primary'])
        style.map("TNotebook.Tab",
                 background=[('selected', self.colors['primary_dark']), ('!selected', self.colors['primary'])],
                 foreground=[('selected', self.colors['white']), ('!selected', self.colors['white'])])
        
        style.configure("TEntry", fieldbackground='white', foreground=self.colors['text'], padding=8)
        
        style.configure("TCombobox", fieldbackground='white', background='white',
                       foreground=self.colors['text'], arrowcolor=self.colors['primary'],
                       selectbackground=self.colors['primary'], selectforeground='white')
        style.map("TCombobox", 
                 fieldbackground=[('readonly', 'white'), ('disabled', 'white'), ('active', 'white')],
                 background=[('readonly', 'white'), ('disabled', 'white'), ('active', 'white')],
                 foreground=[('readonly', self.colors['text']), ('disabled', self.colors['gray'])])
        
        # Стиль таблицы с белым фоном везде
        style.configure("Treeview", 
                       background='white', 
                       fieldbackground='white',
                       foreground=self.colors['text'], 
                       font=("Arial", 10), 
                       rowheight=32,
                       borderwidth=0,
                       relief="flat")
        style.configure("Treeview.Heading", 
                       font=("Arial", 10, "bold"),
                       background=self.colors['primary'], 
                       foreground='white',
                       borderwidth=0,
                       relief="flat",
                       padding=(10, 8))
        style.map("Treeview", 
                 background=[('selected', self.colors['light']), ('!selected', 'white')],
                 fieldbackground=[('!disabled', 'white')],
                 foreground=[('selected', self.colors['primary']), ('!selected', self.colors['text'])])
        style.map("Treeview.Heading", 
                 background=[('active', self.colors['primary_dark'])])
        
        # Убираем серый фон у пустой области Treeview
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe', 'border': '0'})])
        
        # Принудительно белый фон для всех пустых областей
        self.root.option_add('*Treeview*background', 'white')
        self.root.option_add('*Treeview*fieldBackground', 'white')
    
    def bind_mousewheel(self, canvas, scrollable_frame, parent_window=None):
        """Привязать прокрутку колесом мыши к canvas (работает на macOS с trackpad)"""
        
        # Определяем родительское окно
        if parent_window is None:
            parent_window = canvas.winfo_toplevel()
        
        def _scroll(event):
            """Универсальный обработчик скролла"""
            # Проверяем, что canvas существует и видим
            try:
                if not canvas.winfo_exists():
                    return
            except:
                return
            
            import platform
            system = platform.system()
            
            if system == 'Darwin':  # macOS
                # На macOS trackpad отправляет delta как количество пикселей
                # Для плавного скролла используем yview_scroll с "units"
                if event.delta > 0:
                    canvas.yview_scroll(-2, "units")
                elif event.delta < 0:
                    canvas.yview_scroll(2, "units")
            elif system == 'Windows':
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:  # Linux
                if hasattr(event, 'num'):
                    if event.num == 4:
                        canvas.yview_scroll(-2, "units")
                    elif event.num == 5:
                        canvas.yview_scroll(2, "units")
        
        # Флаг для отслеживания состояния мыши над canvas
        canvas._mouse_over = False
        
        def _on_enter(event):
            canvas._mouse_over = True
        
        def _on_leave(event):
            canvas._mouse_over = False
        
        def _global_scroll(event):
            """Глобальный обработчик - проверяет, над каким виджетом мышь"""
            try:
                if canvas._mouse_over and canvas.winfo_exists():
                    _scroll(event)
            except:
                pass
        
        # Привязываем Enter/Leave к canvas
        canvas.bind("<Enter>", _on_enter)
        canvas.bind("<Leave>", _on_leave)
        
        # Привязываем Enter/Leave ко всем дочерним элементам
        def bind_children(widget):
            for child in widget.winfo_children():
                child.bind("<Enter>", lambda e: setattr(canvas, '_mouse_over', True))
                child.bind("<Leave>", lambda e: None)  # Не сбрасываем при переходе между детьми
                bind_children(child)
        
        bind_children(scrollable_frame)
        
        # Глобальная привязка к окну
        import platform
        if platform.system() == 'Darwin':
            parent_window.bind("<MouseWheel>", _global_scroll, add='+')
        elif platform.system() == 'Windows':
            parent_window.bind("<MouseWheel>", _global_scroll, add='+')
        else:
            parent_window.bind("<Button-4>", _global_scroll, add='+')
            parent_window.bind("<Button-5>", _global_scroll, add='+')
    
    def create_white_dropdown(self, parent, variable, values, width=40):
        """Создать выпадающий список с белым фоном (работает на macOS)"""
        # Контейнер с рамкой
        container = tk.Frame(parent, bg=self.colors['primary'], padx=2, pady=2)
        
        # Внутренний фрейм
        inner = tk.Frame(container, bg='white')
        inner.pack(fill=tk.X)
        
        # Используем OptionMenu вместо Combobox для белого фона на macOS
        if values:
            variable.set(values[0] if not variable.get() else variable.get())
        
        dropdown = tk.OptionMenu(inner, variable, *values if values else [''])
        dropdown.config(
            bg='white', fg='black', 
            activebackground=self.colors['light'], activeforeground='black',
            font=("Arial", 11), width=width-5,
            highlightthickness=0, relief='flat',
            anchor='w', padx=10
        )
        dropdown['menu'].config(
            bg='white', fg='black',
            activebackground=self.colors['primary'], activeforeground='white',
            font=("Arial", 11)
        )
        dropdown.pack(fill=tk.X, ipady=5)
        
        return container, dropdown
    
    def clear_root(self):
        """Очистить главное окно"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Показать экран авторизации"""
        self.clear_root()
        
        main_frame = tk.Frame(self.root, bg=self.colors['white'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        left_panel = tk.Frame(main_frame, bg=self.colors['primary'], width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)
        
        left_content = tk.Frame(left_panel, bg=self.colors['primary'])
        left_content.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(left_content, text="💇‍♀️", font=("Arial", 80),
                bg=self.colors['primary'], fg=self.colors['white']).pack(pady=(0, 20))
        tk.Label(left_content, text="BeautyPro", font=("Arial", 36, "bold"),
                bg=self.colors['primary'], fg=self.colors['white']).pack()
        tk.Label(left_content, text="Салон красоты", font=("Arial", 16),
                bg=self.colors['primary'], fg=self.colors['white']).pack(pady=(5, 30))
        tk.Label(left_content, text="✨ Красота начинается здесь ✨", font=("Arial", 12, "italic"),
                bg=self.colors['primary'], fg=self.colors['white']).pack()
        
        right_panel = tk.Frame(main_frame, bg=self.colors['white'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        container = tk.Frame(right_panel, bg=self.colors['white'])
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(container, text="Добро пожаловать!", font=("Arial", 24, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(pady=(0, 5))
        tk.Label(container, text="Войдите в свой аккаунт", font=("Arial", 12),
                bg=self.colors['white'], fg=self.colors['text']).pack(pady=(0, 30))
        
        form_frame = tk.Frame(container, bg=self.colors['white'], padx=30, pady=30)
        form_frame.pack(fill=tk.X)
        
        tk.Label(form_frame, text="📱 Номер телефона", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        self.phone_entry = tk.Entry(form_frame, width=35, font=("Arial", 12), relief="solid", bd=2,
                                   bg=self.colors['primary'], fg="white", insertbackground="white",
                                   highlightthickness=2, highlightcolor=self.colors['primary'],
                                   highlightbackground=self.colors['primary'])
        self.phone_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)
        
        tk.Label(form_frame, text="🔒 Пароль", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        self.password_entry = tk.Entry(form_frame, width=35, font=("Arial", 12), show="●", relief="solid", bd=2,
                                      bg=self.colors['primary'], fg="white", insertbackground="white",
                                      highlightthickness=2, highlightcolor=self.colors['primary'],
                                      highlightbackground=self.colors['primary'])
        self.password_entry.pack(fill=tk.X, pady=(5, 20), ipady=8)
        
        # Кнопка Войти (Frame + Label для macOS)
        login_frame = tk.Frame(form_frame, bg=self.colors['primary'], cursor="hand2")
        login_frame.pack(fill=tk.X)
        login_label = tk.Label(login_frame, text="   Войти   ", font=("Arial", 12, "bold"),
                              bg=self.colors['primary'], fg=self.colors['white'],
                              padx=20, pady=12, cursor="hand2")
        login_label.pack(fill=tk.X)
        
        def login_enter(e):
            login_frame.config(bg=self.colors['primary_dark'])
            login_label.config(bg=self.colors['primary_dark'])
        def login_leave(e):
            login_frame.config(bg=self.colors['primary'])
            login_label.config(bg=self.colors['primary'])
        
        login_frame.bind('<Button-1>', lambda e: self.do_login())
        login_label.bind('<Button-1>', lambda e: self.do_login())
        login_frame.bind('<Enter>', login_enter)
        login_frame.bind('<Leave>', login_leave)
        login_label.bind('<Enter>', login_enter)
        login_label.bind('<Leave>', login_leave)
        
        reg_frame = tk.Frame(container, bg=self.colors['white'])
        reg_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(reg_frame, text="Нет аккаунта?", font=("Arial", 10),
                bg=self.colors['white'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        reg_link_btn = tk.Button(reg_frame, text=" Зарегистрироваться ", font=("Arial", 10, "bold", "underline"),
                                bg=self.colors['white'], fg=self.colors['primary'],
                                activebackground=self.colors['white'], activeforeground=self.colors['primary_dark'],
                                relief="flat", bd=0, cursor="hand2", padx=5, pady=3,
                                command=self.show_register_screen)
        reg_link_btn.pack(side=tk.LEFT, padx=5)
        reg_link_btn.bind('<Button-1>', lambda e: self.show_register_screen())
    
    def show_register_screen(self):
        """Показать экран регистрации"""
        self.clear_root()
        
        main_frame = tk.Frame(self.root, bg=self.colors['white'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        left_panel = tk.Frame(main_frame, bg=self.colors['primary'], width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)
        
        left_content = tk.Frame(left_panel, bg=self.colors['primary'])
        left_content.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(left_content, text="✨", font=("Arial", 80),
                bg=self.colors['primary'], fg=self.colors['white']).pack(pady=(0, 20))
        tk.Label(left_content, text="Присоединяйтесь!", font=("Arial", 28, "bold"),
                bg=self.colors['primary'], fg=self.colors['white']).pack()
        tk.Label(left_content, text="Создайте аккаунт\nи записывайтесь онлайн", font=("Arial", 14),
                bg=self.colors['primary'], fg=self.colors['white'], justify="center").pack(pady=(10, 0))
        
        right_panel = tk.Frame(main_frame, bg=self.colors['white'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        container = tk.Frame(right_panel, bg=self.colors['white'])
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(container, text="Регистрация", font=("Arial", 24, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(pady=(0, 30))
        
        form_frame = tk.Frame(container, bg=self.colors['white'], padx=30, pady=30)
        form_frame.pack(fill=tk.X)
        
        tk.Label(form_frame, text="👤 ФИО", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        self.reg_name_entry = tk.Entry(form_frame, width=35, font=("Arial", 12), relief="solid", bd=2,
                                       bg=self.colors['primary'], fg="white", insertbackground="white",
                                       highlightthickness=2, highlightcolor=self.colors['primary'],
                                       highlightbackground=self.colors['primary'])
        self.reg_name_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)
        
        tk.Label(form_frame, text="📱 Номер телефона", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        self.reg_phone_entry = tk.Entry(form_frame, width=35, font=("Arial", 12), relief="solid", bd=2,
                                        bg=self.colors['primary'], fg="white", insertbackground="white",
                                        highlightthickness=2, highlightcolor=self.colors['primary'],
                                        highlightbackground=self.colors['primary'])
        self.reg_phone_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)
        
        tk.Label(form_frame, text="🔒 Пароль", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        self.reg_password_entry = tk.Entry(form_frame, width=35, font=("Arial", 12), show="●", relief="solid", bd=2,
                                           bg=self.colors['primary'], fg="white", insertbackground="white",
                                           highlightthickness=2, highlightcolor=self.colors['primary'],
                                           highlightbackground=self.colors['primary'])
        self.reg_password_entry.pack(fill=tk.X, pady=(5, 20), ipady=8)
        
        # Кнопка Зарегистрироваться (Frame + Label для macOS)
        reg_frame = tk.Frame(form_frame, bg=self.colors['primary'], cursor="hand2")
        reg_frame.pack(fill=tk.X)
        reg_label = tk.Label(reg_frame, text="   Зарегистрироваться   ", font=("Arial", 12, "bold"),
                            bg=self.colors['primary'], fg=self.colors['white'],
                            padx=20, pady=12, cursor="hand2")
        reg_label.pack(fill=tk.X)
        
        def reg_enter(e):
            reg_frame.config(bg=self.colors['primary_dark'])
            reg_label.config(bg=self.colors['primary_dark'])
        def reg_leave(e):
            reg_frame.config(bg=self.colors['primary'])
            reg_label.config(bg=self.colors['primary'])
        
        reg_frame.bind('<Button-1>', lambda e: self.do_register())
        reg_label.bind('<Button-1>', lambda e: self.do_register())
        reg_frame.bind('<Enter>', reg_enter)
        reg_frame.bind('<Leave>', reg_leave)
        reg_label.bind('<Enter>', reg_enter)
        reg_label.bind('<Leave>', reg_leave)
        
        # Кнопка Назад (Frame + Label для macOS)
        back_frame = tk.Frame(container, bg=self.colors['primary'], cursor="hand2")
        back_frame.pack(pady=(20, 0))
        back_label = tk.Label(back_frame, text="   Назад к входу   ", font=("Arial", 10, "bold"),
                             bg=self.colors['primary'], fg=self.colors['white'],
                             padx=15, pady=8, cursor="hand2")
        back_label.pack()
        
        def back_enter(e):
            back_frame.config(bg=self.colors['primary_dark'])
            back_label.config(bg=self.colors['primary_dark'])
        def back_leave(e):
            back_frame.config(bg=self.colors['primary'])
            back_label.config(bg=self.colors['primary'])
        
        back_frame.bind('<Button-1>', lambda e: self.show_login_screen())
        back_label.bind('<Button-1>', lambda e: self.show_login_screen())
        back_frame.bind('<Enter>', back_enter)
        back_frame.bind('<Leave>', back_leave)
        back_label.bind('<Enter>', back_enter)
        back_label.bind('<Leave>', back_leave)
    
    def do_login(self):
        """Выполнить авторизацию"""
        phone = self.phone_entry.get().strip()
        password = self.password_entry.get()
        
        if not phone or not password:
            messagebox.showwarning("Внимание", "Заполните все поля")
            return
        
        result = self.api.login(phone, password)
        
        if result["success"]:
            self.current_user = result["data"]
            if self.current_user["role"] == "admin":
                self.show_admin_interface()
            else:
                self.show_client_interface()
        else:
            messagebox.showerror("Ошибка", result["error"])
    
    def do_register(self):
        """Выполнить регистрацию"""
        name = self.reg_name_entry.get().strip()
        phone = self.reg_phone_entry.get().strip()
        password = self.reg_password_entry.get()
        
        if not name or not phone or not password:
            messagebox.showwarning("Внимание", "Заполните все поля")
            return
        
        result = self.api.register(phone, password, name)
        
        if result["success"]:
            messagebox.showinfo("Успех", "Регистрация успешна! Теперь вы можете войти.")
            self.show_login_screen()
        else:
            messagebox.showerror("Ошибка", result["error"])
    
    def logout(self):
        """Выйти из аккаунта"""
        self.current_user = None
        self.selected_master = None
        self.selected_service = None
        self.show_login_screen()
    
    def show_client_interface(self):
        """Показать интерфейс клиента"""
        self.clear_root()
        
        header = tk.Frame(self.root, bg=self.colors['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=self.colors['primary'])
        header_content.pack(fill=tk.BOTH, expand=True, padx=20)
        
        tk.Label(header_content, text=f"💇‍♀️ BeautyPro", font=("Arial", 16, "bold"),
                bg=self.colors['primary'], fg=self.colors['white']).pack(side=tk.LEFT, pady=15)
        
        tk.Label(header_content, text=f"👤 {self.current_user['full_name'] or 'Клиент'}",
                font=("Arial", 12), bg=self.colors['primary'], fg=self.colors['white']).pack(side=tk.LEFT, padx=30, pady=15)
        
        logout_btn = self.create_button(header_content, "  Выйти  ", self.logout,
                                       bg=self.colors['white'], fg=self.colors['primary'],
                                       font=("Arial", 10, "bold"), padx=12, pady=6)
        logout_btn.pack(side=tk.RIGHT, pady=15)
        
        # Контейнер для notebook с белым фоном
        notebook_container = tk.Frame(self.root, bg=self.colors['white'])
        notebook_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        notebook = ttk.Notebook(notebook_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Используем tk.Frame вместо ttk.Frame для точного контроля цвета
        booking_tab = tk.Frame(notebook, bg=self.colors['white'])
        notebook.add(booking_tab, text="📝 Новая запись")
        self.create_booking_tab(booking_tab)
        
        appointments_tab = tk.Frame(notebook, bg=self.colors['white'])
        notebook.add(appointments_tab, text="📋 Мои записи")
        self.create_appointments_tab(appointments_tab)
        
        history_tab = tk.Frame(notebook, bg=self.colors['white'])
        notebook.add(history_tab, text="📜 История")
        self.create_history_tab(history_tab)
    
    def create_booking_tab(self, parent):
        """Создать вкладку записи"""
        main_container = tk.Frame(parent, bg=self.colors['white'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        header = tk.Frame(main_container, bg=self.colors['white'])
        header.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header, text="📝 Новая запись", font=("Arial", 20, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(side=tk.LEFT)
        
        self.booking_container = tk.Frame(main_container, bg=self.colors['white'])
        self.booking_container.pack(fill=tk.BOTH, expand=True)
        
        self.show_booking_choice()
    
    def show_booking_choice(self):
        """Показать выбор способа записи"""
        for widget in self.booking_container.winfo_children():
            widget.destroy()
        
        self.selected_master = None
        self.selected_service = None
        
        tk.Label(self.booking_container, text="Выберите способ записи:", font=("Arial", 14),
                bg=self.colors['white'], fg=self.colors['text']).pack(pady=(20, 30))
        
        cards_frame = tk.Frame(self.booking_container, bg=self.colors['white'])
        cards_frame.pack(pady=20)
        
        # Карточка выбора мастера
        master_card = tk.Frame(cards_frame, bg=self.colors['white'], 
                              highlightbackground=self.colors['primary'], highlightthickness=2,
                              padx=20, pady=15, cursor="hand2")
        master_card.pack(side=tk.LEFT, padx=20)
        
        def on_master_click(e=None):
            self.show_masters_list()
        
        def on_master_enter(e=None):
            master_card.config(bg=self.colors['light'])
            for child in master_card.winfo_children():
                child.config(bg=self.colors['light'])
        
        def on_master_leave(e=None):
            master_card.config(bg=self.colors['white'])
            for child in master_card.winfo_children():
                child.config(bg=self.colors['white'])
        
        master_card.bind('<Button-1>', on_master_click)
        master_card.bind('<Enter>', on_master_enter)
        master_card.bind('<Leave>', on_master_leave)
        
        lbl1 = tk.Label(master_card, text="👨‍🎨", font=("Arial", 50), bg=self.colors['white'], cursor="hand2")
        lbl1.pack(pady=(10, 5))
        lbl1.bind('<Button-1>', on_master_click)
        
        lbl2 = tk.Label(master_card, text="Выбрать мастера", font=("Arial", 14, "bold"),
                bg=self.colors['white'], fg=self.colors['primary'], cursor="hand2")
        lbl2.pack()
        lbl2.bind('<Button-1>', on_master_click)
        
        lbl3 = tk.Label(master_card, text="Сначала выберите мастера,\nзатем услугу", font=("Arial", 10),
                bg=self.colors['white'], fg=self.colors['gray'], cursor="hand2")
        lbl3.pack(pady=(5, 10))
        lbl3.bind('<Button-1>', on_master_click)
        
        # Карточка выбора услуги
        service_card = tk.Frame(cards_frame, bg=self.colors['white'], 
                               highlightbackground=self.colors['primary'], highlightthickness=2,
                               padx=20, pady=15, cursor="hand2")
        service_card.pack(side=tk.LEFT, padx=20)
        
        def on_service_click(e=None):
            self.show_services_list()
        
        def on_service_enter(e=None):
            service_card.config(bg=self.colors['light'])
            for child in service_card.winfo_children():
                child.config(bg=self.colors['light'])
        
        def on_service_leave(e=None):
            service_card.config(bg=self.colors['white'])
            for child in service_card.winfo_children():
                child.config(bg=self.colors['white'])
        
        service_card.bind('<Button-1>', on_service_click)
        service_card.bind('<Enter>', on_service_enter)
        service_card.bind('<Leave>', on_service_leave)
        
        lbl4 = tk.Label(service_card, text="✂️", font=("Arial", 50), bg=self.colors['white'], cursor="hand2")
        lbl4.pack(pady=(10, 5))
        lbl4.bind('<Button-1>', on_service_click)
        
        lbl5 = tk.Label(service_card, text="Выбрать услугу", font=("Arial", 14, "bold"),
                bg=self.colors['white'], fg=self.colors['primary'], cursor="hand2")
        lbl5.pack()
        lbl5.bind('<Button-1>', on_service_click)
        
        lbl6 = tk.Label(service_card, text="Сначала выберите услугу,\nзатем мастера", font=("Arial", 10),
                bg=self.colors['white'], fg=self.colors['gray'], cursor="hand2")
        lbl6.pack(pady=(5, 10))
        lbl6.bind('<Button-1>', on_service_click)
    
    def show_masters_list(self):
        """Показать список мастеров"""
        for widget in self.booking_container.winfo_children():
            widget.destroy()
        
        header = tk.Frame(self.booking_container, bg=self.colors['white'])
        header.pack(fill=tk.X, pady=(0, 15))
        
        back_btn = self.create_styled_button(header, "← Назад", self.show_booking_choice, 'secondary')
        back_btn.pack(side=tk.LEFT)
        
        tk.Label(header, text="👨‍🎨 Выберите мастера", font=("Arial", 16, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(side=tk.LEFT, padx=20)
        
        result = self.api.get_masters()
        
        if not result["success"]:
            tk.Label(self.booking_container, text="Ошибка загрузки мастеров",
                    font=("Arial", 12), bg=self.colors['white'], fg=self.colors['danger']).pack(pady=20)
            return
        
        masters = result["data"]
        
        if not masters:
            tk.Label(self.booking_container, text="Нет доступных мастеров",
                    font=("Arial", 12), bg=self.colors['white'], fg=self.colors['gray']).pack(pady=20)
            return
        
        canvas = tk.Canvas(self.booking_container, bg=self.colors['white'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.booking_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['white'])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязка скролла мышью
        self.bind_mousewheel(canvas, scrollable_frame)
        
        # Сетка мастеров - 6 в ряд
        cols = 6
        for i, master in enumerate(masters):
            row = i // cols
            col = i % cols
            
            card = tk.Frame(scrollable_frame, bg=self.colors['white'], 
                          highlightbackground=self.colors['primary'], highlightthickness=2,
                          padx=8, pady=8, width=145, height=130)
            card.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            card.grid_propagate(False)
            card.bind('<Button-1>', lambda e, m=master: self.select_master(m))
            card.bind('<Enter>', lambda e, c=card: c.config(bg=self.colors['light']))
            card.bind('<Leave>', lambda e, c=card: c.config(bg=self.colors['white']))
            
            # Аватар
            avatar = tk.Frame(card, bg=self.colors['white'], width=40, height=40,
                            highlightbackground=self.colors['primary'], highlightthickness=1)
            avatar.pack(pady=(0, 5))
            avatar.pack_propagate(False)
            avatar.bind('<Button-1>', lambda e, m=master: self.select_master(m))
            tk.Label(avatar, text="👨‍🎨", font=("Arial", 16), bg=self.colors['white']).place(relx=0.5, rely=0.5, anchor='center')
            
            # Имя
            name_label = tk.Label(card, text=master['full_name'], font=("Arial", 10, "bold"),
                    bg=self.colors['white'], fg=self.colors['text'], wraplength=130)
            name_label.pack()
            name_label.bind('<Button-1>', lambda e, m=master: self.select_master(m))
            
            # Профессия
            profession = master.get('profession', {}).get('name', '') if master.get('profession') else ''
            prof_label = tk.Label(card, text=profession, font=("Arial", 9),
                    bg=self.colors['white'], fg=self.colors['gray'])
            prof_label.pack()
            prof_label.bind('<Button-1>', lambda e, m=master: self.select_master(m))
            
            # Количество услуг
            services_count = len(master.get('services', []))
            services_label = tk.Label(card, text=f"✂️ {services_count} услуг", font=("Arial", 9),
                    bg=self.colors['white'], fg=self.colors['primary'])
            services_label.pack()
            services_label.bind('<Button-1>', lambda e, m=master: self.select_master(m))
        
        # Настройка колонок для равномерного распределения
        for c in range(cols):
            scrollable_frame.columnconfigure(c, weight=1)
        
        # Привязка скролла после создания всех элементов
        self.bind_mousewheel(canvas, scrollable_frame)
    
    def select_master(self, master):
        """Выбрать мастера"""
        self.selected_master = master
        self.show_master_services()
    
    def show_master_services(self):
        """Показать услуги выбранного мастера"""
        for widget in self.booking_container.winfo_children():
            widget.destroy()
        
        header = tk.Frame(self.booking_container, bg=self.colors['white'])
        header.pack(fill=tk.X, pady=(0, 15))
        
        back_btn = self.create_styled_button(header, "← Назад", self.show_masters_list, 'secondary')
        back_btn.pack(side=tk.LEFT)
        
        tk.Label(header, text=f"✂️ Услуги мастера: {self.selected_master['full_name']}", font=("Arial", 16, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(side=tk.LEFT, padx=20)
        
        master_info = tk.Frame(self.booking_container, bg=self.colors['white'], padx=15, pady=10,
                              highlightbackground=self.colors['primary'], highlightthickness=1)
        master_info.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(master_info, text=f"👨‍🎨 {self.selected_master['full_name']}",
                font=("Arial", 12, "bold"), bg=self.colors['white'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        services = self.selected_master.get('services', [])
        
        if not services:
            tk.Label(self.booking_container, text="У мастера нет доступных услуг",
                    font=("Arial", 12), bg=self.colors['white'], fg=self.colors['gray']).pack(pady=20)
            return
        
        canvas = tk.Canvas(self.booking_container, bg=self.colors['white'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.booking_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['white'])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязка скролла мышью
        self.bind_mousewheel(canvas, scrollable_frame)
        
        for service in services:
            card = tk.Frame(scrollable_frame, bg=self.colors['white'], 
                          highlightbackground=self.colors['primary'], highlightthickness=2,
                          padx=15, pady=10, cursor="hand2")
            card.pack(fill=tk.X, pady=5, padx=5)
            
            def make_click_handler(s):
                return lambda e: self.select_service_and_show_calendar(s)
            
            def make_enter_handler(c):
                return lambda e: c.config(bg=self.colors['light'])
            
            def make_leave_handler(c):
                return lambda e: c.config(bg=self.colors['white'])
            
            click_handler = make_click_handler(service)
            card.bind('<Button-1>', click_handler)
            card.bind('<Enter>', make_enter_handler(card))
            card.bind('<Leave>', make_leave_handler(card))
            
            # Название услуги
            name_lbl = tk.Label(card, text=f"✂️ {service['name']}", font=("Arial", 12, "bold"),
                    bg=self.colors['white'], fg=self.colors['text'], cursor="hand2")
            name_lbl.pack(anchor=tk.W)
            name_lbl.bind('<Button-1>', click_handler)
            
            # Детали (цена и время)
            details = tk.Frame(card, bg=self.colors['white'], cursor="hand2")
            details.pack(anchor=tk.W)
            details.bind('<Button-1>', click_handler)
            
            price_lbl = tk.Label(details, text=f"💰 {service['price']} руб.", font=("Arial", 10),
                    bg=self.colors['white'], fg=self.colors['gray'], cursor="hand2")
            price_lbl.pack(side=tk.LEFT)
            price_lbl.bind('<Button-1>', click_handler)
            
            time_lbl = tk.Label(details, text=f"  •  ⏱️ {service['duration_minutes']} мин.", font=("Arial", 10),
                    bg=self.colors['white'], fg=self.colors['gray'], cursor="hand2")
            time_lbl.pack(side=tk.LEFT)
            time_lbl.bind('<Button-1>', click_handler)
        
        # Привязка скролла после создания всех элементов
        self.bind_mousewheel(canvas, scrollable_frame)
    
    def show_services_list(self):
        """Показать список услуг"""
        for widget in self.booking_container.winfo_children():
            widget.destroy()
        
        header = tk.Frame(self.booking_container, bg=self.colors['white'])
        header.pack(fill=tk.X, pady=(0, 15))
        
        back_btn = self.create_styled_button(header, "← Назад", self.show_booking_choice, 'secondary')
        back_btn.pack(side=tk.LEFT)
        
        tk.Label(header, text="✂️ Выберите услугу", font=("Arial", 16, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(side=tk.LEFT, padx=20)
        
        result = self.api.get_services()
        
        if not result["success"]:
            tk.Label(self.booking_container, text="Ошибка загрузки услуг",
                    font=("Arial", 12), bg=self.colors['white'], fg=self.colors['danger']).pack(pady=20)
            return
        
        services = result["data"]
        
        canvas = tk.Canvas(self.booking_container, bg=self.colors['white'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.booking_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['white'])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязка скролла мышью
        self.bind_mousewheel(canvas, scrollable_frame)
        
        # Сетка услуг - 3 в ряд
        cols = 3
        for i, service in enumerate(services):
            row = i // cols
            col = i % cols
            
            card = tk.Frame(scrollable_frame, bg=self.colors['white'], 
                          highlightbackground=self.colors['primary'], highlightthickness=2,
                          padx=12, pady=10, cursor="hand2", width=280, height=100)
            card.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
            card.grid_propagate(False)
            
            def make_click_handler(s):
                return lambda e: self.select_service(s)
            
            def make_enter_handler(c):
                return lambda e: c.config(bg=self.colors['light'])
            
            def make_leave_handler(c):
                return lambda e: c.config(bg=self.colors['white'])
            
            click_handler = make_click_handler(service)
            card.bind('<Button-1>', click_handler)
            card.bind('<Enter>', make_enter_handler(card))
            card.bind('<Leave>', make_leave_handler(card))
            
            # Название услуги
            name_lbl = tk.Label(card, text=f"✂️ {service['name']}", font=("Arial", 11, "bold"),
                    bg=self.colors['white'], fg=self.colors['text'], cursor="hand2", wraplength=250)
            name_lbl.pack(anchor=tk.W)
            name_lbl.bind('<Button-1>', click_handler)
            
            # Профессия
            profession = service.get('profession', {}).get('name', '') if service.get('profession') else ''
            prof_lbl = tk.Label(card, text=profession, font=("Arial", 9),
                    bg=self.colors['white'], fg=self.colors['gray'], cursor="hand2")
            prof_lbl.pack(anchor=tk.W)
            prof_lbl.bind('<Button-1>', click_handler)
            
            # Детали (цена и время)
            details = tk.Frame(card, bg=self.colors['white'], cursor="hand2")
            details.pack(anchor=tk.W, pady=(5, 0))
            details.bind('<Button-1>', click_handler)
            
            price_lbl = tk.Label(details, text=f"💰 {service['price']} руб.", font=("Arial", 9),
                    bg=self.colors['white'], fg=self.colors['gray'], cursor="hand2")
            price_lbl.pack(side=tk.LEFT)
            price_lbl.bind('<Button-1>', click_handler)
            
            time_lbl = tk.Label(details, text=f"  •  ⏱️ {service['duration_minutes']} мин.", font=("Arial", 9),
                    bg=self.colors['white'], fg=self.colors['gray'], cursor="hand2")
            time_lbl.pack(side=tk.LEFT)
            time_lbl.bind('<Button-1>', click_handler)
        
        # Привязка скролла после создания всех элементов
        self.bind_mousewheel(canvas, scrollable_frame)
    
    def select_service(self, service):
        """Выбрать услугу и показать мастеров"""
        self.selected_service = service
        self.show_service_masters()
    
    def show_service_masters(self):
        """Показать мастеров для выбранной услуги"""
        for widget in self.booking_container.winfo_children():
            widget.destroy()
        
        header = tk.Frame(self.booking_container, bg=self.colors['white'])
        header.pack(fill=tk.X, pady=(0, 15))
        
        back_btn = self.create_styled_button(header, "← Назад", self.show_services_list, 'secondary')
        back_btn.pack(side=tk.LEFT)
        
        tk.Label(header, text=f"👨‍🎨 Мастера для: {self.selected_service['name']}", font=("Arial", 16, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(side=tk.LEFT, padx=20)
        
        service_info = tk.Frame(self.booking_container, bg=self.colors['white'], padx=15, pady=10,
                               highlightbackground=self.colors['primary'], highlightthickness=1)
        service_info.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(service_info, text=f"✂️ {self.selected_service['name']}",
                font=("Arial", 12, "bold"), bg=self.colors['white'], fg=self.colors['text']).pack(side=tk.LEFT)
        tk.Label(service_info, text=f"💰 {self.selected_service['price']} руб.",
                font=("Arial", 11), bg=self.colors['white'], fg=self.colors['primary']).pack(side=tk.RIGHT)
        
        result = self.api.get_service_masters(self.selected_service['id'])
        
        if not result["success"]:
            tk.Label(self.booking_container, text="Ошибка загрузки мастеров",
                    font=("Arial", 12), bg=self.colors['white'], fg=self.colors['danger']).pack(pady=20)
            return
        
        masters = result["data"]
        
        if not masters:
            tk.Label(self.booking_container, text="Нет доступных мастеров для этой услуги",
                    font=("Arial", 12), bg=self.colors['white'], fg=self.colors['gray']).pack(pady=20)
            return
        
        canvas = tk.Canvas(self.booking_container, bg=self.colors['white'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.booking_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['white'])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязка скролла мышью
        self.bind_mousewheel(canvas, scrollable_frame)
        
        # Сетка мастеров - 6 в ряд
        cols = 6
        for i, master in enumerate(masters):
            row = i // cols
            col = i % cols
            
            card = tk.Frame(scrollable_frame, bg=self.colors['white'], 
                          highlightbackground=self.colors['primary'], highlightthickness=2,
                          padx=8, pady=8, width=145, height=110)
            card.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            card.grid_propagate(False)
            card.bind('<Button-1>', lambda e, m=master: self.select_master_and_show_calendar(m))
            card.bind('<Enter>', lambda e, c=card: c.config(bg=self.colors['light']))
            card.bind('<Leave>', lambda e, c=card: c.config(bg=self.colors['white']))
            
            # Аватар
            avatar = tk.Frame(card, bg=self.colors['white'], width=35, height=35,
                            highlightbackground=self.colors['primary'], highlightthickness=1)
            avatar.pack(pady=(0, 3))
            avatar.pack_propagate(False)
            avatar.bind('<Button-1>', lambda e, m=master: self.select_master_and_show_calendar(m))
            tk.Label(avatar, text="👨‍🎨", font=("Arial", 14), bg=self.colors['white']).place(relx=0.5, rely=0.5, anchor='center')
            
            # Имя
            name_label = tk.Label(card, text=master['full_name'], font=("Arial", 9, "bold"),
                    bg=self.colors['white'], fg=self.colors['text'], wraplength=130)
            name_label.pack()
            name_label.bind('<Button-1>', lambda e, m=master: self.select_master_and_show_calendar(m))
            
            # Профессия
            profession = master.get('profession', {}).get('name', '') if master.get('profession') else ''
            prof_label = tk.Label(card, text=profession, font=("Arial", 9),
                    bg=self.colors['white'], fg=self.colors['gray'])
            prof_label.pack()
            prof_label.bind('<Button-1>', lambda e, m=master: self.select_master_and_show_calendar(m))
        
        # Настройка колонок для равномерного распределения
        for c in range(cols):
            scrollable_frame.columnconfigure(c, weight=1)
        
        # Привязка скролла после создания всех элементов
        self.bind_mousewheel(canvas, scrollable_frame)
    
    def select_master_and_show_calendar(self, master):
        """Выбрать мастера и показать календарь"""
        self.selected_master = master
        self.show_date_time_picker()
    
    def select_service_and_show_calendar(self, service):
        """Выбрать услугу и показать календарь"""
        self.selected_service = service
        self.show_date_time_picker()
    
    def show_date_time_picker(self):
        """Показать выбор даты и времени"""
        for widget in self.booking_container.winfo_children():
            widget.destroy()
        
        header = tk.Frame(self.booking_container, bg=self.colors['white'])
        header.pack(fill=tk.X, pady=(0, 15))
        
        back_btn = self.create_styled_button(header, "← Назад", self.show_booking_choice, 'secondary')
        back_btn.pack(side=tk.LEFT)
        
        tk.Label(header, text="📅 Выберите дату и время", font=("Arial", 16, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(side=tk.LEFT, padx=20)
        
        details_frame = tk.Frame(self.booking_container, bg=self.colors['white'], padx=15, pady=15,
                               highlightbackground=self.colors['primary'], highlightthickness=1)
        details_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(details_frame, text=f"👨‍🎨 {self.selected_master['full_name']}", font=("Arial", 11),
                bg=self.colors['white'], fg=self.colors['text']).pack(anchor=tk.W)
        tk.Label(details_frame, text=f"✂️ {self.selected_service['name']}", font=("Arial", 11),
                bg=self.colors['white'], fg=self.colors['text']).pack(anchor=tk.W)
        tk.Label(details_frame, text=f"💰 {self.selected_service['price']} руб.  •  ⏱️ {self.selected_service['duration_minutes']} мин.",
                font=("Arial", 10), bg=self.colors['white'], fg=self.colors['gray']).pack(anchor=tk.W)
        
        content_frame = tk.Frame(self.booking_container, bg=self.colors['white'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        left_frame = tk.Frame(content_frame, bg=self.colors['white'])
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        tk.Label(left_frame, text="📅 Выберите дату:", font=("Arial", 12, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W, pady=(0, 10))
        
        # Используем Calendar вместо DateEntry для стабильной работы на macOS
        cal_frame = tk.Frame(left_frame, bg=self.colors['primary'], padx=2, pady=2)
        cal_frame.pack(pady=(0, 20))
        
        self.date_picker = Calendar(cal_frame, selectmode='day', 
                                   font=("Arial", 10),
                                   background=self.colors['white'],
                                   foreground=self.colors['text'],
                                   headersbackground=self.colors['primary'],
                                   headersforeground='white',
                                   selectbackground=self.colors['primary'],
                                   selectforeground='white',
                                   normalbackground='white',
                                   normalforeground=self.colors['text'],
                                   weekendbackground='white',
                                   weekendforeground=self.colors['primary'],
                                   othermonthbackground='#f0f0f0',
                                   othermonthforeground='#999999',
                                   othermonthwebackground='#f0f0f0',
                                   othermonthweforeground='#999999',
                                   borderwidth=0,
                                   showothermonthdays=True,
                                   mindate=date.today(), 
                                   maxdate=date.today() + timedelta(days=365))
        self.date_picker.pack()
        
        # Настраиваем кнопки навигации
        for child in cal_frame.winfo_children():
            if hasattr(child, 'winfo_children'):
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Button):
                        subchild.config(bg=self.colors['primary'], fg='white', 
                                       activebackground=self.colors['primary_dark'],
                                       relief='flat', cursor='hand2')
        
        self.date_picker.bind("<<CalendarSelected>>", lambda e: self.load_time_slots())
        
        right_frame = tk.Frame(content_frame, bg=self.colors['white'])
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_frame, text="⏰ Доступное время:", font=("Arial", 12, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W, pady=(0, 10))
        
        self.slots_container = tk.Frame(right_frame, bg=self.colors['white'])
        self.slots_container.pack(fill=tk.BOTH, expand=True)
        
        self.load_time_slots()
    
    def load_time_slots(self):
        """Загрузить доступные временные слоты"""
        for widget in self.slots_container.winfo_children():
            widget.destroy()
        
        selected_date = self.date_picker.selection_get()
        
        result = self.api.get_available_slots(
            self.selected_master['id'],
            self.selected_service['id'],
            selected_date
        )
        
        if not result["success"]:
            tk.Label(self.slots_container, text="Ошибка загрузки слотов",
                    font=("Arial", 12), bg=self.colors['white'], fg=self.colors['danger']).pack(pady=20)
            return
        
        slots = result["data"].get("slots", [])
        
        if not slots:
            tk.Label(self.slots_container, text="Нет доступного времени на эту дату",
                    font=("Arial", 12), bg=self.colors['white'], fg=self.colors['gray']).pack(pady=20)
            return
        
        slots_grid = tk.Frame(self.slots_container, bg=self.colors['white'])
        slots_grid.pack(fill=tk.BOTH, expand=True)
        
        for i, slot in enumerate(slots):
            row = i // 4
            col = i % 4
            
            def make_slot_callback(s):
                return lambda: self.confirm_booking(s)
            
            slot_btn = tk.Button(
                slots_grid, text=f"  {slot['time']}  ", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['text'],
                activebackground=self.colors['light'], activeforeground=self.colors['text'],
                relief="solid", bd=1, cursor="hand2", padx=10, pady=8,
                highlightbackground=self.colors['primary'],
                command=make_slot_callback(slot)
            )
            slot_btn.grid(row=row, column=col, padx=5, pady=5)
            slot_btn.bind('<Button-1>', lambda e, s=slot: self.confirm_booking(s))
    
    def confirm_booking(self, slot):
        """Подтвердить запись"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Подтверждение записи")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['white'])
        
        # Заголовок
        header = tk.Frame(dialog, bg=self.colors['primary'])
        header.pack(fill=tk.X)
        tk.Label(header, text="✅ Подтвердите запись", font=("Arial", 16, "bold"),
                bg=self.colors['primary'], fg=self.colors['white']).pack(pady=15)
        
        # Детали записи
        frame = tk.Frame(dialog, bg=self.colors['white'], padx=25, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        details = [
            ("👨‍🎨", "Мастер", self.selected_master['full_name']),
            ("✂️", "Услуга", self.selected_service['name']),
            ("📅", "Дата", self.date_picker.selection_get().strftime("%d.%m.%Y")),
            ("⏰", "Время", slot['time']),
            ("💰", "Стоимость", f"{self.selected_service['price']} руб."),
            ("⏱️", "Длительность", f"{self.selected_service['duration_minutes']} мин."),
        ]
        
        for icon, label, value in details:
            row = tk.Frame(frame, bg=self.colors['white'])
            row.pack(fill=tk.X, pady=5)
            
            tk.Label(row, text=icon, font=("Arial", 16), bg=self.colors['white']).pack(side=tk.LEFT)
            
            text_frame = tk.Frame(row, bg=self.colors['white'])
            text_frame.pack(side=tk.LEFT, padx=10)
            
            tk.Label(text_frame, text=label, font=("Arial", 9), 
                    bg=self.colors['white'], fg=self.colors['gray']).pack(anchor=tk.W)
            tk.Label(text_frame, text=value, font=("Arial", 11, "bold"), 
                    bg=self.colors['white'], fg=self.colors['text']).pack(anchor=tk.W)
        
        # Кнопки
        btn_frame = tk.Frame(dialog, bg=self.colors['white'], padx=25, pady=20)
        btn_frame.pack(fill=tk.X)
        
        def do_confirm():
            dialog.destroy()
            self.do_booking(slot)
        
        # Кнопка Подтвердить (Frame + Label для macOS)
        confirm_frame = tk.Frame(btn_frame, bg=self.colors['primary'], cursor="hand2")
        confirm_frame.pack(fill=tk.X, pady=(0, 10))
        confirm_label = tk.Label(confirm_frame, text="   Подтвердить запись   ", font=("Arial", 12, "bold"),
                                bg=self.colors['primary'], fg=self.colors['white'],
                                padx=20, pady=12, cursor="hand2")
        confirm_label.pack(fill=tk.X)
        
        def confirm_enter(e):
            confirm_frame.config(bg=self.colors['primary_dark'])
            confirm_label.config(bg=self.colors['primary_dark'])
        def confirm_leave(e):
            confirm_frame.config(bg=self.colors['primary'])
            confirm_label.config(bg=self.colors['primary'])
        
        confirm_frame.bind('<Button-1>', lambda e: do_confirm())
        confirm_label.bind('<Button-1>', lambda e: do_confirm())
        confirm_frame.bind('<Enter>', confirm_enter)
        confirm_frame.bind('<Leave>', confirm_leave)
        confirm_label.bind('<Enter>', confirm_enter)
        confirm_label.bind('<Leave>', confirm_leave)
        
        # Кнопка Отмена (Frame + Label для macOS)
        cancel_frame = tk.Frame(btn_frame, bg=self.colors['primary'], cursor="hand2")
        cancel_frame.pack(fill=tk.X)
        cancel_label = tk.Label(cancel_frame, text="   Отмена   ", font=("Arial", 11, "bold"),
                               bg=self.colors['primary'], fg=self.colors['white'],
                               padx=20, pady=10, cursor="hand2")
        cancel_label.pack(fill=tk.X)
        
        def cancel_enter(e):
            cancel_frame.config(bg=self.colors['primary_dark'])
            cancel_label.config(bg=self.colors['primary_dark'])
        def cancel_leave(e):
            cancel_frame.config(bg=self.colors['primary'])
            cancel_label.config(bg=self.colors['primary'])
        
        cancel_frame.bind('<Button-1>', lambda e: dialog.destroy())
        cancel_label.bind('<Button-1>', lambda e: dialog.destroy())
        cancel_frame.bind('<Enter>', cancel_enter)
        cancel_frame.bind('<Leave>', cancel_leave)
        cancel_label.bind('<Enter>', cancel_enter)
        cancel_label.bind('<Leave>', cancel_leave)
        
        # Центрируем диалог после создания всех элементов
        dialog.update_idletasks()
        width = dialog.winfo_reqwidth()
        height = dialog.winfo_reqheight()
        x = (dialog.winfo_screenwidth() - width) // 2
        y = (dialog.winfo_screenheight() - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.minsize(400, height)
    
    def do_booking(self, slot):
        """Выполнить запись"""
        appointment_datetime = datetime.fromisoformat(slot['datetime'])
        
        result = self.api.create_appointment(
            self.current_user['id'],
            self.selected_master['id'],
            self.selected_service['id'],
            appointment_datetime
        )
        
        if result["success"]:
            messagebox.showinfo("Успех", "✅ Запись успешно создана!")
            self.load_active_appointments()
            self.load_history()
            self.show_booking_choice()
        else:
            messagebox.showerror("Ошибка", result["error"])
    
    def create_appointments_tab(self, parent):
        """Создать вкладку записей"""
        frame = tk.Frame(parent, bg=self.colors['white'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        header = tk.Frame(frame, bg=self.colors['white'])
        header.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header, text="📋 Мои записи", font=("Arial", 16, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(side=tk.LEFT)
        
        refresh_btn = self.create_styled_button(header, "🔄 Обновить", self.load_active_appointments, 'secondary')
        refresh_btn.pack(side=tk.RIGHT)
        
        # Контейнер с синей рамкой для таблицы (не expand, чтобы таблица не растягивалась)
        table_border = tk.Frame(frame, bg=self.colors['primary'], padx=1, pady=1)
        table_border.pack(fill=tk.X, anchor=tk.N)
        
        table_inner = tk.Frame(table_border, bg='white')
        table_inner.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "date", "time", "master", "service", "status")
        self.appointments_tree = ttk.Treeview(table_inner, columns=columns, show="headings", height=15)
        self.appointments_tree.tag_configure('white_bg', background='white')
        
        self.appointments_tree.heading("id", text="ID")
        self.appointments_tree.heading("date", text="Дата")
        self.appointments_tree.heading("time", text="Время")
        self.appointments_tree.heading("master", text="Мастер")
        self.appointments_tree.heading("service", text="Услуга")
        self.appointments_tree.heading("status", text="Статус")
        
        self.appointments_tree.column("id", width=50, anchor="center")
        self.appointments_tree.column("date", width=100, anchor="center")
        self.appointments_tree.column("time", width=80, anchor="center")
        self.appointments_tree.column("master", width=150, anchor="w")
        self.appointments_tree.column("service", width=200, anchor="w")
        self.appointments_tree.column("status", width=100, anchor="center")
        
        scrollbar = tk.Scrollbar(table_inner, orient=tk.VERTICAL, command=self.appointments_tree.yview,
                                bg='white', troughcolor='white')
        self.appointments_tree.configure(yscrollcommand=scrollbar.set)
        
        self.appointments_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        btn_frame = tk.Frame(frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        cancel_btn = self.create_styled_button(btn_frame, "❌ Отменить запись", self.cancel_selected_appointment, 'danger')
        cancel_btn.pack(side=tk.LEFT)
        
        # Белый фон для оставшегося пространства
        spacer = tk.Frame(frame, bg=self.colors['white'])
        spacer.pack(fill=tk.BOTH, expand=True)
        
        self.load_active_appointments()
    
    def load_active_appointments(self):
        """Загрузить активные записи"""
        if not hasattr(self, 'appointments_tree'):
            return
        if not self.appointments_tree.winfo_exists():
            return
            
        for item in self.appointments_tree.get_children():
            self.appointments_tree.delete(item)
        
        result = self.api.get_appointments(self.current_user['id'], upcoming_only=True)
        
        if result["success"]:
            appointments = result["data"]
            for apt in appointments:
                if apt['status'] == 'scheduled':
                    dt = datetime.fromisoformat(apt['appointment_datetime'].replace('Z', '+00:00'))
                    status_text = "🟢 Активна"
                    
                    self.appointments_tree.insert("", "end", values=(
                        apt['id'],
                        dt.strftime("%d.%m.%Y"),
                        dt.strftime("%H:%M"),
                        apt['master']['full_name'],
                        apt['service']['name'],
                        status_text
                    ), tags=(str(apt['id']),))
    
    def cancel_selected_appointment(self):
        """Отменить выбранную запись"""
        selection = self.appointments_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите запись для отмены")
            return
        
        item = self.appointments_tree.item(selection[0])
        appointment_id = int(item["tags"][0])
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите отменить запись?"):
            result = self.api.cancel_appointment(appointment_id, self.current_user['id'])
            if result["success"]:
                messagebox.showinfo("Успех", "Запись отменена")
                self.load_active_appointments()
                self.load_history()
            else:
                messagebox.showerror("Ошибка", result["error"])
    
    def create_history_tab(self, parent):
        """Создать вкладку истории"""
        frame = tk.Frame(parent, bg=self.colors['white'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        header = tk.Frame(frame, bg=self.colors['white'])
        header.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header, text="📜 История записей", font=("Arial", 16, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(side=tk.LEFT)
        
        refresh_btn = self.create_styled_button(header, "🔄 Обновить", self.load_history, 'secondary')
        refresh_btn.pack(side=tk.RIGHT)
        
        # Контейнер с синей рамкой для таблицы (не expand, чтобы таблица не растягивалась)
        table_border = tk.Frame(frame, bg=self.colors['primary'], padx=1, pady=1)
        table_border.pack(fill=tk.X, anchor=tk.N)
        
        table_inner = tk.Frame(table_border, bg='white')
        table_inner.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "date", "time", "master", "service", "status")
        self.history_tree = ttk.Treeview(table_inner, columns=columns, show="headings", height=18)
        self.history_tree.tag_configure('white_bg', background='white')
        
        self.history_tree.heading("id", text="ID")
        self.history_tree.heading("date", text="Дата")
        self.history_tree.heading("time", text="Время")
        self.history_tree.heading("master", text="Мастер")
        self.history_tree.heading("service", text="Услуга")
        self.history_tree.heading("status", text="Статус")
        
        self.history_tree.column("id", width=50, anchor="center")
        self.history_tree.column("date", width=100, anchor="center")
        self.history_tree.column("time", width=80, anchor="center")
        self.history_tree.column("master", width=150, anchor="w")
        self.history_tree.column("service", width=200, anchor="w")
        self.history_tree.column("status", width=100, anchor="center")
        
        scrollbar = tk.Scrollbar(table_inner, orient=tk.VERTICAL, command=self.history_tree.yview,
                                bg='white', troughcolor='white')
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Белый фон для оставшегося пространства
        spacer = tk.Frame(frame, bg=self.colors['white'])
        spacer.pack(fill=tk.BOTH, expand=True)
        
        self.load_history()
    
    def load_history(self):
        """Загрузить историю записей"""
        if not hasattr(self, 'history_tree'):
            return
        if not self.history_tree.winfo_exists():
            return
            
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        result = self.api.get_appointments(self.current_user['id'])
        
        if result["success"]:
            appointments = result["data"]
            for apt in appointments:
                dt = datetime.fromisoformat(apt['appointment_datetime'].replace('Z', '+00:00'))
                
                status_map = {
                    'scheduled': '🟢 Активна',
                    'completed': '✅ Завершена',
                    'canceled': '❌ Отменена'
                }
                status_text = status_map.get(apt['status'], apt['status'])
                
                self.history_tree.insert("", "end", values=(
                    apt['id'],
                    dt.strftime("%d.%m.%Y"),
                    dt.strftime("%H:%M"),
                    apt['master']['full_name'],
                    apt['service']['name'],
                    status_text
                ))
    
    def show_admin_interface(self):
        """Показать интерфейс администратора"""
        self.clear_root()
        
        header = tk.Frame(self.root, bg=self.colors['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=self.colors['primary'])
        header_content.pack(fill=tk.BOTH, expand=True, padx=20)
        
        tk.Label(header_content, text="🔧 Панель администратора", font=("Arial", 16, "bold"),
                bg=self.colors['primary'], fg=self.colors['white']).pack(side=tk.LEFT, pady=15)
        
        tk.Label(header_content, text="BeautyPro", font=("Arial", 12),
                bg=self.colors['primary'], fg=self.colors['white']).pack(side=tk.LEFT, padx=20, pady=15)
        
        logout_btn = self.create_button(header_content, "  Выйти  ", self.logout,
                                       bg=self.colors['white'], fg=self.colors['primary'],
                                       font=("Arial", 10, "bold"), padx=12, pady=6)
        logout_btn.pack(side=tk.RIGHT, pady=15)
        
        # Контейнер для notebook с белым фоном
        notebook_container = tk.Frame(self.root, bg=self.colors['white'])
        notebook_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        notebook = ttk.Notebook(notebook_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Используем tk.Frame вместо ttk.Frame для точного контроля цвета
        masters_tab = tk.Frame(notebook, bg=self.colors['white'])
        notebook.add(masters_tab, text="👨‍🎨 Мастера")
        self.create_masters_management_tab(masters_tab)
        
        services_tab = tk.Frame(notebook, bg=self.colors['white'])
        notebook.add(services_tab, text="✂️ Услуги")
        self.create_services_view_tab(services_tab)
    
    def create_masters_management_tab(self, parent):
        """Создать вкладку управления мастерами"""
        main_frame = tk.Frame(parent, bg=self.colors['white'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        header = tk.Frame(main_frame, bg=self.colors['white'])
        header.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header, text="👨‍🎨 Управление мастерами", font=("Arial", 16, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(side=tk.LEFT)
        
        btn_frame = tk.Frame(main_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Левая группа кнопок
        left_btns = tk.Frame(btn_frame, bg=self.colors['white'])
        left_btns.pack(side=tk.LEFT)
        
        add_btn = self.create_button(left_btns, "  Добавить  ", self.show_add_master_dialog)
        add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        edit_btn = self.create_button(left_btns, "  Редактировать  ", self.show_edit_master_dialog)
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_btn = self.create_button(left_btns, "  Удалить  ", self.delete_selected_master,
                                       bg=self.colors['danger'])
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        services_btn = self.create_button(left_btns, "  Назначить услуги  ", self.show_assign_services_dialog)
        services_btn.pack(side=tk.LEFT)
        
        # Кнопка обновить справа
        refresh_btn = self.create_button(btn_frame, "  Обновить  ", self.load_masters_list)
        refresh_btn.pack(side=tk.RIGHT)
        
        content_frame = tk.Frame(main_frame, bg=self.colors['white'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        left_frame = tk.Frame(content_frame, bg=self.colors['white'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Контейнер с синей рамкой для таблицы (не expand, чтобы таблица не растягивалась)
        table_border = tk.Frame(left_frame, bg=self.colors['primary'], padx=1, pady=1)
        table_border.pack(fill=tk.X, anchor=tk.N)
        
        table_inner = tk.Frame(table_border, bg='white')
        table_inner.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "name", "profession", "contact", "services")
        self.masters_tree = ttk.Treeview(table_inner, columns=columns, show="headings", height=18)
        self.masters_tree.tag_configure('white_bg', background='white')
        
        self.masters_tree.heading("id", text="ID")
        self.masters_tree.heading("name", text="ФИО")
        self.masters_tree.heading("profession", text="Профессия")
        self.masters_tree.heading("contact", text="Контакт")
        self.masters_tree.heading("services", text="Услуги")
        
        self.masters_tree.column("id", width=80, anchor="center")
        self.masters_tree.column("name", width=200, anchor="w")
        self.masters_tree.column("profession", width=180, anchor="w")
        self.masters_tree.column("contact", width=180, anchor="w")
        self.masters_tree.column("services", width=100, anchor="center")
        
        scrollbar = tk.Scrollbar(table_inner, orient=tk.VERTICAL, command=self.masters_tree.yview,
                                bg='white', troughcolor='white')
        self.masters_tree.configure(yscrollcommand=scrollbar.set)
        
        self.masters_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.masters_tree.bind('<<TreeviewSelect>>', self.on_master_select)
        
        # Белый фон для оставшегося пространства под таблицей
        spacer = tk.Frame(left_frame, bg=self.colors['white'])
        spacer.pack(fill=tk.BOTH, expand=True)
        
        right_frame = tk.Frame(content_frame, bg=self.colors['white'], width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        right_frame.pack_propagate(False)
        
        tk.Label(right_frame, text="✂️ Услуги мастера", font=("Arial", 12, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W, pady=(0, 10))
        
        list_container = tk.Frame(right_frame, bg=self.colors['white'], padx=5, pady=5,
                                 highlightbackground=self.colors['primary'], highlightthickness=1)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.master_services_list = tk.Listbox(list_container, height=20, width=30,
                                               font=("Arial", 10), bg=self.colors['white'],
                                               fg=self.colors['text'],
                                               selectbackground=self.colors['primary'],
                                               selectforeground=self.colors['white'],
                                               relief='flat', highlightthickness=0)
        self.master_services_list.pack(fill=tk.BOTH, expand=True)
        
        self.load_masters_list()
    
    def load_masters_list(self):
        """Загрузить список мастеров"""
        for item in self.masters_tree.get_children():
            self.masters_tree.delete(item)
        
        result = self.api.get_masters(active_only=False)
        
        if result["success"]:
            self.masters_data = result["data"]
            for master in self.masters_data:
                profession = master.get('profession', {}).get('name', '') if master.get('profession') else ''
                services_count = len(master.get('services', []))
                
                self.masters_tree.insert("", "end", values=(
                    master['id'],
                    master['full_name'],
                    profession,
                    master.get('contact_info', ''),
                    f"{services_count} услуг"
                ), tags=(str(master['id']),))
    
    def on_master_select(self, event):
        """Обработчик выбора мастера"""
        self.master_services_list.delete(0, tk.END)
        
        selection = self.masters_tree.selection()
        if not selection:
            return
        
        item = self.masters_tree.item(selection[0])
        master_id = int(item["tags"][0])
        
        master = next((m for m in self.masters_data if m['id'] == master_id), None)
        if master:
            for service in master.get('services', []):
                self.master_services_list.insert(tk.END, f"✂️ {service['name']} - {service['price']} руб.")
    
    def show_add_master_dialog(self):
        """Показать диалог добавления мастера"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить мастера")
        dialog.geometry("450x400")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['white'])
        
        header = tk.Frame(dialog, bg=self.colors['secondary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="➕ Добавить мастера", font=("Arial", 16, "bold"),
                bg=self.colors['secondary'], fg=self.colors['white']).pack(pady=15)
        
        frame = tk.Frame(dialog, bg=self.colors['white'], padx=25, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="👤 ФИО:", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        name_entry = tk.Entry(frame, width=40, font=("Arial", 11), relief="solid", bd=2,
                             bg="#0066FF", fg="white", insertbackground="white",
                             highlightthickness=2, highlightcolor="#0066FF", highlightbackground="#0066FF")
        name_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)
        
        tk.Label(frame, text="💼 Профессия:", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        profession_var = tk.StringVar()
        
        result = self.api.get_professions()
        professions = []
        profession_names = []
        if result["success"]:
            professions = result["data"]
            profession_names = [p["name"] for p in professions]
        
        prof_container, _ = self.create_white_dropdown(frame, profession_var, profession_names)
        prof_container.pack(fill=tk.X, pady=(5, 15))
        
        tk.Label(frame, text="📞 Контакт:", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        contact_entry = tk.Entry(frame, width=40, font=("Arial", 11), relief="solid", bd=2,
                                bg="#0066FF", fg="white", insertbackground="white",
                                highlightthickness=2, highlightcolor="#0066FF", highlightbackground="#0066FF")
        contact_entry.pack(fill=tk.X, pady=(5, 20), ipady=8)
        
        def save():
            name = name_entry.get().strip()
            profession_name = profession_var.get()
            contact = contact_entry.get().strip()
            
            if not name or not profession_name:
                messagebox.showwarning("Внимание", "Заполните обязательные поля")
                return
            
            profession_id = next((p["id"] for p in professions if p["name"] == profession_name), None)
            
            result = self.api.create_master(name, profession_id, contact)
            
            if result["success"]:
                messagebox.showinfo("Успех", "Мастер добавлен!")
                dialog.destroy()
                self.load_masters_list()
            else:
                messagebox.showerror("Ошибка", result["error"])
        
        btn_frame = tk.Frame(frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X)
        
        save_btn = self.create_styled_button(btn_frame, "💾 Сохранить", save, 'accent')
        save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=8)
        
        cancel_btn = self.create_styled_button(btn_frame, "❌ Отмена", dialog.destroy, 'secondary')
        cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=8)
    
    def show_edit_master_dialog(self):
        """Показать диалог редактирования мастера"""
        selection = self.masters_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите мастера")
            return
        
        item = self.masters_tree.item(selection[0])
        master_id = int(item["tags"][0])
        master = next((m for m in self.masters_data if m['id'] == master_id), None)
        
        if not master:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать мастера")
        dialog.geometry("450x400")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['white'])
        
        header = tk.Frame(dialog, bg=self.colors['secondary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="✏️ Редактировать мастера", font=("Arial", 16, "bold"),
                bg=self.colors['secondary'], fg=self.colors['white']).pack(pady=15)
        
        frame = tk.Frame(dialog, bg=self.colors['white'], padx=25, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="👤 ФИО:", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        name_entry = tk.Entry(frame, width=40, font=("Arial", 11), relief="solid", bd=2,
                             bg="#0066FF", fg="white", insertbackground="white",
                             highlightthickness=2, highlightcolor="#0066FF", highlightbackground="#0066FF")
        name_entry.insert(0, master['full_name'])
        name_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)
        
        tk.Label(frame, text="💼 Профессия:", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        profession_var = tk.StringVar()
        
        result = self.api.get_professions()
        professions = []
        profession_names = []
        if result["success"]:
            professions = result["data"]
            profession_names = [p["name"] for p in professions]
            if master.get('profession'):
                profession_var.set(master['profession']['name'])
        
        prof_container, _ = self.create_white_dropdown(frame, profession_var, profession_names)
        prof_container.pack(fill=tk.X, pady=(5, 15))
        
        tk.Label(frame, text="📞 Контакт:", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        contact_entry = tk.Entry(frame, width=40, font=("Arial", 11), relief="solid", bd=2,
                                bg="#0066FF", fg="white", insertbackground="white",
                                highlightthickness=2, highlightcolor="#0066FF", highlightbackground="#0066FF")
        contact_entry.insert(0, master.get('contact_info', ''))
        contact_entry.pack(fill=tk.X, pady=(5, 20), ipady=8)
        
        def save():
            name = name_entry.get().strip()
            profession_name = profession_var.get()
            contact = contact_entry.get().strip()
            
            profession_id = next((p["id"] for p in professions if p["name"] == profession_name), None)
            
            result = self.api.update_master(master_id, name, profession_id, contact)
            
            if result["success"]:
                messagebox.showinfo("Успех", "Мастер обновлён!")
                dialog.destroy()
                self.load_masters_list()
            else:
                messagebox.showerror("Ошибка", result["error"])
        
        btn_frame = tk.Frame(frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X)
        
        save_btn = self.create_styled_button(btn_frame, "💾 Сохранить", save, 'accent')
        save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=8)
        
        cancel_btn = self.create_styled_button(btn_frame, "❌ Отмена", dialog.destroy, 'secondary')
        cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=8)
    
    def delete_selected_master(self):
        """Удалить выбранного мастера"""
        selection = self.masters_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите мастера")
            return
        
        item = self.masters_tree.item(selection[0])
        master_id = int(item["tags"][0])
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить мастера?"):
            result = self.api.delete_master(master_id)
            if result["success"]:
                messagebox.showinfo("Успех", "Мастер удалён")
                self.load_masters_list()
            else:
                messagebox.showerror("Ошибка", result["error"])
    
    def show_assign_services_dialog(self):
        """Показать диалог назначения услуг мастеру"""
        selection = self.masters_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите мастера")
            return
        
        item = self.masters_tree.item(selection[0])
        master_id = int(item["tags"][0])
        master = next((m for m in self.masters_data if m['id'] == master_id), None)
        
        if not master:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Услуги мастера: {master['full_name']}")
        dialog.geometry("500x550")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['white'])
        
        header = tk.Frame(dialog, bg=self.colors['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text=f"✂️ Услуги: {master['full_name']}", font=("Arial", 14, "bold"),
                bg=self.colors['primary'], fg=self.colors['white']).pack(pady=15)
        
        frame = tk.Frame(dialog, bg=self.colors['white'], padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Выберите услуги:", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W, pady=(0, 10))
        
        result = self.api.get_services()
        services = result["data"] if result["success"] else []
        
        current_service_ids = [s['id'] for s in master.get('services', [])]
        
        # Контейнер для canvas и scrollbar с рамкой
        canvas_container = tk.Frame(frame, bg=self.colors['primary'], padx=1, pady=1)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        inner_container = tk.Frame(canvas_container, bg=self.colors['white'])
        inner_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(inner_container, bg=self.colors['white'], highlightthickness=0, height=350)
        scrollbar = tk.Scrollbar(inner_container, orient="vertical", command=canvas.yview, 
                                bg=self.colors['white'], troughcolor=self.colors['light'],
                                activebackground=self.colors['primary'])
        scrollable_frame = tk.Frame(canvas, bg=self.colors['white'])
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=430)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        service_vars = {}
        checkbuttons = []
        
        for service in services:
            var = tk.BooleanVar(value=service['id'] in current_service_ids)
            service_vars[service['id']] = var
            
            cb_frame = tk.Frame(scrollable_frame, bg=self.colors['white'], pady=3)
            cb_frame.pack(fill=tk.X)
            
            cb = tk.Checkbutton(cb_frame, text=f"✂️ {service['name']}", font=("Arial", 10),
                               variable=var, bg=self.colors['white'], fg=self.colors['text'],
                               activebackground=self.colors['white'], selectcolor=self.colors['white'])
            cb.pack(side=tk.LEFT)
            checkbuttons.append(cb)
            
            price_label = tk.Label(cb_frame, text=f"💰 {service['price']} руб. • ⏱️ {service['duration_minutes']} мин.",
                    font=("Arial", 9), bg=self.colors['white'], fg=self.colors['gray'])
            price_label.pack(side=tk.RIGHT)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Обновляем scrollregion после создания всех элементов
        scrollable_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Привязка скролла колесом мыши
        self.bind_mousewheel(canvas, scrollable_frame, dialog)
        
        def save():
            selected_ids = [sid for sid, var in service_vars.items() if var.get()]
            result = self.api.update_master(master_id, service_ids=selected_ids)
            
            if result["success"]:
                messagebox.showinfo("Успех", f"✅ Услуги успешно назначены! ({len(selected_ids)} услуг)")
                dialog.destroy()
                self.load_masters_list()
            else:
                messagebox.showerror("Ошибка", result["error"])
        
        btn_frame = tk.Frame(frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        save_btn = self.create_styled_button(btn_frame, "💾 Сохранить", save, 'accent')
        save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=8)
        
        cancel_btn = self.create_styled_button(btn_frame, "❌ Отмена", dialog.destroy, 'secondary')
        cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=8)
    
    def create_services_view_tab(self, parent):
        """Создать вкладку управления услугами"""
        self.services_tab_frame = tk.Frame(parent, bg=self.colors['white'], padx=20, pady=20)
        self.services_tab_frame.pack(fill=tk.BOTH, expand=True)
        
        header = tk.Frame(self.services_tab_frame, bg=self.colors['white'])
        header.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header, text="✂️ Управление услугами", font=("Arial", 16, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(side=tk.LEFT)
        
        self.services_count_label = tk.Label(header, text="", font=("Arial", 11),
                                            bg=self.colors['white'], fg=self.colors['gray'])
        self.services_count_label.pack(side=tk.LEFT, padx=15)
        
        btn_frame = tk.Frame(self.services_tab_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Левая группа кнопок
        left_btns = tk.Frame(btn_frame, bg=self.colors['white'])
        left_btns.pack(side=tk.LEFT)
        
        add_btn = self.create_button(left_btns, "  Добавить  ", self.show_add_service_dialog)
        add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        edit_btn = self.create_button(left_btns, "  Редактировать  ", self.show_edit_service_dialog)
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_btn = self.create_button(left_btns, "  Удалить  ", self.delete_selected_service,
                                       bg=self.colors['danger'])
        delete_btn.pack(side=tk.LEFT)
        
        # Кнопка обновить справа
        refresh_btn = self.create_button(btn_frame, "  Обновить  ", self.load_services_list)
        refresh_btn.pack(side=tk.RIGHT)
        
        self.services_stats_frame = tk.Frame(self.services_tab_frame, bg=self.colors['white'], padx=15, pady=10)
        self.services_stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Контейнер с синей рамкой для таблицы (не expand, чтобы таблица не растягивалась)
        table_border = tk.Frame(self.services_tab_frame, bg=self.colors['primary'], padx=1, pady=1)
        table_border.pack(fill=tk.X, anchor=tk.N)
        
        table_container = tk.Frame(table_border, bg='white')
        table_container.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "name", "profession", "price", "duration")
        self.services_tree = ttk.Treeview(table_container, columns=columns, show="headings", height=18)
        self.services_tree.tag_configure('white_bg', background='white')
        
        self.services_tree.heading("id", text="ID")
        self.services_tree.heading("name", text="Название")
        self.services_tree.heading("profession", text="Профессия")
        self.services_tree.heading("price", text="Цена")
        self.services_tree.heading("duration", text="Время")
        
        self.services_tree.column("id", width=80, anchor="center")
        self.services_tree.column("name", width=350, anchor="w")
        self.services_tree.column("profession", width=200, anchor="w")
        self.services_tree.column("price", width=120, anchor="e")
        self.services_tree.column("duration", width=120, anchor="e")
        
        scrollbar = tk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.services_tree.yview,
                                bg='white', troughcolor='white')
        self.services_tree.configure(yscrollcommand=scrollbar.set)
        
        self.services_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Белый фон для оставшегося пространства
        spacer = tk.Frame(self.services_tab_frame, bg=self.colors['white'])
        spacer.pack(fill=tk.BOTH, expand=True)
        
        self.load_services_list()
    
    def load_services_list(self):
        """Загрузить список услуг"""
        for item in self.services_tree.get_children():
            self.services_tree.delete(item)
        
        result = self.api.get_services()
        
        if result["success"]:
            self.services_data = result["data"]
            
            self.services_count_label.config(text=f"Всего: {len(self.services_data)}")
            
            for widget in self.services_stats_frame.winfo_children():
                widget.destroy()
            
            prof_stats = {}
            for service in self.services_data:
                prof = service["profession"]["name"] if service.get("profession") else "Другое"
                if prof not in prof_stats:
                    prof_stats[prof] = 0
                prof_stats[prof] += 1
            
            tk.Label(self.services_stats_frame, text=f"Всего услуг: {len(self.services_data)}", 
                    font=("Arial", 11, "bold"), bg=self.colors['white'], fg=self.colors['text']).pack(side=tk.LEFT)
            
            for prof, count in prof_stats.items():
                tk.Label(self.services_stats_frame, text=f"  •  {prof}: {count}",
                        font=("Arial", 10), bg=self.colors['white'], fg=self.colors['gray']).pack(side=tk.LEFT)
            
            for service in self.services_data:
                profession_name = service["profession"]["name"] if service.get("profession") else ""
                self.services_tree.insert("", "end", values=(
                    service["id"],
                    service["name"],
                    profession_name,
                    f"{service['price']} руб.",
                    f"{service['duration_minutes']} мин."
                ), tags=(str(service["id"]),))
    
    def show_add_service_dialog(self):
        """Показать диалог добавления услуги"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить услугу")
        dialog.geometry("450x450")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['white'])
        
        header = tk.Frame(dialog, bg=self.colors['secondary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="➕ Добавить услугу", font=("Arial", 16, "bold"),
                bg=self.colors['secondary'], fg=self.colors['white']).pack(pady=15)
        
        frame = tk.Frame(dialog, bg=self.colors['white'], padx=25, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="✂️ Название услуги:", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        name_entry = tk.Entry(frame, width=40, font=("Arial", 11), relief="solid", bd=2,
                             bg="#0066FF", fg="white", insertbackground="white",
                             highlightthickness=2, highlightcolor="#0066FF", highlightbackground="#0066FF")
        name_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)
        
        tk.Label(frame, text="💼 Профессия:", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        profession_var = tk.StringVar()
        
        result = self.api.get_professions()
        professions = []
        profession_names = []
        if result["success"]:
            professions = result["data"]
            profession_names = [p["name"] for p in professions]
        
        prof_container, _ = self.create_white_dropdown(frame, profession_var, profession_names)
        prof_container.pack(fill=tk.X, pady=(5, 15))
        
        tk.Label(frame, text="💰 Цена (руб.):", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        price_entry = tk.Entry(frame, width=40, font=("Arial", 11), relief="solid", bd=2,
                              bg="#0066FF", fg="white", insertbackground="white",
                              highlightthickness=2, highlightcolor="#0066FF", highlightbackground="#0066FF")
        price_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)
        
        tk.Label(frame, text="⏱️ Длительность (мин.):", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        duration_entry = tk.Entry(frame, width=40, font=("Arial", 11), relief="solid", bd=2,
                                 bg="#0066FF", fg="white", insertbackground="white",
                                 highlightthickness=2, highlightcolor="#0066FF", highlightbackground="#0066FF")
        duration_entry.pack(fill=tk.X, pady=(5, 20), ipady=8)
        
        def save():
            name = name_entry.get().strip()
            profession_name = profession_var.get()
            price_str = price_entry.get().strip()
            duration_str = duration_entry.get().strip()
            
            if not name or not profession_name or not price_str or not duration_str:
                messagebox.showwarning("Внимание", "Заполните все поля")
                return
            
            try:
                price = float(price_str)
                duration = int(duration_str)
            except ValueError:
                messagebox.showwarning("Внимание", "Цена и длительность должны быть числами")
                return
            
            profession_id = next((p["id"] for p in professions if p["name"] == profession_name), None)
            
            result = self.api.create_service(name, price, duration, profession_id)
            
            if result["success"]:
                messagebox.showinfo("Успех", "✅ Услуга успешно добавлена!")
                dialog.destroy()
                self.load_services_list()
            else:
                messagebox.showerror("Ошибка", result["error"])
        
        btn_frame = tk.Frame(frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X)
        
        save_btn = self.create_styled_button(btn_frame, "💾 Сохранить", save, 'accent')
        save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=8)
        
        cancel_btn = self.create_styled_button(btn_frame, "❌ Отмена", dialog.destroy, 'secondary')
        cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=8)
    
    def show_edit_service_dialog(self):
        """Показать диалог редактирования услуги"""
        selection = self.services_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите услугу")
            return
        
        item = self.services_tree.item(selection[0])
        service_id = int(item["tags"][0])
        service = next((s for s in self.services_data if s["id"] == service_id), None)
        
        if not service:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать услугу")
        dialog.geometry("450x450")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['white'])
        
        header = tk.Frame(dialog, bg=self.colors['secondary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="✏️ Редактировать услугу", font=("Arial", 16, "bold"),
                bg=self.colors['secondary'], fg=self.colors['white']).pack(pady=15)
        
        frame = tk.Frame(dialog, bg=self.colors['white'], padx=25, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="✂️ Название услуги:", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        name_entry = tk.Entry(frame, width=40, font=("Arial", 11), relief="solid", bd=2,
                             bg="#0066FF", fg="white", insertbackground="white",
                             highlightthickness=2, highlightcolor="#0066FF", highlightbackground="#0066FF")
        name_entry.insert(0, service["name"])
        name_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)
        
        tk.Label(frame, text="💼 Профессия:", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        profession_var = tk.StringVar()
        
        result = self.api.get_professions()
        professions = []
        profession_names = []
        if result["success"]:
            professions = result["data"]
            profession_names = [p["name"] for p in professions]
            if service.get("profession"):
                profession_var.set(service["profession"]["name"])
        
        prof_container, _ = self.create_white_dropdown(frame, profession_var, profession_names)
        prof_container.pack(fill=tk.X, pady=(5, 15))
        
        tk.Label(frame, text="💰 Цена (руб.):", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        price_entry = tk.Entry(frame, width=40, font=("Arial", 11), relief="solid", bd=2,
                              bg="#0066FF", fg="white", insertbackground="white",
                              highlightthickness=2, highlightcolor="#0066FF", highlightbackground="#0066FF")
        price_entry.insert(0, str(service["price"]))
        price_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)
        
        tk.Label(frame, text="⏱️ Длительность (мин.):", font=("Arial", 11, "bold"),
                bg=self.colors['white'], fg=self.colors['primary']).pack(anchor=tk.W)
        duration_entry = tk.Entry(frame, width=40, font=("Arial", 11), relief="solid", bd=2,
                                 bg="#0066FF", fg="white", insertbackground="white",
                                 highlightthickness=2, highlightcolor="#0066FF", highlightbackground="#0066FF")
        duration_entry.insert(0, str(service["duration_minutes"]))
        duration_entry.pack(fill=tk.X, pady=(5, 20), ipady=8)
        
        def save():
            name = name_entry.get().strip()
            profession_name = profession_var.get()
            price_str = price_entry.get().strip()
            duration_str = duration_entry.get().strip()
            
            if not name:
                messagebox.showwarning("Внимание", "Введите название")
                return
            
            try:
                price = float(price_str) if price_str else None
                duration = int(duration_str) if duration_str else None
            except ValueError:
                messagebox.showwarning("Внимание", "Цена и длительность должны быть числами")
                return
            
            profession_id = next((p["id"] for p in professions if p["name"] == profession_name), None)
            
            result = self.api.update_service(service_id, name, price, duration, profession_id)
            
            if result["success"]:
                messagebox.showinfo("Успех", "✅ Услуга успешно обновлена!")
                dialog.destroy()
                self.load_services_list()
            else:
                messagebox.showerror("Ошибка", result["error"])
        
        btn_frame = tk.Frame(frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X)
        
        save_btn = self.create_styled_button(btn_frame, "💾 Сохранить", save, 'accent')
        save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=8)
        
        cancel_btn = self.create_styled_button(btn_frame, "❌ Отмена", dialog.destroy, 'secondary')
        cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=8)
    
    def delete_selected_service(self):
        """Удалить выбранную услугу"""
        selection = self.services_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите услугу")
            return
        
        item = self.services_tree.item(selection[0])
        service_id = int(item["tags"][0])
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту услугу?"):
            result = self.api.delete_service(service_id)
            if result["success"]:
                messagebox.showinfo("Успех", "Услуга удалена")
                self.load_services_list()
            else:
                messagebox.showerror("Ошибка", result["error"])


if __name__ == "__main__":
    root = tk.Tk()
    app = BeautyProApp(root)
    root.mainloop()
