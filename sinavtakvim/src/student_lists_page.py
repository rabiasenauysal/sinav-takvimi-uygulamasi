# student_lists_page.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit, QSpinBox,
    QHeaderView, QMessageBox, QDialog, QDialogButtonBox, QFormLayout,
    QFrame, QGraphicsDropShadowEffect, QComboBox, QGroupBox, QTextEdit,
    QSplitter, QTabWidget
)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt

class AddStudentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Ders Ekle")
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 10px;
            }
            QLabel {
                color: #2c3e50;
                font-weight: 600;
            }
            QLineEdit, QSpinBox, QComboBox {
                padding: 8px;
                border: 2px solid #e0e6ed;
                border-radius: 8px;
                font-size: 12px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border-color: #667eea;
            }
        """)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        form_layout = QFormLayout()
        
        self.grade_combo = QComboBox()
        self.grade_combo.addItems(["1", "2", "3", "4"])
        
        self.course_code_edit = QLineEdit()
        self.course_code_edit.setPlaceholderText("Örn: BMH123")
        
        self.group_spin = QSpinBox()
        self.group_spin.setRange(1, 10)
        self.group_spin.setValue(1)
        
        self.course_name_edit = QLineEdit()
        self.course_name_edit.setPlaceholderText("Ders adını giriniz")
        
        self.student_count_spin = QSpinBox()
        self.student_count_spin.setRange(0, 500)
        self.student_count_spin.setValue(30)
        
        self.instructor_edit = QLineEdit()
        self.instructor_edit.setPlaceholderText("Öğretim üyesi adı")
        
        form_layout.addRow("Sınıf:", self.grade_combo)
        form_layout.addRow("Ders Kodu:", self.course_code_edit)
        form_layout.addRow("Grup No:", self.group_spin)
        form_layout.addRow("Ders Adı:", self.course_name_edit)
        form_layout.addRow("Öğrenci Sayısı:", self.student_count_spin)
        form_layout.addRow("Öğretim Üyesi:", self.instructor_edit)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setStyleSheet("""
            QPushButton {
                background: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #5a6fd8;
            }
        """)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
    def get_data(self):
        return {
            'grade': self.grade_combo.currentText(),
            'course_code': self.course_code_edit.text().strip(),
            'group': self.group_spin.value(),
            'course_name': self.course_name_edit.text().strip(),
            'student_count': self.student_count_spin.value(),
            'instructor': self.instructor_edit.text().strip()
        }

class EditStudentDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ders Düzenle")
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 10px;
            }
            QLabel {
                color: #2c3e50;
                font-weight: 600;
            }
            QLineEdit, QSpinBox, QComboBox {
                padding: 8px;
                border: 2px solid #e0e6ed;
                border-radius: 8px;
                font-size: 12px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border-color: #667eea;
            }
        """)
        self.setup_ui(data)
        
    def setup_ui(self, data):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        form_layout = QFormLayout()
        
        self.grade_combo = QComboBox()
        self.grade_combo.addItems(["1", "2", "3", "4"])
        self.grade_combo.setCurrentText(str(data['grade']))
        
        self.course_code_edit = QLineEdit(data['course_code'])
        
        self.group_spin = QSpinBox()
        self.group_spin.setRange(1, 10)
        self.group_spin.setValue(data['group'])
        
        self.course_name_edit = QLineEdit(data['course_name'])
        
        self.student_count_spin = QSpinBox()
        self.student_count_spin.setRange(0, 500)
        self.student_count_spin.setValue(data['student_count'])
        
        self.instructor_edit = QLineEdit(data['instructor'])
        
        form_layout.addRow("Sınıf:", self.grade_combo)
        form_layout.addRow("Ders Kodu:", self.course_code_edit)
        form_layout.addRow("Grup No:", self.group_spin)
        form_layout.addRow("Ders Adı:", self.course_name_edit)
        form_layout.addRow("Öğrenci Sayısı:", self.student_count_spin)
        form_layout.addRow("Öğretim Üyesi:", self.instructor_edit)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setStyleSheet("""
            QPushButton {
                background: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #5a6fd8;
            }
        """)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
    def get_data(self):
        return {
            'grade': int(self.grade_combo.currentText()),
            'course_code': self.course_code_edit.text().strip(),
            'group': self.group_spin.value(),
            'course_name': self.course_name_edit.text().strip(),
            'student_count': self.student_count_spin.value(),
            'instructor': self.instructor_edit.text().strip()
        }

class StudentListsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ders Bazlı Öğrenci Sayıları")
        self.setGeometry(200, 200, 1200, 700)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f8f9fa, stop: 1 #e9ecef);
            }
        """)
        
        # Başlangıç verileri (DersBazliOgrenciSayisi2025Bahar.pdf'den)
        self.student_data = [
            {'grade': 1, 'course_code': 'ATA002', 'group': 1, 'course_name': 'Atatürk İlkeleri ve İnkılâp Tarihi II', 'student_count': 89, 'instructor': 'Öğr. Gör. Başak KUZUCUOĞLU'},
            {'grade': 1, 'course_code': 'BMH122', 'group': 1, 'course_name': 'Elektrik Devreleri', 'student_count': 161, 'instructor': 'Dr. Öğr. Üyesi Halil İbrahim COŞAR'},
            {'grade': 1, 'course_code': 'BMH123', 'group': 1, 'course_name': 'Bilgisayar Programlama II', 'student_count': 84, 'instructor': 'Prof. Dr. Mehmet BAKIR'},
            {'grade': 1, 'course_code': 'BMH123', 'group': 2, 'course_name': 'Bilgisayar Programlama II', 'student_count': 104, 'instructor': 'Dr. Öğr. Üyesi Çağrı ARISOY'},
            {'grade': 1, 'course_code': 'KP001', 'group': 1, 'course_name': 'Kariyer Planlama', 'student_count': 95, 'instructor': 'Dr. Öğr. Üyesi Ahmet Sertol KÖKSAL'},
            {'grade': 1, 'course_code': 'MMF001', 'group': 1, 'course_name': 'İş Sağlığı ve Güvenliği I', 'student_count': 109, 'instructor': 'Öğr. Gör. Esra DEMİRCİ ELMALI'},
            {'grade': 1, 'course_code': 'MMF102', 'group': 1, 'course_name': 'Fizik-II', 'student_count': 93, 'instructor': 'Dr. Öğr. Üyesi Tarık AKAN'},
            {'grade': 1, 'course_code': 'MMF102', 'group': 2, 'course_name': 'Fizik-II', 'student_count': 87, 'instructor': 'Prof. Dr. Ümüt TEMİZER'},
            {'grade': 1, 'course_code': 'MMF104', 'group': 1, 'course_name': 'Matematik-II', 'student_count': 82, 'instructor': 'Prof. Dr. Yusuf PANDIR'},
            {'grade': 1, 'course_code': 'MMF104', 'group': 2, 'course_name': 'Matematik-II', 'student_count': 81, 'instructor': 'Doç. Dr. Hüseyin KAMACI'},
            {'grade': 1, 'course_code': 'TDI002', 'group': 1, 'course_name': 'Türk Dili II', 'student_count': 91, 'instructor': 'Öğr. Gör. Akın UYAR'},
            {'grade': 1, 'course_code': 'YDL002', 'group': 1, 'course_name': 'Yabancı Dil II (İngilizce)', 'student_count': 44, 'instructor': 'Öğr. Gör. Emel EGEMEN'},
            {'grade': 2, 'course_code': 'BMH240', 'group': 1, 'course_name': 'Diferansiyel Denklemler', 'student_count': 110, 'instructor': 'Doç. Dr. Volkan ASLAN'},
            {'grade': 2, 'course_code': 'BMH243', 'group': 1, 'course_name': 'Veri Yapıları ve Algoritmalar', 'student_count': 121, 'instructor': 'Dr. Öğr. Üyesi Gökalp ÇINARER'},
            {'grade': 2, 'course_code': 'BMH244', 'group': 1, 'course_name': 'Ayrık İşlemsel Yapılar', 'student_count': 101, 'instructor': 'Dr. Öğr. Üyesi Demet TAYLAN'},
            {'grade': 2, 'course_code': 'BMH246', 'group': 1, 'course_name': 'Veri Analizine Giriş', 'student_count': 114, 'instructor': 'Dr. Öğr. Üyesi Mehmet KARABULUT'},
            {'grade': 2, 'course_code': 'BMH247', 'group': 1, 'course_name': 'Staj I', 'student_count': 12, 'instructor': 'Dr. Öğr. Üyesi Çağrı ARISOY'},
            {'grade': 2, 'course_code': 'BMH248', 'group': 1, 'course_name': 'Olasılık ve İstatistik', 'student_count': 88, 'instructor': 'Dr. Öğr. Üyesi Ahmet Sertol KÖKSAL'},
            {'grade': 2, 'course_code': 'BMH248', 'group': 2, 'course_name': 'Olasılık ve İstatistik', 'student_count': 61, 'instructor': 'Dr. Öğr. Üyesi Ahmet Sertol KÖKSAL'},
            {'grade': 2, 'course_code': 'BMH249', 'group': 1, 'course_name': 'Dosya Organizasyonu', 'student_count': 120, 'instructor': 'Dr. Öğr. Üyesi Çağrı ARISOY'},
            {'grade': 3, 'course_code': 'ADSL04', 'group': 1, 'course_name': 'Alan Dışı Seçmeli Ders', 'student_count': 0, 'instructor': '-'},
            {'grade': 3, 'course_code': 'BMH361', 'group': 1, 'course_name': 'Bilgisayar Ağları', 'student_count': 119, 'instructor': 'Prof. Dr. Mehmet BAKIR'},
            {'grade': 3, 'course_code': 'BMH364', 'group': 1, 'course_name': 'Algoritma Analizi ve Tasarımı', 'student_count': 65, 'instructor': 'Dr. Öğr. Üyesi Gökalp ÇINARER'},
            {'grade': 3, 'course_code': 'BMH367', 'group': 1, 'course_name': 'Yapay Zeka', 'student_count': 102, 'instructor': 'Dr. Öğr. Üyesi Hasan ULUTAŞ'},
            {'grade': 3, 'course_code': 'BMH521', 'group': 1, 'course_name': 'Veri İletişimi', 'student_count': 64, 'instructor': 'Prof. Dr. Mehmet BAKIR'},
            {'grade': 3, 'course_code': 'BMH522', 'group': 1, 'course_name': 'Gömülü Sistemler', 'student_count': 100, 'instructor': 'Dr. Öğr. Üyesi Mehmet KARABULUT'},
            {'grade': 3, 'course_code': 'BMH523', 'group': 1, 'course_name': 'İşletim Sistemleri Kavramları', 'student_count': 29, 'instructor': 'Dr. Öğr. Üyesi Çağrı ARISOY'},
            {'grade': 3, 'course_code': 'BMH594', 'group': 1, 'course_name': 'Temel İş İngilizcesi', 'student_count': 58, 'instructor': 'Doç. Dr. Muhammet Emin ŞAHİN'},
            {'grade': 4, 'course_code': 'BMH473', 'group': 1, 'course_name': 'Staj II', 'student_count': 9, 'instructor': 'Dr. Öğr. Üyesi Çağrı ARISOY'},
            {'grade': 4, 'course_code': 'BMH474', 'group': 1, 'course_name': 'Bilgisayar Mühendisliği Tasarımı', 'student_count': 6, 'instructor': 'Dr. Öğr. Üyesi Mehmet KARABULUT'},
            {'grade': 4, 'course_code': 'BMH474', 'group': 2, 'course_name': 'Bilgisayar Mühendisliği Tasarımı', 'student_count': 10, 'instructor': 'Dr. Öğr. Üyesi Hasan ULUTAŞ'},
            {'grade': 4, 'course_code': 'BMH481', 'group': 1, 'course_name': 'Bitirme Projesi', 'student_count': 14, 'instructor': 'Dr. Öğr. Üyesi Ahmet Sertol KÖKSAL'},
            {'grade': 4, 'course_code': 'BMH481', 'group': 2, 'course_name': 'Bitirme Projesi', 'student_count': 0, 'instructor': ''},
            {'grade': 4, 'course_code': 'BMH481', 'group': 3, 'course_name': 'Bitirme Projesi', 'student_count': 11, 'instructor': 'Dr. Öğr. Üyesi Hasan ULUTAŞ'},
            {'grade': 4, 'course_code': 'BMH481', 'group': 4, 'course_name': 'Bitirme Projesi', 'student_count': 8, 'instructor': 'Prof. Dr. Mehmet BAKIR'},
            {'grade': 4, 'course_code': 'BMH481', 'group': 5, 'course_name': 'Bitirme Projesi', 'student_count': 10, 'instructor': 'Dr. Öğr. Üyesi Mehmet KARABULUT'},
            {'grade': 4, 'course_code': 'BMH481', 'group': 6, 'course_name': 'Bitirme Projesi', 'student_count': 5, 'instructor': 'Dr. Öğr. Üyesi Gökalp ÇINARER'},
            {'grade': 4, 'course_code': 'BMH481', 'group': 7, 'course_name': 'Bitirme Projesi', 'student_count': 12, 'instructor': 'Dr. Öğr. Üyesi Çağrı ARISOY'},
            {'grade': 4, 'course_code': 'BMH481', 'group': 8, 'course_name': 'Bitirme Projesi', 'student_count': 2, 'instructor': 'Doç. Dr. Muhammet Emin ŞAHİN'},
            {'grade': 4, 'course_code': 'MMF002', 'group': 1, 'course_name': 'İş Sağlığı ve Güvenliği II', 'student_count': 81, 'instructor': 'Öğr. Gör. Esra DEMİRCİ ELMALI'},
            {'grade': 4, 'course_code': 'BMH705', 'group': 1, 'course_name': 'Biyomedikal Mühendisliğin Temelleri', 'student_count': 34, 'instructor': 'Doç. Dr. Muhammet Emin ŞAHİN'},
            {'grade': 4, 'course_code': 'BMH708', 'group': 1, 'course_name': 'Veri Madenciliğine Giriş', 'student_count': 37, 'instructor': 'Öğr. Gör. Kazım KILIÇ'},
            {'grade': 4, 'course_code': 'BMH713', 'group': 1, 'course_name': 'Veri Tabanı Programlama', 'student_count': 18, 'instructor': 'Dr. Öğr. Üyesi Hasan ULUTAŞ'},
            {'grade': 4, 'course_code': 'BMH715', 'group': 1, 'course_name': 'Bilgi Güvenliği', 'student_count': 43, 'instructor': 'Dr. Öğr. Üyesi Ahmet Sertol KÖKSAL'},
            {'grade': 4, 'course_code': 'BMH722', 'group': 1, 'course_name': 'Mikrokontrolcü Uygulamaları', 'student_count': 37, 'instructor': 'Dr. Öğr. Üyesi Mehmet KARABULUT'},
            {'grade': 4, 'course_code': 'BMH732', 'group': 1, 'course_name': 'Genetik Algoritmalar ve Programlama', 'student_count': 26, 'instructor': 'Dr. Öğr. Üyesi Gökalp ÇINARER'},
            {'grade': 4, 'course_code': 'BMH739', 'group': 1, 'course_name': 'Kalite Kontrol', 'student_count': 34, 'instructor': 'Dr. Öğr. Üyesi Hasan ULUTAŞ'},
        ]
        
        self.setup_ui()
        self.populate_table()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Başlık
        title_frame = QFrame()
        title_frame.setFixedHeight(80)
        title_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #667eea, stop: 1 #764ba2);
                border-radius: 15px;
            }
        """)
        
        title_layout = QVBoxLayout(title_frame)
        
        title = QLabel("👥 Ders Bazlı Öğrenci Sayıları")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: white; background: none;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("2025 Bahar Dönemi - Mevcut öğrenci sayılarını görüntüleyin ve yönetin")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 180); background: none;")
        subtitle.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        layout.addWidget(title_frame)
        
        # İstatistik kartları
        stats_layout = QHBoxLayout()
        
        total_courses = len(self.student_data)
        total_students = sum(item['student_count'] for item in self.student_data)
        total_instructors = len(set(item['instructor'] for item in self.student_data if item['instructor'] and item['instructor'] != '-'))
        
        stats = [
            ("📚", "Toplam Ders", str(total_courses)),
            ("👨‍🎓", "Toplam Öğrenci", str(total_students)),
            ("👨‍🏫", "Öğretim Üyesi", str(total_instructors))
        ]
        
        for icon, title, value in stats:
            card = self.create_stat_card(icon, title, value)
            stats_layout.addWidget(card)
        
        layout.addLayout(stats_layout)
        
        # Arama ve buton alanı
        controls_layout = QHBoxLayout()
        
        # Arama
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Ders kodu, ders adı veya öğretim üyesi ara...")
        self.search_edit.setFixedHeight(40)
        self.search_edit.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #e0e6ed;
                border-radius: 10px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        self.search_edit.textChanged.connect(self.filter_table)
        
        # Sınıf filtresi
        self.grade_filter = QComboBox()
        self.grade_filter.addItems(["Tüm Sınıflar", "1. Sınıf", "2. Sınıf", "3. Sınıf", "4. Sınıf"])
        self.grade_filter.setFixedHeight(40)
        self.grade_filter.setStyleSheet("""
            QComboBox {
                padding: 10px 15px;
                border: 2px solid #e0e6ed;
                border-radius: 10px;
                font-size: 14px;
                background: white;
            }
        """)
        self.grade_filter.currentTextChanged.connect(self.filter_table)
        
        # Butonlar
        self.add_btn = QPushButton("➕ Yeni Ders Ekle")
        self.edit_btn = QPushButton("✏️ Düzenle")
        self.delete_btn = QPushButton("🗑️ Sil")
        
        buttons = [self.add_btn, self.edit_btn, self.delete_btn]
        button_styles = [
            "background: #27ae60; color: white;",
            "background: #f39c12; color: white;",
            "background: #e74c3c; color: white;"
        ]
        
        for btn, style in zip(buttons, button_styles):
            btn.setFixedHeight(40)
            btn.setFixedWidth(150)
            btn.setStyleSheet(f"""
                QPushButton {{
                    {style}
                    border: none;
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
        
        controls_layout.addWidget(self.search_edit)
        controls_layout.addWidget(self.grade_filter)
        controls_layout.addStretch()
        controls_layout.addWidget(self.add_btn)
        controls_layout.addWidget(self.edit_btn)
        controls_layout.addWidget(self.delete_btn)
        
        layout.addLayout(controls_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Sıra", "Sınıf", "Ders Kodu", "Grup", "Ders Adı", "Öğrenci Sayısı", "Öğretim Üyesi"
        ])
        
        # Tablo stili
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: none;
                border-radius: 10px;
                gridline-color: #e0e6ed;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #e0e6ed;
            }
            QTableWidget::item:selected {
                background: #667eea;
                color: white;
            }
            QHeaderView::section {
                background: #f8f9fa;
                color: #2c3e50;
                border: none;
                padding: 12px;
                font-weight: 600;
                font-size: 12px;
            }
        """)
        
        # Tablo ayarları
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 60)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 60)
        self.table.setColumnWidth(5, 100)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        
        # Gölge efekti
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.table.setGraphicsEffect(shadow)
        
        layout.addWidget(self.table)
        
        # Buton bağlantıları
        self.add_btn.clicked.connect(self.add_student_record)
        self.edit_btn.clicked.connect(self.edit_student_record)
        self.delete_btn.clicked.connect(self.delete_student_record)
        
    def create_stat_card(self, icon, title, value):
        card = QFrame()
        card.setFixedHeight(100)
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                border: 1px solid #e0e6ed;
            }
        """)
        
        # Gölge efekti
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 20))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 20))
        icon_label.setStyleSheet("background: none; border: none;")
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        value_label.setStyleSheet("color: #667eea; background: none; border: none;")
        value_label.setAlignment(Qt.AlignRight)
        
        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        header_layout.addWidget(value_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_label.setStyleSheet("color: #7f8c8d; background: none; border: none;")
        
        layout.addLayout(header_layout)
        layout.addWidget(title_label)
        
        return card
        
    def populate_table(self):
        self.table.setRowCount(len(self.student_data))
        
        for row, data in enumerate(self.student_data):
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(str(data['grade'])))
            self.table.setItem(row, 2, QTableWidgetItem(data['course_code']))
            self.table.setItem(row, 3, QTableWidgetItem(str(data['group'])))
            self.table.setItem(row, 4, QTableWidgetItem(data['course_name']))
            self.table.setItem(row, 5, QTableWidgetItem(str(data['student_count'])))
            self.table.setItem(row, 6, QTableWidgetItem(data['instructor']))
            
            # Hizalama
            for col in [0, 1, 3, 5]:
                self.table.item(row, col).setTextAlignment(Qt.AlignCenter)
    
    def filter_table(self):
        search_text = self.search_edit.text().lower()
        grade_filter = self.grade_filter.currentText()
        
        for row in range(self.table.rowCount()):
            should_show = True
            
            # Arama filtresi
            if search_text:
                course_code = self.table.item(row, 2).text().lower()
                course_name = self.table.item(row, 4).text().lower()
                instructor = self.table.item(row, 6).text().lower()
                
                if not (search_text in course_code or search_text in course_name or search_text in instructor):
                    should_show = False
            
            # Sınıf filtresi
            if grade_filter != "Tüm Sınıflar" and should_show:
                grade = self.table.item(row, 1).text()
                expected_grade = grade_filter.split('.')[0]
                if grade != expected_grade:
                    should_show = False
            
            self.table.setRowHidden(row, not should_show)
    
    def add_student_record(self):
        dialog = AddStudentDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if not data['course_code'] or not data['course_name']:
                QMessageBox.warning(self, "Uyarı", "Ders kodu ve ders adı boş olamaz!")
                return
            
            self.student_data.append(data)
            self.populate_table()
            self.update_stats()
            QMessageBox.information(self, "Başarılı", "Yeni ders başarıyla eklendi!")
    
    def edit_student_record(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek istediğiniz dersi seçin!")
            return
        
        data = self.student_data[current_row]
        dialog = EditStudentDialog(data, self)
        
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_data()
            
            if not new_data['course_code'] or not new_data['course_name']:
                QMessageBox.warning(self, "Uyarı", "Ders kodu ve ders adı boş olamaz!")
                return
            
            self.student_data[current_row] = new_data
            self.populate_table()
            self.update_stats()
            QMessageBox.information(self, "Başarılı", "Ders bilgileri başarıyla güncellendi!")
    
    def delete_student_record(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek istediğiniz dersi seçin!")
            return
        
        data = self.student_data[current_row]
        reply = QMessageBox.question(
            self, "Onay", 
            f"'{data['course_code']} - {data['course_name']}' dersini silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.student_data[current_row]
            self.populate_table()
            self.update_stats()
            QMessageBox.information(self, "Başarılı", "Ders başarıyla silindi!")
    
    def update_stats(self):
        # İstatistikleri güncelle
        self.setup_ui()
        self.populate_table()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentListsPage()
    window.show()
    sys.exit(app.exec_())