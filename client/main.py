"""
BeautyPro Desktop Application
Современное приложение с GUI на PySide6
"""
import sys
import os
from datetime import datetime, date, timedelta

# Поддержка High DPI для Windows (до импорта Qt)
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFrame, QScrollArea, QGridLayout,
    QStackedWidget, QTabWidget, QMessageBox, QDialog, QComboBox,
    QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView, QListWidget,
    QListWidgetItem, QCheckBox, QSizePolicy, QSpacerItem, QCalendarWidget
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QDate
from PySide6.QtGui import QFont, QColor, QPalette, QIcon, QFontDatabase

from client.api_client import BeautyProAPI


class Colors:
    """Современная цветовая палитра приложения"""
    # Основные цвета - насыщенный синий градиент
    PRIMARY = "#4F46E5"           # Indigo-600
    PRIMARY_DARK = "#4338CA"      # Indigo-700
    PRIMARY_LIGHT = "#EEF2FF"     # Indigo-50
    PRIMARY_GRADIENT_START = "#6366F1"  # Indigo-500
    PRIMARY_GRADIENT_END = "#4F46E5"    # Indigo-600
    
    # Фоны
    WHITE = "#FFFFFF"
    BACKGROUND = "#F8FAFC"        # Slate-50 - очень светлый
    SURFACE = "#FFFFFF"
    
    # Текст
    TEXT = "#0F172A"              # Slate-900 - глубокий тёмный
    TEXT_SECONDARY = "#64748B"    # Slate-500
    TEXT_MUTED = "#94A3B8"        # Slate-400
    
    # Акцентные цвета
    DANGER = "#EF4444"            # Red-500
    DANGER_LIGHT = "#FEF2F2"      # Red-50
    SUCCESS = "#10B981"           # Emerald-500
    SUCCESS_LIGHT = "#ECFDF5"     # Emerald-50
    WARNING = "#F59E0B"           # Amber-500
    
    # Границы и разделители
    BORDER = "#E2E8F0"            # Slate-200
    BORDER_LIGHT = "#F1F5F9"      # Slate-100
    
    # Карточки и hover
    CARD = "#FFFFFF"
    CARD_HOVER = "#F8FAFC"
    HOVER = "#EEF2FF"             # Indigo-50
    
    # Тени (для справки в стилях)
    SHADOW = "rgba(15, 23, 42, 0.08)"
    SHADOW_HOVER = "rgba(15, 23, 42, 0.12)"


class Styles:
    """Глобальные стили приложения"""
    
    MAIN_STYLE = f"""
        QMainWindow, QWidget {{
            background-color: {Colors.BACKGROUND};
            font-family: 'Arial', 'Helvetica Neue', sans-serif;
        }}
        
        QLabel {{
            color: {Colors.TEXT};
            font-size: 14px;
        }}
        
        QLineEdit {{
            padding: 14px 18px;
            border: 2px solid {Colors.BORDER};
            border-radius: 12px;
            background-color: {Colors.WHITE};
            font-size: 15px;
            color: {Colors.TEXT};
            selection-background-color: {Colors.PRIMARY_LIGHT};
        }}
        
        QLineEdit:focus {{
            border-color: {Colors.PRIMARY};
            background-color: {Colors.WHITE};
        }}
        
        QLineEdit:hover {{
            border-color: {Colors.TEXT_MUTED};
        }}
        
        QLineEdit::placeholder {{
            color: {Colors.TEXT_MUTED};
        }}
        
        QPushButton {{
            padding: 14px 28px;
            border: none;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 600;
            letter-spacing: 0.3px;
        }}
        
        QPushButton#primary {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667EEA, stop:1 #764BA2);
            color: white;
            font-weight: bold;
            font-size: 14px;
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
        }}
        
        QPushButton#primary:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #5A67D8, stop:1 #6B46C1);
        }}
        
        QPushButton#primary:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4C51BF, stop:1 #553C9A);
        }}
        
        QPushButton#secondary {{
            background-color: {Colors.WHITE};
            color: {Colors.PRIMARY};
            border: 2px solid {Colors.PRIMARY};
        }}
        
        QPushButton#secondary:hover {{
            background-color: {Colors.PRIMARY_LIGHT};
            border-color: {Colors.PRIMARY_DARK};
        }}
        
        QPushButton#secondary:pressed {{
            background-color: {Colors.HOVER};
        }}
        
        QPushButton#danger {{
            background-color: {Colors.DANGER};
            color: white;
        }}
        
        QPushButton#danger:hover {{
            background-color: #DC2626;
        }}
        
        QPushButton#ghost {{
            background-color: transparent;
            color: {Colors.TEXT_SECONDARY};
            border: none;
        }}
        
        QPushButton#ghost:hover {{
            background-color: {Colors.BORDER_LIGHT};
            color: {Colors.TEXT};
        }}
        
        QPushButton#link {{
            background-color: transparent;
            color: {Colors.PRIMARY};
            font-weight: 600;
            padding: 4px 8px;
            border: none;
        }}
        
        QPushButton#link:hover {{
            color: {Colors.PRIMARY_DARK};
            text-decoration: underline;
        }}
        
        QTabWidget::pane {{
            border: none;
            background-color: {Colors.BACKGROUND};
            padding-top: 8px;
        }}
        
        QTabBar::tab {{
            padding: 14px 28px;
            margin-right: 8px;
            margin-top: 8px;
            background-color: {Colors.WHITE};
            border: none;
            border-radius: 12px 12px 0 0;
            font-weight: 600;
            font-size: 14px;
            color: {Colors.TEXT_SECONDARY};
        }}
        
        QTabBar::tab:selected {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {Colors.PRIMARY_GRADIENT_START}, stop:1 {Colors.PRIMARY_GRADIENT_END});
            color: white;
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {Colors.PRIMARY_LIGHT};
            color: {Colors.PRIMARY};
        }}
        
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        QScrollBar:vertical {{
            background-color: {Colors.BACKGROUND};
            width: 10px;
            border-radius: 5px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {Colors.BORDER};
            border-radius: 5px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {Colors.PRIMARY};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QComboBox {{
            padding: 12px 16px;
            border: 2px solid {Colors.BORDER};
            border-radius: 8px;
            background-color: {Colors.WHITE};
            font-size: 14px;
            color: {Colors.TEXT};
        }}
        
        QComboBox:focus {{
            border-color: {Colors.PRIMARY};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {Colors.WHITE};
            border: 2px solid {Colors.BORDER};
            border-radius: 8px;
            selection-background-color: {Colors.PRIMARY};
            selection-color: white;
            outline: none;
        }}
        
        QComboBox QAbstractItemView::item {{
            background-color: {Colors.WHITE};
            color: {Colors.TEXT};
            padding: 10px 16px;
            min-height: 30px;
        }}
        
        QComboBox QAbstractItemView::item:hover {{
            background-color: {Colors.PRIMARY_LIGHT};
            color: {Colors.PRIMARY};
        }}
        
        QComboBox QAbstractItemView::item:selected {{
            background-color: {Colors.PRIMARY};
            color: white;
        }}
        
        QTableWidget {{
            background-color: {Colors.WHITE};
            border: none;
            border-radius: 8px;
            gridline-color: {Colors.BORDER};
            color: {Colors.TEXT};
            alternate-background-color: {Colors.BACKGROUND};
        }}
        
        QTableWidget::item {{
            padding: 12px;
            border-bottom: 1px solid {Colors.BORDER};
            color: {Colors.TEXT};
            background-color: {Colors.WHITE};
        }}
        
        QTableWidget::item:selected {{
            background-color: {Colors.PRIMARY_LIGHT};
            color: {Colors.TEXT};
        }}
        
        QTableWidget::item:alternate {{
            background-color: {Colors.BACKGROUND};
            color: {Colors.TEXT};
        }}
        
        QHeaderView::section {{
            background-color: {Colors.PRIMARY};
            color: white;
            padding: 12px;
            border: none;
            font-weight: bold;
        }}
        
        QTableCornerButton::section {{
            background-color: {Colors.PRIMARY};
            border: none;
        }}
        
        QCalendarWidget {{
            background-color: {Colors.WHITE};
        }}
        
        QCalendarWidget QToolButton {{
            color: {Colors.TEXT};
            background-color: transparent;
            border: none;
            border-radius: 4px;
            padding: 8px;
            font-weight: bold;
        }}
        
        QCalendarWidget QToolButton:hover {{
            background-color: {Colors.PRIMARY_LIGHT};
        }}
        
        QCalendarWidget QMenu {{
            background-color: {Colors.WHITE};
        }}
        
        QCalendarWidget QSpinBox {{
            background-color: {Colors.WHITE};
            border: 1px solid {Colors.BORDER};
            border-radius: 4px;
        }}
        
        QCalendarWidget QAbstractItemView:enabled {{
            background-color: {Colors.WHITE};
            color: {Colors.TEXT};
            selection-background-color: {Colors.PRIMARY};
            selection-color: white;
        }}
        
        QMessageBox {{
            background-color: {Colors.WHITE};
        }}
        
        QMessageBox QLabel {{
            color: {Colors.TEXT};
            font-size: 14px;
            background: transparent;
        }}
        
        QMessageBox QLabel#qt_msgbox_label {{
            background: transparent;
        }}
        
        QMessageBox QLabel#qt_msgboxex_icon_label {{
            background: transparent;
        }}
        
        QMessageBox QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667EEA, stop:1 #764BA2);
            color: white;
            font-weight: bold;
            font-size: 13px;
            padding: 8px 16px;
            border-radius: 6px;
            border: none;
            min-width: 70px;
        }}
        
        QMessageBox QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #5A67D8, stop:1 #6B46C1);
        }}
        
        QMessageBox QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4C51BF, stop:1 #553C9A);
        }}
    """


