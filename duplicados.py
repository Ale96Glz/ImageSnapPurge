import os
import sys
import imagehash
from PIL import Image
import io
import subprocess
from send2trash import send2trash
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QListWidget, QListWidgetItem, QSlider, QMessageBox, QHBoxLayout, QAbstractItemView,
    QScrollArea, QFrame, QSizePolicy, QGroupBox, QGridLayout, QSplitter, QCheckBox,
    QDialog
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPalette, QColor, QPainter, QPen
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QSize, QRect, QTimer

class Worker(QObject):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)
    cancelled = pyqtSignal() 

    def __init__(self, folder, threshold, exclude_subfolders=False):
        super().__init__()
        self.folder = folder
        self.threshold = threshold
        self.exclude_subfolders = exclude_subfolders
        self._isRunning = True

    def run(self):
        images = {}
        try:
            # Contar archivos primero para progreso
            if self.exclude_subfolders:
                total_files = sum(1 for f in os.listdir(self.folder) 
                                 if os.path.isfile(os.path.join(self.folder, f)) and 
                                 f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')))
            else:
                total_files = sum(1 for _, _, files in os.walk(self.folder) 
                                 for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')))
            processed = 0
            
            if self.exclude_subfolders:
                # Procesar solo la carpeta principal
                for f in os.listdir(self.folder):
                    if not self._isRunning:
                        break
                        
                    file_path = os.path.join(self.folder, f)
                    if os.path.isfile(file_path) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                        try:
                            img = Image.open(file_path)
                            h = imagehash.phash(img)
                            images.setdefault(h, []).append(file_path)
                            processed += 1
                            self.progress.emit(int((processed / total_files) * 100))
                        except Exception as e:
                            print(f"Error con {file_path}: {e}")
            else:
                # Procesar incluyendo subcarpetas
                for root, _, files in os.walk(self.folder):
                    if not self._isRunning:
                        break
                        
                    for f in files:
                        if not self._isRunning:
                            break
                            
                        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                            path = os.path.join(root, f)
                            try:
                                img = Image.open(path)
                                h = imagehash.phash(img)
                                images.setdefault(h, []).append(path)
                                processed += 1
                                self.progress.emit(int((processed / total_files) * 100))
                            except Exception as e:
                                print(f"Error con {path}: {e}")
            
            # Si la búsqueda fue cancelada, no continuar con el procesamiento
            if not self._isRunning:
                self.cancelled.emit()
                self.finished.emit({})
                return
            
            # Algoritmo optimizado para agrupar hashes similares
            # Convertir el diccionario a una lista de hashes
            hashes = list(images.keys())
            n = len(hashes)
            
            # Inicializar el arreglo de padres para el union-find
            parent = list(range(n))
            rank = [0] * n
            
            # Función para encontrar la raíz de un elemento
            def find(x):
                if parent[x] != x:
                    parent[x] = find(parent[x])
                return parent[x]
            
            # Función para unir dos conjuntos
            def union(x, y):
                rx, ry = find(x), find(y)
                if rx == ry:
                    return
                if rank[rx] < rank[ry]:
                    parent[rx] = ry
                elif rank[rx] > rank[ry]:
                    parent[ry] = rx
                else:
                    parent[ry] = rx
                    rank[rx] += 1
            
            # Comparar todos los pares de hashes
            for i in range(n):
                if not self._isRunning:
                    break
                for j in range(i + 1, n):
                    if not self._isRunning:
                        break
                    scaled_threshold = self.threshold * 3  
                    if abs(hashes[i] - hashes[j]) <= scaled_threshold:
                        union(i, j)
            
            # Si la búsqueda fue cancelada, no continuar con el procesamiento
            if not self._isRunning:
                self.cancelled.emit()
                self.finished.emit({})
                return
            
            # Recopilar los grupos
            groups = {}
            for i in range(n):
                if not self._isRunning:
                    break
                root = find(i)
                if root not in groups:
                    groups[root] = []
                groups[root].append(hashes[i])
            
            # Crear el diccionario de duplicados
            duplicates = {}
            for root, group_hashes in groups.items():
                if not self._isRunning:
                    break
                all_files = []
                for h in group_hashes:
                    all_files.extend(images[h])
                
                if len(all_files) > 1:
                    duplicates[group_hashes[0]] = all_files
            
            # Si la búsqueda fue cancelada, no continuar con el procesamiento
            if not self._isRunning:
                self.cancelled.emit()
                self.finished.emit({})
                return
            
            self.finished.emit(duplicates)
        except Exception as e:
            self.error.emit(f"Error procesando imágenes: {str(e)}")
            self.finished.emit({})

    def stop(self):
        if self._isRunning:
            self._isRunning = False
            self.cancelled.emit()  # Emitir señal de cancelación

class CustomSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        # Configurar las marcas para que sean más visibles
        self.setTickPosition(QSlider.TicksBelow)
        self.setTickInterval(1)  # Marca para cada valor
        
    def paintEvent(self, event):
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Configurar el estilo de las marcas principales
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        
        width = self.width()
        height = self.height()
        
        # Posiciones de los niveles principales (0, 5, 10, 15, 20)
        positions = [0, 5, 10, 15, 20]
        
        for pos in positions:
            # Calcular la posición x en píxeles
            x = int((pos / 20) * (width - 20)) + 10  # 10px de margen
            
            # Dibujar una línea vertical más larga para los niveles principales
            painter.drawLine(x, height - 18, x, height - 8)
            
        # Dibujar líneas más cortas para los valores intermedios
        painter.setPen(QPen(QColor(180, 180, 180), 1))
        for i in range(21):
            if i not in positions:  # No dibujar donde ya están las líneas principales
                x = int((i / 20) * (width - 20)) + 10
                painter.drawLine(x, height - 15, x, height - 10)

class ImageGroupWidget(QWidget):
    def __init__(self, files, parent=None):
        super().__init__(parent)
        self.files = files
        self.selected_files = set()
        self.thumbnails_loaded = False
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        
        # Widget contenedor para las imágenes
        self.images_container = QWidget()
        self.images_layout = QHBoxLayout(self.images_container)
        self.images_layout.setSpacing(10)
        self.images_layout.setAlignment(Qt.AlignLeft)
        self.images_layout.setContentsMargins(0, 0, 0, 0)
        
        # Añadir cada imagen como un botón
        self.image_buttons = []
        for file_path in files:
            self.add_image_button(file_path)
        
        # Ajustar el tamaño del contenedor al contenido
        self.images_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.images_container.setMinimumHeight(150)
        
        self.layout.addWidget(self.images_container)
        
        # Carga diferida de miniaturas después de un pequeño retraso
        QTimer.singleShot(100, self.load_thumbnails)
    
    def add_image_button(self, file_path):
        try:
            btn = QPushButton()
            btn.setFixedSize(120, 140)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, path=file_path: self.toggle_selection(path, checked))
            
            btn_layout = QVBoxLayout(btn)
            btn_layout.setContentsMargins(5, 5, 5, 5)
            btn_layout.setSpacing(5)
            
            # Etiqueta para la imagen (inicialmente vacía)
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignCenter)
            img_label.setMinimumSize(100, 100)
            img_label.setMaximumSize(100, 100)
            img_label.setStyleSheet("background-color: #f0f0f0; border: 1px dashed #ccc;")
            btn_layout.addWidget(img_label)
            
            # Etiqueta para el nombre del archivo
            filename = os.path.basename(file_path)
            if len(filename) > 15:
                filename = filename[:12] + "..."
            
            name_label = QLabel(filename)
            name_label.setWordWrap(True)
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet("font-size: 9px;")
            btn_layout.addWidget(name_label)
            
            btn.file_path = file_path
            btn.img_label = img_label
            self.image_buttons.append(btn)
            self.images_layout.addWidget(btn)
        except Exception as e:
            print(f"No se pudo crear botón para {file_path}: {e}")
    
    def load_thumbnails(self):
        if self.thumbnails_loaded:
            return
            
        self.thumbnails_loaded = True
        for btn in self.image_buttons:
            try:
                file_path = btn.file_path
                img = Image.open(file_path)
                img.thumbnail((100, 100))
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())
                btn.img_label.setPixmap(pixmap)
                btn.img_label.setStyleSheet("")
            except Exception as e:
                print(f"No se pudo cargar miniatura de {file_path}: {e}")
                btn.img_label.setText("Error")
                btn.img_label.setStyleSheet("color: red;")
    
    def toggle_selection(self, file_path, selected):
        if selected:
            self.selected_files.add(file_path)
        else:
            self.selected_files.discard(file_path)
    
    def select_all(self):
        for btn in self.image_buttons:
            if hasattr(btn, 'file_path'):
                btn.setChecked(True)
                self.selected_files.add(btn.file_path)
    
    def deselect_all(self):
        for btn in self.image_buttons:
            if hasattr(btn, 'file_path'):
                btn.setChecked(False)
                self.selected_files.discard(btn.file_path)
    
    def invert_selection(self):
        for btn in self.image_buttons:
            if hasattr(btn, 'file_path'):
                if btn.isChecked():
                    btn.setChecked(False)
                    self.selected_files.discard(btn.file_path)
                else:
                    btn.setChecked(True)
                    self.selected_files.add(btn.file_path)

