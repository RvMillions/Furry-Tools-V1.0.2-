import sys
import os
import shutil
import subprocess
import time
import urllib.request
import json
import zipfile
import ctypes
import re
import winreg
import hashlib
import traceback
import threading
import tempfile
import webbrowser
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QMenu,
                             QMessageBox, QAction, QDialog, QVBoxLayout,
                             QHBoxLayout, QSlider, QSpinBox, QListWidget,
                             QCheckBox, QLineEdit, QPushButton, QGroupBox,
                             QListWidgetItem, QInputDialog, QFileDialog,
                             QProgressDialog, QProgressBar, QDesktopWidget,
                             QScrollArea, QGridLayout, QFrame, QWidgetAction,
                             QComboBox, QSizePolicy, QToolTip, QTabWidget,
                             QSplitter, QApplication)
from PyQt5.QtCore import Qt, QPoint, QUrl, QThread, pyqtSignal, QSize, QTimer, QRect
from PyQt5.QtGui import (QPixmap, QCursor, QDesktopServices, QFont, 
                         QFontDatabase, QIcon, QMovie, QClipboard, QFontMetrics,
                         QColor, QPalette)

try:
    from pypresence import Presence
    PPRESENCE_AVAILABLE = True
except ImportError:
    PPRESENCE_AVAILABLE = False

def get_current_version():
    try:
        version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.txt")
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                version = f.read().strip()
                if version:
                    return version
    except Exception as e:
        print(f"Erreur lecture version.txt: {e}")
    return "1.0.8"

CURRENT_VERSION = get_current_version()
VERSION_URL = "https://raw.githubusercontent.com/RvMillions/Furry-Tools/main/version.txt"
REPO_URL = "https://github.com/RvMillions/Furry-Tools"
API_URL = "https://api.github.com/repos/RvMillions/Furry-Tools/releases/latest"

def global_excepthook(exctype, value, tb):
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    log_dir = os.path.join(os.environ['APPDATA'], 'FurryTools', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f'error_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"Python: {sys.version}\n")
        f.write(f"OS: {sys.platform}\n")
        f.write(f"Erreur: {error_msg}\n")
    try:
        QMessageBox.critical(None, "Erreur inattendue",
                           f"Une erreur est survenue. Un log a été créé :\n{log_file}\n\n{str(value)[:200]}")
    except:
        pass
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = global_excepthook

CONFIG_DIR = os.path.join(os.environ['APPDATA'], 'FurryTools')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
CACHE_FILE = os.path.join(CONFIG_DIR, 'cache.json')
DISCORD_CLIENT_ID = "1482031246463996127"

THEMES = {
    "Gris foncé": {
        'bg_primary': '#2b2b2b',
        'bg_secondary': '#3c3c3c',
        'bg_tertiary': '#4a4a4a',
        'text_primary': '#f0f0f0',
        'text_secondary': '#cccccc',
        'border': '#555555',
        'border_focus': '#6c6c6c',
        'accent': '#5c5c5c',
        'accent_hover': '#6c6c6c'
    },
    "Sombre": {
        'bg_primary': '#1e1e1e',
        'bg_secondary': '#2d2d2d',
        'bg_tertiary': '#3d3d3d',
        'text_primary': '#ffffff',
        'text_secondary': '#e0e0e0',
        'border': '#404040',
        'border_focus': '#606060',
        'accent': '#4a4a4a',
        'accent_hover': '#5a5a5a'
    },
    "Bleu nuit": {
        'bg_primary': '#1a2634',
        'bg_secondary': '#2a3a4c',
        'bg_tertiary': '#3a4e64',
        'text_primary': '#ecf0f1',
        'text_secondary': '#bdc3c7',
        'border': '#34495e',
        'border_focus': '#5d6d7e',
        'accent': '#4a6b8a',
        'accent_hover': '#5a7b9a'
    },
    "Noir": {
        'bg_primary': '#000000',
        'bg_secondary': '#1a1a1a',
        'bg_tertiary': '#2a2a2a',
        'text_primary': '#f0f0f0',
        'text_secondary': '#cccccc',
        'border': '#333333',
        'border_focus': '#555555',
        'accent': '#4a4a4a',
        'accent_hover': '#5a5a5a'
    },
    "Violet profond": {
        'bg_primary': '#2d1b3a',
        'bg_secondary': '#3d2a4a',
        'bg_tertiary': '#4d3a5a',
        'text_primary': '#f0e6ff',
        'text_secondary': '#d4c2e6',
        'border': '#6b4f8c',
        'border_focus': '#8f6eb3',
        'accent': '#7e5aa8',
        'accent_hover': '#9e7ac8'
    },
    "Violet clair": {
        'bg_primary': '#3a2a4a',
        'bg_secondary': '#4a3a5a',
        'bg_tertiary': '#5a4a6a',
        'text_primary': '#ffffff',
        'text_secondary': '#e6d9ff',
        'border': '#8a6cb0',
        'border_focus': '#aa8cd0',
        'accent': '#9a7cc0',
        'accent_hover': '#ba9ce0'
    },
    "Galaxy": {
        'bg_primary': '#0c0b1a',
        'bg_secondary': '#1a1a2e',
        'bg_tertiary': '#2a2a3e',
        'text_primary': '#ffffff',
        'text_secondary': '#b8b8d0',
        'border': '#4a3a6a',
        'border_focus': '#6a4a8a',
        'accent': '#5a3a7a',
        'accent_hover': '#7a4a9a'
    },
    "Galaxy nébuleuse": {
        'bg_primary': '#0f0b1a',
        'bg_secondary': '#1f1a2e',
        'bg_tertiary': '#2f2a3e',
        'text_primary': '#f0e6ff',
        'text_secondary': '#c2b8d0',
        'border': '#5a3a6a',
        'border_focus': '#7a4a8a',
        'accent': '#6a3a7a',
        'accent_hover': '#8a4a9a'
    },
    "Galaxy profond": {
        'bg_primary': '#0a0b1a',
        'bg_secondary': '#1a1b2a',
        'bg_tertiary': '#2a2b3a',
        'text_primary': '#e0e0ff',
        'text_secondary': '#b0b0d0',
        'border': '#3a3a5a',
        'border_focus': '#5a5a7a',
        'accent': '#4a4a6a',
        'accent_hover': '#6a6a8a'
    },
    "Rose bonbon": {
        'bg_primary': '#3a1a2a',
        'bg_secondary': '#4a2a3a',
        'bg_tertiary': '#5a3a4a',
        'text_primary': '#ffe6f0',
        'text_secondary': '#ffccdd',
        'border': '#d48cb0',
        'border_focus': '#e4acd0',
        'accent': '#b46c90',
        'accent_hover': '#d48cb0'
    },
    "Vert forêt": {
        'bg_primary': '#1a2a1a',
        'bg_secondary': '#2a3a2a',
        'bg_tertiary': '#3a4a3a',
        'text_primary': '#e0f0e0',
        'text_secondary': '#b0d0b0',
        'border': '#4a6a4a',
        'border_focus': '#6a8a6a',
        'accent': '#5a7a5a',
        'accent_hover': '#7a9a7a'
    },
    "Rouge rubis": {
        'bg_primary': '#2a1a1a',
        'bg_secondary': '#3a2a2a',
        'bg_tertiary': '#4a3a3a',
        'text_primary': '#ffe6e6',
        'text_secondary': '#ffcccc',
        'border': '#b46c6c',
        'border_focus': '#d48c8c',
        'accent': '#a45c5c',
        'accent_hover': '#c47c7c'
    }
}

os.makedirs(CONFIG_DIR, exist_ok=True)

def load_config():
    default_config = {
        'icon_size': 150,
        'private_games': [],
        'logo_path': '',
        'enable_discord_rpc': False,
        'font_size': 10,
        'font_family': 'Segoe UI',
        'grid_columns': 2,
        'grid_width': 400,
        'grid_max_height': 500,
        'button_min_width': 180,
        'button_max_width': 250,
        'button_height': 40,
        'name_max_length': 40,
        'dialog_width': 600,
        'dialog_height': 600,
        'theme': 'Gris foncé',
        'start_with_windows': False,
        'auto_launch_steam': False,
        'auto_check_updates': True,
        'auto_add_all_dlc': False
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                config.pop('private_password_hash', None)
                config.pop('discord_client_id', None)
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
        except Exception as e:
            return default_config
    return default_config

def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config_copy = config.copy()
    config_copy.pop('private_password_hash', None)
    config_copy.pop('discord_client_id', None)
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_copy, f, indent=4)
    except Exception as e:
        pass

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=4)
    except Exception as e:
        pass

def get_scaled_font(base_size=10, base_family='Segoe UI'):
    screen = QApplication.primaryScreen()
    if not screen:
        return QFont(base_family, base_size)
    dpi = screen.logicalDotsPerInch()
    scale_factor = dpi / 96.0
    if scale_factor < 1.0:
        scale_factor = 1.0
    scaled_size = max(8, int(base_size * scale_factor))
    return QFont(base_family, scaled_size)

def get_scaled_size(base_width, base_height, config=None):
    screen = QApplication.primaryScreen()
    if not screen:
        return base_width, base_height
    rect = screen.availableGeometry()
    if config and 'dialog_width' in config:
        base_width = config['dialog_width']
        base_height = config['dialog_height']
    return base_width, base_height

def center_window(window):
    frame = window.frameGeometry()
    screen = QApplication.primaryScreen().availableGeometry().center()
    frame.moveCenter(screen)
    window.move(frame.topLeft())

def get_theme_stylesheet(theme_name):
    theme = THEMES.get(theme_name, THEMES["Gris foncé"])
    return f"""
        QDialog, QMainWindow, QWidget {{
            background-color: {theme['bg_primary']};
            color: {theme['text_primary']};
        }}
        QGroupBox {{
            color: {theme['text_primary']};
            border: 2px solid {theme['border']};
            border-radius: 6px;
            margin-top: 8px;
            font-weight: bold;
            padding-top: 8px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
        }}
        QListWidget, QTextEdit, QPlainTextEdit {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            border-radius: 4px;
            padding: 4px;
        }}
        QPushButton {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            border-radius: 4px;
            padding: 6px 12px;
            font-weight: normal;
        }}
        QPushButton:hover {{
            background-color: {theme['accent_hover']};
            border: 1px solid {theme['border_focus']};
        }}
        QPushButton:pressed {{
            background-color: {theme['accent']};
        }}
        QPushButton:disabled {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_secondary']};
            border: 1px solid {theme['border']};
        }}
        QSlider::groove:horizontal {{
            height: 6px;
            background: {theme['bg_secondary']};
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: {theme['text_primary']};
            width: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }}
        QSpinBox, QDoubleSpinBox, QLineEdit {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            border-radius: 4px;
            padding: 4px;
            min-width: 50px;
        }}
        QCheckBox {{
            color: {theme['text_primary']};
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {theme['border']};
            border-radius: 4px;
            background-color: {theme['bg_secondary']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {theme['accent']};
            border: 2px solid {theme['border_focus']};
            image: none;
        }}
        QCheckBox::indicator:checked:hover {{
            background-color: {theme['accent_hover']};
        }}
        QCheckBox::indicator:unchecked:hover {{
            border: 2px solid {theme['border_focus']};
            background-color: {theme['bg_tertiary']};
        }}
        QComboBox {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            border-radius: 4px;
            padding: 4px;
            min-width: 80px;
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid {theme['text_primary']};
            width: 0;
            height: 0;
            margin-right: 4px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            selection-background-color: {theme['accent']};
        }}
        QLabel {{
            color: {theme['text_primary']};
        }}
        QTabWidget::pane {{
            border: 2px solid {theme['border']};
            border-radius: 6px;
            background-color: {theme['bg_primary']};
        }}
        QTabBar::tab {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 6px 12px;
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background-color: {theme['bg_primary']};
            border-bottom: 2px solid {theme['accent']};
        }}
        QTabBar::tab:hover {{
            background-color: {theme['accent_hover']};
        }}
        QScrollArea {{
            border: none;
            background-color: {theme['bg_primary']};
        }}
        QScrollBar:vertical {{
            background-color: {theme['bg_secondary']};
            width: 10px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {theme['accent']};
            border-radius: 5px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {theme['accent_hover']};
        }}
        QScrollBar:horizontal {{
            background-color: {theme['bg_secondary']};
            height: 10px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {theme['accent']};
            border-radius: 5px;
            min-width: 20px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {theme['accent_hover']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
        }}
    """