class Card(QFrame):
    """Современная карточка с улучшенным дизайном"""
    clicked = Signal()
    
    def __init__(self, parent=None, clickable=False, padding=20):
        super().__init__(parent)
        self.clickable = clickable
        self._padding = padding
        
        # Базовый стиль карточки
        base_style = f"""
            Card {{
                background-color: {Colors.WHITE};
                border-radius: 16px;
                border: 1px solid {Colors.BORDER};
                padding: {padding}px;
            }}
        """
        
        if clickable:
            self.setStyleSheet(base_style + f"""
                Card:hover {{
                    border-color: {Colors.PRIMARY};
                    background-color: {Colors.PRIMARY_LIGHT};
                }}
            """)
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setStyleSheet(base_style)
    
    def mousePressEvent(self, event):
        if self.clickable:
            self.clicked.emit()
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        if self.clickable:
            # Добавляем эффект подъёма при наведении
            pass
        super().enterEvent(event)


class ModernButton(QPushButton):
    """Современная кнопка с улучшенным дизайном"""
    
    def __init__(self, text, style="primary", parent=None, icon=None):
        super().__init__(text, parent)
        self.setObjectName(style)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(48)
        
        # Добавляем иконку если передана
        if icon:
            self.setText(f"{icon}  {text}")
        
        # Устанавливаем шрифт
        font = self.font()
        font.setWeight(QFont.DemiBold)
        self.setFont(font)


class ModernInput(QLineEdit):
    """Современное поле ввода с улучшенным дизайном"""
    
    def __init__(self, placeholder="", parent=None, password=False):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        if password:
            self.setEchoMode(QLineEdit.Password)
        self.setMinimumHeight(48)


