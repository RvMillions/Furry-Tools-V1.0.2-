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
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QMenu,
                             QMessageBox, QAction, QDialog, QVBoxLayout,
                             QHBoxLayout, QSlider, QSpinBox, QListWidget,
                             QCheckBox, QLineEdit, QPushButton, QGroupBox,
                             QListWidgetItem, QInputDialog, QFileDialog,
                             QProgressDialog, QProgressBar)
from PyQt5.QtCore import Qt, QPoint, QUrl, QThread, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QPixmap, QCursor, QDesktopServices, QFont, QIcon, QMovie, QClipboard

try:
    from pypresence import Presence
    PPRESENCE_AVAILABLE = True
except ImportError:
    PPRESENCE_AVAILABLE = False

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

os.makedirs(CONFIG_DIR, exist_ok=True)

def load_config():
    default_config = {
        'icon_size': 150,
        'private_games': [],
        'logo_path': '',
        'enable_discord_rpc': False
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

class SettingsDialog(QDialog):
    def __init__(self, parent, config, all_appids, known_names):
        super().__init__(parent)
        self.parent = parent
        self.config = config.copy()
        self.all_appids = all_appids
        self.known_names = known_names.copy()
        self.name_fetcher = None
        self.setWindowTitle("Paramètres")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.initUI()
        self.fetch_missing_names()

    def initUI(self):
        layout = QVBoxLayout()
        
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QGroupBox {
                color: #f0f0f0;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QListWidget {
                background-color: #3c3c3c;
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #3c3c3c;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #f0f0f0;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSpinBox {
                background-color: #3c3c3c;
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 2px;
            }
            QCheckBox {
                color: #f0f0f0;
            }
        """)
        
        size_group = QGroupBox("Taille du logo")
        size_layout = QHBoxLayout()
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
        layout.addWidget(size_group)

        logo_group = QGroupBox("Logo personnalisé")
        logo_layout = QVBoxLayout()
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
        layout.addWidget(logo_group)

        discord_group = QGroupBox("Présence Discord")
        discord_layout = QVBoxLayout()
        self.discord_check = QCheckBox("Activer la présence Discord")
        self.discord_check.setChecked(self.config.get('enable_discord_rpc', False))
        if not PPRESENCE_AVAILABLE:
            self.discord_check.setEnabled(False)
            self.discord_check.setText("Activer la présence Discord (pypresence non installé)")
        discord_layout.addWidget(self.discord_check)
        discord_group.setLayout(discord_layout)
        layout.addWidget(discord_group)

        games_group = QGroupBox("Jeux privés")
        games_layout = QVBoxLayout()
        self.games_list = QListWidget()
        self.games_list.setSelectionMode(QListWidget.NoSelection)
        self.list_items = {}
        
        for appid in sorted(self.all_appids):
            display = self.known_names.get(appid, appid)
            item = QListWidgetItem(display)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if appid in self.config['private_games'] else Qt.Unchecked)
            item.setData(Qt.UserRole, appid)
            self.games_list.addItem(item)
            self.list_items[appid] = item
        
        games_layout.addWidget(self.games_list)
        games_group.setLayout(games_layout)
        layout.addWidget(games_group)

        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

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
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QGroupBox {
                color: #f0f0f0;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QListWidget {
                background-color: #3c3c3c;
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QCheckBox {
                color: #f0f0f0;
            }
        """)
        
        layout = QVBoxLayout()
        
        label = QLabel("Sélectionnez les jeux à inclure dans le profile :")
        label.setStyleSheet("color: #f0f0f0;")
        layout.addWidget(label)

        self.games_list = QListWidget()
        self.games_list.setSelectionMode(QListWidget.NoSelection)
        self.list_items = {}
        
        for appid in sorted(self.appids_with_paths.keys()):
            display = self.known_names.get(appid, appid)
            item = QListWidgetItem(display)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, appid)
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
        create_btn.clicked.connect(self.create_profile)
        cancel_btn = QPushButton("Annuler")
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