def add_to_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_SET_VALUE)
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
        winreg.SetValueEx(key, "FurryTools", 0, winreg.REG_SZ, f'"{exe_path}"')
        winreg.CloseKey(key)
        return True
    except Exception as e:
        return False

def remove_from_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "FurryTools")
        winreg.CloseKey(key)
        return True
    except Exception as e:
        return False

def is_in_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_READ)
        winreg.QueryValueEx(key, "FurryTools")
        winreg.CloseKey(key)
        return True
    except:
        return False

class GameDLCDownloadThread(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list, list, list)
    error = pyqtSignal(str)
    
    def __init__(self, game_appid, target_folder):
        super().__init__()
        self.game_appid = game_appid
        self.target_folder = target_folder
        
    def run(self):
        added_dlcs = []
        skipped_dlcs = []
        failed_dlcs = []
        try:
            url = f"https://store.steampowered.com/api/appdetails?appids={self.game_appid}&l=french"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                if data.get(self.game_appid, {}).get('success'):
                    game_data = data[self.game_appid]['data']
                    if game_data.get('dlc'):
                        total_dlcs = len(game_data['dlc'])
                        steamtools_file = os.path.join(self.target_folder, "Steamtools.lua")
                        
                        existing_lines = []
                        if os.path.exists(steamtools_file):
                            with open(steamtools_file, 'r', encoding='utf-8') as f:
                                existing_lines = f.read().splitlines()
                        
                        for i, dlc_id in enumerate(game_data['dlc']):
                            percent = int((i + 1) * 100 / total_dlcs)
                            self.progress.emit(percent, f"Vérification DLC {dlc_id}...")
                            
                            line_to_add = f"addappid({dlc_id}, 1)"
                            
                            if line_to_add not in existing_lines:
                                try:
                                    with open(steamtools_file, 'a', encoding='utf-8') as f:
                                        f.write(line_to_add + "\n")
                                    added_dlcs.append(str(dlc_id))
                                    self.progress.emit(percent, f"Ajouté DLC {dlc_id}")
                                except Exception as e:
                                    failed_dlcs.append(str(dlc_id))
                                    self.progress.emit(percent, f"Échec DLC {dlc_id}")
                            else:
                                skipped_dlcs.append(str(dlc_id))
                                self.progress.emit(percent, f"DLC {dlc_id} déjà présent")
            self.finished.emit(added_dlcs, skipped_dlcs, failed_dlcs)
        except Exception as e:
            self.error.emit(str(e))

class SelectGameForDLCDialog(QDialog):
    def __init__(self, parent, config, target_folder, games_with_dlc_status, game_names):
        super().__init__(parent)
        self.parent = parent
        self.config = config
        self.target_folder = target_folder
        self.games_with_dlc_status = games_with_dlc_status
        self.game_names = game_names
        self.selected_games = []
        
        theme = self.config.get('theme', 'Gris foncé')
        self.setStyleSheet(get_theme_stylesheet(theme))
        self.setWindowTitle("Sélectionner les jeux pour ajouter les DLC")
        self.setModal(True)
        width, height = get_scaled_size(600, 500)
        self.resize(width, height)
        self.initUI()
        center_window(self)
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        info_label = QLabel("Sélectionnez les jeux pour lesquels vous voulez ajouter tous les DLC manquants :")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        self.games_list = QListWidget()
        self.games_list.setSelectionMode(QListWidget.MultiSelection)
        theme = self.config.get('theme', 'Gris foncé')
        theme_colors = THEMES.get(theme, THEMES["Gris foncé"])
        self.games_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {theme_colors['bg_secondary']};
                color: {theme_colors['text_primary']};
                border: 1px solid {theme_colors['border']};
                border-radius: 4px;
                padding: 4px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {theme_colors['border']};
                color: {theme_colors['text_primary']};
                background-color: {theme_colors['bg_secondary']};
            }}
            QListWidget::item:selected {{
                background-color: {theme_colors['accent']};
                color: {theme_colors['text_primary']};
            }}
            QListWidget::item:hover {{
                background-color: {theme_colors['accent_hover']};
            }}
        """)
        
        for appid, (name, missing_count) in self.games_with_dlc_status.items():
            item = QListWidgetItem(f"{name} (APPID: {appid}) - {missing_count} DLC manquant(s)")
            item.setData(Qt.UserRole, appid)
            self.games_list.addItem(item)
        
        layout.addWidget(self.games_list)
        
        select_buttons_layout = QHBoxLayout()
        select_all_btn = QPushButton("Tout sélectionner")
        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn = QPushButton("Tout désélectionner")
        deselect_all_btn.clicked.connect(self.deselect_all)
        select_buttons_layout.addStretch()
        select_buttons_layout.addWidget(select_all_btn)
        select_buttons_layout.addWidget(deselect_all_btn)
        select_buttons_layout.addStretch()
        layout.addLayout(select_buttons_layout)
        
        buttons_layout = QHBoxLayout()
        add_btn = QPushButton("Ajouter les DLC sélectionnés")
        add_btn.setMinimumWidth(150)
        add_btn.clicked.connect(self.add_selected_dlcs)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def select_all(self):
        self.games_list.selectAll()
    
    def deselect_all(self):
        self.games_list.clearSelection()
    
    def add_selected_dlcs(self):
        self.selected_games = []
        for item in self.games_list.selectedItems():
            appid = item.data(Qt.UserRole)
            if appid:
                self.selected_games.append(appid)
        
        if not self.selected_games:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner au moins un jeu.")
            return
        
        self.accept()

class SteamDLCSearchThread(QThread):
    results_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        results = []
        try:
            import urllib.parse
            encoded_query = urllib.parse.quote(self.query)
            
            url = f"https://store.steampowered.com/api/storesearch/?term={encoded_query}&l=french&cc=fr"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                if data.get('items'):
                    for item in data['items']:
                        if item.get('type') == 'dlc':
                            results.append({
                                'appid': str(item['id']),
                                'name': item['name'],
                                'type': 'dlc'
                            })
                        elif item.get('type') == 'game':
                            appid = str(item['id'])
                            try:
                                dlc_url = f"https://store.steampowered.com/api/appdetails?appids={appid}&l=french"
                                req_dlc = urllib.request.Request(dlc_url, headers={'User-Agent': 'Mozilla/5.0'})
                                with urllib.request.urlopen(req_dlc, timeout=3) as response_dlc:
                                    data_dlc = json.loads(response_dlc.read().decode())
                                    if data_dlc.get(appid, {}).get('success'):
                                        game_data = data_dlc[appid]['data']
                                        if game_data.get('dlc'):
                                            for dlc_id in game_data['dlc']:
                                                results.append({
                                                    'appid': str(dlc_id),
                                                    'name': f"DLC {dlc_id}",
                                                    'type': 'dlc'
                                                })
                            except:
                                pass
                else:
                    url = f"https://store.steampowered.com/api/appdetails?appids={encoded_query}&l=french"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=3) as response:
                        data = json.loads(response.read().decode())
                        for appid, app_data in data.items():
                            if app_data.get('success'):
                                if app_data['data'].get('type') == 'dlc':
                                    results.append({
                                        'appid': appid,
                                        'name': app_data['data'].get('name', appid),
                                        'type': 'dlc'
                                    })
        except Exception as e:
            self.error_occurred.emit(str(e))
        
        if not results:
            try:
                import urllib.parse
                encoded_query = urllib.parse.quote(self.query)
                search_url = f"https://store.steampowered.com/search/?term={encoded_query}&category1=21&l=french"
                req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    html = response.read().decode('utf-8', errors='ignore')
                    appid_pattern = r'data-ds-appid="(\d+)"'
                    name_pattern = r'class="title"[^>]*>([^<]+)</span>'
                    appids = re.findall(appid_pattern, html)
                    names = re.findall(name_pattern, html)
                    for i, appid in enumerate(appids):
                        if i < len(names):
                            results.append({
                                'appid': appid,
                                'name': names[i].strip(),
                                'type': 'dlc'
                            })
            except Exception as e:
                pass
        
        self.results_ready.emit(results)

class DLCSearchDialog(QDialog):
    def __init__(self, parent, config, target_folder):
        super().__init__(parent)
        self.parent = parent
        self.config = config
        self.target_folder = target_folder
        self.search_thread = None
        theme = self.config.get('theme', 'Gris foncé')
        self.setStyleSheet(get_theme_stylesheet(theme))
        self.setWindowTitle("Recherche de DLC")
        self.setModal(True)
        width, height = get_scaled_size(700, 600)
        self.resize(width, height)
        self.initUI()
        center_window(self)

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        search_group = QGroupBox("Recherche")
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(10, 10, 10, 10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tapez le nom d'un jeu ou d'un DLC...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_input)
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        results_group = QGroupBox("Résultats")
        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(10, 10, 10, 10)
        self.results_list = QListWidget()
        self.results_list.setAlternatingRowColors(True)
        self.results_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        theme = self.config.get('theme', 'Gris foncé')
        theme_colors = THEMES.get(theme, THEMES["Gris foncé"])
        self.results_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {theme_colors['bg_secondary']};
                color: {theme_colors['text_primary']};
                border: 1px solid {theme_colors['border']};
                border-radius: 4px;
                padding: 4px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {theme_colors['border']};
                color: {theme_colors['text_primary']};
                background-color: {theme_colors['bg_secondary']};
            }}
            QListWidget::item:selected {{
                background-color: {theme_colors['accent']};
                color: {theme_colors['text_primary']};
            }}
            QListWidget::item:hover {{
                background-color: {theme_colors['accent_hover']};
            }}
        """)
        results_layout.addWidget(self.results_list)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        info_label = QLabel("Double-cliquez sur un DLC pour l'ajouter au fichier Steamtools.lua")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        self.setLayout(layout)

    def on_search_text_changed(self, text):
        if len(text) < 2:
            self.results_list.clear()
            self.status_label.setText("")
            return
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.terminate()
            self.search_thread.wait()
        self.status_label.setText("Recherche en cours...")
        self.search_thread = SteamDLCSearchThread(text)
        self.search_thread.results_ready.connect(self.display_results)
        self.search_thread.error_occurred.connect(self.on_search_error)
        self.search_thread.start()

    def display_results(self, results):
        self.results_list.clear()
        if not results:
            self.status_label.setText("Aucun DLC trouvé. Essayez un autre terme.")
            return
        self.status_label.setText(f"{len(results)} DLC trouvé(s).")
        for dlc in results:
            display_text = f"{dlc['name']} (APPID: {dlc['appid']})"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, dlc)
            self.results_list.addItem(item)

    def on_search_error(self, error_msg):
        self.status_label.setText(f"Erreur: {error_msg}")

    def on_item_double_clicked(self, item):
        dlc = item.data(Qt.UserRole)
        if not dlc:
            return

        if not self.target_folder or not os.path.exists(self.target_folder):
            QMessageBox.warning(self, "Erreur", 
                "Le dossier SteamTools n'existe pas.\nVeuillez installer SteamTools d'abord.")
            return

        steamtools_file = os.path.join(self.target_folder, "Steamtools.lua")
        appid = dlc['appid']

        existing_lines = []
        if os.path.exists(steamtools_file):
            with open(steamtools_file, 'r', encoding='utf-8') as f:
                existing_lines = f.read().splitlines()

        line_to_add = f"addappid({appid}, 1)"
        if line_to_add in existing_lines:
            QMessageBox.information(self, "Déjà présent", 
                f"Le DLC {dlc['name']} (APPID: {appid}) est déjà dans le fichier.")
            return

        try:
            with open(steamtools_file, 'a', encoding='utf-8') as f:
                f.write(line_to_add + "\n")
            QMessageBox.information(self, "Succès", 
                f"DLC ajouté avec succès !\n{line_to_add}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'écrire dans le fichier: {e}")