class BeautyProApp(QMainWindow):
    """Главное приложение BeautyPro"""
    
    def __init__(self):
        super().__init__()
        self.api = BeautyProAPI()
        self.current_user = None
        self.selected_master = None
        self.selected_service = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle("BeautyPro - Салон красоты")
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(Styles.MAIN_STYLE)
        
        # Центральный виджет со стеком экранов
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        
        # Создаем экраны
        self.login_screen = self.create_login_screen()
        self.register_screen = self.create_register_screen()
        self.client_screen = None
        self.admin_screen = None
        
        self.central_widget.addWidget(self.login_screen)
        self.central_widget.addWidget(self.register_screen)
        
        self.show_login()
    
    def show_login(self):
        """Показать экран входа"""
        self.central_widget.setCurrentWidget(self.login_screen)
    
    def show_register(self):
        """Показать экран регистрации"""
        self.central_widget.setCurrentWidget(self.register_screen)
    
    def styled_question(self, parent, title, message):
        """Создать стилизованный диалог подтверждения"""
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Question)
        
        # Добавляем кнопки
        yes_btn = msg_box.addButton("Да", QMessageBox.YesRole)
        no_btn = msg_box.addButton("Нет", QMessageBox.NoRole)
        
        # Стилизуем кнопки
        button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667EEA, stop:1 #764BA2);
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 24px;
                border-radius: 8px;
                border: none;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A67D8, stop:1 #6B46C1);
            }
        """
        yes_btn.setStyleSheet(button_style)
        no_btn.setStyleSheet(button_style.replace("#667EEA", "#6B7280").replace("#764BA2", "#4B5563").replace("#5A67D8", "#4B5563").replace("#6B46C1", "#374151"))
        
        msg_box.exec()
        return msg_box.clickedButton() == yes_btn
    
    def styled_info(self, parent, title, message):
        """Создать стилизованное информационное сообщение"""
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        
        ok_btn = msg_box.addButton("OK", QMessageBox.AcceptRole)
        ok_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667EEA, stop:1 #764BA2);
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 20px;
                border-radius: 6px;
                border: none;
                min-width: 70px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A67D8, stop:1 #6B46C1);
            }
        """)
        
        msg_box.exec()
    
    def create_login_screen(self):
        """Создать экран входа"""
        screen = QWidget()
        layout = QHBoxLayout(screen)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Левая панель с градиентом
        left_panel = QFrame()
        left_panel.setFixedWidth(480)
        left_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {Colors.PRIMARY_GRADIENT_START}, 
                    stop:0.5 {Colors.PRIMARY},
                    stop:1 {Colors.PRIMARY_DARK});
            }}
            QLabel {{
                color: white;
                background: transparent;
            }}
        """)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignCenter)
        left_layout.setSpacing(16)
        left_layout.setContentsMargins(40, 40, 40, 40)
        
        # Логотип - красивый круг
        logo_container = QLabel("✦")
        logo_container.setFont(QFont("Arial", 64))
        logo_container.setAlignment(Qt.AlignCenter)
        logo_container.setStyleSheet("font-size: 64px;")
        left_layout.addWidget(logo_container)
        
        title = QLabel("BeautyPro")
        title.setFont(QFont("Arial", 42, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)
        
        subtitle = QLabel("Салон красоты")
        subtitle.setFont(QFont("Arial", 18))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.85);")
        subtitle.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(subtitle)
        
        # Разделитель
        left_layout.addSpacing(30)
        
        slogan = QLabel("✨ Красота начинается здесь ✨")
        slogan.setFont(QFont("Arial", 14))
        slogan.setStyleSheet("font-style: italic; color: rgba(255, 255, 255, 0.7);")
        slogan.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(slogan)
        
        layout.addWidget(left_panel)
        
        # Правая панель (форма)
        right_panel = QFrame()
        right_panel.setStyleSheet(f"background-color: {Colors.WHITE};")
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignCenter)
        
        # Форма входа
        form_container = QWidget()
        form_container.setFixedWidth(420)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(8)
        
        welcome_label = QLabel("Добро пожаловать!")
        welcome_label.setFont(QFont("Arial", 32, QFont.Bold))
        welcome_label.setStyleSheet(f"color: {Colors.TEXT};")
        welcome_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(welcome_label)
        
        subtitle_label = QLabel("Войдите в свой аккаунт")
        subtitle_label.setFont(QFont("Arial", 15))
        subtitle_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin-bottom: 32px;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(subtitle_label)
        
        # Поля формы с иконками
        phone_label = QLabel("📱  Номер телефона")
        phone_label.setFont(QFont("Arial", 13, QFont.DemiBold))
        phone_label.setStyleSheet(f"color: {Colors.TEXT}; margin-top: 8px;")
        form_layout.addWidget(phone_label)
        
        self.login_phone = ModernInput("+7 (999) 123-45-67")
        form_layout.addWidget(self.login_phone)
        
        password_label = QLabel("🔒  Пароль")
        password_label.setFont(QFont("Arial", 13, QFont.DemiBold))
        password_label.setStyleSheet(f"color: {Colors.TEXT}; margin-top: 12px;")
        form_layout.addWidget(password_label)
        
        self.login_password = ModernInput("Введите пароль", password=True)
        form_layout.addWidget(self.login_password)
        
        # Отступ перед кнопкой
        form_layout.addSpacing(24)
        
        # Кнопка входа
        login_btn = ModernButton("Войти →", "primary")
        login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667EEA, stop:1 #764BA2);
                color: white;
                font-weight: bold;
                font-size: 15px;
                padding: 14px 28px;
                border-radius: 12px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A67D8, stop:1 #6B46C1);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4C51BF, stop:1 #553C9A);
            }
        """)
        login_btn.clicked.connect(self.do_login)
        form_layout.addWidget(login_btn)
        
        # Ссылка на регистрацию
        form_layout.addSpacing(16)
        
        reg_container = QWidget()
        reg_layout = QHBoxLayout(reg_container)
        reg_layout.setAlignment(Qt.AlignCenter)
        
        reg_text = QLabel("Нет аккаунта?")
        reg_text.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        reg_layout.addWidget(reg_text)
        
        reg_btn = ModernButton("Зарегистрироваться", "link")
        reg_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {Colors.PRIMARY};
                font-weight: bold;
                font-size: 14px;
                padding: 8px 16px;
                border: none;
                text-decoration: underline;
            }}
            QPushButton:hover {{
                color: {Colors.PRIMARY_DARK};
            }}
        """)
        reg_btn.clicked.connect(self.show_register)
        reg_layout.addWidget(reg_btn)
        
        form_layout.addWidget(reg_container)
        
        right_layout.addWidget(form_container)
        layout.addWidget(right_panel)
        
        return screen
    
    def create_register_screen(self):
        """Создать экран регистрации"""
        screen = QWidget()
        layout = QHBoxLayout(screen)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Левая панель
        left_panel = QFrame()
        left_panel.setFixedWidth(480)
        left_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {Colors.PRIMARY_GRADIENT_START}, 
                    stop:0.5 {Colors.PRIMARY},
                    stop:1 {Colors.PRIMARY_DARK});
            }}
            QLabel {{
                color: white;
                background: transparent;
            }}
        """)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignCenter)
        left_layout.setSpacing(16)
        left_layout.setContentsMargins(40, 40, 40, 40)
        
        icon = QLabel("✦")
        icon.setFont(QFont("Arial", 64))
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 64px;")
        left_layout.addWidget(icon)
        
        title = QLabel("Присоединяйтесь!")
        title.setFont(QFont("Arial", 42, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)
        
        subtitle = QLabel("Создайте аккаунт\nи записывайтесь онлайн")
        subtitle.setFont(QFont("Arial", 18))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.85);")
        subtitle.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(subtitle)
        
        # Разделитель
        left_layout.addSpacing(30)
        
        slogan = QLabel("✨ Станьте частью красоты ✨")
        slogan.setFont(QFont("Arial", 14))
        slogan.setStyleSheet("font-style: italic; color: rgba(255, 255, 255, 0.7);")
        slogan.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(slogan)
        
        layout.addWidget(left_panel)
        
        # Правая панель
        right_panel = QFrame()
        right_panel.setStyleSheet(f"background-color: {Colors.WHITE};")
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignCenter)
        
        form_container = QWidget()
        form_container.setFixedWidth(400)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        
        title_label = QLabel("Регистрация")
        title_label.setFont(QFont("Arial", 32, QFont.Bold))
        title_label.setStyleSheet(f"color: {Colors.PRIMARY}; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title_label)
        
        # Поля
        name_label = QLabel("ФИО")
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        name_label.setStyleSheet(f"color: {Colors.PRIMARY};")
        form_layout.addWidget(name_label)
        
        self.reg_name = ModernInput("Иванов Иван Иванович")
        form_layout.addWidget(self.reg_name)
        
        phone_label = QLabel("Номер телефона")
        phone_label.setFont(QFont("Arial", 12, QFont.Bold))
        phone_label.setStyleSheet(f"color: {Colors.PRIMARY};")
        form_layout.addWidget(phone_label)
        
        self.reg_phone = ModernInput("+7 (999) 123-45-67")
        form_layout.addWidget(self.reg_phone)
        
        password_label = QLabel("Пароль")
        password_label.setFont(QFont("Arial", 12, QFont.Bold))
        password_label.setStyleSheet(f"color: {Colors.PRIMARY};")
        form_layout.addWidget(password_label)
        
        self.reg_password = ModernInput("Придумайте пароль", password=True)
        form_layout.addWidget(self.reg_password)
        
        # Кнопки
        reg_btn = ModernButton("Зарегистрироваться", "primary")
        reg_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667EEA, stop:1 #764BA2);
                color: white;
                font-weight: bold;
                font-size: 15px;
                padding: 14px 28px;
                border-radius: 12px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A67D8, stop:1 #6B46C1);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4C51BF, stop:1 #553C9A);
            }
        """)
        reg_btn.clicked.connect(self.do_register)
        form_layout.addWidget(reg_btn)
        
        back_btn = ModernButton("← Назад к входу", "secondary")
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.WHITE};
                color: {Colors.PRIMARY};
                font-weight: bold;
                font-size: 14px;
                padding: 12px 24px;
                border-radius: 12px;
                border: 2px solid {Colors.PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_LIGHT};
            }}
        """)
        back_btn.clicked.connect(self.show_login)
        form_layout.addWidget(back_btn)
        
        right_layout.addWidget(form_container)
        layout.addWidget(right_panel)
        
        return screen
    
    def do_login(self):
        """Выполнить вход"""
        phone = self.login_phone.text().strip()
        password = self.login_password.text()
        
        if not phone or not password:
            QMessageBox.warning(self, "Внимание", "Заполните все поля")
            return
        
        result = self.api.login(phone, password)
        
        if result["success"]:
            self.current_user = result["data"]
            if self.current_user["role"] == "admin":
                self.show_admin_interface()
            else:
                self.show_client_interface()
        else:
            QMessageBox.critical(self, "Ошибка", result["error"])
    
    def do_register(self):
        """Выполнить регистрацию"""
        name = self.reg_name.text().strip()
        phone = self.reg_phone.text().strip()
        password = self.reg_password.text()
        
        if not name or not phone or not password:
            QMessageBox.warning(self, "Внимание", "Заполните все поля")
            return
        
        result = self.api.register(phone, password, name)
        
        if result["success"]:
            QMessageBox.information(self, "Успех", "Регистрация успешна! Теперь вы можете войти.")
            self.show_login()
        else:
            QMessageBox.critical(self, "Ошибка", result["error"])
    
    def logout(self):
        """Выйти из аккаунта"""
        self.current_user = None
        self.selected_master = None
        self.selected_service = None
        self.login_phone.clear()
        self.login_password.clear()
        self.show_login()
    
    def show_client_interface(self):
        """Показать интерфейс клиента"""
        if self.client_screen:
            self.central_widget.removeWidget(self.client_screen)
            self.client_screen.deleteLater()
        
        self.client_screen = self.create_client_screen()
        self.central_widget.addWidget(self.client_screen)
        self.central_widget.setCurrentWidget(self.client_screen)
    
    def create_client_screen(self):
        """Создать экран клиента"""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Хедер с современным градиентом
        header = QFrame()
        header.setFixedHeight(72)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY_GRADIENT_START}, 
                    stop:1 {Colors.PRIMARY_DARK});
            }}
            QLabel {{
                color: white;
                background: transparent;
            }}
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(32, 0, 32, 0)
        
        # Логотип с иконкой
        logo = QLabel("✦ BeautyPro")
        logo.setFont(QFont("Arial", 20, QFont.Bold))
        header_layout.addWidget(logo)
        
        header_layout.addSpacing(24)
        
        # Имя пользователя с иконкой
        user_name = QLabel(f"👤  {self.current_user.get('full_name', 'Клиент')}")
        user_name.setFont(QFont("Arial", 13))
        user_name.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        header_layout.addWidget(user_name)
        
        header_layout.addStretch()
        
        logout_btn = QPushButton("Выйти")
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                padding: 10px 24px;
                border-radius: 10px;
                font-weight: 600;
                font-size: 13px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.25);
                border-color: rgba(255, 255, 255, 0.4);
            }}
        """)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)
        
        layout.addWidget(header)
        
        # Табы
        self.client_tabs = QTabWidget()
        self.client_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {Colors.BACKGROUND};
                padding: 20px;
            }}
        """)
        
        # Вкладка записи
        booking_tab = self.create_booking_tab()
        self.client_tabs.addTab(booking_tab, "Новая запись")
        
        # Вкладка записей
        appointments_tab = self.create_appointments_tab()
        self.client_tabs.addTab(appointments_tab, "Мои записи")
        
        # История
        history_tab = self.create_history_tab()
        self.client_tabs.addTab(history_tab, "История")
        
        layout.addWidget(self.client_tabs)
        
        return screen
    
    def create_booking_tab(self):
        """Создать вкладку записи"""
        tab = QWidget()
        tab.setStyleSheet(f"background-color: {Colors.BACKGROUND};")
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("Новая запись")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet(f"color: {Colors.PRIMARY};")
        layout.addWidget(title)
        
        # Стек для переключения между экранами
        self.booking_stack = QStackedWidget()
        layout.addWidget(self.booking_stack)
        
        # Экран выбора способа записи
        choice_screen = self.create_booking_choice()
        self.booking_stack.addWidget(choice_screen)
        
        return tab
    
    def create_booking_choice(self):
        """Создать экран выбора способа записи"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        
        cards_container = QWidget()
        cards_layout = QHBoxLayout(cards_container)
        cards_layout.setSpacing(30)
        cards_layout.setAlignment(Qt.AlignCenter)
        
        # Карточка выбора мастера
        master_card = Card(clickable=True)
        master_card.setFixedSize(250, 200)
        master_layout = QVBoxLayout(master_card)
        master_layout.setAlignment(Qt.AlignCenter)
        
        master_icon = QLabel("👨‍🎨")
        master_icon.setFont(QFont("Arial", 48))
        master_icon.setAlignment(Qt.AlignCenter)
        master_icon.setStyleSheet("background: transparent; border: none;")
        master_layout.addWidget(master_icon)
        
        master_title = QLabel("Выбрать мастера")
        master_title.setFont(QFont("Arial", 14, QFont.Bold))
        master_title.setStyleSheet(f"color: {Colors.PRIMARY}; background: transparent; border: none; text-decoration: none;")
        master_title.setAlignment(Qt.AlignCenter)
        master_layout.addWidget(master_title)
        
        master_desc = QLabel("Сначала выберите мастера,\nзатем услугу")
        master_desc.setFont(QFont("Arial", 11))
        master_desc.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; background: transparent; border: none;")
        master_desc.setAlignment(Qt.AlignCenter)
        master_layout.addWidget(master_desc)
        
        master_card.clicked.connect(self.show_masters_list)
        cards_layout.addWidget(master_card)
        
        # Карточка выбора услуги
        service_card = Card(clickable=True)
        service_card.setFixedSize(250, 200)
        service_layout = QVBoxLayout(service_card)
        service_layout.setAlignment(Qt.AlignCenter)
        
        service_icon = QLabel("✂️")
        service_icon.setFont(QFont("Arial", 48))
        service_icon.setAlignment(Qt.AlignCenter)
        service_icon.setStyleSheet("background: transparent; border: none;")
        service_layout.addWidget(service_icon)
        
        service_title = QLabel("Выбрать услугу")
        service_title.setFont(QFont("Arial", 14, QFont.Bold))
        service_title.setStyleSheet(f"color: {Colors.PRIMARY}; background: transparent; border: none; text-decoration: none;")
        service_title.setAlignment(Qt.AlignCenter)
        service_layout.addWidget(service_title)
        
        service_desc = QLabel("Сначала выберите услугу,\nзатем мастера")
        service_desc.setFont(QFont("Arial", 11))
        service_desc.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; background: transparent; border: none;")
        service_desc.setAlignment(Qt.AlignCenter)
        service_layout.addWidget(service_desc)
        
        service_card.clicked.connect(self.show_services_list)
        cards_layout.addWidget(service_card)
        
        layout.addWidget(cards_container)
        
        return widget
    
    def show_masters_list(self):
        """Показать список мастеров"""
        # Удаляем ВСЕ виджеты кроме первого (choice screen)
        while self.booking_stack.count() > 1:
            old_widget = self.booking_stack.widget(1)
            self.booking_stack.removeWidget(old_widget)
            old_widget.deleteLater()
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Заголовок с кнопкой назад
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        back_btn = ModernButton("← Назад", "secondary")
        back_btn.setFixedWidth(140)
        back_btn.clicked.connect(lambda: self.booking_stack.setCurrentIndex(0))
        header_layout.addWidget(back_btn)
        
        title = QLabel("Выберите мастера")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {Colors.PRIMARY};")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        # Загружаем мастеров
        result = self.api.get_masters()
        
        if not result["success"]:
            error_label = QLabel("Ошибка загрузки мастеров")
            error_label.setStyleSheet(f"color: {Colors.DANGER};")
            layout.addWidget(error_label)
        else:
            masters = result["data"]
            
            if not masters:
                empty_label = QLabel("Нет доступных мастеров")
                empty_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
                layout.addWidget(empty_label)
            else:
                # Скролл-область
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setStyleSheet("background-color: transparent;")
                
                scroll_content = QWidget()
                grid = QGridLayout(scroll_content)
                grid.setSpacing(8)
                grid.setContentsMargins(5, 5, 5, 5)
                
                cols = 5
                for i, master in enumerate(masters):
                    row = i // cols
                    col = i % cols
                    
                    card = Card(clickable=True, padding=10)
                    card.setFixedSize(170, 150)
                    card_layout = QVBoxLayout(card)
                    card_layout.setAlignment(Qt.AlignCenter)
                    
                    card_layout.setSpacing(2)
                    card_layout.setContentsMargins(5, 5, 5, 5)
                    
                    avatar = QLabel("👨‍🎨")
                    avatar.setFont(QFont("Arial", 24))
                    avatar.setAlignment(Qt.AlignCenter)
                    card_layout.addWidget(avatar)
                    
                    name = QLabel(master['full_name'])
                    name.setFont(QFont("Arial", 11, QFont.Bold))
                    name.setWordWrap(True)
                    name.setAlignment(Qt.AlignCenter)
                    card_layout.addWidget(name)
                    
                    profession = master.get('profession', {}).get('name', '') if master.get('profession') else ''
                    prof_label = QLabel(profession)
                    prof_label.setFont(QFont("Arial", 9))
                    prof_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
                    prof_label.setAlignment(Qt.AlignCenter)
                    card_layout.addWidget(prof_label)
                    
                    services_count = len(master.get('services', []))
                    services_label = QLabel(f"{services_count} услуг")
                    services_label.setFont(QFont("Arial", 9))
                    services_label.setStyleSheet(f"color: {Colors.PRIMARY};")
                    services_label.setAlignment(Qt.AlignCenter)
                    card_layout.addWidget(services_label)
                    
                    card.clicked.connect(lambda m=master: self.select_master(m))
                    grid.addWidget(card, row, col)
                
                scroll.setWidget(scroll_content)
                layout.addWidget(scroll)
        
        self.booking_stack.addWidget(widget)
        self.booking_stack.setCurrentIndex(1)
    
    def go_back_to_masters(self):
        """Вернуться к списку мастеров"""
        # Удаляем виджеты выше индекса 1
        while self.booking_stack.count() > 2:
            old_widget = self.booking_stack.widget(2)
            self.booking_stack.removeWidget(old_widget)
            old_widget.deleteLater()
        self.booking_stack.setCurrentIndex(1)
    
    def go_back_to_services(self):
        """Вернуться к списку услуг"""
        # Удаляем виджеты выше индекса 1
        while self.booking_stack.count() > 2:
            old_widget = self.booking_stack.widget(2)
            self.booking_stack.removeWidget(old_widget)
            old_widget.deleteLater()
        self.booking_stack.setCurrentIndex(1)
    
    def select_master(self, master):
        """Выбрать мастера и показать его услуги"""
        self.selected_master = master
        self.show_master_services()
    
    def show_master_services(self):
        """Показать услуги мастера"""
        if self.booking_stack.count() > 2:
            old_widget = self.booking_stack.widget(2)
            self.booking_stack.removeWidget(old_widget)
            old_widget.deleteLater()
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Заголовок
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        back_btn = ModernButton("← Назад", "secondary")
        back_btn.setFixedWidth(140)
        back_btn.clicked.connect(self.go_back_to_masters)
        header_layout.addWidget(back_btn)
        
        title = QLabel(f"Услуги: {self.selected_master['full_name']}")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {Colors.PRIMARY};")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        services = self.selected_master.get('services', [])
        
        if not services:
            empty_label = QLabel("У мастера нет доступных услуг")
            empty_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
            layout.addWidget(empty_label)
        else:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("background-color: transparent;")
            
            scroll_content = QWidget()
            services_layout = QVBoxLayout(scroll_content)
            services_layout.setSpacing(6)
            services_layout.setContentsMargins(10, 10, 10, 10)
            services_layout.setAlignment(Qt.AlignTop)
            
            for service in services:
                card = Card(clickable=True, padding=10)
                card.setFixedHeight(60)
                card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                card_layout = QHBoxLayout(card)
                card_layout.setContentsMargins(10, 5, 10, 5)
                
                info = QWidget()
                info_layout = QVBoxLayout(info)
                info_layout.setContentsMargins(0, 0, 0, 0)
                info_layout.setSpacing(4)
                
                name = QLabel(service['name'])
                name.setFont(QFont("Arial", 13, QFont.Bold))
                info_layout.addWidget(name)
                
                details = QLabel(f"{service['price']} руб. • {service['duration_minutes']} мин.")
                details.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
                info_layout.addWidget(details)
                
                card_layout.addWidget(info)
                card_layout.addStretch()
                
                card.clicked.connect(lambda s=service: self.select_service_and_show_calendar(s))
                services_layout.addWidget(card)
            
            services_layout.addStretch()
            scroll.setWidget(scroll_content)
            layout.addWidget(scroll)
        
        self.booking_stack.addWidget(widget)
        self.booking_stack.setCurrentIndex(2)
    
    def show_services_list(self):
        """Показать список услуг"""
        # Удаляем ВСЕ виджеты кроме первого (choice screen)
        while self.booking_stack.count() > 1:
            old_widget = self.booking_stack.widget(1)
            self.booking_stack.removeWidget(old_widget)
            old_widget.deleteLater()
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        back_btn = ModernButton("← Назад", "secondary")
        back_btn.setFixedWidth(140)
        back_btn.clicked.connect(lambda: self.booking_stack.setCurrentIndex(0))
        header_layout.addWidget(back_btn)
        
        title = QLabel("Выберите услугу")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {Colors.PRIMARY};")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        result = self.api.get_services()
        
        if not result["success"]:
            error_label = QLabel("Ошибка загрузки услуг")
            error_label.setStyleSheet(f"color: {Colors.DANGER};")
            layout.addWidget(error_label)
        else:
            services = result["data"]
            
            if not services:
                empty_label = QLabel("Нет доступных услуг")
                empty_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
                layout.addWidget(empty_label)
            else:
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setStyleSheet("background-color: transparent;")
                
                scroll_content = QWidget()
                grid = QGridLayout(scroll_content)
                grid.setSpacing(15)
                
                cols = 3
                for i, service in enumerate(services):
                    row = i // cols
                    col = i % cols
                    
                    card = Card(clickable=True)
                    card.setMinimumHeight(120)
                    card_layout = QVBoxLayout(card)
                    
                    name = QLabel(service['name'])
                    name.setFont(QFont("Arial", 13, QFont.Bold))
                    name.setWordWrap(True)
                    card_layout.addWidget(name)
                    
                    details = QLabel(f"{service['price']} руб. • {service['duration_minutes']} мин.")
                    details.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
                    card_layout.addWidget(details)
                    
                    card.clicked.connect(lambda s=service: self.select_service_and_show_service_masters(s))
                    grid.addWidget(card, row, col)
                
                scroll.setWidget(scroll_content)
                layout.addWidget(scroll)
        
        self.booking_stack.addWidget(widget)
        self.booking_stack.setCurrentIndex(1)
    
    def select_service_and_show_service_masters(self, service):
        """Выбрать услугу и показать мастеров"""
        self.selected_service = service
        self.show_service_masters()
    
    def show_service_masters(self):
        """Показать мастеров для услуги"""
        if self.booking_stack.count() > 2:
            old_widget = self.booking_stack.widget(2)
            self.booking_stack.removeWidget(old_widget)
            old_widget.deleteLater()
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        back_btn = ModernButton("← Назад", "secondary")
        back_btn.setFixedWidth(140)
        back_btn.clicked.connect(self.go_back_to_services)
        header_layout.addWidget(back_btn)
        
        title = QLabel(f"Мастера для: {self.selected_service['name']}")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {Colors.PRIMARY};")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        result = self.api.get_service_masters(self.selected_service['id'])
        
        if not result["success"]:
            error_label = QLabel("Ошибка загрузки мастеров")
            error_label.setStyleSheet(f"color: {Colors.DANGER};")
            layout.addWidget(error_label)
        else:
            masters = result["data"]
            
            if not masters:
                empty_label = QLabel("Нет доступных мастеров для этой услуги")
                empty_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
                layout.addWidget(empty_label)
            else:
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setStyleSheet("background-color: transparent;")
                
                scroll_content = QWidget()
                grid = QGridLayout(scroll_content)
                grid.setSpacing(8)
                grid.setContentsMargins(5, 5, 5, 5)
                
                cols = 5
                for i, master in enumerate(masters):
                    row = i // cols
                    col = i % cols
                    
                    card = Card(clickable=True, padding=10)
                    card.setFixedSize(170, 120)
                    card_layout = QVBoxLayout(card)
                    card_layout.setAlignment(Qt.AlignCenter)
                    card_layout.setSpacing(2)
                    card_layout.setContentsMargins(5, 5, 5, 5)
                    
                    avatar = QLabel("👨‍🎨")
                    avatar.setFont(QFont("Arial", 24))
                    avatar.setAlignment(Qt.AlignCenter)
                    card_layout.addWidget(avatar)
                    
                    name = QLabel(master['full_name'])
                    name.setFont(QFont("Arial", 11, QFont.Bold))
                    name.setWordWrap(True)
                    name.setAlignment(Qt.AlignCenter)
                    card_layout.addWidget(name)
                    
                    card.clicked.connect(lambda m=master: self.select_master_and_show_calendar(m))
                    grid.addWidget(card, row, col)
                
                scroll.setWidget(scroll_content)
                layout.addWidget(scroll)
        
        self.booking_stack.addWidget(widget)
        self.booking_stack.setCurrentIndex(2)
    
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
        dialog = QDialog(self)
        dialog.setWindowTitle("Выбор даты и времени")
        dialog.setFixedSize(850, 580)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.WHITE};
            }}
            QCalendarWidget {{
                background-color: {Colors.WHITE};
            }}
            QCalendarWidget QToolButton {{
                color: {Colors.TEXT};
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: {Colors.PRIMARY_LIGHT};
            }}
            QCalendarWidget QToolButton:pressed {{
                background-color: {Colors.HOVER};
            }}
            QCalendarWidget QMenu {{
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
            }}
            QCalendarWidget QSpinBox {{
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                padding: 4px;
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background-color: {Colors.WHITE};
            }}
            QCalendarWidget QTableView {{
                background-color: {Colors.WHITE};
                selection-background-color: {Colors.PRIMARY};
                selection-color: white;
            }}
            QCalendarWidget QTableView::item {{
                padding: 8px;
            }}
            QCalendarWidget QTableView::item:selected {{
                background-color: {Colors.PRIMARY};
                color: white;
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                background-color: {Colors.WHITE};
                color: {Colors.TEXT};
                selection-background-color: {Colors.PRIMARY};
                selection-color: white;
                outline: none;
            }}
            QCalendarWidget QAbstractItemView:disabled {{
                color: {Colors.TEXT_MUTED};
            }}
            QCalendarWidget QWidget {{
                alternate-background-color: {Colors.WHITE};
                background-color: {Colors.WHITE};
            }}
            QCalendarWidget #qt_calendar_calendarview {{
                background-color: {Colors.WHITE};
            }}
        """)
        
        layout = QHBoxLayout(dialog)
        layout.setSpacing(24)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Левая часть - информация и календарь
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setSpacing(16)
        
        # Информация о записи
        info_card = Card(padding=16)
        info_layout = QVBoxLayout(info_card)
        info_layout.setSpacing(8)
        
        master_label = QLabel(f"👨‍🎨  Мастер: {self.selected_master['full_name']}")
        master_label.setFont(QFont("Arial", 13, QFont.Bold))
        master_label.setStyleSheet("background: transparent; border: none;")
        info_layout.addWidget(master_label)
        
        service_label = QLabel(f"✂️  Услуга: {self.selected_service['name']}")
        service_label.setFont(QFont("Arial", 13))
        service_label.setStyleSheet("background: transparent; border: none;")
        info_layout.addWidget(service_label)
        
        price_label = QLabel(f"💰  Стоимость: {self.selected_service['price']} руб.")
        price_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; background: transparent; border: none;")
        price_label.setFont(QFont("Arial", 12))
        info_layout.addWidget(price_label)
        
        left_layout.addWidget(info_card)
        
        # Календарь
        calendar_label = QLabel("📅  Выберите дату:")
        calendar_label.setFont(QFont("Arial", 14, QFont.Bold))
        calendar_label.setStyleSheet("background: transparent; border: none;")
        left_layout.addWidget(calendar_label)
        
        self.dialog_ref = dialog  # Сохраняем ссылку на диалог
        
        self.calendar = QCalendarWidget()
        self.calendar.setMinimumDate(QDate.currentDate())
        self.calendar.setMaximumDate(QDate.currentDate().addMonths(2))
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)
        
        # Убираем выпадающий список месяца - только стрелки
        # Находим и скрываем combobox месяца
        for child in self.calendar.findChildren(QComboBox):
            child.setVisible(False)
        
        # Устанавливаем фиксированный размер для корректного отображения всех дней
        self.calendar.setFixedSize(450, 320)
        
        # Подключаем сигнал selectionChanged вместо clicked для лучшей работы
        self.calendar.selectionChanged.connect(self.on_calendar_date_changed)
        
        left_layout.addWidget(self.calendar)
        
        layout.addWidget(left)
        
        # Правая часть - время
        right = QWidget()
        right.setMinimumWidth(280)
        right_layout = QVBoxLayout(right)
        right_layout.setSpacing(16)
        
        time_label = QLabel("🕐  Доступное время:")
        time_label.setFont(QFont("Arial", 14, QFont.Bold))
        time_label.setStyleSheet("background: transparent; border: none;")
        right_layout.addWidget(time_label)
        
        self.time_scroll = QScrollArea()
        self.time_scroll.setWidgetResizable(True)
        self.time_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
                background-color: {Colors.BACKGROUND};
            }}
        """)
        self.time_container = QWidget()
        self.time_container.setStyleSheet(f"background-color: {Colors.BACKGROUND};")
        self.time_layout = QVBoxLayout(self.time_container)
        self.time_layout.setSpacing(8)
        self.time_layout.setContentsMargins(12, 12, 12, 12)
        self.time_scroll.setWidget(self.time_container)
        right_layout.addWidget(self.time_scroll)
        
        # Кнопки
        buttons = QWidget()
        buttons_layout = QHBoxLayout(buttons)
        buttons_layout.setContentsMargins(0, 8, 0, 0)
        
        cancel_btn = ModernButton("Отмена", "secondary")
        cancel_btn.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_btn)
        
        right_layout.addWidget(buttons)
        
        layout.addWidget(right)
        
        # Загружаем слоты для выбранной даты
        self.selected_slot = None
        self.load_time_slots(dialog)
        
        result = dialog.exec()
        
        # Если диалог закрыт без записи - очищаем стек
        if result == QDialog.Rejected:
            while self.booking_stack.count() > 1:
                widget = self.booking_stack.widget(1)
                self.booking_stack.removeWidget(widget)
                widget.deleteLater()
            self.booking_stack.setCurrentIndex(0)
            self.selected_master = None
            self.selected_service = None
    
    def on_calendar_date_changed(self):
        """Обработчик изменения даты в календаре"""
        if hasattr(self, 'dialog_ref') and self.dialog_ref:
            self.load_time_slots(self.dialog_ref)
    
    def load_time_slots(self, dialog):
        """Загрузить временные слоты"""
        # Очищаем предыдущие слоты
        while self.time_layout.count():
            item = self.time_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        selected_date = self.calendar.selectedDate().toPython()
        
        result = self.api.get_available_slots(
            self.selected_master['id'],
            self.selected_service['id'],
            selected_date
        )
        
        if not result["success"]:
            error_label = QLabel("Ошибка загрузки")
            error_label.setStyleSheet(f"color: {Colors.DANGER};")
            self.time_layout.addWidget(error_label)
            return
        
        data = result["data"]
        
        # Обрабатываем разные форматы ответа API
        # Может быть: список ["10:00", "11:00"] или dict {"date": "...", "slots": [...]}
        if isinstance(data, dict):
            slots = data.get('slots', [])
        elif isinstance(data, list):
            slots = data
        else:
            slots = []
        
        if not slots:
            empty_label = QLabel("Нет доступного времени на эту дату")
            empty_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 14px;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.time_layout.addWidget(empty_label)
            return
        
        for slot in slots:
            # slot может быть строкой "10:00" или dict {'time': '10:00'}
            if isinstance(slot, dict):
                time_str = slot.get('time', str(slot))
            else:
                time_str = str(slot)
            
            btn = ModernButton(f"🕐  {time_str}", "secondary")
            btn.clicked.connect(lambda checked, s=time_str: self.select_slot_and_confirm(s, dialog))
            self.time_layout.addWidget(btn)
        
        self.time_layout.addStretch()
    
    def select_slot_and_confirm(self, slot, dialog):
        """Выбрать слот и подтвердить запись"""
        selected_date = self.calendar.selectedDate().toPython()
        
        # slot теперь строка времени "10:00"
        time_str = slot['time'] if isinstance(slot, dict) else slot
        
        # Диалог подтверждения
        confirm = self.styled_question(
            dialog,
            "Подтверждение записи",
            f"Подтвердить запись?\n\n"
            f"Мастер: {self.selected_master['full_name']}\n"
            f"Услуга: {self.selected_service['name']}\n"
            f"Дата: {selected_date.strftime('%d.%m.%Y')}\n"
            f"Время: {time_str}\n"
            f"Стоимость: {self.selected_service['price']} руб."
        )
        
        if confirm:
            # Создаем datetime
            appointment_datetime = datetime.combine(
                selected_date,
                datetime.strptime(time_str, '%H:%M').time()
            )
            
            result = self.api.create_appointment(
                self.current_user['id'],
                self.selected_master['id'],
                self.selected_service['id'],
                appointment_datetime
            )
            
            if result["success"]:
                self.styled_info(dialog, "Успех", "Запись успешно создана!")
                dialog.accept()
                # Очищаем все промежуточные виджеты из стека
                while self.booking_stack.count() > 1:
                    widget = self.booking_stack.widget(1)
                    self.booking_stack.removeWidget(widget)
                    widget.deleteLater()
                self.booking_stack.setCurrentIndex(0)
                self.selected_master = None
                self.selected_service = None
                # Обновляем записи и историю
                self.load_appointments()
                self.load_history()
            else:
                QMessageBox.critical(dialog, "Ошибка", result["error"])
    
    def create_appointments_tab(self):
        """Создать вкладку записей"""
        tab = QWidget()
        tab.setStyleSheet(f"background-color: {Colors.BACKGROUND};")
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        title = QLabel("Мои записи")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet(f"color: {Colors.PRIMARY};")
        layout.addWidget(title)
        
        # Кнопка обновления
        refresh_btn = ModernButton("Обновить", "secondary")
        refresh_btn.setFixedWidth(150)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667EEA, stop:1 #764BA2);
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 16px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A67D8, stop:1 #6B46C1);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4C51BF, stop:1 #553C9A);
            }
        """)
        refresh_btn.clicked.connect(lambda: self.refresh_appointments(layout))
        layout.addWidget(refresh_btn)
        
        # Контейнер для записей
        self.appointments_container = QWidget()
        self.appointments_layout = QVBoxLayout(self.appointments_container)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent;")
        scroll.setWidget(self.appointments_container)
        layout.addWidget(scroll)
        
        # Загружаем записи
        self.load_appointments()
        
        return tab
    
    def load_appointments(self):
        """Загрузить записи"""
        # Очищаем
        while self.appointments_layout.count():
            item = self.appointments_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        result = self.api.get_appointments(self.current_user['id'], upcoming_only=True)
        
        if not result["success"]:
            error_label = QLabel("Ошибка загрузки записей")
            error_label.setStyleSheet(f"color: {Colors.DANGER};")
            self.appointments_layout.addWidget(error_label)
            return
        
        appointments = result["data"]
        
        if not appointments:
            empty_label = QLabel("У вас пока нет предстоящих записей")
            empty_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 16px;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.appointments_layout.addWidget(empty_label)
            self.appointments_layout.setAlignment(Qt.AlignCenter)
            return
        
        for appointment in appointments:
            card = Card()
            card_layout = QHBoxLayout(card)
            
            # Информация
            info = QWidget()
            info_layout = QVBoxLayout(info)
            info_layout.setContentsMargins(0, 0, 0, 0)
            
            service_name = appointment.get('service', {}).get('name', 'Услуга')
            master_name = appointment.get('master', {}).get('full_name', 'Мастер')
            
            service_label = QLabel(service_name)
            service_label.setFont(QFont("Arial", 14, QFont.Bold))
            info_layout.addWidget(service_label)
            
            master_label = QLabel(f"Мастер: {master_name}")
            info_layout.addWidget(master_label)
            
            dt = datetime.fromisoformat(appointment['appointment_datetime'].replace('Z', '+00:00'))
            date_label = QLabel(f"Дата: {dt.strftime('%d.%m.%Y')} в {dt.strftime('%H:%M')}")
            date_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
            info_layout.addWidget(date_label)
            
            card_layout.addWidget(info)
            card_layout.addStretch()
            
            # Кнопка отмены
            if appointment.get('status') == 'scheduled':
                cancel_btn = ModernButton("Отменить", "danger")
                cancel_btn.setFixedWidth(140)
                cancel_btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #EF4444, stop:1 #DC2626);
                        color: white;
                        font-weight: bold;
                        font-size: 13px;
                        padding: 10px 16px;
                        border-radius: 8px;
                        border: none;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #DC2626, stop:1 #B91C1C);
                    }
                    QPushButton:pressed {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #B91C1C, stop:1 #991B1B);
                    }
                """)
                cancel_btn.clicked.connect(lambda checked, a=appointment: self.cancel_appointment(a))
                card_layout.addWidget(cancel_btn)
            
            self.appointments_layout.addWidget(card)
        
        self.appointments_layout.addStretch()
    
    def refresh_appointments(self, layout):
        """Обновить записи"""
        self.load_appointments()
    
    def cancel_appointment(self, appointment):
        """Отменить запись"""
        confirm = self.styled_question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите отменить запись?"
        )
        
        if confirm:
            result = self.api.cancel_appointment(appointment['id'], self.current_user['id'])
            
            if result["success"]:
                QMessageBox.information(self, "Успех", "Запись отменена")
                self.load_appointments()
                self.load_history()
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])
    
    def create_history_tab(self):
        """Создать вкладку истории"""
        tab = QWidget()
        tab.setStyleSheet(f"background-color: {Colors.BACKGROUND};")
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # Заголовок с кнопкой обновления
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("История записей")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet(f"color: {Colors.PRIMARY};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        refresh_btn = ModernButton("Обновить", "primary")
        refresh_btn.setFixedWidth(150)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667EEA, stop:1 #764BA2);
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 16px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A67D8, stop:1 #6B46C1);
            }
        """)
        refresh_btn.clicked.connect(self.load_history)
        header_layout.addWidget(refresh_btn)
        
        layout.addWidget(header)
        
        # Таблица
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Дата", "Время", "Услуга", "Мастер", "Статус"])
        # Настраиваем ширину колонок
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Дата
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Время
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Услуга
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Мастер
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Статус
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.history_table)
        
        # Сообщение о пустой истории (поверх таблицы)
        self.history_empty_label = QLabel("История записей пуста")
        self.history_empty_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 16px;")
        self.history_empty_label.setAlignment(Qt.AlignCenter)
        self.history_empty_label.setVisible(False)
        layout.addWidget(self.history_empty_label)
        
        # Растягиваем пустое пространство вниз
        layout.addStretch()
        
        # Загружаем историю
        self.load_history()
        
        return tab
    
    def load_history(self):
        """Загрузить историю записей"""
        if not hasattr(self, 'history_table'):
            return
            
        result = self.api.get_appointments(self.current_user['id'])
        
        if result["success"]:
            appointments = result["data"]
            # Очищаем таблицу перед загрузкой
            self.history_table.clearContents()
            self.history_table.setRowCount(len(appointments))
            
            # Показываем/скрываем сообщение о пустой истории
            if hasattr(self, 'history_empty_label'):
                if not appointments:
                    self.history_empty_label.setVisible(True)
                    self.history_table.setVisible(False)
                else:
                    self.history_empty_label.setVisible(False)
                    self.history_table.setVisible(True)
            
            for i, appointment in enumerate(appointments):
                dt = datetime.fromisoformat(appointment['appointment_datetime'].replace('Z', '+00:00'))
                
                self.history_table.setItem(i, 0, QTableWidgetItem(dt.strftime('%d.%m.%Y')))
                self.history_table.setItem(i, 1, QTableWidgetItem(dt.strftime('%H:%M')))
                self.history_table.setItem(i, 2, QTableWidgetItem(appointment.get('service', {}).get('name', '')))
                self.history_table.setItem(i, 3, QTableWidgetItem(appointment.get('master', {}).get('full_name', '')))
                
                status_map = {
                    'scheduled': 'Запланировано',
                    'completed': 'Завершено',
                    'cancelled': 'Отменено',
                    'canceled': 'Отменено'  # Оба варианта написания
                }
                status = appointment.get('status', '')
                status_text = status_map.get(status, status if status else 'Неизвестно')
                self.history_table.setItem(i, 4, QTableWidgetItem(status_text))
            
            # Обновляем отображение
            self.history_table.viewport().update()
    
    def show_admin_interface(self):
        """Показать интерфейс администратора"""
        if self.admin_screen:
            self.central_widget.removeWidget(self.admin_screen)
            self.admin_screen.deleteLater()
        
        self.admin_screen = self.create_admin_screen()
        self.central_widget.addWidget(self.admin_screen)
        self.central_widget.setCurrentWidget(self.admin_screen)
    
    def create_admin_screen(self):
        """Создать экран администратора"""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Хедер
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY_DARK}, stop:1 {Colors.PRIMARY});
            }}
            QLabel {{
                color: white;
            }}
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        logo = QLabel("BeautyPro Admin")
        logo.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(logo)
        
        header_layout.addStretch()
        
        logout_btn = QPushButton("Выйти")
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                color: {Colors.PRIMARY};
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_LIGHT};
            }}
        """)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)
        
        layout.addWidget(header)
        
        # Табы
        tabs = QTabWidget()
        
        # Мастера
        masters_tab = self.create_masters_management_tab()
        tabs.addTab(masters_tab, "Мастера")
        
        # Услуги
        services_tab = self.create_services_management_tab()
        tabs.addTab(services_tab, "Услуги")
        
        layout.addWidget(tabs)
        
        return screen
    
    def create_masters_management_tab(self):
        """Создать вкладку управления мастерами"""
        tab = QWidget()
        tab.setStyleSheet(f"background-color: {Colors.BACKGROUND};")
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок и кнопка добавления
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Управление мастерами")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet(f"color: {Colors.PRIMARY};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        add_btn = ModernButton("+ Добавить мастера", "primary")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667EEA, stop:1 #764BA2);
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 24px;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A67D8, stop:1 #6B46C1);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4C51BF, stop:1 #553C9A);
            }}
        """)
        add_btn.clicked.connect(self.show_add_master_dialog)
        header_layout.addWidget(add_btn)
        
        layout.addWidget(header)
        
        # Таблица мастеров
        self.masters_table = QTableWidget()
        self.masters_table.setColumnCount(5)
        self.masters_table.setHorizontalHeaderLabels(["ID", "ФИО", "Профессия", "Контакт", "Действия"])
        
        # Настраиваем ширину колонок для оптимального отображения
        masters_header = self.masters_table.horizontalHeader()
        masters_header.setStretchLastSection(False)  # Отключаем растягивание последней колонки
        
        # ID - компактная колонка для чисел до 9999
        masters_header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.masters_table.setColumnWidth(0, 50)
        
        # ФИО - растягивается, занимает оставшееся пространство
        masters_header.setSectionResizeMode(1, QHeaderView.Stretch)
        masters_header.setMinimumSectionSize(200)
        
        # Профессия - автоподстройка под содержимое с минимумом
        masters_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.masters_table.horizontalHeader().setMinimumSectionSize(130)
        
        # Контакт - фиксированная ширина для телефонов "+7 (999) 000-00-00"
        masters_header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.masters_table.setColumnWidth(3, 160)
        
        # Действия - фиксированная ширина для двух кнопок (130+130+15+20=295 -> 300px)
        masters_header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.masters_table.setColumnWidth(4, 300)
        
        self.masters_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.masters_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.masters_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.masters_table)
        
        # Загружаем мастеров
        self.load_masters_table()
        
        return tab
    
    def load_masters_table(self):
        """Загрузить таблицу мастеров"""
        result = self.api.get_masters(active_only=False)
        
        if not result["success"]:
            return
        
        masters = result["data"]
        self.masters_table.setRowCount(len(masters))
        
        # Устанавливаем высоту строк для видимости кнопок
        self.masters_table.verticalHeader().setDefaultSectionSize(75)
        
        for i, master in enumerate(masters):
            self.masters_table.setItem(i, 0, QTableWidgetItem(str(master['id'])))
            self.masters_table.setItem(i, 1, QTableWidgetItem(master['full_name']))
            
            profession = master.get('profession', {}).get('name', '') if master.get('profession') else ''
            self.masters_table.setItem(i, 2, QTableWidgetItem(profession))
            self.masters_table.setItem(i, 3, QTableWidgetItem(master.get('contact_info', '')))
            
            # Кнопки действий - контейнер с выравниванием по правому краю
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(5, 10, 10, 10)  # Вертикальные отступы для центрирования
            actions_layout.setSpacing(8)  # Промежуток между кнопками
            actions_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            edit_btn = QPushButton("Изменить")
            edit_btn.setFixedSize(130, 36)  # Фиксированный размер кнопки
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.PRIMARY};
                    color: white;
                    font-weight: bold;
                    font-size: 13px;
                    border: none;
                    border-radius: 5px;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background-color: {Colors.PRIMARY_DARK};
                }}
                QPushButton:pressed {{
                    background-color: #3730A3;
                }}
            """)
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.clicked.connect(lambda checked, m=master: self.show_edit_master_dialog(m))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("Удалить")
            delete_btn.setFixedSize(130, 36)  # Фиксированный размер кнопки
            delete_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.DANGER};
                    color: white;
                    font-weight: bold;
                    font-size: 13px;
                    border: none;
                    border-radius: 5px;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background-color: #DC2626;
                }}
                QPushButton:pressed {{
                    background-color: #B91C1C;
                }}
            """)
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.clicked.connect(lambda checked, m=master: self.delete_master(m))
            actions_layout.addWidget(delete_btn)
            
            self.masters_table.setCellWidget(i, 4, actions)
    
    def show_add_master_dialog(self):
        """Показать диалог добавления мастера"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить мастера")
        dialog.setFixedSize(550, 650)
        dialog.setStyleSheet(f"background-color: {Colors.WHITE};")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Новый мастер")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {Colors.PRIMARY};")
        layout.addWidget(title)
        
        # ФИО
        name_label = QLabel("ФИО")
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(name_label)
        
        name_input = ModernInput("Введите ФИО")
        layout.addWidget(name_input)
        
        # Профессия
        prof_label = QLabel("Профессия")
        prof_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(prof_label)
        
        prof_input = ModernInput("Введите профессию")
        layout.addWidget(prof_input)
        
        # Загружаем профессии для поиска
        result = self.api.get_professions()
        professions = result["data"] if result["success"] else []
        
        # Контакт
        contact_label = QLabel("Контакт")
        contact_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(contact_label)
        
        contact_input = ModernInput("Телефон или email")
        layout.addWidget(contact_input)
        
        # Услуги
        services_label = QLabel("Услуги мастера")
        services_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(services_label)
        
        # Загружаем услуги
        services_result = self.api.get_services()
        all_services = services_result["data"] if services_result["success"] else []
        
        # Скроллируемая область для чекбоксов услуг
        services_scroll = QScrollArea()
        services_scroll.setWidgetResizable(True)
        services_scroll.setMaximumHeight(150)
        services_scroll.setStyleSheet("background-color: transparent; border: 1px solid #E2E8F0; border-radius: 8px;")
        
        services_widget = QWidget()
        services_layout = QVBoxLayout(services_widget)
        services_layout.setSpacing(8)
        services_layout.setContentsMargins(10, 10, 10, 10)
        
        service_checkboxes = {}
        for service in all_services:
            checkbox = QCheckBox(f"{service['name']} ({service['price']} руб.)")
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {Colors.TEXT};
                    font-size: 12px;
                    padding: 4px;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid {Colors.PRIMARY};
                    border-radius: 4px;
                    background-color: white;
                }}
                QCheckBox::indicator:checked {{
                    background-color: {Colors.PRIMARY};
                    border-color: {Colors.PRIMARY};
                }}
            """)
            service_checkboxes[service['id']] = checkbox
            services_layout.addWidget(checkbox)
        
        services_layout.addStretch()
        services_scroll.setWidget(services_widget)
        layout.addWidget(services_scroll)
        
        layout.addStretch()
        
        # Кнопки
        buttons = QWidget()
        buttons_layout = QHBoxLayout(buttons)
        
        cancel_btn = ModernButton("Отмена", "secondary")
        cancel_btn.setStyleSheet(f"""
            background-color: {Colors.WHITE};
            color: {Colors.PRIMARY};
            border: 2px solid {Colors.PRIMARY};
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: bold;
        """)
        cancel_btn.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = ModernButton("Сохранить", "primary")
        save_btn.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667EEA, stop:1 #764BA2);
            color: white;
            font-weight: bold;
            font-size: 14px;
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
        """)
        
        def save_master():
            name = name_input.text().strip()
            profession_name = prof_input.text().strip()
            contact = contact_input.text().strip()
            
            if not name:
                QMessageBox.warning(dialog, "Внимание", "Введите ФИО")
                return
            
            # Ищем профессию по имени
            profession_id = None
            for prof in professions:
                if prof['name'].lower() == profession_name.lower():
                    profession_id = prof['id']
                    break
            
            # Собираем выбранные услуги
            selected_service_ids = [service_id for service_id, checkbox in service_checkboxes.items() if checkbox.isChecked()]
            
            result = self.api.create_master(name, profession_id, contact, selected_service_ids)
            
            if result["success"]:
                self.styled_info(dialog, "Успех", "Мастер добавлен")
                dialog.accept()
                self.load_masters_table()
            else:
                QMessageBox.critical(dialog, "Ошибка", result["error"])
        
        save_btn.clicked.connect(save_master)
        buttons_layout.addWidget(save_btn)
        
        layout.addWidget(buttons)
        
        dialog.exec()
    
    def show_edit_master_dialog(self, master):
        """Показать диалог редактирования мастера"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать мастера")
        dialog.setFixedSize(550, 650)
        dialog.setStyleSheet(f"background-color: {Colors.WHITE};")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Редактирование")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {Colors.PRIMARY};")
        layout.addWidget(title)
        
        # ФИО
        name_label = QLabel("ФИО")
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(name_label)
        
        name_input = ModernInput()
        name_input.setText(master['full_name'])
        layout.addWidget(name_input)
        
        # Профессия
        prof_label = QLabel("Профессия")
        prof_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(prof_label)
        
        prof_input = ModernInput()
        # Устанавливаем текущую профессию
        if master.get('profession'):
            prof_input.setText(master['profession'].get('name', ''))
        layout.addWidget(prof_input)
        
        # Загружаем профессии для поиска
        result = self.api.get_professions()
        professions = result["data"] if result["success"] else []
        
        # Контакт
        contact_label = QLabel("Контакт")
        contact_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(contact_label)
        
        contact_input = ModernInput()
        contact_input.setText(master.get('contact_info', ''))
        layout.addWidget(contact_input)
        
        # Услуги
        services_label = QLabel("Услуги мастера")
        services_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(services_label)
        
        # Загружаем услуги
        services_result = self.api.get_services()
        all_services = services_result["data"] if services_result["success"] else []
        
        # Получаем текущие услуги мастера
        current_service_ids = [s['id'] for s in master.get('services', [])]
        
        # Скроллируемая область для чекбоксов услуг
        services_scroll = QScrollArea()
        services_scroll.setWidgetResizable(True)
        services_scroll.setMaximumHeight(150)
        services_scroll.setStyleSheet("background-color: transparent; border: 1px solid #E2E8F0; border-radius: 8px;")
        
        services_widget = QWidget()
        services_layout = QVBoxLayout(services_widget)
        services_layout.setSpacing(8)
        services_layout.setContentsMargins(10, 10, 10, 10)
        
        service_checkboxes = {}
        for service in all_services:
            checkbox = QCheckBox(f"{service['name']} ({service['price']} руб.)")
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {Colors.TEXT};
                    font-size: 12px;
                    padding: 4px;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid {Colors.PRIMARY};
                    border-radius: 4px;
                    background-color: white;
                }}
                QCheckBox::indicator:checked {{
                    background-color: {Colors.PRIMARY};
                    border-color: {Colors.PRIMARY};
                }}
            """)
            # Отмечаем текущие услуги мастера
            if service['id'] in current_service_ids:
                checkbox.setChecked(True)
            service_checkboxes[service['id']] = checkbox
            services_layout.addWidget(checkbox)
        
        services_layout.addStretch()
        services_scroll.setWidget(services_widget)
        layout.addWidget(services_scroll)
        
        layout.addStretch()
        
        # Кнопки
        buttons = QWidget()
        buttons_layout = QHBoxLayout(buttons)
        
        cancel_btn = ModernButton("Отмена", "secondary")
        cancel_btn.setStyleSheet(f"""
            background-color: {Colors.WHITE};
            color: {Colors.PRIMARY};
            border: 2px solid {Colors.PRIMARY};
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: bold;
        """)
        cancel_btn.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = ModernButton("Сохранить", "primary")
        save_btn.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667EEA, stop:1 #764BA2);
            color: white;
            font-weight: bold;
            font-size: 14px;
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
        """)
        
        def update_master():
            name = name_input.text().strip()
            profession_name = prof_input.text().strip()
            contact = contact_input.text().strip()
            
            if not name:
                QMessageBox.warning(dialog, "Внимание", "Введите ФИО")
                return
            
            # Ищем профессию по имени
            profession_id = None
            for prof in professions:
                if prof['name'].lower() == profession_name.lower():
                    profession_id = prof['id']
                    break
            
            # Собираем выбранные услуги
            selected_service_ids = [service_id for service_id, checkbox in service_checkboxes.items() if checkbox.isChecked()]
            
            result = self.api.update_master(master['id'], name, profession_id, contact, selected_service_ids)
            
            if result["success"]:
                self.styled_info(dialog, "Успех", "Мастер обновлен")
                dialog.accept()
                self.load_masters_table()
            else:
                QMessageBox.critical(dialog, "Ошибка", result["error"])
        
        save_btn.clicked.connect(update_master)
        buttons_layout.addWidget(save_btn)
        
        layout.addWidget(buttons)
        
        dialog.exec()
    
    def delete_master(self, master):
        """Удалить мастера"""
        confirm = self.styled_question(
            self,
            "Подтверждение",
            f"Удалить мастера {master['full_name']}?"
        )
        
        if confirm:
            result = self.api.delete_master(master['id'])
            
            if result["success"]:
                QMessageBox.information(self, "Успех", "Мастер удален")
                self.load_masters_table()
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])
    
    def create_services_management_tab(self):
        """Создать вкладку управления услугами"""
        tab = QWidget()
        tab.setStyleSheet(f"background-color: {Colors.BACKGROUND};")
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Управление услугами")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet(f"color: {Colors.PRIMARY};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        add_btn = ModernButton("+ Добавить услугу", "primary")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667EEA, stop:1 #764BA2);
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 24px;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A67D8, stop:1 #6B46C1);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4C51BF, stop:1 #553C9A);
            }}
        """)
        add_btn.clicked.connect(self.show_add_service_dialog)
        header_layout.addWidget(add_btn)
        
        layout.addWidget(header)
        
        # Таблица услуг
        self.services_table = QTableWidget()
        self.services_table.setColumnCount(5)
        self.services_table.setHorizontalHeaderLabels(["ID", "Название", "Цена", "Время (мин)", "Действия"])
        
        # Настраиваем ширину колонок для оптимального отображения
        services_header = self.services_table.horizontalHeader()
        services_header.setStretchLastSection(False)  # Отключаем растягивание последней колонки
        
        # ID - компактная колонка
        services_header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.services_table.setColumnWidth(0, 50)
        
        # Название - растягивается, занимает оставшееся пространство
        services_header.setSectionResizeMode(1, QHeaderView.Stretch)
        services_header.setMinimumSectionSize(200)
        
        # Цена - автоподстройка под содержимое
        services_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        # Время - автоподстройка под содержимое
        services_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        # Действия - фиксированная ширина для двух кнопок
        services_header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.services_table.setColumnWidth(4, 300)
        
        self.services_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.services_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.services_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.services_table)
        
        self.load_services_table()
        
        return tab
    
    def load_services_table(self):
        """Загрузить таблицу услуг"""
        result = self.api.get_services()
        
        if not result["success"]:
            return
        
        services = result["data"]
        self.services_table.setRowCount(len(services))
        
        # Устанавливаем высоту строк для видимости кнопок
        self.services_table.verticalHeader().setDefaultSectionSize(75)
        
        for i, service in enumerate(services):
            self.services_table.setItem(i, 0, QTableWidgetItem(str(service['id'])))
            self.services_table.setItem(i, 1, QTableWidgetItem(service['name']))
            self.services_table.setItem(i, 2, QTableWidgetItem(f"{service['price']} руб."))
            self.services_table.setItem(i, 3, QTableWidgetItem(str(service['duration_minutes'])))
            
            # Кнопки действий - контейнер с выравниванием по правому краю
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(5, 10, 10, 10)  # Вертикальные отступы для центрирования
            actions_layout.setSpacing(8)  # Промежуток между кнопками
            actions_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            edit_btn = QPushButton("Изменить")
            edit_btn.setFixedSize(130, 36)  # Фиксированный размер кнопки
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.PRIMARY};
                    color: white;
                    font-weight: bold;
                    font-size: 13px;
                    border: none;
                    border-radius: 5px;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background-color: {Colors.PRIMARY_DARK};
                }}
                QPushButton:pressed {{
                    background-color: #3730A3;
                }}
            """)
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.clicked.connect(lambda checked, s=service: self.show_edit_service_dialog(s))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("Удалить")
            delete_btn.setFixedSize(130, 36)  # Фиксированный размер кнопки
            delete_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.DANGER};
                    color: white;
                    font-weight: bold;
                    font-size: 13px;
                    border: none;
                    border-radius: 5px;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background-color: #DC2626;
                }}
                QPushButton:pressed {{
                    background-color: #B91C1C;
                }}
            """)
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.clicked.connect(lambda checked, s=service: self.delete_service(s))
            actions_layout.addWidget(delete_btn)
            
            self.services_table.setCellWidget(i, 4, actions)
    
    def show_add_service_dialog(self):
        """Показать диалог добавления услуги"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить услугу")
        dialog.setFixedSize(500, 580)
        dialog.setStyleSheet(f"background-color: {Colors.WHITE};")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Новая услуга")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {Colors.PRIMARY};")
        layout.addWidget(title)
        
        # Название
        name_label = QLabel("Название")
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(name_label)
        
        name_input = ModernInput("Название услуги")
        layout.addWidget(name_input)
        
        # Профессия
        prof_label = QLabel("Профессия")
        prof_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(prof_label)
        
        prof_input = ModernInput("Введите профессию")
        layout.addWidget(prof_input)
        
        # Загружаем профессии для поиска
        result = self.api.get_professions()
        professions = result["data"] if result["success"] else []
        
        # Цена
        price_label = QLabel("Цена (руб.)")
        price_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(price_label)
        
        price_input = QSpinBox()
        price_input.setMinimum(0)
        price_input.setMaximum(100000)
        price_input.setValue(1000)
        price_input.setButtonSymbols(QSpinBox.NoButtons)
        price_input.setMinimumHeight(48)
        price_input.setStyleSheet(f"""
            QSpinBox {{
                padding: 12px;
                border: 2px solid {Colors.BORDER};
                border-radius: 8px;
                font-size: 14px;
                background-color: {Colors.WHITE};
                color: {Colors.TEXT};
            }}
        """)
        layout.addWidget(price_input)
        
        # Время
        time_label = QLabel("Время (мин.)")
        time_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(time_label)
        
        time_input = QSpinBox()
        time_input.setMinimum(15)
        time_input.setMaximum(480)
        time_input.setValue(60)
        time_input.setSingleStep(15)
        time_input.setButtonSymbols(QSpinBox.NoButtons)
        time_input.setMinimumHeight(48)
        time_input.setStyleSheet(f"""
            QSpinBox {{
                padding: 12px;
                border: 2px solid {Colors.BORDER};
                border-radius: 8px;
                font-size: 14px;
                background-color: {Colors.WHITE};
                color: {Colors.TEXT};
            }}
        """)
        layout.addWidget(time_input)
        
        layout.addStretch()
        
        # Кнопки
        buttons = QWidget()
        buttons_layout = QHBoxLayout(buttons)
        
        cancel_btn = ModernButton("Отмена", "secondary")
        cancel_btn.setStyleSheet(f"""
            background-color: {Colors.WHITE};
            color: {Colors.PRIMARY};
            border: 2px solid {Colors.PRIMARY};
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: bold;
        """)
        cancel_btn.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = ModernButton("Сохранить", "primary")
        save_btn.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667EEA, stop:1 #764BA2);
            color: white;
            font-weight: bold;
            font-size: 14px;
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
        """)
        
        def save_service():
            name = name_input.text().strip()
            profession_name = prof_input.text().strip()
            price = price_input.value()
            duration = time_input.value()
            
            if not name:
                QMessageBox.warning(dialog, "Внимание", "Введите название")
                return
            
            # Ищем профессию по имени
            profession_id = None
            for prof in professions:
                if prof['name'].lower() == profession_name.lower():
                    profession_id = prof['id']
                    break
            
            result = self.api.create_service(name, price, duration, profession_id)
            
            if result["success"]:
                self.styled_info(dialog, "Успех", "Услуга добавлена")
                dialog.accept()
                self.load_services_table()
            else:
                QMessageBox.critical(dialog, "Ошибка", result["error"])
        
        save_btn.clicked.connect(save_service)
        buttons_layout.addWidget(save_btn)
        
        layout.addWidget(buttons)
        
        dialog.exec()
    
    def show_edit_service_dialog(self, service):
        """Показать диалог редактирования услуги"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать услугу")
        dialog.setFixedSize(500, 580)
        dialog.setStyleSheet(f"background-color: {Colors.WHITE};")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Редактирование")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {Colors.PRIMARY};")
        layout.addWidget(title)
        
        # Название
        name_label = QLabel("Название")
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(name_label)
        
        name_input = ModernInput()
        name_input.setText(service['name'])
        layout.addWidget(name_input)
        
        # Профессия
        prof_label = QLabel("Профессия")
        prof_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(prof_label)
        
        prof_input = ModernInput()
        # Устанавливаем текущую профессию
        result = self.api.get_professions()
        professions = result["data"] if result["success"] else []
        for prof in professions:
            if prof['id'] == service.get('profession_id'):
                prof_input.setText(prof['name'])
                break
        layout.addWidget(prof_input)
        
        # Цена
        price_label = QLabel("Цена (руб.)")
        price_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(price_label)
        
        price_input = QSpinBox()
        price_input.setMinimum(0)
        price_input.setMaximum(100000)
        price_input.setValue(int(service['price']))
        price_input.setButtonSymbols(QSpinBox.NoButtons)
        price_input.setMinimumHeight(48)
        price_input.setStyleSheet(f"""
            QSpinBox {{
                padding: 12px;
                border: 2px solid {Colors.BORDER};
                border-radius: 8px;
                font-size: 14px;
                background-color: {Colors.WHITE};
                color: {Colors.TEXT};
            }}
        """)
        layout.addWidget(price_input)
        
        # Время
        time_label = QLabel("Время (мин.)")
        time_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(time_label)
        
        time_input = QSpinBox()
        time_input.setMinimum(15)
        time_input.setMaximum(480)
        time_input.setValue(service['duration_minutes'])
        time_input.setSingleStep(15)
        time_input.setButtonSymbols(QSpinBox.NoButtons)
        time_input.setMinimumHeight(48)
        time_input.setStyleSheet(f"""
            QSpinBox {{
                padding: 12px;
                border: 2px solid {Colors.BORDER};
                border-radius: 8px;
                font-size: 14px;
                background-color: {Colors.WHITE};
                color: {Colors.TEXT};
            }}
        """)
        layout.addWidget(time_input)
        
        layout.addStretch()
        
        # Кнопки
        buttons = QWidget()
        buttons_layout = QHBoxLayout(buttons)
        
        cancel_btn = ModernButton("Отмена", "secondary")
        cancel_btn.setStyleSheet(f"""
            background-color: {Colors.WHITE};
            color: {Colors.PRIMARY};
            border: 2px solid {Colors.PRIMARY};
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: bold;
        """)
        cancel_btn.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = ModernButton("Сохранить", "primary")
        save_btn.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667EEA, stop:1 #764BA2);
            color: white;
            font-weight: bold;
            font-size: 14px;
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
        """)
        
        def update_service():
            name = name_input.text().strip()
            profession_name = prof_input.text().strip()
            price = price_input.value()
            duration = time_input.value()
            
            if not name:
                QMessageBox.warning(dialog, "Внимание", "Введите название")
                return
            
            # Ищем профессию по имени
            profession_id = None
            for prof in professions:
                if prof['name'].lower() == profession_name.lower():
                    profession_id = prof['id']
                    break
            
            result = self.api.update_service(service['id'], name, price, duration, profession_id)
            
            if result["success"]:
                self.styled_info(dialog, "Успех", "Услуга обновлена")
                dialog.accept()
                self.load_services_table()
            else:
                QMessageBox.critical(dialog, "Ошибка", result["error"])
        
        save_btn.clicked.connect(update_service)
        buttons_layout.addWidget(save_btn)
        
        layout.addWidget(buttons)
        
        dialog.exec()
    
    def delete_service(self, service):
        """Удалить услугу"""
        confirm = self.styled_question(
            self,
            "Подтверждение",
            f"Удалить услугу {service['name']}?"
        )
        
        if confirm:
            result = self.api.delete_service(service['id'])
            
            if result["success"]:
                QMessageBox.information(self, "Успех", "Услуга удалена")
                self.load_services_table()
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])


def main():
    # Создание приложения
    app = QApplication(sys.argv)
    
    # Fusion стиль для единообразного отображения на всех ОС
    app.setStyle('Fusion')
    
    # Установка кодировки для Windows
    if sys.platform == 'win32':
        import locale
        locale.setlocale(locale.LC_ALL, '')
    
    # Установка шрифта по умолчанию
    default_font = QFont("Arial", 10)
    app.setFont(default_font)
    
    window = BeautyProApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
