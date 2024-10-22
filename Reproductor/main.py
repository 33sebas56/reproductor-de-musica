import sys
import os
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, 
    QPushButton, QDockWidget,
    QStatusBar, QTabWidget, QWidget, 
    QHBoxLayout, QVBoxLayout, QListWidget,
    QFileDialog, QListWidgetItem, QSlider
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import (QPixmap, QAction, QKeySequence, QIcon)
from PyQt6.QtCore import (Qt, QStandardPaths)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initialize_ui()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.current_music_folder = ""
        with open('diseño.css', 'r') as file:
            style = file.read()
        self.setStyleSheet(style)
        self.player = None
        self.playing_reproductor = False

    def initialize_ui(self):
        self.setGeometry(100, 100, 800, 500)
        self.setWindowTitle("Reproductor musical")
        self.generate_main_window()
        self.generate_settings_tab()  
        self.create_dock()
        self.create_action()
        self.create_menu()
        self.show()

    def generate_main_window(self):
        tab_bar = QTabWidget(self)
        self.reproductor_container = QWidget()
        self.settings_container = QWidget()
        tab_bar.addTab(self.reproductor_container, "Reproductor")
        tab_bar.addTab(self.settings_container, "Settings")
        
        self.generate_reproductor_tab()

        tab_h_box = QHBoxLayout()
        tab_h_box.addWidget(tab_bar)

        main_container = QWidget()
        main_container.setLayout(tab_h_box)
        self.setCentralWidget(main_container)

    def generate_reproductor_tab(self):

        main_v_box = QVBoxLayout()
        buttons_h_box = QHBoxLayout()

        song_image = QLabel()
        pixmap = QPixmap("images/lobo_con_audifonos.png").scaled(450, 450)
        song_image.setPixmap(pixmap)
        song_image.setScaledContents(True)

        button_repeat = QPushButton()
        button_repeat.setObjectName('button_repeat')
        button_before = QPushButton()
        button_before.setObjectName('button_before')
        self.button_play = QPushButton()
        self.button_play.setObjectName('button_play')
        self.button_play.clicked.connect(self.playpause_song)
        button_next = QPushButton()
        button_next.setObjectName('button_next')
        button_radom = QPushButton()
        button_radom.setObjectName('button_radom')
        button_radom.clicked.connect(self.play_random_song)  # Botón aleatorio
        button_repeat.setFixedSize(50, 50)
        button_before.setFixedSize(50, 50)
        self.button_play.setFixedSize(60, 60)
        button_next.setFixedSize(50, 50)
        button_radom.setFixedSize(50, 50)

        buttons_h_box.addWidget(button_repeat)
        buttons_h_box.addWidget(button_before)
        buttons_h_box.addWidget(self.button_play)
        buttons_h_box.addWidget(button_next)
        buttons_h_box.addWidget(button_radom)

        buttons_container = QWidget()
        buttons_container.setLayout(buttons_h_box)

        main_v_box.addWidget(song_image)
        main_v_box.addWidget(buttons_container)        
        
        self.reproductor_container.setLayout(main_v_box)

        button_before.clicked.connect(self.play_previous_song)
        button_next.clicked.connect(self.play_next_song)

    def create_action(self):
        self.list_music_action = QAction("Listar música", self, checkable=True)
        self.list_music_action.setShortcut(QKeySequence("ctrl+l"))
        self.list_music_action.setStatusTip("Conforme su playlist")
        self.list_music_action.triggered.connect(self.list_music)
        self.list_music_action.setChecked(True)

        self.open_folder_music_action = QAction("Abrir carpeta", self)
        self.open_folder_music_action.setShortcut(QKeySequence("ctrl+o"))
        self.open_folder_music_action.setStatusTip("Ir a carpeta de música")
        self.open_folder_music_action.triggered.connect(self.open_folder_music)

    def create_menu(self):
        self.menuBar()

        menu_file = self.menuBar().addMenu("Archivo")
        menu_file.addAction(self.open_folder_music_action)

        menu_view = self.menuBar().addMenu("Ver")
        menu_view.addAction(self.list_music_action)

    def create_dock(self):
        self.songs_list = QListWidget()
        self.dock = QDockWidget()
        self.dock.setWindowTitle("Lista de canciones")
        self.dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.songs_list.itemSelectionChanged.connect(self.handle_song_selection)
        self.dock.setWidget(self.songs_list)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)

    def list_music(self):
        if self.list_music_action.isChecked():
            self.dock.show()
        else:
            self.dock.hide()
    
    def open_folder_music(self):
        initial_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.MusicLocation)
        
        self.current_music_folder = QFileDialog.getExistingDirectory(None, "Selecciona una carpeta", initial_dir)
        icon = QIcon("images/musica-cd.ico")
        
        for archivo in os.listdir(self.current_music_folder):
            ruta_archivo = os.path.join(self.current_music_folder, archivo)
            if ruta_archivo.endswith(".mp3"):
                item = QListWidgetItem(archivo)
                item.setIcon(icon)
                self.songs_list.addItem(item)

    def create_player(self):
        if self.player:
            self.player.deleteLater()
        self.player = QMediaPlayer()
        self.audioOutput = QAudioOutput()
        self.player.setAudioOutput(self.audioOutput)
        self.player.mediaStatusChanged.connect(self.media_status_changed)
        self.audioOutput.setVolume(1.0)

    def playpause_song(self):
        if not self.player:
            return
        if self.playing_reproductor:
            self.button_play.setStyleSheet("image: url(images/boton-de-pausa.png);")
            self.player.pause()
            self.playing_reproductor = False
        else:
            self.button_play.setStyleSheet("image: url(images/punta-de-flecha-del-boton-de-reproduccion.png);")
            self.player.play()
            self.playing_reproductor = True

    def media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_next_song()

    def handle_song_selection(self):
        selected_item = self.songs_list.currentItem()
        if selected_item:
            song_name = selected_item.data(0)
            song_folder_path = os.path.join(self.current_music_folder, song_name)
            self.create_player()
            source = QUrl.fromLocalFile(song_folder_path)
            self.player.setSource(source)

    def play_next_song(self):
        """Reproduce la siguiente canción de la lista. Si llega al final, vuelve a la primera canción."""
        current_index = self.songs_list.currentRow()
        if current_index < self.songs_list.count() - 1:
            self.songs_list.setCurrentRow(current_index + 1)
        else:
            self.songs_list.setCurrentRow(0)
        self.handle_song_selection()

    def play_previous_song(self):
        """Reproduce la canción anterior de la lista. Si está en la primera, vuelve a la última."""
        current_index = self.songs_list.currentRow()
        if current_index > 0:
            self.songs_list.setCurrentRow(current_index - 1)
        else:
            self.songs_list.setCurrentRow(self.songs_list.count() - 1)
        self.handle_song_selection()

    def play_random_song(self):
        """Reproduce una canción aleatoria de la lista."""
        if self.songs_list.count() > 0:
            random_index = random.randint(0, self.songs_list.count() - 1)
            random_item = self.songs_list.item(random_index)
            self.songs_list.setCurrentItem(random_item)
            self.handle_song_selection()
        else:
            self.status_bar.showMessage("No hay canciones disponibles", 5000)

    def generate_settings_tab(self):
        """Genera las configuraciones para la pestaña de Settings."""
        settings_v_box = QVBoxLayout()

        volume_label = QLabel("Volumen")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.change_volume)

        settings_v_box.addWidget(volume_label)
        settings_v_box.addWidget(self.volume_slider)

        self.settings_container.setLayout(settings_v_box)

        theme_label = QLabel("Tema")
        self.theme_toggle_button = QPushButton("Modo Oscuro")
        self.theme_toggle_button.setCheckable(True)
        self.theme_toggle_button.toggled.connect(self.toggle_theme)

        settings_v_box.addWidget(theme_label)
        settings_v_box.addWidget(self.theme_toggle_button)


        speed_label = QLabel("Velocidad de Reproducción")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(50)
        self.speed_slider.setMaximum(150)
        self.speed_slider.setValue(100)
        self.speed_slider.valueChanged.connect(self.change_speed)

        settings_v_box.addWidget(speed_label)
        settings_v_box.addWidget(self.speed_slider)

        self.settings_container.setLayout(settings_v_box)

        balance_label = QLabel("Balance")
        self.balance_slider = QSlider(Qt.Orientation.Horizontal)
        self.balance_slider.setMinimum(-100)  
        self.balance_slider.setMaximum(100)   
        self.balance_slider.setValue(0)      
        self.balance_slider.valueChanged.connect(self.change_balance)

        settings_v_box.addWidget(balance_label)
        settings_v_box.addWidget(self.balance_slider)


        eq_label = QLabel("Ecualizador (Ajuste de frecuencias)")
        self.eq_slider_low = QSlider(Qt.Orientation.Horizontal)
        self.eq_slider_mid = QSlider(Qt.Orientation.Horizontal)
        self.eq_slider_high = QSlider(Qt.Orientation.Horizontal)

        self.eq_slider_low.setRange(-12, 12)  
        self.eq_slider_mid.setRange(-12, 12)
        self.eq_slider_high.setRange(-12, 12)

        self.eq_slider_low.setValue(0)
        self.eq_slider_mid.setValue(0)
        self.eq_slider_high.setValue(0)

        self.eq_slider_low.valueChanged.connect(self.change_eq)
        self.eq_slider_mid.valueChanged.connect(self.change_eq)
        self.eq_slider_high.valueChanged.connect(self.change_eq)

        settings_v_box.addWidget(eq_label)
        settings_v_box.addWidget(QLabel("Bajo:"))
        settings_v_box.addWidget(self.eq_slider_low)
        settings_v_box.addWidget(QLabel("Medio:"))
        settings_v_box.addWidget(self.eq_slider_mid)
        settings_v_box.addWidget(QLabel("Alto:"))
        settings_v_box.addWidget(self.eq_slider_high)

        self.settings_container.setLayout(settings_v_box)
        

    def change_volume(self, value):
        """Cambia el volumen del reproductor de audio."""
        if self.audioOutput:
            self.audioOutput.setVolume(value / 100)
        self.status_bar.showMessage(f"Volumen: {value}%", 200)
    
    def toggle_theme(self, checked):
        """Alterna entre tema claro y oscuro."""
        if checked:
            self.setStyleSheet("background-color: black; color: white;")
            self.theme_toggle_button.setText("Modo Claro")
        else:
            self.setStyleSheet("") 
            self.theme_toggle_button.setText("Modo Oscuro")

    def change_speed(self, value):
        """Cambia la velocidad de reproducción."""
        if self.player:
            self.player.setPlaybackRate(value / 100)
        self.status_bar.showMessage(f"Velocidad: {value}%", 2000)

    def change_balance(self, value):
        """Cambia el balance del audio."""
        if self.audioOutput:
            
            left_volume = max(0, 1.0 + (value / 100.0))
            right_volume = max(0, 1.0 - (value / 100.0))
            self.audioOutput.setVolume(left_volume if value < 0 else right_volume)

        self.status_bar.showMessage(f"Balance: {value}", 2000)

    def change_eq(self):
        """Ajusta las frecuencias del ecualizador."""
        
        low = self.eq_slider_low.value()
        mid = self.eq_slider_mid.value()
        high = self.eq_slider_high.value()
        
        self.status_bar.showMessage(f"Ecualizador - Bajo: {low}, Medio: {mid}, Alto: {high}", 2000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())