class UpdateChecker(QThread):
    update_checked = pyqtSignal(bool, str, str)
    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version
    def run(self):
        try:
            req = urllib.request.Request(VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                latest_version = response.read().decode().strip()
                has_update = self.compare_versions(latest_version, self.current_version)
                self.update_checked.emit(has_update, latest_version, self.current_version)
        except Exception as e:
            self.update_checked.emit(False, self.current_version, self.current_version)
    def compare_versions(self, v1, v2):
        try:
            v1_parts = [int(x) for x in v1.split('.')]
            v2_parts = [int(x) for x in v2.split('.')]
            for i in range(max(len(v1_parts), len(v2_parts))):
                v1_val = v1_parts[i] if i < len(v1_parts) else 0
                v2_val = v2_parts[i] if i < len(v2_parts) else 0
                if v1_val > v2_val:
                    return True
                elif v1_val < v2_val:
                    return False
            return False
        except:
            return False

class UpdateDownloader(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    def __init__(self, download_url, save_path):
        super().__init__()
        self.download_url = download_url
        self.save_path = save_path
    def run(self):
        try:
            req = urllib.request.Request(self.download_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                chunk_size = 8192
                with open(self.save_path, 'wb') as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = int(downloaded * 100 / total_size)
                            self.progress.emit(percent)
            self.finished.emit(self.save_path)
        except Exception as e:
            self.error.emit(str(e))

class SteamSearchThread(QThread):
    results_ready = pyqtSignal(list)
    def __init__(self, query):
        super().__init__()
        self.query = query
    def run(self):
        results = []
        try:
            import urllib.parse
            encoded_query = urllib.parse.quote(self.query)
            url = f"https://store.steampowered.com/api/storesearch/?term={encoded_query}&l=english&cc=us"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                if data.get('items'):
                    for item in data['items']:
                        results.append({
                            'appid': str(item['id']),
                            'name': item['name'],
                            'price': item.get('price', {}).get('final_formatted', 'Gratuit'),
                            'type': item.get('type', 'game')
                        })
        except Exception as e:
            print(f"Erreur recherche Steam: {e}")
        self.results_ready.emit(results)

class SearchDialog(QDialog):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.parent = parent
        self.config = config
        self.search_thread = None
        theme = self.config.get('theme', 'Gris foncé')
        self.setStyleSheet(get_theme_stylesheet(theme))
        self.setWindowTitle("Recherche de jeux Steam")
        self.setModal(True)
        width, height = get_scaled_size(600, 500)
        self.resize(width, height)
        self.initUI()
        center_window(self)

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tapez le nom d'un jeu (les espaces sont acceptés)...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_input)
        self.results_list = QListWidget()
        self.results_list.setAlternatingRowColors(True)
        theme = self.config.get('theme', 'Gris foncé')
        theme_colors = THEMES.get(theme, THEMES["Gris foncé"])
        self.results_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {theme_colors['bg_secondary']};
                color: {theme_colors['text_primary']};
                border: 1px solid {theme_colors['border']};
                border-radius: 4px;
                padding: 4px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 6px;
                border-bottom: 1px solid {theme_colors['border']};
                color: {theme_colors['text_primary']};
                background-color: {theme_colors['bg_secondary']};
            }}
            QListWidget::item:selected {{
                background-color: {theme_colors['accent']};
                color: {theme_colors['text_primary']};
            }}
            QListWidget::item:hover {{
                background-color: {theme_colors['accent_hover']};
            }}
            QListWidget::item:alternate {{
                background-color: {theme_colors['bg_tertiary']};
            }}
        """)
        self.results_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addLayout(search_layout)
        layout.addWidget(self.results_list)
        info_label = QLabel("Double-cliquez sur un jeu pour voir les options")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        self.setLayout(layout)

    def on_search_text_changed(self, text):
        if len(text) < 3:
            self.results_list.clear()
            return
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.terminate()
            self.search_thread.wait()
        self.search_thread = SteamSearchThread(text)
        self.search_thread.results_ready.connect(self.display_results)
        self.search_thread.start()

    def display_results(self, results):
        self.results_list.clear()
        if not results:
            item = QListWidgetItem("Aucun résultat trouvé")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.results_list.addItem(item)
            return
        for game in results:
            display_text = f"{game['name']} (APPID: {game['appid']})"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, game)
            self.results_list.addItem(item)

    def on_item_double_clicked(self, item):
        game = item.data(Qt.UserRole)
        if not game:
            return
        menu = QMenu(self)
        copy_appid_action = QAction("Copier l'APPID", menu)
        copy_appid_action.triggered.connect(lambda: self.copy_appid(game['appid']))
        menu.addAction(copy_appid_action)
        copy_command_action = QAction("Copier la commande /gen", menu)
        copy_command_action.triggered.connect(lambda: self.copy_command(game['appid']))
        menu.addAction(copy_command_action)
        steamdb_action = QAction("Ouvrir dans SteamDB", menu)
        steamdb_action.triggered.connect(lambda: self.open_steamdb(game['appid']))
        menu.addAction(steamdb_action)
        
        if self.config.get('auto_add_all_dlc', False):
            add_all_dlc_action = QAction("Ajouter tous les DLC", menu)
            add_all_dlc_action.triggered.connect(lambda: self.add_all_dlc_for_game(game['appid']))
            menu.addAction(add_all_dlc_action)
        
        menu.exec_(QCursor.pos())

    def copy_appid(self, appid):
        clipboard = QApplication.clipboard()
        clipboard.setText(appid)
        QMessageBox.information(self, "Copié", f"APPID {appid} copié dans le presse-papiers")

    def copy_command(self, appid):
        clipboard = QApplication.clipboard()
        clipboard.setText(f"/gen appid:{appid}")
        QMessageBox.information(self, "Copié", f"Commande /gen appid:{appid} copiée dans le presse-papiers")

    def open_steamdb(self, appid):
        url = QUrl(f"https://steamdb.info/app/{appid}/")
        QDesktopServices.openUrl(url)
    
    def add_all_dlc_for_game(self, game_appid):
        if not hasattr(self.parent, 'target_folder') or not self.parent.target_folder:
            QMessageBox.warning(self, "Erreur", "Le dossier SteamTools n'existe pas.")
            return
        
        self.dlc_thread = GameDLCDownloadThread(game_appid, self.parent.target_folder)
        self.progress_dialog = QProgressDialog("Récupération des DLC...", "Annuler", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setAutoReset(True)
        self.progress_dialog.setMinimumWidth(350)
        self.progress_dialog.canceled.connect(self.dlc_thread.terminate)
        self.dlc_thread.progress.connect(self.on_dlc_progress)
        self.dlc_thread.finished.connect(self.on_dlc_finished)
        self.dlc_thread.error.connect(self.on_dlc_error)
        self.dlc_thread.start()
    
    def on_dlc_progress(self, value, message):
        self.progress_dialog.setValue(value)
        self.progress_dialog.setLabelText(message)
    
    def on_dlc_finished(self, added_dlcs, skipped_dlcs, failed_dlcs):
        self.progress_dialog.close()
        if added_dlcs:
            msg = f"{len(added_dlcs)} DLC ajoutés avec succès.\n"
            if skipped_dlcs:
                msg += f"{len(skipped_dlcs)} DLC déjà présents.\n"
            if failed_dlcs:
                msg += f"{len(failed_dlcs)} DLC ont échoué."
            QMessageBox.information(self, "Succès", msg)
        else:
            QMessageBox.information(self, "Info", "Aucun DLC trouvé pour ce jeu.")
    
    def on_dlc_error(self, error_msg):
        self.progress_dialog.close()
        QMessageBox.critical(self, "Erreur", f"Erreur lors de la récupération des DLC:\n{error_msg}")

class NameFetcher(QThread):
    names_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, appids):
        super().__init__()
        self.appids = appids

    def run(self):
        result = {}
        for appid in self.appids:
            if appid.isdigit():
                try:
                    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as response:
                        data = json.loads(response.read().decode())
                        if data.get(appid, {}).get('success'):
                            name = data[appid]['data']['name']
                            result[appid] = name
                        else:
                            result[appid] = appid
                except Exception as e:
                    result[appid] = appid
            else:
                result[appid] = appid
        self.names_ready.emit(result)

class ZipCreationThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, file_paths, zip_name, download_folder):
        super().__init__()
        self.file_paths = file_paths
        self.zip_name = zip_name
        self.download_folder = download_folder

    def run(self):
        try:
            zip_path = os.path.join(self.download_folder, self.zip_name)
            total = len(self.file_paths)
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for i, file_path in enumerate(self.file_paths):
                    if os.path.exists(file_path):
                        zipf.write(file_path, os.path.basename(file_path))
                    self.progress.emit(int((i+1)/total*100))
            self.finished.emit(zip_path)
        except Exception as e:
            self.error.emit(str(e))

class ZipExtractThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, zip_path, target_folder):
        super().__init__()
        self.zip_path = zip_path
        self.target_folder = target_folder

    def run(self):
        try:
            extracted = []
            with zipfile.ZipFile(self.zip_path, 'r') as zipf:
                members = [m for m in zipf.namelist() if m.lower().endswith('.lua')]
                total = len(members)
                for i, member in enumerate(members):
                    zipf.extract(member, self.target_folder)
                    extracted.append(member)
                    self.progress.emit(int((i+1)/total*100))
            self.finished.emit(extracted)
        except Exception as e:
            self.error.emit(str(e))

class GameGridMenu(QMenu):
    def __init__(self, title, parent=None, config=None):
        super().__init__(title, parent)
        self.config = config if config else {}
        theme = self.config.get('theme', 'Gris foncé')
        theme_colors = THEMES.get(theme, THEMES["Gris foncé"])
        
        self.setStyleSheet(f"""
            QMenu {{
                background-color: {theme_colors['bg_primary']};
                border: 2px solid {theme_colors['border']};
                border-radius: 10px;
                padding: 10px;
            }}
            QMenu::item {{
                background-color: transparent;
                color: {theme_colors['text_primary']};
            }}
            QMenu::item:selected {{
                background-color: {theme_colors['bg_secondary']};
            }}
        """)
        
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet(f"background-color: {theme_colors['bg_primary']};")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(8)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.grid_widget)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {theme_colors['bg_primary']};
            }}
            QScrollBar:vertical {{
                background-color: {theme_colors['bg_secondary']};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {theme_colors['accent']};
                border-radius: 5px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {theme_colors['accent_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
            QScrollBar:horizontal {{
                height: 0px;
            }}
        """)
        
        grid_width = self.config.get('grid_width', 400)
        grid_max_height = self.config.get('grid_max_height', 500)
        self.scroll.setMinimumWidth(grid_width - 20)
        self.scroll.setMaximumWidth(grid_width)
        self.scroll.setMaximumHeight(grid_max_height)
        
        action = QWidgetAction(self)
        action.setDefaultWidget(self.scroll)
        self.addAction(action)
        
        self.game_buttons = []
        
    def add_game(self, appid, display_name, parent_window, font_size=10, font_family='Segoe UI'):
        from PyQt5.QtWidgets import QPushButton
        
        short_name = display_name
        max_len = self.config.get('name_max_length', 40)
        if len(short_name) > max_len:
            short_name = short_name[:max_len-3] + "..."
        
        btn = QPushButton(short_name)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setToolTip(display_name)
        
        font = QFont(font_family, font_size)
        btn.setFont(font)
        
        btn_min_width = self.config.get('button_min_width', 180)
        btn_max_width = self.config.get('button_max_width', 250)
        btn_height = self.config.get('button_height', 40)
        
        btn.setMinimumWidth(btn_min_width)
        btn.setMaximumWidth(btn_max_width)
        btn.setMinimumHeight(btn_height)
        
        theme = self.config.get('theme', 'Gris foncé')
        theme_colors = THEMES.get(theme, THEMES["Gris foncé"])
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_colors['bg_secondary']};
                color: {theme_colors['text_primary']};
                border: 1px solid {theme_colors['border']};
                border-radius: 4px;
                padding: 8px;
                text-align: left;
                font-size: {font_size}px;
                font-family: '{font_family}';
            }}
            QPushButton:hover {{
                background-color: {theme_colors['accent_hover']};
                border: 1px solid {theme_colors['border_focus']};
            }}
            QPushButton:pressed {{
                background-color: {theme_colors['accent']};
            }}
        """)
        
        def show_game_menu():
            menu = QMenu(btn)
            menu.setStyleSheet(f"""
                QMenu {{
                    background-color: {theme_colors['bg_primary']};
                    color: {theme_colors['text_primary']};
                    border: 2px solid {theme_colors['border']};
                    border-radius: 6px;
                    padding: 5px;
                    font-size: {font_size}px;
                    font-family: '{font_family}';
                }}
                QMenu::item {{
                    padding: 6px 15px;
                    border-radius: 3px;
                    color: {theme_colors['text_primary']};
                }}
                QMenu::item:selected {{
                    background-color: {theme_colors['bg_secondary']};
                }}
            """)
            
            delete_action = QAction("Supprimer", menu)
            delete_action.triggered.connect(lambda: parent_window.delete_game(appid))
            menu.addAction(delete_action)
            
            steamdb_action = QAction("SteamDB", menu)
            steamdb_action.triggered.connect(lambda: parent_window.open_steamdb(appid))
            menu.addAction(steamdb_action)
            
            if parent_window.config.get('auto_add_all_dlc', False):
                add_dlc_action = QAction("Ajouter tous les DLC", menu)
                add_dlc_action.triggered.connect(lambda: parent_window.add_all_dlc_for_game(appid))
                menu.addAction(add_dlc_action)
            
            menu.exec_(btn.mapToGlobal(QPoint(0, btn.height())))
        
        btn.clicked.connect(show_game_menu)
        
        self.game_buttons.append((appid, btn, display_name))
        
    def layout_games(self):
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        
        if not self.game_buttons:
            return
        
        max_cols = self.config.get('grid_columns', 2)
        
        row = 0
        col = 0
        
        for appid, btn, full_name in self.game_buttons:
            self.grid_layout.addWidget(btn, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

class SettingsDialog(QDialog):
    def __init__(self, parent, config, all_appids, known_names):
        super().__init__(parent)
        self.parent = parent
        self.config = config.copy()
        self.all_appids = all_appids
        self.known_names = known_names.copy()
        self.name_fetcher = None
        self.update_checker = None
        self.update_downloader = None
        self.latest_version = None
        self.game_names = known_names.copy()
        
        width = self.config.get('dialog_width', 600)
        height = self.config.get('dialog_height', 600)
        self.resize(width, height)
        
        self.setWindowTitle("Paramètres")
        self.setModal(True)
        self.initUI()
        self.fetch_missing_names()
        center_window(self)

    def initUI(self):
        theme = self.config.get('theme', 'Gris foncé')
        self.setStyleSheet(get_theme_stylesheet(theme))
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        tabs = QTabWidget()
        
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        general_layout.setSpacing(10)
        
        size_group = QGroupBox("Taille du logo")
        size_layout = QHBoxLayout()
        size_layout.setContentsMargins(10, 10, 10, 10)
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(50, 300)
        self.size_slider.setValue(self.config['icon_size'])
        self.size_spin = QSpinBox()
        self.size_spin.setRange(50, 300)
        self.size_spin.setValue(self.config['icon_size'])
        self.size_slider.valueChanged.connect(self.size_spin.setValue)
        self.size_spin.valueChanged.connect(self.size_slider.setValue)
        size_layout.addWidget(self.size_slider)
        size_layout.addWidget(self.size_spin)
        size_group.setLayout(size_layout)
        general_layout.addWidget(size_group)

        font_group = QGroupBox("Police d'écriture")
        font_layout = QGridLayout()
        font_layout.setContentsMargins(10, 10, 10, 10)
        font_layout.setSpacing(8)
        
        font_family_label = QLabel("Famille :")
        font_family_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_layout.addWidget(font_family_label, 0, 0)
        
        self.font_family_combo = QComboBox()
        font_families = QFontDatabase().families()
        self.font_family_combo.addItems(font_families)
        index = self.font_family_combo.findText(self.config.get('font_family', 'Segoe UI'))
        if index >= 0:
            self.font_family_combo.setCurrentIndex(index)
        font_layout.addWidget(self.font_family_combo, 0, 1, 1, 2)
        
        font_size_label = QLabel("Taille :")
        font_size_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_layout.addWidget(font_size_label, 1, 0)
        
        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(8, 16)
        self.font_size_slider.setValue(self.config.get('font_size', 10))
        font_layout.addWidget(self.font_size_slider, 1, 1)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 16)
        self.font_size_spin.setValue(self.config.get('font_size', 10))
        self.font_size_slider.valueChanged.connect(self.font_size_spin.setValue)
        self.font_size_spin.valueChanged.connect(self.font_size_slider.setValue)
        font_layout.addWidget(self.font_size_spin, 1, 2)
        
        preview_label = QLabel("Aperçu :")
        preview_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_layout.addWidget(preview_label, 2, 0)
        
        self.preview_text = QLabel("Furry Tools - Jeux")
        self.preview_text.setStyleSheet("background-color: #3c3c3c; padding: 4px; border-radius: 3px;")
        font_layout.addWidget(self.preview_text, 2, 1, 1, 2)
        
        font_group.setLayout(font_layout)
        general_layout.addWidget(font_group)

        theme_group = QGroupBox("Thème")
        theme_layout = QHBoxLayout()
        theme_layout.setContentsMargins(10, 10, 10, 10)
        
        theme_label = QLabel("Thème :")
        theme_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()))
        self.theme_combo.setCurrentText(self.config.get('theme', 'Gris foncé'))
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        
        theme_layout.addStretch()
        theme_group.setLayout(theme_layout)
        general_layout.addWidget(theme_group)

        logo_group = QGroupBox("Logo personnalisé")
        logo_layout = QVBoxLayout()
        logo_layout.setContentsMargins(10, 10, 10, 10)
        logo_layout.setSpacing(8)
        self.logo_label = QLabel()
        self.update_logo_display()
        logo_layout.addWidget(self.logo_label)
        
        change_logo_btn = QPushButton("Changer le logo...")
        change_logo_btn.clicked.connect(self.change_logo)
        logo_layout.addWidget(change_logo_btn)
        
        reset_logo_btn = QPushButton("Restaurer le logo par défaut")
        reset_logo_btn.clicked.connect(self.reset_logo)
        logo_layout.addWidget(reset_logo_btn)
        
        logo_group.setLayout(logo_layout)
        general_layout.addWidget(logo_group)

        dlc_group = QGroupBox("Options DLC")
        dlc_layout = QVBoxLayout()
        dlc_layout.setContentsMargins(10, 10, 10, 10)
        self.auto_add_all_dlc_check = QCheckBox("Ajouter automatiquement tous les DLC d'un jeu quand on l'ajoute")
        self.auto_add_all_dlc_check.setChecked(self.config.get('auto_add_all_dlc', False))
        dlc_layout.addWidget(self.auto_add_all_dlc_check)
        
        add_dlc_manually_btn = QPushButton("Ajouter tous les DLC des jeux existants")
        add_dlc_manually_btn.clicked.connect(self.add_dlc_for_existing_games)
        dlc_layout.addWidget(add_dlc_manually_btn)
        
        dlc_group.setLayout(dlc_layout)
        general_layout.addWidget(dlc_group)

        discord_group = QGroupBox("Présence Discord")
        discord_layout = QVBoxLayout()
        discord_layout.setContentsMargins(10, 10, 10, 10)
        self.discord_check = QCheckBox("Activer la présence Discord")
        self.discord_check.setChecked(self.config.get('enable_discord_rpc', False))
        if not PPRESENCE_AVAILABLE:
            self.discord_check.setEnabled(False)
            self.discord_check.setText("Activer la présence Discord (pypresence non installé)")
        discord_layout.addWidget(self.discord_check)
        discord_group.setLayout(discord_layout)
        general_layout.addWidget(discord_group)

        startup_group = QGroupBox("Démarrage")
        startup_layout = QVBoxLayout()
        startup_layout.setContentsMargins(10, 10, 10, 10)
        self.startup_check = QCheckBox("Lancer Furry Tools au démarrage de Windows")
        self.startup_check.setChecked(is_in_startup())
        startup_layout.addWidget(self.startup_check)
        startup_group.setLayout(startup_layout)
        general_layout.addWidget(startup_group)

        auto_steam_group = QGroupBox("Lancement automatique de Steam")
        auto_steam_layout = QVBoxLayout()
        auto_steam_layout.setContentsMargins(10, 10, 10, 10)
        self.auto_steam_check = QCheckBox("Lancer automatiquement Steam au démarrage de Furry Tools")
        self.auto_steam_check.setChecked(self.config.get('auto_launch_steam', False))
        info_label = QLabel("Si activé, Steam sera lancé (et son cache nettoyé) au démarrage de Furry Tools")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #aaaaaa; font-size: 9px;")
        auto_steam_layout.addWidget(self.auto_steam_check)
        auto_steam_layout.addWidget(info_label)
        auto_steam_group.setLayout(auto_steam_layout)
        general_layout.addWidget(auto_steam_group)

        general_layout.addStretch()
        tabs.addTab(general_tab, "Général")

        games_tab = QWidget()
        games_layout = QVBoxLayout(games_tab)
        games_layout.setSpacing(10)

        grid_group = QGroupBox("Configuration de la grille")
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(10, 10, 10, 10)
        grid_layout.setSpacing(8)
        
        cols_label = QLabel("Nombre de colonnes :")
        cols_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid_layout.addWidget(cols_label, 0, 0)
        
        self.grid_cols_spin = QSpinBox()
        self.grid_cols_spin.setRange(1, 4)
        self.grid_cols_spin.setValue(self.config.get('grid_columns', 2))
        grid_layout.addWidget(self.grid_cols_spin, 0, 1)
        
        width_label = QLabel("Largeur de la grille (px) :")
        width_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid_layout.addWidget(width_label, 1, 0)
        
        self.grid_width_spin = QSpinBox()
        self.grid_width_spin.setRange(300, 800)
        self.grid_width_spin.setValue(self.config.get('grid_width', 400))
        grid_layout.addWidget(self.grid_width_spin, 1, 1)
        
        height_label = QLabel("Hauteur maximale (px) :")
        height_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid_layout.addWidget(height_label, 2, 0)
        
        self.grid_height_spin = QSpinBox()
        self.grid_height_spin.setRange(300, 800)
        self.grid_height_spin.setValue(self.config.get('grid_max_height', 500))
        grid_layout.addWidget(self.grid_height_spin, 2, 1)
        
        grid_group.setLayout(grid_layout)
        games_layout.addWidget(grid_group)

        btn_group = QGroupBox("Configuration des boutons")
        btn_layout = QGridLayout()
        btn_layout.setContentsMargins(10, 10, 10, 10)
        btn_layout.setSpacing(8)
        
        btn_min_label = QLabel("Largeur min (px) :")
        btn_min_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        btn_layout.addWidget(btn_min_label, 0, 0)
        
        self.btn_min_spin = QSpinBox()
        self.btn_min_spin.setRange(120, 300)
        self.btn_min_spin.setValue(self.config.get('button_min_width', 180))
        btn_layout.addWidget(self.btn_min_spin, 0, 1)
        
        btn_max_label = QLabel("Largeur max (px) :")
        btn_max_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        btn_layout.addWidget(btn_max_label, 1, 0)
        
        self.btn_max_spin = QSpinBox()
        self.btn_max_spin.setRange(150, 400)
        self.btn_max_spin.setValue(self.config.get('button_max_width', 250))
        btn_layout.addWidget(self.btn_max_spin, 1, 1)
        
        btn_height_label = QLabel("Hauteur (px) :")
        btn_height_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        btn_layout.addWidget(btn_height_label, 2, 0)
        
        self.btn_height_spin = QSpinBox()
        self.btn_height_spin.setRange(30, 80)
        self.btn_height_spin.setValue(self.config.get('button_height', 40))
        btn_layout.addWidget(self.btn_height_spin, 2, 1)
        
        name_len_label = QLabel("Longueur max des noms :")
        name_len_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        btn_layout.addWidget(name_len_label, 3, 0)
        
        self.name_len_spin = QSpinBox()
        self.name_len_spin.setRange(20, 60)
        self.name_len_spin.setValue(self.config.get('name_max_length', 40))
        btn_layout.addWidget(self.name_len_spin, 3, 1)
        
        btn_group.setLayout(btn_layout)
        games_layout.addWidget(btn_group)

        games_layout.addStretch()
        tabs.addTab(games_tab, "Affichage des jeux")

        window_tab = QWidget()
        window_layout = QVBoxLayout(window_tab)
        window_layout.setSpacing(10)

        window_group = QGroupBox("Taille de la fenêtre des paramètres")
        window_grid = QGridLayout()
        window_grid.setContentsMargins(10, 10, 10, 10)
        window_grid.setSpacing(8)
        
        dialog_width_label = QLabel("Largeur (px) :")
        dialog_width_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        window_grid.addWidget(dialog_width_label, 0, 0)
        
        self.dialog_width_spin = QSpinBox()
        self.dialog_width_spin.setRange(400, 1000)
        self.dialog_width_spin.setValue(self.config.get('dialog_width', 600))
        window_grid.addWidget(self.dialog_width_spin, 0, 1)
        
        dialog_height_label = QLabel("Hauteur (px) :")
        dialog_height_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        window_grid.addWidget(dialog_height_label, 1, 0)
        
        self.dialog_height_spin = QSpinBox()
        self.dialog_height_spin.setRange(400, 900)
        self.dialog_height_spin.setValue(self.config.get('dialog_height', 600))
        window_grid.addWidget(self.dialog_height_spin, 1, 1)
        
        window_group.setLayout(window_grid)
        window_layout.addWidget(window_group)
        window_layout.addStretch()
        tabs.addTab(window_tab, "Fenêtre")

        private_tab = QWidget()
        private_layout = QVBoxLayout(private_tab)
        private_layout.setSpacing(10)

        private_group = QGroupBox("Jeux privés")
        private_grid = QVBoxLayout()
        private_grid.setContentsMargins(10, 10, 10, 10)
        
        self.games_list = QListWidget()
        self.games_list.setSelectionMode(QListWidget.NoSelection)
        self.games_list.setWordWrap(True)
        self.games_list.setUniformItemSizes(False)
        self.games_list.setMinimumHeight(200)
        self.list_items = {}
        
        for appid in sorted(self.all_appids):
            display = self.known_names.get(appid, appid)
            item = QListWidgetItem(display)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if appid in self.config['private_games'] else Qt.Unchecked)
            item.setData(Qt.UserRole, appid)
            item.setSizeHint(QSize(item.sizeHint().width(), 30))
            self.games_list.addItem(item)
            self.list_items[appid] = item
        
        private_grid.addWidget(self.games_list)
        private_group.setLayout(private_grid)
        private_layout.addWidget(private_group)

        tabs.addTab(private_tab, "Jeux privés")

        update_tab = QWidget()
        update_layout = QVBoxLayout(update_tab)
        update_layout.setSpacing(10)

        version_group = QGroupBox("Version actuelle")
        version_layout = QHBoxLayout()
        version_layout.setContentsMargins(10, 10, 10, 10)
        version_label = QLabel(f"Furry Tools V{CURRENT_VERSION}")
        version_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ff00;")
        version_layout.addWidget(version_label)
        version_group.setLayout(version_layout)
        update_layout.addWidget(version_group)

        check_group = QGroupBox("Vérification des mises à jour")
        check_layout = QVBoxLayout()
        check_layout.setContentsMargins(10, 10, 10, 10)
        check_layout.setSpacing(8)

        self.auto_update_check = QCheckBox("Vérifier automatiquement les mises à jour au démarrage")
        self.auto_update_check.setChecked(self.config.get('auto_check_updates', True))
        check_layout.addWidget(self.auto_update_check)

        check_now_btn = QPushButton("Vérifier les mises à jour maintenant")
        check_now_btn.clicked.connect(self.check_for_updates)
        check_layout.addWidget(check_now_btn)

        self.update_status_label = QLabel("")
        self.update_status_label.setWordWrap(True)
        check_layout.addWidget(self.update_status_label)

        check_group.setLayout(check_layout)
        update_layout.addWidget(check_group)

        download_group = QGroupBox("Mise à jour")
        download_layout = QVBoxLayout()
        download_layout.setContentsMargins(10, 10, 10, 10)
        download_layout.setSpacing(8)

        self.download_btn = QPushButton("Télécharger la mise à jour")
        self.download_btn.clicked.connect(self.download_update)
        self.download_btn.setEnabled(False)
        download_layout.addWidget(self.download_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        download_layout.addWidget(self.progress_bar)

        github_btn = QPushButton("Ouvrir la page GitHub")
        github_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(REPO_URL)))
        download_layout.addWidget(github_btn)

        download_group.setLayout(download_layout)
        update_layout.addWidget(download_group)

        update_layout.addStretch()
        tabs.addTab(update_tab, "Mise à jour")

        main_layout.addWidget(tabs)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        ok_btn = QPushButton("OK")
        ok_btn.setMinimumWidth(80)
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setMinimumWidth(80)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
        
        self.font_family_combo.currentTextChanged.connect(self.update_preview_font)
        self.font_size_slider.valueChanged.connect(self.update_preview_font)

        if self.config.get('auto_check_updates', True):
            QTimer.singleShot(500, self.check_for_updates)

    def add_dlc_for_existing_games(self):
        if not hasattr(self.parent, 'target_folder') or not self.parent.target_folder:
            QMessageBox.warning(self, "Erreur", "Le dossier SteamTools n'existe pas.")
            return
        
        if not os.path.exists(self.parent.target_folder):
            QMessageBox.warning(self, "Erreur", "Le dossier SteamTools n'existe pas.")
            return
        
        try:
            files = [f for f in os.listdir(self.parent.target_folder) 
                    if f.lower().endswith('.lua') and f.lower() != 'steamtools.lua']
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de lister les fichiers: {e}")
            return
        
        if not files:
            QMessageBox.information(self, "Info", "Aucun fichier .lua trouvé.")
            return
        
        appids = [os.path.splitext(f)[0] for f in files]
        
        self.analysis_progress = QProgressDialog("", "Annuler", 0, len(appids), self)
        self.analysis_progress.setWindowTitle("Analyse des jeux")
        self.analysis_progress.setWindowModality(Qt.WindowModal)
        self.analysis_progress.setMinimumWidth(450)
        self.analysis_progress.setMinimumDuration(0)
        self.analysis_progress.setValue(0)
        
        steamtools_file = os.path.join(self.parent.target_folder, "Steamtools.lua")
        existing_dlcs = []
        if os.path.exists(steamtools_file):
            self.analysis_progress.setLabelText("Lecture des DLC existants...")
            QApplication.processEvents()
            with open(steamtools_file, 'r', encoding='utf-8') as f:
                for line in f:
                    match = re.search(r'addappid\((\d+),', line)
                    if match:
                        existing_dlcs.append(match.group(1))
        
        games_with_dlc_status = {}
        total_appids = len(appids)
        
        for i, appid in enumerate(appids):
            if self.analysis_progress.wasCanceled():
                self.analysis_progress.close()
                return
            
            percent = int((i + 1) * 100 / total_appids)
            self.analysis_progress.setValue(i + 1)
            self.analysis_progress.setLabelText(f"[{percent}%] Analyse du jeu...")
            QApplication.processEvents()
            
            try:
                url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode())
                    if data.get(appid, {}).get('success'):
                        game_data = data[appid]['data']
                        game_name = game_data.get('name', appid)
                        self.game_names[appid] = game_name
                        
                        if game_data.get('dlc'):
                            game_dlcs = [str(dlc_id) for dlc_id in game_data['dlc']]
                            missing_dlcs = [dlc for dlc in game_dlcs if dlc not in existing_dlcs]
                            has_all_dlc = len(missing_dlcs) == 0
                            
                            if not has_all_dlc:
                                games_with_dlc_status[appid] = (game_name, len(missing_dlcs))
                                self.analysis_progress.setLabelText(f"[{percent}%] {game_name} : {len(missing_dlcs)} DLC manquants")
                            else:
                                self.analysis_progress.setLabelText(f"[{percent}%] {game_name} : tous les DLC déjà présents")
                        else:
                            self.analysis_progress.setLabelText(f"[{percent}%] {game_name} : aucun DLC disponible")
                    QApplication.processEvents()
            except Exception as e:
                self.analysis_progress.setLabelText(f"[{percent}%] Erreur analyse")
                QApplication.processEvents()
        
        self.analysis_progress.close()
        
        games_with_dlc_status = {k: v for k, v in sorted(games_with_dlc_status.items(), key=lambda x: x[1][0])}
        
        if not games_with_dlc_status:
            QMessageBox.information(self, "Info", "Tous les jeux ont déjà tous leurs DLC.")
            return
        
        dialog = SelectGameForDLCDialog(self, self.config, self.parent.target_folder, games_with_dlc_status, self.game_names)
        if dialog.exec_() == QDialog.Accepted:
            selected_games = dialog.selected_games
            if selected_games:
                self.process_dlc_for_games(selected_games)
    
    def process_dlc_for_games(self, game_appids):
        self.current_thread_index = 0
        self.total_added = 0
        self.total_skipped = 0
        self.total_failed = 0
        self.game_dlc_threads = []
        
        self.process_progress = QProgressDialog("", "Annuler", 0, len(game_appids), self)
        self.process_progress.setWindowTitle("Ajout des DLC")
        self.process_progress.setWindowModality(Qt.WindowModal)
        self.process_progress.setMinimumWidth(450)
        self.process_progress.setMinimumDuration(0)
        self.process_progress.canceled.connect(self.cancel_dlc_processing)
        
        self.process_dlc_next_game(game_appids)
    
    def process_dlc_next_game(self, game_appids):
        if self.current_thread_index >= len(game_appids):
            self.process_progress.close()
            msg = f"Terminé !\n\n"
            msg += f"DLC ajoutés : {self.total_added}\n"
            if self.total_skipped > 0:
                msg += f"DLC déjà présents : {self.total_skipped}\n"
            if self.total_failed > 0:
                msg += f"DLC en échec : {self.total_failed}"
            QMessageBox.information(self, "Succès", msg)
            return
        
        appid = game_appids[self.current_thread_index]
        game_name = self.game_names.get(appid, appid)
        progress_percent = int((self.current_thread_index + 1) * 100 / len(game_appids))
        self.process_progress.setLabelText(f"[{progress_percent}%] Ajout des DLC pour {game_name}...")
        self.process_progress.setValue(self.current_thread_index + 1)
        QApplication.processEvents()
        
        thread = GameDLCDownloadThread(appid, self.parent.target_folder)
        thread.finished.connect(lambda added, skipped, failed: self.on_game_dlc_finished(added, skipped, failed, game_appids))
        thread.error.connect(lambda err: self.on_game_dlc_error(err, game_appids))
        self.game_dlc_threads.append(thread)
        thread.start()
    
    def on_game_dlc_finished(self, added_dlcs, skipped_dlcs, failed_dlcs, game_appids):
        self.total_added += len(added_dlcs)
        self.total_skipped += len(skipped_dlcs)
        self.total_failed += len(failed_dlcs)
        self.current_thread_index += 1
        self.process_dlc_next_game(game_appids)
    
    def on_game_dlc_error(self, error_msg, game_appids):
        self.current_thread_index += 1
        self.process_dlc_next_game(game_appids)
    
    def cancel_dlc_processing(self):
        for thread in self.game_dlc_threads:
            if thread.isRunning():
                thread.terminate()
        self.process_progress.close()
        QMessageBox.information(self, "Annulé", "L'ajout des DLC a été annulé.")

    def check_for_updates(self):
        self.update_status_label.setText("Vérification en cours...")
        self.download_btn.setEnabled(False)
        self.update_checker = UpdateChecker(CURRENT_VERSION)
        self.update_checker.update_checked.connect(self.on_update_checked)
        self.update_checker.start()

    def on_update_checked(self, has_update, latest_version, current_version):
        if has_update:
            self.update_status_label.setText(f"Une nouvelle version V{latest_version} est disponible !")
            self.download_btn.setEnabled(True)
            self.latest_version = latest_version
        else:
            self.update_status_label.setText(f"Vous utilisez la dernière version V{current_version}")
            self.download_btn.setEnabled(False)

    def download_update(self):
        try:
            download_url = f"https://github.com/RvMillions/Furry-Tools/archive/refs/heads/main.zip"
            save_path = os.path.join(tempfile.gettempdir(), f"FurryTools_Update_{self.latest_version}.zip")
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.download_btn.setEnabled(False)
            self.update_status_label.setText("Téléchargement en cours...")
            
            self.update_downloader = UpdateDownloader(download_url, save_path)
            self.update_downloader.progress.connect(self.progress_bar.setValue)
            self.update_downloader.finished.connect(self.on_download_finished)
            self.update_downloader.error.connect(self.on_download_error)
            self.update_downloader.start()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de récupérer la mise à jour: {e}")

    def on_download_finished(self, file_path):
        self.progress_bar.setVisible(False)
        reply = QMessageBox.question(self, "Mise à jour téléchargée",
                                   f"La mise à jour a été téléchargée.\nVoulez-vous l'installer maintenant ?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.install_update(file_path)

    def install_update(self, zip_path):
        try:
            extract_dir = os.path.join(tempfile.gettempdir(), f"FurryTools_Update_{self.latest_version}")
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            os.makedirs(extract_dir)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            extracted_folders = [f for f in os.listdir(extract_dir) if os.path.isdir(os.path.join(extract_dir, f))]
            if extracted_folders:
                source_dir = os.path.join(extract_dir, extracted_folders[0])
            else:
                source_dir = extract_dir
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            backup_dir = os.path.join(tempfile.gettempdir(), f"FurryTools_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copytree(current_dir, backup_dir)
            
            for item in os.listdir(source_dir):
                s = os.path.join(source_dir, item)
                d = os.path.join(current_dir, item)
                if os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d)
                    shutil.copytree(s, d)
                else:
                    if os.path.exists(d):
                        os.remove(d)
                    shutil.copy2(s, d)
            
            QMessageBox.information(self, "Mise à jour terminée",
                                   f"La mise à jour a été installée avec succès.\nUne sauvegarde de l'ancienne version a été créée dans :\n{backup_dir}")
            
            reply = QMessageBox.question(self, "Redémarrer",
                                       "L'application va redémarrer pour appliquer les changements.\nVoulez-vous continuer ?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                python = sys.executable
                os.execl(python, python, *sys.argv)
            else:
                self.accept()
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur d'installation",
                               f"Une erreur est survenue lors de l'installation : {str(e)}")

    def on_download_error(self, error_msg):
        self.progress_bar.setVisible(False)
        reply = QMessageBox.question(self, "Erreur de téléchargement",
                                   f"Erreur lors du téléchargement: {error_msg}\n\nVoulez-vous ouvrir la page GitHub pour télécharger manuellement ?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            QDesktopServices.openUrl(QUrl(REPO_URL))
        self.download_btn.setEnabled(True)
        self.update_status_label.setText("Une nouvelle version est disponible !")

    def on_theme_changed(self, theme_name):
        self.setStyleSheet(get_theme_stylesheet(theme_name))

    def update_preview_font(self):
        family = self.font_family_combo.currentText()
        size = self.font_size_slider.value()
        font = QFont(family, size)
        self.preview_text.setFont(font)

    def update_logo_display(self):
        if self.config.get('logo_path') and os.path.exists(self.config['logo_path']):
            self.logo_label.setText(f"Logo actuel : {os.path.basename(self.config['logo_path'])}")
        else:
            self.logo_label.setText("Logo actuel : par défaut")

    def change_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir un logo",
            os.path.expanduser("~"),
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.ico *.svg)"
        )
        if not file_path:
            return
        try:
            ext = os.path.splitext(file_path)[1].lower()
            dest_filename = "custom_logo" + ext
            dest_path = os.path.join(CONFIG_DIR, dest_filename)
            shutil.copy2(file_path, dest_path)
            self.config['logo_path'] = dest_path
            self.update_logo_display()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de la copie du logo : {e}")

    def reset_logo(self):
        self.config['logo_path'] = ''
        self.update_logo_display()

    def fetch_missing_names(self):
        missing = [aid for aid in self.all_appids if aid not in self.known_names]
        if missing:
            self.name_fetcher = NameFetcher(missing)
            self.name_fetcher.names_ready.connect(self.update_names)
            self.name_fetcher.error_occurred.connect(lambda msg: print(f"Erreur fetch: {msg}"))
            self.name_fetcher.start()

    def update_names(self, new_names):
        self.known_names.update(new_names)
        for appid, name in new_names.items():
            if appid in self.list_items:
                self.list_items[appid].setText(name)

    def get_updated_config(self):
        self.config['icon_size'] = self.size_slider.value()
        self.config['enable_discord_rpc'] = self.discord_check.isChecked()
        self.config['start_with_windows'] = self.startup_check.isChecked()
        self.config['auto_launch_steam'] = self.auto_steam_check.isChecked()
        self.config['auto_check_updates'] = self.auto_update_check.isChecked()
        self.config['auto_add_all_dlc'] = self.auto_add_all_dlc_check.isChecked()
        self.config['font_family'] = self.font_family_combo.currentText()
        self.config['font_size'] = self.font_size_slider.value()
        self.config['theme'] = self.theme_combo.currentText()
        self.config['grid_columns'] = self.grid_cols_spin.value()
        self.config['grid_width'] = self.grid_width_spin.value()
        self.config['grid_max_height'] = self.grid_height_spin.value()
        self.config['button_min_width'] = self.btn_min_spin.value()
        self.config['button_max_width'] = self.btn_max_spin.value()
        self.config['button_height'] = self.btn_height_spin.value()
        self.config['name_max_length'] = self.name_len_spin.value()
        self.config['dialog_width'] = self.dialog_width_spin.value()
        self.config['dialog_height'] = self.dialog_height_spin.value()
        
        private = []
        for i in range(self.games_list.count()):
            item = self.games_list.item(i)
            if item.checkState() == Qt.Checked:
                appid = item.data(Qt.UserRole)
                private.append(appid)
        self.config['private_games'] = private
        return self.config

class ProfileCreationDialog(QDialog):
    def __init__(self, parent, appids_with_paths, known_names):
        super().__init__(parent)
        self.appids_with_paths = appids_with_paths
        self.known_names = known_names
        self.setWindowTitle("Créer un profile")
        self.setModal(True)
        
        if hasattr(parent, 'config'):
            self.config = parent.config
        else:
            self.config = load_config()
        
        width = self.config.get('dialog_width', 500)
        height = self.config.get('dialog_height', 550)
        self.resize(width, height)
        
        self.initUI()
        center_window(self)

    def initUI(self):
        theme = self.config.get('theme', 'Gris foncé')
        self.setStyleSheet(get_theme_stylesheet(theme))
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        label = QLabel("Sélectionnez les jeux à inclure dans le profile :")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.games_list = QListWidget()
        self.games_list.setSelectionMode(QListWidget.NoSelection)
        self.games_list.setWordWrap(True)
        self.games_list.setUniformItemSizes(False)
        self.games_list.setMinimumHeight(250)
        self.list_items = {}
        
        for appid in sorted(self.appids_with_paths.keys()):
            display = self.known_names.get(appid, appid)
            item = QListWidgetItem(display)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, appid)
            item.setSizeHint(QSize(item.sizeHint().width(), 30))
            self.games_list.addItem(item)
            self.list_items[appid] = item
        
        layout.addWidget(self.games_list)

        select_buttons_layout = QHBoxLayout()
        select_all_btn = QPushButton("Tout sélectionner")
        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn = QPushButton("Tout désélectionner")
        deselect_all_btn.clicked.connect(self.deselect_all)
        select_buttons_layout.addStretch()
        select_buttons_layout.addWidget(select_all_btn)
        select_buttons_layout.addWidget(deselect_all_btn)
        select_buttons_layout.addStretch()
        layout.addLayout(select_buttons_layout)

        buttons_layout = QHBoxLayout()
        create_btn = QPushButton("Créer")
        create_btn.setMinimumWidth(100)
        create_btn.clicked.connect(self.create_profile)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(create_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

    def select_all(self):
        for i in range(self.games_list.count()):
            self.games_list.item(i).setCheckState(Qt.Checked)

    def deselect_all(self):
        for i in range(self.games_list.count()):
            self.games_list.item(i).setCheckState(Qt.Unchecked)

    def create_profile(self):
        selected_appids = []
        for i in range(self.games_list.count()):
            item = self.games_list.item(i)
            if item.checkState() == Qt.Checked:
                appid = item.data(Qt.UserRole)
                selected_appids.append(appid)
        
        if not selected_appids:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner au moins un jeu.")
            return
        
        file_paths = [self.appids_with_paths[appid] for appid in selected_appids if appid in self.appids_with_paths]
        if not file_paths:
            QMessageBox.warning(self, "Erreur", "Aucun fichier trouvé pour les jeux sélectionnés.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"profile_{timestamp}.zip"
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        
        self.thread = ZipCreationThread(file_paths, zip_name, downloads)
        self.progress_dialog = QProgressDialog("Création du profile en cours...", "Annuler", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setAutoReset(True)
        self.progress_dialog.setMinimumWidth(350)
        self.progress_dialog.canceled.connect(self.thread.terminate)
        self.thread.progress.connect(self.progress_dialog.setValue)
        self.thread.finished.connect(self.on_creation_finished)
        self.thread.error.connect(self.on_creation_error)
        self.thread.start()

    def on_creation_finished(self, zip_path):
        self.progress_dialog.close()
        QMessageBox.information(self, "Succès", f"Profile créé avec succès :\n{zip_path}")
        self.accept()

    def on_creation_error(self, error_msg):
        self.progress_dialog.close()
        QMessageBox.critical(self, "Erreur", f"Échec de la création du profile :\n{error_msg}")

class SteamPathDetector(QThread):
    finished = pyqtSignal(object, object, object)
    def run(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            steam_reg_path, _ = winreg.QueryValueEx(key, "SteamPath")
            winreg.CloseKey(key)
            steam_reg_path = steam_reg_path.replace('/', '\\')
            if os.path.exists(os.path.join(steam_reg_path, "steam.exe")):
                self.finished.emit(steam_reg_path,
                                 os.path.join(steam_reg_path, "steam.exe"),
                                 os.path.join(steam_reg_path, "config", "stplug-in"))
                return
        except:
            pass

        common_paths = [
            os.path.expandvars(r"%ProgramFiles(x86)%\Steam"),
            os.path.expandvars(r"%ProgramFiles%\Steam"),
            os.path.expandvars(r"%LOCALAPPDATA%\Steam"),
            "C:\\Program Files (x86)\\Steam",
            "C:\\Program Files\\Steam",
            "D:\\Steam",
            "E:\\Steam"
        ]
        
        for path in common_paths:
            expanded = os.path.expandvars(path)
            steam_exe = os.path.join(expanded, "steam.exe")
            if os.path.exists(steam_exe):
                self.finished.emit(expanded, steam_exe, os.path.join(expanded, "config", "stplug-in"))
                return
        
        self.finished.emit(None, None, None)

class FurryTools(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.steam_folder = None
        self.steam_path = None
        self.target_folder = None
        self.movie = None
        self.game_names = load_cache()
        self.name_fetcher = None
        self.file_map = {}
        self.discord_rpc_thread = None
        self.discord_rpc_active = False
        self.public_grid_menu = None
        self.private_grid_menu = None
        
        self.initUI()
        self.drag_position = None
        self.start_discord_rpc_if_enabled()
        
        QTimer.singleShot(100, self.detect_steam_path_async)

    def detect_steam_path_async(self):
        self.detector = SteamPathDetector()
        self.detector.finished.connect(self.on_steam_path_detected)
        self.detector.start()

    def on_steam_path_detected(self, folder, exe, target):
        self.steam_folder = folder
        self.steam_path = exe
        self.target_folder = target
        
        if folder is None:
            QTimer.singleShot(200, self.ask_steam_path_manually)

    def ask_steam_path_manually(self):
        reply = QMessageBox.question(self, "Steam non trouvé",
                                   "Impossible de trouver Steam automatiquement.\n"
                                   "Voulez-vous sélectionner le dossier Steam manuellement ?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            folder = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier Steam")
            if folder and os.path.exists(os.path.join(folder, "steam.exe")):
                self.steam_folder = folder
                self.steam_path = os.path.join(folder, "steam.exe")
                self.target_folder = os.path.join(folder, "config", "stplug-in")

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        icon_size = self.config.get('icon_size', 150)
        self.setFixedSize(icon_size, icon_size)
        
        self.logo_label = QLabel(self)
        self.logo_label.setScaledContents(True)
        self.load_logo()
        self.logo_label.setGeometry(0, 0, icon_size, icon_size)
        
        self.setAcceptDrops(True)

        base_font = QFont(self.config.get('font_family', 'Segoe UI'), self.config.get('font_size', 10))
        
        screen = QApplication.primaryScreen()
        dpi = screen.logicalDotsPerInch() if screen else 96
        font_size = max(10, int(self.config.get('font_size', 10) * dpi / 96))
        
        theme = self.config.get('theme', 'Gris foncé')
        theme_colors = THEMES.get(theme, THEMES["Gris foncé"])
        
        menu_style = f"""
            QMenu {{
                background-color: {theme_colors['bg_primary']};
                color: {theme_colors['text_primary']};
                border: 2px solid {theme_colors['border']};
                border-radius: 10px;
                padding: 5px 0px;
                font-size: {font_size}px;
                font-family: '{self.config.get('font_family', 'Segoe UI')}';
            }}
            QMenu::item {{
                background-color: transparent;
                padding: 8px 25px;
                margin: 2px 5px;
                border-radius: 5px;
                color: {theme_colors['text_primary']};
            }}
            QMenu::item:selected {{
                background-color: {theme_colors['bg_secondary']};
            }}
            QMenu::item:disabled {{
                color: {theme_colors['text_secondary']};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {theme_colors['border']};
                margin: 5px 10px;
            }}
            QMenu::icon {{
                padding-right: 10px;
            }}
        """
        
        self.context_menu = QMenu(self)
        self.context_menu.setStyleSheet(menu_style)

        self.jeux_menu = self.context_menu.addMenu("Jeux")
        self.jeux_menu.setStyleSheet(menu_style)
        self.jeux_menu.aboutToShow.connect(self.safe_populate_jeux_menu)

        self.profile_menu = self.context_menu.addMenu("Profile")
        self.profile_menu.setStyleSheet(menu_style)
        self.profile_menu.aboutToShow.connect(self.populate_profile_menu)

        self.restart_action = self.context_menu.addAction("Redémarrer Steam")
        self.restart_action.triggered.connect(self.restart_steam)
        
        reset_cache_action = self.context_menu.addAction("Reset cache")
        reset_cache_action.triggered.connect(self.reset_cache)
        
        settings_action = self.context_menu.addAction("Paramètres")
        settings_action.triggered.connect(self.open_settings)
        
        open_folder_action = self.context_menu.addAction("Ouvrir le dossier des jeux")
        open_folder_action.triggered.connect(self.open_target_folder)
        
        open_cache_folder_action = self.context_menu.addAction("Ouvrir le dossier cache de Furry Tools")
        open_cache_folder_action.triggered.connect(self.open_cache_folder)
        
        extract_appid_action = self.context_menu.addAction("Extraire AppID du lien")
        extract_appid_action.triggered.connect(self.extract_appid_from_clipboard)
        
        search_action = self.context_menu.addAction("Rechercher un jeu Steam")
        search_action.triggered.connect(self.open_search_dialog)
        
        dlc_search_action = self.context_menu.addAction("Rechercher des DLC")
        dlc_search_action.triggered.connect(self.open_dlc_search_dialog)
        
        discord_action = self.context_menu.addAction("Project Lightning")
        discord_action.triggered.connect(self.open_discord)
        
        credits_action = self.context_menu.addAction("Crédits")
        credits_action.triggered.connect(self.show_credits)
        
        steamtools_action = self.context_menu.addAction("Downloads SteamTools")
        steamtools_action.triggered.connect(self.download_steamtools)

        open_cache_action = self.context_menu.addAction("Ouvrir le dossier cache")
        open_cache_action.triggered.connect(self.open_cache_folder)

        clear_cache_action = self.context_menu.addAction("Vider le cache")
        clear_cache_action.triggered.connect(self.clear_app_cache)
        
        quit_action = self.context_menu.addAction("Quitter Furry Tools")
        quit_action.triggered.connect(self.close_application)

    def open_search_dialog(self):
        dialog = SearchDialog(self, self.config)
        dialog.exec_()

    def open_dlc_search_dialog(self):
        if not self.target_folder:
            QMessageBox.warning(self, "Erreur", "Le dossier Steam n'a pas été trouvé.\nVeuillez d'abord installer Steam.")
            return
        dialog = DLCSearchDialog(self, self.config, self.target_folder)
        dialog.exec_()

    def populate_profile_menu(self):
        self.profile_menu.clear()
        create_action = self.profile_menu.addAction("Créer un profile")
        create_action.triggered.connect(self.create_profile)
        import_action = self.profile_menu.addAction("Importer un profile")
        import_action.triggered.connect(self.import_profile)

    def add_all_dlc_for_game(self, game_appid):
        if not self.target_folder:
            QMessageBox.warning(self, "Erreur", "Le dossier SteamTools n'existe pas.")
            return
        
        self.dlc_thread = GameDLCDownloadThread(game_appid, self.target_folder)
        self.progress_dialog = QProgressDialog("Récupération des DLC...", "Annuler", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setAutoReset(True)
        self.progress_dialog.setMinimumWidth(350)
        self.progress_dialog.canceled.connect(self.dlc_thread.terminate)
        self.dlc_thread.progress.connect(self.on_dlc_progress)
        self.dlc_thread.finished.connect(self.on_dlc_finished)
        self.dlc_thread.error.connect(self.on_dlc_error)
        self.dlc_thread.start()
    
    def on_dlc_progress(self, value, message):
        self.progress_dialog.setValue(value)
        self.progress_dialog.setLabelText(message)
    
    def on_dlc_finished(self, added_dlcs, skipped_dlcs, failed_dlcs):
        self.progress_dialog.close()
        if added_dlcs:
            msg = f"{len(added_dlcs)} DLC ajoutés avec succès.\n"
            if skipped_dlcs:
                msg += f"{len(skipped_dlcs)} DLC déjà présents.\n"
            if failed_dlcs:
                msg += f"{len(failed_dlcs)} DLC ont échoué."
            QMessageBox.information(self, "Succès", msg)
        else:
            QMessageBox.information(self, "Info", "Aucun DLC trouvé pour ce jeu.")
    
    def on_dlc_error(self, error_msg):
        self.progress_dialog.close()
        QMessageBox.critical(self, "Erreur", f"Erreur lors de la récupération des DLC:\n{error_msg}")

    def load_logo(self):
        if self.movie is not None:
            self.movie.stop()
            self.movie = None
            self.logo_label.setMovie(None)

        logo_path = self.config.get('logo_path', '')
        if logo_path and os.path.exists(logo_path):
            ext = os.path.splitext(logo_path)[1].lower()
            if ext == '.gif':
                self.movie = QMovie(logo_path)
                self.movie.setScaledSize(QSize(self.width(), self.height()))
                self.logo_label.setMovie(self.movie)
                self.movie.start()
                return
            else:
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    self.logo_label.setPixmap(pixmap)
                    return

        possible_paths = []
        
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        possible_paths.append(os.path.join(base_path, "logo.png"))
        
        possible_paths.append(os.path.join(os.getcwd(), "logo.png"))
        
        possible_paths.append(os.path.join(CONFIG_DIR, "logo.png"))

        for path in possible_paths:
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    self.logo_label.setPixmap(pixmap)
                    return

        self.logo_label.setText("🐾")
        self.logo_label.setAlignment(Qt.AlignCenter)
        screen = QApplication.primaryScreen()
        dpi = screen.logicalDotsPerInch() if screen else 96
        scaled_size = max(40, int(80 * dpi / 96))
        self.logo_label.setStyleSheet(f"font-size: {scaled_size}px; color: #ccc;")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = None
            event.accept()

    def contextMenuEvent(self, event):
        try:
            if self.steam_path and os.path.exists(self.steam_path):
                if self.is_steam_running():
                    self.restart_action.setText("Redémarrer Steam")
                else:
                    self.restart_action.setText("Lancer Steam")
                self.restart_action.setEnabled(True)
            else:
                self.restart_action.setText("Steam non trouvé")
                self.restart_action.setEnabled(False)
            
            self.context_menu.exec_(event.globalPos())
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur menu: {str(e)}")

    def is_steam_running(self):
        try:
            output = subprocess.check_output('tasklist /FI "IMAGENAME eq steam.exe"', shell=True, text=True)
            return "steam.exe" in output
        except:
            return False

    def open_discord(self):
        QDesktopServices.openUrl(QUrl("https://discord.gg/g7eqjzykrw"))

    def show_credits(self):
        QMessageBox.information(self, "Crédits", "by rvmillions")

    def download_steamtools(self):
        QDesktopServices.openUrl(QUrl("https://www.steamtools.net/download"))

    def open_target_folder(self):
        if not self.target_folder:
            QMessageBox.warning(self, "Erreur", "Dossier Steam non trouvé")
            return
        
        try:
            if not os.path.exists(self.target_folder):
                os.makedirs(self.target_folder)
            os.startfile(self.target_folder)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le dossier: {e}")

    def open_cache_folder(self):
        try:
            if not os.path.exists(CONFIG_DIR):
                os.makedirs(CONFIG_DIR)
            os.startfile(CONFIG_DIR)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le dossier cache: {e}")

    def clear_app_cache(self):
        reply = QMessageBox.question(self, "Confirmation",
                                   "Voulez-vous vraiment vider tout le cache ?\n"
                                   "Cela supprimera tous les noms de jeux en cache.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                if os.path.exists(CACHE_FILE):
                    os.remove(CACHE_FILE)
                self.game_names = {}
                QMessageBox.information(self, "Succès", "Cache vidé avec succès.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de vider le cache: {e}")

    def extract_appid_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if not text:
            QMessageBox.warning(self, "Erreur", "Le presse-papiers est vide.")
            return
        
        match = re.search(r'\b(\d{1,7})\b', text)
        if match:
            appid = match.group(1)
            clipboard.setText(appid)
            QMessageBox.information(self, "Succès", f"AppID {appid} copié dans le presse-papiers.")
        else:
            QMessageBox.warning(self, "Erreur", "Aucun nombre (AppID) trouvé dans le texte.")

    def open_settings(self):
        try:
            current_appids = []
            if self.target_folder and os.path.exists(self.target_folder):
                try:
                    files = [f for f in os.listdir(self.target_folder) if f.lower().endswith('.lua')]
                    current_appids = [os.path.splitext(f)[0] for f in files]
                except:
                    pass
            
            dialog = SettingsDialog(self, self.config, current_appids, self.game_names)
            dialog.exec_()
            
            if dialog.result() == QDialog.Accepted:
                new_config = dialog.get_updated_config()
                old_discord_enabled = self.config.get('enable_discord_rpc', False)
                new_discord_enabled = new_config.get('enable_discord_rpc', False)
                
                old_startup = is_in_startup()
                new_startup = new_config.get('start_with_windows', False)
                
                if new_startup and not old_startup:
                    add_to_startup()
                elif not new_startup and old_startup:
                    remove_from_startup()
                
                self.config = new_config
                save_config(self.config)

                new_size = self.config['icon_size']
                self.setFixedSize(new_size, new_size)
                self.logo_label.setGeometry(0, 0, new_size, new_size)
                self.load_logo()
                
                self.game_names.update(dialog.known_names)
                save_cache(self.game_names)

                if new_discord_enabled and not old_discord_enabled:
                    self.start_discord_rpc_if_enabled()
                elif not new_discord_enabled and old_discord_enabled:
                    self.stop_discord_rpc()
                    
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur paramètres: {str(e)}")
            traceback.print_exc()

    def start_discord_rpc_if_enabled(self):
        if not PPRESENCE_AVAILABLE:
            return
        if self.config.get('enable_discord_rpc', False) and not self.discord_rpc_active:
            self.discord_rpc_active = True
            self.discord_rpc_thread = threading.Thread(target=self.discord_rpc_loop, daemon=True)
            self.discord_rpc_thread.start()

    def stop_discord_rpc(self):
        self.discord_rpc_active = False

    def discord_rpc_loop(self):
        if not DISCORD_CLIENT_ID or len(DISCORD_CLIENT_ID) < 17 or not DISCORD_CLIENT_ID.isdigit():
            self.discord_rpc_active = False
            return
        
        try:
            RPC = Presence(DISCORD_CLIENT_ID)
            RPC.connect()
            start_time = int(time.time())
            
            while self.discord_rpc_active:
                RPC.update(
                    state="Furry Tools",
                    details="by rvmillions",
                    large_image="logo",
                    large_text="Furry Tools",
                    start=start_time,
                    buttons=[
                        {"label": "Discord", "url": "https://discord.gg/g7eqjzykrw"},
                        {"label": "GitHub", "url": "https://github.com/RvMillions/Furry-Tools"}
                    ]
                )
                for _ in range(15):
                    if not self.discord_rpc_active:
                        break
                    time.sleep(1)
            RPC.close()
        except Exception as e:
            self.discord_rpc_active = False

    def create_profile(self):
        if not self.target_folder:
            QMessageBox.warning(self, "Erreur", "Dossier Steam non trouvé")
            return
            
        if not os.path.exists(self.target_folder):
            QMessageBox.warning(self, "Erreur", "Le dossier cible n'existe pas.")
            return
        
        try:
            files = [f for f in os.listdir(self.target_folder) if f.lower().endswith('.lua')]
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de lister les fichiers: {e}")
            return
        
        if not files:
            QMessageBox.information(self, "Info", "Aucun fichier .lua trouvé.")
            return
        
        appids_with_paths = {}
        for f in files:
            appid = os.path.splitext(f)[0]
            appids_with_paths[appid] = os.path.join(self.target_folder, f)
        
        dialog = ProfileCreationDialog(self, appids_with_paths, self.game_names)
        dialog.exec_()

    def import_profile(self):
        if not self.target_folder:
            QMessageBox.warning(self, "Erreur", "Dossier Steam non trouvé")
            return
            
        zip_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier profile",
            os.path.join(os.path.expanduser("~"), "Downloads"),
            "Fichiers ZIP (*.zip)"
        )
        if not zip_path:
            return
        
        if not os.path.exists(self.target_folder):
            try:
                os.makedirs(self.target_folder)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de créer le dossier cible: {e}")
                return
        
        self.extract_thread = ZipExtractThread(zip_path, self.target_folder)
        self.progress_dialog = QProgressDialog("Import du profile en cours...", "Annuler", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setAutoReset(True)
        self.progress_dialog.setMinimumWidth(350)
        self.progress_dialog.canceled.connect(self.extract_thread.terminate)
        self.extract_thread.progress.connect(self.progress_dialog.setValue)
        self.extract_thread.finished.connect(self.on_import_finished)
        self.extract_thread.error.connect(self.on_import_error)
        self.extract_thread.start()

    def on_import_finished(self, extracted_files):
        self.progress_dialog.close()
        if extracted_files:
            QMessageBox.information(self, "Succès",
                                  f"{len(extracted_files)} fichier(s) .lua importé(s) avec succès.")
        else:
            QMessageBox.information(self, "Info", "Aucun fichier .lua trouvé dans l'archive.")

    def on_import_error(self, error_msg):
        self.progress_dialog.close()
        QMessageBox.critical(self, "Erreur", f"Échec de l'import:\n{error_msg}")

    def safe_populate_jeux_menu(self):
        try:
            self.populate_jeux_menu()
        except Exception as e:
            error_msg = traceback.format_exc()
            self.jeux_menu.clear()
            error_action = self.jeux_menu.addAction("Erreur de chargement")
            error_action.setEnabled(False)

    def populate_jeux_menu(self):
        self.jeux_menu.clear()
        
        if not self.target_folder or not os.path.exists(self.target_folder):
            action = self.jeux_menu.addAction("Dossier Steam introuvable")
            action.setEnabled(False)
            return
        
        try:
            files = [f for f in os.listdir(self.target_folder) if f.lower().endswith('.lua')]
        except Exception as e:
            action = self.jeux_menu.addAction("Erreur accès dossier")
            action.setEnabled(False)
            return
        
        if not files:
            action = self.jeux_menu.addAction("Aucun jeu trouvé")
            action.setEnabled(False)
            return
        
        appids = [os.path.splitext(f)[0] for f in files]
        self.file_map = {appid: os.path.join(self.target_folder, f) for appid, f in zip(appids, files)}
        
        private_set = set(self.config.get('private_games', []))
        public_appids = [aid for aid in appids if aid not in private_set]
        private_appids = [aid for aid in appids if aid in private_set]
        
        font_size = self.config.get('font_size', 10)
        font_family = self.config.get('font_family', 'Segoe UI')
        
        if public_appids:
            public_menu = GameGridMenu("Public", self, self.config)
            for appid in sorted(public_appids):
                display_name = self.game_names.get(appid, appid)
                public_menu.add_game(appid, display_name, self, font_size, font_family)
            public_menu.layout_games()
            self.jeux_menu.addMenu(public_menu)
        else:
            action = self.jeux_menu.addAction("Public (aucun)")
            action.setEnabled(False)
        
        if private_appids:
            private_menu = GameGridMenu("Privé", self, self.config)
            for appid in sorted(private_appids):
                display_name = self.game_names.get(appid, appid)
                private_menu.add_game(appid, display_name, self, font_size, font_family)
            private_menu.layout_games()
            self.jeux_menu.addMenu(private_menu)
        else:
            action = self.jeux_menu.addAction("Privé (aucun)")
            action.setEnabled(False)
        
        all_to_fetch = set(public_appids) | set(private_appids)
        missing = [aid for aid in all_to_fetch if aid not in self.game_names]
        if missing:
            self._start_name_fetcher(missing)

    def _start_name_fetcher(self, appids):
        if self.name_fetcher is not None and self.name_fetcher.isRunning():
            self.name_fetcher.quit()
            self.name_fetcher.wait(1000)
        self.name_fetcher = NameFetcher(appids)
        self.name_fetcher.names_ready.connect(self.on_names_fetched)
        self.name_fetcher.error_occurred.connect(lambda msg: print(f"Erreur fetch: {msg}"))
        self.name_fetcher.start()

    def on_names_fetched(self, new_names):
        self.game_names.update(new_names)
        save_cache(self.game_names)

    def delete_game(self, appid):
        try:
            file_path = self.file_map.get(appid)
            if not file_path or not os.path.exists(file_path):
                QMessageBox.warning(self, "Erreur", "Fichier introuvable.")
                return
            
            reply = QMessageBox.question(self, "Confirmation",
                                        f"Supprimer définitivement {appid}.lua ?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                os.remove(file_path)
                self.file_map.pop(appid, None)
                if appid in self.config['private_games']:
                    self.config['private_games'].remove(appid)
                    save_config(self.config)
                QMessageBox.information(self, "Succès", "Fichier supprimé.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de supprimer: {e}")

    def open_steamdb(self, appid):
        QDesktopServices.openUrl(QUrl(f"https://steamdb.info/app/{appid}/"))

    def restart_steam(self):
        if not self.steam_path or not os.path.exists(self.steam_path):
            QMessageBox.warning(self, "Erreur", "Steam non trouvé")
            return
            
        try:
            if self.is_steam_running():
                self._kill_steam()
                time.sleep(1)
            self._launch_steam()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur redémarrage: {e}")

    def reset_cache(self):
        if not self.steam_folder or not os.path.exists(self.steam_folder):
            QMessageBox.warning(self, "Erreur", "Steam non trouvé")
            return
            
        try:
            if self.is_steam_running():
                self._kill_steam()
                time.sleep(1)
            self._clear_cache()
            self._launch_steam()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur reset cache: {e}")

    def _kill_steam(self):
        subprocess.run(["taskkill", "/F", "/IM", "steam.exe"], capture_output=True)

    def _launch_steam(self):
        if os.path.exists(self.steam_path):
            subprocess.Popen([self.steam_path])
        else:
            QMessageBox.warning(self, "Erreur", f"Steam introuvable")

    def _clear_cache(self):
        cache_folders = ['appcache', 'depotcache']
        cleared_any = False
        
        for folder in cache_folders:
            folder_path = os.path.join(self.steam_folder, folder)
            if os.path.exists(folder_path):
                try:
                    for item in os.listdir(folder_path):
                        item_path = os.path.join(folder_path, item)
                        if os.path.isfile(item_path) or os.path.islink(item_path):
                            os.unlink(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                    cleared_any = True
                except Exception as e:
                    pass
        
        if cleared_any:
            QMessageBox.information(self, "Cache vidé", "Les caches Steam ont été nettoyés.")
        else:
            QMessageBox.information(self, "Info", "Aucun cache trouvé à nettoyer.")

    def close_application(self):
        self.stop_discord_rpc()
        QApplication.quit()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile().lower()
                    if file_path.endswith('.lua') or file_path.endswith('.zip'):
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dropEvent(self, event):
        if not self.target_folder:
            QMessageBox.warning(self, "Erreur", "Dossier Steam non trouvé")
            return
            
        try:
            if not os.path.exists(self.target_folder):
                os.makedirs(self.target_folder)
            
            copied_files = []
            extracted_files = []
            
            for url in event.mimeData().urls():
                if not url.isLocalFile():
                    continue
                
                file_path = url.toLocalFile()
                lower_path = file_path.lower()
                
                if lower_path.endswith('.lua'):
                    shutil.copy(file_path, self.target_folder)
                    copied_files.append(os.path.basename(file_path))
                elif lower_path.endswith('.zip'):
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        for member in zip_ref.namelist():
                            if member.lower().endswith('.lua'):
                                zip_ref.extract(member, self.target_folder)
                                extracted_files.append(os.path.basename(member))
            
            if copied_files or extracted_files:
                msg = ""
                if copied_files:
                    msg += f"{len(copied_files)} fichier(s) .lua copié(s).\n"
                if extracted_files:
                    msg += f"{len(extracted_files)} fichier(s) .lua extrait(s) du/des zip."
                QMessageBox.information(self, "Opération terminée", msg)
            else:
                QMessageBox.information(self, "Info", "Aucun fichier .lua trouvé.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du drop: {e}")

def single_instance_check():
    mutex_name = "FurryTools_Instance_Mutex"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    last_error = ctypes.windll.kernel32.GetLastError()
    if last_error == 183:
        ctypes.windll.kernel32.CloseHandle(mutex)
        return False
    return True

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    if not single_instance_check():
        QMessageBox.critical(None, "Erreur", "Furry Tools est déjà en cours d'exécution.")
        return
    
    window = FurryTools()
    window.show()
    
    if window.config.get('auto_launch_steam', False) and window.steam_path and os.path.exists(window.steam_path):
        QTimer.singleShot(500, window.restart_steam)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