class FurryTools(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.steam_folder = None
        self.steam_path = None
        self.target_folder = None
        self.detect_steam_path()
        self.movie = None
        self.game_names = load_cache()
        self.name_fetcher = None
        self.file_map = {}
        self.discord_rpc_thread = None
        self.discord_rpc_active = False
        
        self.initUI()
        self.drag_position = None
        self.start_discord_rpc_if_enabled()

    def detect_steam_path(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            steam_reg_path, _ = winreg.QueryValueEx(key, "SteamPath")
            winreg.CloseKey(key)
            steam_reg_path = steam_reg_path.replace('/', '\\')
            if os.path.exists(os.path.join(steam_reg_path, "steam.exe")):
                self.steam_folder = steam_reg_path
                self.steam_path = os.path.join(steam_reg_path, "steam.exe")
                self.target_folder = os.path.join(steam_reg_path, "config", "stplug-in")
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
                self.steam_folder = expanded
                self.steam_path = steam_exe
                self.target_folder = os.path.join(expanded, "config", "stplug-in")
                return
        
        reply = QMessageBox.question(None, "Steam non trouvé",
                                   "Impossible de trouver Steam automatiquement.\n"
                                   "Voulez-vous sélectionner le dossier Steam manuellement ?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            folder = QFileDialog.getExistingDirectory(None, "Sélectionner le dossier Steam")
            if folder and os.path.exists(os.path.join(folder, "steam.exe")):
                self.steam_folder = folder
                self.steam_path = os.path.join(folder, "steam.exe")
                self.target_folder = os.path.join(folder, "config", "stplug-in")
                return
        
        self.steam_folder = None
        self.steam_path = None
        self.target_folder = None

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

        menu_style = """
            QMenu {
                background-color: #2b2b2b;
                color: #f0f0f0;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 5px 0px;
                font-size: 12px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 25px;
                margin: 2px 5px;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: #3c3c3c;
                color: #ffffff;
            }
            QMenu::item:disabled {
                color: #6c6c6c;
                background-color: transparent;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3c3c3c;
                margin: 5px 10px;
            }
        """
        
        self.context_menu = QMenu(self)
        self.context_menu.setStyleSheet(menu_style)

        self.jeux_menu = QMenu("Jeux", self)
        self.jeux_menu.setStyleSheet(menu_style)
        self.jeux_menu.aboutToShow.connect(self.safe_populate_jeux_menu)
        self.context_menu.addMenu(self.jeux_menu)

        self.profile_menu = QMenu("Profile", self)
        self.profile_menu.setStyleSheet(menu_style)
        self.profile_menu.aboutToShow.connect(self.populate_profile_menu)
        self.context_menu.addMenu(self.profile_menu)

        self.restart_action = self.context_menu.addAction("Redémarrer Steam")
        self.restart_action.triggered.connect(self.restart_steam)
        
        reset_cache_action = self.context_menu.addAction("Reset cache")
        reset_cache_action.triggered.connect(self.reset_cache)
        
        settings_action = self.context_menu.addAction("Paramètres")
        settings_action.triggered.connect(self.open_settings)
        
        open_folder_action = self.context_menu.addAction("Ouvrir le dossier des jeux")
        open_folder_action.triggered.connect(self.open_target_folder)
        
        extract_appid_action = self.context_menu.addAction("Extraire AppID du lien")
        extract_appid_action.triggered.connect(self.extract_appid_from_clipboard)
        
        discord_action = self.context_menu.addAction("Project Lightning")
        discord_action.triggered.connect(self.open_discord)
        
        credits_action = self.context_menu.addAction("Crédits")
        credits_action.triggered.connect(self.show_credits)
        
        steamtools_action = self.context_menu.addAction("Downloads SteamTools")
        steamtools_action.triggered.connect(self.download_steamtools)
        
        quit_action = self.context_menu.addAction("Quitter Furry Tools")
        quit_action.triggered.connect(self.close_application)

    def populate_profile_menu(self):
        self.profile_menu.clear()
        create_action = self.profile_menu.addAction("Créer un profile")
        create_action.triggered.connect(self.create_profile)
        import_action = self.profile_menu.addAction("Importer un profile")
        import_action.triggered.connect(self.import_profile)

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
        self.logo_label.setStyleSheet("font-size: 80px; color: #ccc;")

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
            else:
                self.restart_action.setText("Steam non trouvé")
                self.restart_action.setEnabled(False)
            
            self.context_menu.exec_(QCursor.pos())
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
            if dialog.exec_() == QDialog.Accepted:
                new_config = dialog.get_updated_config()
                old_discord_enabled = self.config.get('enable_discord_rpc', False)
                new_discord_enabled = new_config.get('enable_discord_rpc', False)
                
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
            self.jeux_menu.clear()
            error_action = self.jeux_menu.addAction(f"Erreur de chargement")
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
            action = self.jeux_menu.addAction(f"Erreur accès dossier")
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
        
        if public_appids:
            public_menu = QMenu("Public", self)
            public_menu.setStyleSheet(self.context_menu.styleSheet())
            self._build_game_submenu(public_menu, public_appids)
            self.jeux_menu.addMenu(public_menu)
        else:
            action = self.jeux_menu.addAction("Public (aucun)")
            action.setEnabled(False)
        
        if private_appids:
            private_menu = QMenu("Privé", self)
            private_menu.setStyleSheet(self.context_menu.styleSheet())
            self._build_game_submenu(private_menu, private_appids)
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

    def _build_game_submenu(self, menu, appids):
        for appid in sorted(appids):
            display_name = self.game_names.get(appid, appid)
            game_submenu = QMenu(display_name, self)
            game_submenu.setStyleSheet(self.context_menu.styleSheet())
            
            delete_action = QAction("Supprimer", self)
            delete_action.triggered.connect(lambda checked, a=appid: self.delete_game(a))
            game_submenu.addAction(delete_action)
            
            steamdb_action = QAction("SteamDB", self)
            steamdb_action.triggered.connect(lambda checked, a=appid: self.open_steamdb(a))
            game_submenu.addAction(steamdb_action)
            
            menu.addMenu(game_submenu)

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
    if not single_instance_check():
        QMessageBox.critical(None, "Erreur", "Furry Tools est déjà en cours d'exécution.")
        return
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = FurryTools()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