class PreviewDialog(QDialog):
    def __init__(self, image_paths, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vista previa de imágenes")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        container = QWidget()
        container_layout = QHBoxLayout(container)
        
        for path in image_paths:
            try:
                img = Image.open(path)
                img.thumbnail((400, 400))
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())
                
                label = QLabel()
                label.setPixmap(pixmap)
                label.setAlignment(Qt.AlignCenter)
                
                filename = os.path.basename(path)
                name_label = QLabel(filename)
                name_label.setAlignment(Qt.AlignCenter)
                name_label.setWordWrap(True)
                name_label.setMaximumWidth(400)
                
                img_layout = QVBoxLayout()
                img_layout.addWidget(label)
                img_layout.addWidget(name_label)
                
                container_layout.addLayout(img_layout)
            except Exception as e:
                print(f"Error al cargar {path}: {e}")
        
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

class DuplicateFinder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ImageSnapPurge - Eliminar duplicados de imágenes")
        self.resize(1300, 800)
        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # Estilo general de la ventana
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QPushButton:checked {
                background-color: #28a745;
                border: 3px solid #1e7e34;
                color: white;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QPushButton#cancel_button {
                background-color: #dc3545;
            }
            QPushButton#cancel_button:hover {
                background-color: #c82333;
            }
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
            }
            QGroupBox {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin-top: 35px;
                padding-top: 20px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 0 0 10px;
                background-color: transparent;
                color: #495057;
                font-weight: bold;
                font-size: 16px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #dee2e6;
                background: white;
                height: 8px;
                border-radius: 4px;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #4a86e8;
                border: 1px solid #3a76d8;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #3a76d8;
            }
            QSlider::add-page:horizontal {
                background: #e9ecef;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #4a86e8;
                border-radius: 4px;
            }
            QSlider:disabled {
                opacity: 0.7;
            }
            QLabel {
                color: #495057;
            }
            QCheckBox {
                color: #495057;
                font-size: 13px;
            }
            .info-label {
                background-color: #e3f2fd;
                color: #0d47a1;
                padding: 8px 12px;
                border-radius: 6px;
                font-weight: 600;
            }
            .progress-label {
                background-color: #e9ecef;
                color: #495057;
                padding: 8px 12px;
                border-radius: 6px;
                font-weight: 600;
            }
            .separator {
                background-color: #dee2e6;
                height: 1px;
                margin: 10px 0;
            }
            .group-title {
                color: #495057;
                font-size: 16px;
                font-weight: 600;
                padding: 10px;
                background-color: transparent;
                border-bottom: 2px solid #4a86e8;
                margin: 0px 0px 15px 0px;
            }
            .section-title {
                color: #495057;
                font-size: 13px;
                font-weight: 600;
                padding: 5px 0px 5px 10px;
                background-color: #f1f3f5;
                border-radius: 4px;
                margin: 5px 0px 10px 0px;
                border-left: 4px solid #4a86e8;
            }
        """)
        
        # Panel izquierdo - VISTA DE IMÁGENES
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # Título de resultados
        self.results_title = QLabel("Grupos de imágenes duplicadas")
        self.results_title.setProperty("class", "group-title")
        left_layout.addWidget(self.results_title)
        
        # Contenedor para los grupos de duplicados con scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Widget contenedor para los grupos
        self.groups_container = QWidget()
        self.groups_layout = QVBoxLayout(self.groups_container)
        self.groups_layout.setSpacing(15)
        self.groups_layout.setAlignment(Qt.AlignTop)
        self.groups_layout.setContentsMargins(10, 10, 10, 10)
        
        self.scroll_area.setWidget(self.groups_container)
        left_layout.addWidget(self.scroll_area)
        
        # Panel de paginación
        self.pagination_panel = QWidget()
        self.pagination_layout = QHBoxLayout(self.pagination_panel)
        self.pagination_layout.setContentsMargins(0, 10, 0, 10)
        
        self.btn_prev_page = QPushButton("← Anterior")
        self.btn_prev_page.clicked.connect(self.prev_page)
        self.btn_prev_page.setEnabled(False)
        self.pagination_layout.addWidget(self.btn_prev_page)
        
        self.page_label = QLabel("Página 1 de 1")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setStyleSheet("font-weight: 600; color: #495057;")
        self.pagination_layout.addWidget(self.page_label, 1)
        
        self.btn_next_page = QPushButton("Siguiente →")
        self.btn_next_page.clicked.connect(self.next_page)
        self.btn_next_page.setEnabled(False)
        self.pagination_layout.addWidget(self.btn_next_page)
        
        left_layout.addWidget(self.pagination_panel)
        self.pagination_panel.hide()
        
        # Panel derecho - CONFIGURACIÓN
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Grupo de selección de carpeta
        folder_group = QGroupBox("Origen de imágenes:")
        folder_layout = QVBoxLayout()
        folder_layout.setContentsMargins(15, 20, 15, 15)
        folder_layout.setSpacing(15)
        
        self.btn_select = QPushButton("📁 Seleccionar carpeta")
        self.btn_select.setMinimumWidth(180)
        self.btn_select.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.btn_select)
        
        # Botón de cancelar búsqueda (inicialmente oculto)
        self.btn_cancel = QPushButton("❌ Cancelar búsqueda")
        self.btn_cancel.setObjectName("cancel_button")
        self.btn_cancel.setMinimumWidth(180)
        self.btn_cancel.clicked.connect(self.cancel_search)
        self.btn_cancel.hide()
        folder_layout.addWidget(self.btn_cancel)
        
        folder_group.setLayout(folder_layout)
        right_layout.addWidget(folder_group)
        
        # Grupo de configuración de búsqueda
        config_group = QGroupBox("Configuración de búsqueda:")
        config_layout = QVBoxLayout()
        config_layout.setContentsMargins(15, 20, 15, 15)
        config_layout.setSpacing(15)
        
        # Opción para excluir subcarpetas
        self.exclude_subfolders = QCheckBox("Excluir subcarpetas")
        self.exclude_subfolders.setChecked(False)
        config_layout.addWidget(self.exclude_subfolders)
        
        # Nivel de similitud - Título de sección mejorado
        self.rigidez_title = QLabel("Nivel de similitud")
        self.rigidez_title.setProperty("class", "section-title")
        config_layout.addWidget(self.rigidez_title)
        
        # Slider personalizado con marcadores mejorados
        self.slider = CustomSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(20)
        self.slider.setValue(15)  # Valor por defecto en Alta (corregido)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(5)
        self.slider.valueChanged.connect(self.update_rigidez_label)
        config_layout.addWidget(self.slider)
        
        # Etiquetas de niveles con mejor alineación
        niveles_layout = QHBoxLayout()
        niveles_layout.setContentsMargins(0, 0, 0, 0)
        
        self.label_muy_baja = QLabel("Muy baja")
        self.label_muy_baja.setAlignment(Qt.AlignLeft)
        self.label_muy_baja.setStyleSheet("color: #2e7d32; font-weight: bold; font-size: 11px;")
        
        self.label_baja = QLabel("Baja")
        self.label_baja.setAlignment(Qt.AlignCenter)
        self.label_baja.setStyleSheet("color: #4caf50; font-weight: bold; font-size: 11px;")
        
        self.label_media = QLabel("Media")
        self.label_media.setAlignment(Qt.AlignCenter)
        self.label_media.setStyleSheet("color: #ffc107; font-weight: bold; font-size: 11px;")
        
        self.label_alta = QLabel("Alta")
        self.label_alta.setAlignment(Qt.AlignCenter)
        self.label_alta.setStyleSheet("color: #ff9800; font-weight: bold; font-size: 11px;")
        
        self.label_exacto = QLabel("Exacto")
        self.label_exacto.setAlignment(Qt.AlignRight)
        self.label_exacto.setStyleSheet("color: #d32f2f; font-weight: bold; font-size: 11px;")
        
        niveles_layout.addWidget(self.label_muy_baja)
        niveles_layout.addWidget(self.label_baja)
        niveles_layout.addWidget(self.label_media)
        niveles_layout.addWidget(self.label_alta)
        niveles_layout.addWidget(self.label_exacto)
        
        config_layout.addLayout(niveles_layout)
        
        # Descripción del nivel actual
        self.rigidez_desc = QLabel("Nivel actual: Alta (15)")  # Corregido para mostrar Alta por defecto
        self.rigidez_desc.setAlignment(Qt.AlignCenter)
        self.rigidez_desc.setStyleSheet("color: #ff9800; font-weight: 600; font-size: 12px;")
        config_layout.addWidget(self.rigidez_desc)
        
        config_group.setLayout(config_layout)
        right_layout.addWidget(config_group)
        
        # Grupo de información
        info_group = QGroupBox("Información:")
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(15, 20, 15, 15)
        info_layout.setSpacing(15)
        
        self.info_label = QLabel("Listo para buscar duplicados")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setProperty("class", "info-label")
        info_layout.addWidget(self.info_label)
        
        # Barra de progreso
        self.progress_label = QLabel("Progreso: 0%")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setProperty("class", "progress-label")
        info_layout.addWidget(self.progress_label)
        
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)
        
        # Grupo de acciones
        actions_group = QGroupBox("Acciones:")
        actions_layout = QVBoxLayout()
        actions_layout.setContentsMargins(15, 20, 15, 15)
        actions_layout.setSpacing(10)
        
        # Botones de selección - Título de sección mejorado
        selection_title = QLabel("Selección")
        selection_title.setProperty("class", "section-title")
        actions_layout.addWidget(selection_title)
        
        self.btn_select_all = QPushButton("✓ Seleccionar todas")
        self.btn_select_all.clicked.connect(self.select_all_images)
        actions_layout.addWidget(self.btn_select_all)
        
        self.btn_deselect_all = QPushButton("✗ Deseleccionar todas")
        self.btn_deselect_all.clicked.connect(self.deselect_all_images)
        actions_layout.addWidget(self.btn_deselect_all)
        
        self.btn_invert_selection = QPushButton("⇄ Invertir selección")
        self.btn_invert_selection.clicked.connect(self.invert_selection)
        actions_layout.addWidget(self.btn_invert_selection)

        # Auto-selección inteligente (mantener mejor resolución)
        self.btn_autoselect_best = QPushButton("⭐ Seleccionar duplicados (mantener mejor)")
        self.btn_autoselect_best.clicked.connect(self.autoselect_keep_best)
        actions_layout.addWidget(self.btn_autoselect_best)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setProperty("class", "separator")
        actions_layout.addWidget(separator)
        
        # Botones de acción - Título de sección mejorado
        action_title = QLabel("Operaciones")
        action_title.setProperty("class", "section-title")
        actions_layout.addWidget(action_title)
        
        self.btn_delete = QPushButton("🗑️ Eliminar seleccionados")
        self.btn_delete.clicked.connect(self.delete_selected)
        actions_layout.addWidget(self.btn_delete)
        
        self.btn_move = QPushButton("📂 Mover seleccionados")
        self.btn_move.clicked.connect(self.move_selected)
        actions_layout.addWidget(self.btn_move)
        
        # Estadísticas
        self.stats_label = QLabel("No hay resultados")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setStyleSheet("background-color: #f8f9fa; color: #6c757d; padding: 10px; border-radius: 6px; border: 1px solid #dee2e6;")
        actions_layout.addWidget(self.stats_label)
        
        actions_group.setLayout(actions_layout)
        right_layout.addWidget(actions_group)
        
        # Espacio flexible al final
        right_layout.addStretch()
        
        # Añadir paneles al layout principal
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)   # Panel izquierdo: Vista de imágenes
        splitter.addWidget(right_panel)  # Panel derecho: Configuración
        splitter.setSizes([900, 350])    # Ancho inicial
        splitter.setCollapsible(0, False) # Panel izquierdo no colapsable
        splitter.setCollapsible(1, False) # Panel derecho no colapsable
        
        self.layout.addWidget(splitter)
        
        # Aplicar estilo de negrita y tamaño mayor a los títulos de los QGroupBox
        self.applyGroupBoxTitleStyle()
        
        self.images = {}
        self.thread = None
        self.worker = None
        self.group_widgets = []
        
        # Variables para paginación
        self.current_page = 1
        self.groups_per_page = 5
        self.total_pages = 1
        
        # Forzar la actualización inicial del slider
        self.update_rigidez_label(self.slider.value())

    def applyGroupBoxTitleStyle(self):
        # Buscar todos los QGroupBox en la interfaz
        for group_box in self.findChildren(QGroupBox):
            # Crear una fuente en negrita y con tamaño mayor
            font = QFont()
            font.setBold(True)
            font.setPointSize(12)  # Tamaño de fuente mayor
            
            # Aplicar la fuente al QGroupBox
            group_box.setFont(font)
            
            # Forzar el estilo del título mediante CSS
            group_box.setStyleSheet("""
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 0 0 10px;
                    background-color: transparent;
                    color: #495057;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)

    def update_rigidez_label(self, value):
        # Lógica corregida: de menor a mayor (menos estricto a más estricto)
        if value == 0:
            nivel = "Muy baja"
            color = "#2e7d32"
        elif value <= 5:
            nivel = "Baja"
            color = "#4caf50"
        elif value <= 10:
            nivel = "Media"
            color = "#ffc107"
        elif value <= 15:
            nivel = "Alta"
            color = "#ff9800"
        else:
            nivel = "Exacto"
            color = "#d32f2f"
            
        self.rigidez_desc.setText(f"Nivel actual: {nivel} ({value})")
        self.rigidez_desc.setStyleSheet(f"color: {color}; font-weight: 600; font-size: 12px;")

    def select_folder(self):
        if self.thread and self.thread.isRunning():
            QMessageBox.information(self, "Proceso en curso", 
                                   "Ya hay un proceso en ejecución. Espere a que termine.")
            return
            
        folder = QFileDialog.getExistingDirectory(self, "Selecciona carpeta de imágenes")
        if folder:
            self.clear_groups()
            self.btn_select.setEnabled(False)
            self.btn_cancel.show()  # Mostrar botón de cancelar
            self.slider.setEnabled(False)  # Deshabilitar slider
            self.exclude_subfolders.setEnabled(False)  # Deshabilitar checkbox
            self.progress_label.setText("Progreso: 0%")
            self.info_label.setText("Buscando duplicados...")
            
            self.thread = QThread()
            # Invertimos el valor para el Worker (más alto = más permisivo)
            self.worker = Worker(folder, 20 - self.slider.value(), self.exclude_subfolders.isChecked())
            self.worker.moveToThread(self.thread)
            
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.on_finished)
            self.worker.progress.connect(self.update_progress)
            self.worker.error.connect(self.on_error)
            self.worker.cancelled.connect(self.on_cancelled)  # Conectar señal de cancelación
            
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.finished.connect(self.on_thread_finished)
            
            self.thread.start()

    def cancel_search(self):
        if self.worker:
            self.worker.stop()
            self.info_label.setText("Cancelando búsqueda...")
            self.btn_cancel.setEnabled(False)

    def on_cancelled(self):
        self.info_label.setText("Búsqueda cancelada")
        self.progress_label.setStyleSheet("background-color: #ffc107; color: white; padding: 8px 12px; border-radius: 6px; font-weight: 600;")
        self.reset_ui_after_search()

    def clear_groups(self):
        for i in reversed(range(self.groups_layout.count())): 
            self.groups_layout.itemAt(i).widget().setParent(None)
        self.group_widgets = []
        self.current_page = 1
        self.pagination_panel.hide()
        self.stats_label.setText("No hay resultados")

    def update_progress(self, value):
        self.progress_label.setText(f"Progreso: {value}%")
        if value < 33:
            color = "#f44336"
        elif value < 66:
            color = "#ff9800"
        else:
            color = "#4caf50"
            
        self.progress_label.setStyleSheet(f"background-color: {color}; color: white; padding: 8px 12px; border-radius: 6px; font-weight: 600;")

    def on_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.reset_ui_after_search()
        self.info_label.setText("Error en la búsqueda")
        self.progress_label.setStyleSheet("background-color: #e9ecef; color: #495057; padding: 8px 12px; border-radius: 6px; font-weight: 600;")

    def on_finished(self, duplicates):
        self.images = duplicates
        self.progress_label.setText("Búsqueda completada")
        self.progress_label.setStyleSheet("background-color: #4caf50; color: white; padding: 8px 12px; border-radius: 6px; font-weight: 600;")
        
        if not duplicates:
            # Mostrar mensaje de no se encontraron duplicados
            self.info_label.setText("No se encontraron imágenes duplicadas")
            self.reset_ui_after_search()
            QMessageBox.information(self, "Resultado", "No se encontraron imágenes duplicadas.")
            return
        
        total_groups = len(duplicates)
        total_images = sum(len(files) for files in duplicates.values())
        total_duplicates = total_images - total_groups
        
        self.info_label.setText(f"Búsqueda completada: {total_groups} grupos, {total_duplicates} duplicados")
        
        for files in duplicates.values():
            group_widget = ImageGroupWidget(files)
            self.group_widgets.append(group_widget)
        
        self.total_pages = max(1, (len(self.group_widgets) + self.groups_per_page - 1) // self.groups_per_page)
        self.current_page = 1
        
        self.show_page(1)
        
        if self.total_pages > 1:
            self.pagination_panel.show()
        
        self.update_stats(total_groups, total_images, total_duplicates)
        self.reset_ui_after_search()

    def reset_ui_after_search(self):
        # Restaurar el estado de la interfaz después de la búsqueda
        self.btn_select.setEnabled(True)
        self.btn_cancel.hide()
        self.btn_cancel.setEnabled(True)  # Rehabilitar el botón para la próxima búsqueda
        self.slider.setEnabled(True)
        self.exclude_subfolders.setEnabled(True)

    def update_stats(self, groups, images, duplicates):
        self.stats_label.setText(
            f"<b>Grupos:</b> {groups} | "
            f"<b>Imágenes:</b> {images} | "
            f"<b>Duplicados:</b> {duplicates}"
        )

    def on_thread_finished(self):
        self.thread = None
        self.worker = None

    def show_page(self, page_num):
        for i in reversed(range(self.groups_layout.count())): 
            self.groups_layout.itemAt(i).widget().setParent(None)
        
        start_idx = (page_num - 1) * self.groups_per_page
        end_idx = min(start_idx + self.groups_per_page, len(self.group_widgets))
        
        for i in range(start_idx, end_idx):
            group_widget = self.group_widgets[i]
            self.groups_layout.addWidget(group_widget)
            
            if i < end_idx - 1:
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Sunken)
                separator.setStyleSheet("background-color: #dee2e6;")
                self.groups_layout.addWidget(separator)
        
        self.page_label.setText(f"Página {page_num} de {self.total_pages}")
        self.btn_prev_page.setEnabled(page_num > 1)
        self.btn_next_page.setEnabled(page_num < self.total_pages)
        self.current_page = page_num

    def prev_page(self):
        if self.current_page > 1:
            self.show_page(self.current_page - 1)

    def next_page(self):
        if self.current_page < self.total_pages:
            self.show_page(self.current_page + 1)

    def get_selected_files(self):
        selected_files = []
        for group_widget in self.group_widgets:
            selected_files.extend(group_widget.selected_files)
        return selected_files

    def select_all_images(self):
        for group_widget in self.group_widgets:
            group_widget.select_all()

    def deselect_all_images(self):
        for group_widget in self.group_widgets:
            group_widget.deselect_all()

    def invert_selection(self):
        for group_widget in self.group_widgets:
            group_widget.invert_selection()

    def delete_selected(self):
        selected_files = self.get_selected_files()
        if not selected_files:
            QMessageBox.information(self, "Atención", "No seleccionaste nada.")
            return
            
        reply = QMessageBox.question(self, "Confirmar eliminación", 
                                    f"¿Seguro que quieres eliminar {len(selected_files)} archivos?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            deleted = 0
            for file_path in selected_files:
                try:
                    send2trash(file_path)
                    deleted += 1
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"No se pudo borrar {file_path}:\n{e}")
            
            self.refresh_groups()
            QMessageBox.information(self, "Listo", f"Se eliminaron {deleted} archivos.")

    def autoselect_keep_best(self):
        """Selecciona automáticamente todos los duplicados de cada grupo
        manteniendo sin seleccionar la imagen de mejor resolución.
        Criterio: mayor área (ancho*alto); en empate, mayor tamaño en bytes; luego más reciente por mtime.
        """
        groups_processed = 0
        for group_widget in self.group_widgets:
            files = list(group_widget.files)
            if len(files) < 2:
                continue

            best_file = None
            best_area = -1
            best_size = -1
            best_mtime = -1

            # Calcular métricas por archivo
            for path in files:
                width = height = 0
                try:
                    with Image.open(path) as img:
                        width, height = img.size
                except Exception:
                    pass
                area = width * height
                try:
                    size_bytes = os.path.getsize(path)
                except Exception:
                    size_bytes = -1
                try:
                    mtime = os.path.getmtime(path)
                except Exception:
                    mtime = -1

                candidate_better = False
                if area > best_area:
                    candidate_better = True
                elif area == best_area and size_bytes > best_size:
                    candidate_better = True
                elif area == best_area and size_bytes == best_size and mtime > best_mtime:
                    candidate_better = True

                if candidate_better:
                    best_file = path
                    best_area = area
                    best_size = size_bytes
                    best_mtime = mtime

            # Aplicar selección: marcar todos excepto el mejor
            if best_file:
                group_widget.deselect_all()
                for btn in group_widget.image_buttons:
                    if hasattr(btn, 'file_path'):
                        if btn.file_path != best_file:
                            btn.setChecked(True)
                            group_widget.selected_files.add(btn.file_path)
                        else:
                            btn.setChecked(False)
                            group_widget.selected_files.discard(btn.file_path)
                groups_processed += 1

        QMessageBox.information(self, "Auto-selección", f"Se aplicó la auto-selección en {groups_processed} grupos.")

    def move_selected(self):
        selected_files = self.get_selected_files()
        if not selected_files:
            QMessageBox.information(self, "Atención", "No seleccionaste nada.")
            return
            
        folder = QFileDialog.getExistingDirectory(self, "Selecciona carpeta destino")
        if not folder:
            return
            
        moved = 0
        for file_path in selected_files:
            try:
                filename = os.path.basename(file_path)
                new_path = os.path.join(folder, filename)
                
                if os.path.exists(new_path):
                    base, ext = os.path.splitext(filename)
                    i = 1
                    while os.path.exists(os.path.join(folder, f"{base}_{i}{ext}")):
                        i += 1
                    new_path = os.path.join(folder, f"{base}_{i}{ext}")
                
                os.rename(file_path, new_path)
                moved += 1
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo mover {file_path}:\n{e}")
        
        self.refresh_groups()
        QMessageBox.information(self, "Listo", f"Se movieron {moved} archivos.")

    def refresh_groups(self):
        selected_files = set(self.get_selected_files())
        
        remaining_duplicates = {}
        for hash_key, files in self.images.items():
            remaining_files = [f for f in files if os.path.exists(f)]
            if len(remaining_files) > 1:
                remaining_duplicates[hash_key] = remaining_files
        
        self.images = remaining_duplicates
        
        self.group_widgets = []
        for files in remaining_duplicates.values():
            group_widget = ImageGroupWidget(files)
            self.group_widgets.append(group_widget)
            
            for file_path in files:
                if file_path in selected_files:
                    for btn in group_widget.image_buttons:
                        if hasattr(btn, 'file_path') and btn.file_path == file_path:
                            btn.setChecked(True)
                            group_widget.selected_files.add(file_path)
                            break
        
        self.total_pages = max(1, (len(self.group_widgets) + self.groups_per_page - 1) // self.groups_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        
        self.show_page(self.current_page)
        
        if self.total_pages > 1:
            self.pagination_panel.show()
        else:
            self.pagination_panel.hide()
        
        # Actualizar estadísticas
        if remaining_duplicates:
            total_groups = len(remaining_duplicates)
            total_images = sum(len(files) for files in remaining_duplicates.values())
            total_duplicates = total_images - total_groups
            self.update_stats(total_groups, total_images, total_duplicates)
        else:
            self.stats_label.setText("No hay resultados")

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
        
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            if not self.thread.wait(3000):
                print("Advertencia: El hilo no terminó a tiempo")
            
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DuplicateFinder()
    window.show()
    sys.exit(app.exec_())