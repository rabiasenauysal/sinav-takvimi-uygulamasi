# courses_page.py
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QLineEdit, QComboBox, QMessageBox,
    QDialog, QFormLayout, QDialogButtonBox, QGraphicsDropShadowEffect, QSpinBox
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

class AddCourseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Ders Ekle")
        self.setFixedSize(450, 350)
        self.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 10px;
            }
        """)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title = QLabel("Yeni Ders")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Form alanları
        form_layout = QFormLayout()
        
        self.code_edit = QLineEdit()
        self.code_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #e0e6ed;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        
        self.name_edit = QLineEdit()
        self.name_edit.setStyleSheet(self.code_edit.styleSheet())
        
        self.grade_combo = QComboBox()
        self.grade_combo.addItems(["1", "2", "3", "4"])
        self.grade_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #e0e6ed;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        
        self.group_spin = QSpinBox()
        self.group_spin.setMinimum(1)
        self.group_spin.setMaximum(10)
        self.group_spin.setValue(1)
        self.group_spin.setStyleSheet(self.grade_combo.styleSheet())
        
        self.student_count_spin = QSpinBox()
        self.student_count_spin.setMinimum(0)
        self.student_count_spin.setMaximum(500)
        self.student_count_spin.setValue(0)
        self.student_count_spin.setStyleSheet(self.grade_combo.styleSheet())
        
        self.instructor_edit = QLineEdit()
        self.instructor_edit.setStyleSheet(self.code_edit.styleSheet())
        
        form_layout.addRow("Ders Kodu:", self.code_edit)
        form_layout.addRow("Ders Adı:", self.name_edit)
        form_layout.addRow("Sınıf:", self.grade_combo)
        form_layout.addRow("Grup No:", self.group_spin)
        form_layout.addRow("Öğrenci Sayısı:", self.student_count_spin)
        form_layout.addRow("Öğretim Görevlisi:", self.instructor_edit)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton[text="OK"] {
                background: #667eea;
                color: white;
                border: none;
            }
            QPushButton[text="Cancel"] {
                background: #95a5a6;
                color: white;
                border: none;
            }
        """)
        
        layout.addWidget(button_box)
    
    def get_course_data(self):
        return {
            'code': self.code_edit.text(),
            'name': self.name_edit.text(),
            'grade': self.grade_combo.currentText(),
            'group': self.group_spin.value(),
            'student_count': self.student_count_spin.value(),
            'instructor': self.instructor_edit.text()
        }

class CoursesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ders Listesi")
        self.setGeometry(150, 150, 1200, 700)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f8f9fa, stop: 1 #e9ecef);
            }
        """)
        
        # PDF'den çıkarılan ders verileri
        self.courses_data = [
            {"code": "ATA002", "name": "Atatürk İlkeleri ve İnkılâp Tarihi II", "grade": "1", "group": 1, "student_count": 89, "instructor": "Öğr. Gör. Başak KUZUCUOĞLU"},
            {"code": "BMH122", "name": "Elektrik Devreleri", "grade": "1", "group": 1, "student_count": 161, "instructor": "Dr. Öğr. Üyesi Halil İbrahim COŞAR"},
            {"code": "BMH123", "name": "Bilgisayar Programlama II", "grade": "1", "group": 1, "student_count": 84, "instructor": "Prof. Dr. Mehmet BAKIR"},
            {"code": "BMH123", "name": "Bilgisayar Programlama II", "grade": "1", "group": 2, "student_count": 104, "instructor": "Dr. Öğr. Üyesi Çağrı ARISOY"},
            {"code": "KP001", "name": "Kariyer Planlama", "grade": "1", "group": 1, "student_count": 95, "instructor": "Dr. Öğr. Üyesi Ahmet Sertol KÖKSAL"},
            {"code": "MMF001", "name": "İş Sağlığı ve Güvenliği I", "grade": "1", "group": 1, "student_count": 109, "instructor": "Öğr. Gör. Esra DEMİRCİ ELMALI"},
            {"code": "MMF102", "name": "Fizik-II", "grade": "1", "group": 1, "student_count": 93, "instructor": "Dr. Öğr. Üyesi Tarık AKAN"},
            {"code": "MMF102", "name": "Fizik-II", "grade": "1", "group": 2, "student_count": 87, "instructor": "Prof. Dr. Ümüt TEMİZER"},
            {"code": "MMF104", "name": "Matematik-II", "grade": "1", "group": 1, "student_count": 82, "instructor": "Prof. Dr. Yusuf PANDIR"},
            {"code": "MMF104", "name": "Matematik-II", "grade": "1", "group": 2, "student_count": 81, "instructor": "Doç. Dr. Hüseyin KAMACI"},
            {"code": "TDI002", "name": "Türk Dili II", "grade": "1", "group": 1, "student_count": 91, "instructor": "Öğr. Gör. Akın UYAR"},
            {"code": "YDL002", "name": "Yabancı Dil II (İngilizce)", "grade": "1", "group": 1, "student_count": 44, "instructor": "Öğr. Gör. Emel EGEMEN"},
            
            {"code": "BMH240", "name": "Diferansiyel Denklemler", "grade": "2", "group": 1, "student_count": 110, "instructor": "Doç. Dr. Volkan ASLAN"},
            {"code": "BMH243", "name": "Veri Yapıları ve Algoritmalar", "grade": "2", "group": 1, "student_count": 121, "instructor": "Dr. Öğr. Üyesi Gökalp ÇINARER"},
            {"code": "BMH244", "name": "Ayrık İşlemsel Yapılar", "grade": "2", "group": 1, "student_count": 101, "instructor": "Dr. Öğr. Üyesi Demet TAYLAN"},
            {"code": "BMH246", "name": "Veri Analizine Giriş", "grade": "2", "group": 1, "student_count": 114, "instructor": "Dr. Öğr. Üyesi Mehmet KARABULUT"},
            {"code": "BMH247", "name": "Staj I", "grade": "2", "group": 1, "student_count": 12, "instructor": "Dr. Öğr. Üyesi Çağrı ARISOY"},
            {"code": "BMH248", "name": "Olasılık ve İstatistik", "grade": "2", "group": 1, "student_count": 88, "instructor": "Dr. Öğr. Üyesi Ahmet Sertol KÖKSAL"},
            {"code": "BMH248", "name": "Olasılık ve İstatistik", "grade": "2", "group": 2, "student_count": 61, "instructor": "Dr. Öğr. Üyesi Ahmet Sertol KÖKSAL"},
            {"code": "BMH249", "name": "Dosya Organizasyonu", "grade": "2", "group": 1, "student_count": 120, "instructor": "Dr. Öğr. Üyesi Çağrı ARISOY"},
            
            {"code": "ADSL04", "name": "Alan Dışı Seçmeli Ders", "grade": "3", "group": 1, "student_count": 0, "instructor": "-"},
            {"code": "BMH361", "name": "Bilgisayar Ağları", "grade": "3", "group": 1, "student_count": 119, "instructor": "Prof. Dr. Mehmet BAKIR"},
            {"code": "BMH364", "name": "Algoritma Analizi ve Tasarımı", "grade": "3", "group": 1, "student_count": 65, "instructor": "Dr. Öğr. Üyesi Gökalp ÇINARER"},
            {"code": "BMH367", "name": "Yapay Zeka", "grade": "3", "group": 1, "student_count": 102, "instructor": "Dr. Öğr. Üyesi Hasan ULUTAŞ"},
            {"code": "BMH521", "name": "Veri İletişimi", "grade": "3", "group": 1, "student_count": 64, "instructor": "Prof. Dr. Mehmet BAKIR"},
            {"code": "BMH522", "name": "Gömülü Sistemler", "grade": "3", "group": 1, "student_count": 100, "instructor": "Dr. Öğr. Üyesi Mehmet KARABULUT"},
            {"code": "BMH523", "name": "İşletim Sistemleri Kavramları", "grade": "3", "group": 1, "student_count": 29, "instructor": "Dr. Öğr. Üyesi Çağrı ARISOY"},
            {"code": "BMH594", "name": "Temel İş İngilizcesi", "grade": "3", "group": 1, "student_count": 58, "instructor": "Doç. Dr. Muhammet Emin ŞAHİN"},
            
            {"code": "BMH473", "name": "Staj II", "grade": "4", "group": 1, "student_count": 9, "instructor": "Dr. Öğr. Üyesi Çağrı ARISOY"},
            {"code": "BMH474", "name": "Bilgisayar Mühendisliği Tasarımı", "grade": "4", "group": 1, "student_count": 6, "instructor": "Dr. Öğr. Üyesi Mehmet KARABULUT"},
            {"code": "BMH474", "name": "Bilgisayar Mühendisliği Tasarımı", "grade": "4", "group": 2, "student_count": 10, "instructor": "Dr. Öğr. Üyesi Hasan ULUTAŞ"},
            {"code": "BMH481", "name": "Bitirme Projesi", "grade": "4", "group": 1, "student_count": 14, "instructor": "Dr. Öğr. Üyesi Ahmet Sertol KÖKSAL"},
            {"code": "BMH481", "name": "Bitirme Projesi", "grade": "4", "group": 2, "student_count": 0, "instructor": ""},
            {"code": "BMH481", "name": "Bitirme Projesi", "grade": "4", "group": 3, "student_count": 11, "instructor": "Dr. Öğr. Üyesi Hasan ULUTAŞ"},
            {"code": "BMH481", "name": "Bitirme Projesi", "grade": "4", "group": 4, "student_count": 8, "instructor": "Prof. Dr. Mehmet BAKIR"},
            {"code": "BMH481", "name": "Bitirme Projesi", "grade": "4", "group": 5, "student_count": 10, "instructor": "Dr. Öğr. Üyesi Mehmet KARABULUT"},
            {"code": "BMH481", "name": "Bitirme Projesi", "grade": "4", "group": 6, "student_count": 5, "instructor": "Dr. Öğr. Üyesi Gökalp ÇINARER"},
            {"code": "BMH481", "name": "Bitirme Projesi", "grade": "4", "group": 7, "student_count": 12, "instructor": "Dr. Öğr. Üyesi Çağrı ARISOY"},
            {"code": "BMH481", "name": "Bitirme Projesi", "grade": "4", "group": 8, "student_count": 2, "instructor": "Doç. Dr. Muhammet Emin ŞAHİN"},
            {"code": "MMF002", "name": "İş Sağlığı ve Güvenliği II", "grade": "4", "group": 1, "student_count": 81, "instructor": "Öğr. Gör. Esra DEMİRCİ ELMALI"},
            {"code": "BMH705", "name": "Biyomedikal Mühendisliğin Temelleri", "grade": "4", "group": 1, "student_count": 34, "instructor": "Doç. Dr. Muhammet Emin ŞAHİN"},
            {"code": "BMH708", "name": "Veri Madenciliğine Giriş", "grade": "4", "group": 1, "student_count": 37, "instructor": "Öğr. Gör. Kazım KILIÇ"},
            {"code": "BMH713", "name": "Veri Tabanı Programlama", "grade": "4", "group": 1, "student_count": 18, "instructor": "Dr. Öğr. Üyesi Hasan ULUTAŞ"},
            {"code": "BMH715", "name": "Bilgi Güvenliği", "grade": "4", "group": 1, "student_count": 43, "instructor": "Dr. Öğr. Üyesi Ahmet Sertol KÖKSAL"},
            {"code": "BMH722", "name": "Mikrokontrolcü Uygulamaları", "grade": "4", "group": 1, "student_count": 37, "instructor": "Dr. Öğr. Üyesi Mehmet KARABULUT"},
            {"code": "BMH732", "name": "Genetik Algoritmalar ve Programlama", "grade": "4", "group": 1, "student_count": 26, "instructor": "Dr. Öğr. Üyesi Gökalp ÇINARER"},
            {"code": "BMH739", "name": "Kalite Kontrol", "grade": "4", "group": 1, "student_count": 34, "instructor": "Dr. Öğr. Üyesi Hasan ULUTAŞ"}
        ]
        
        self.setup_ui()
        self.populate_table()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Başlık bölümü
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #667eea, stop: 1 #764ba2);
                border-radius: 15px;
            }
        """)
        
        # Gölge efekti
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 30))
        header_frame.setGraphicsEffect(shadow)
        
        header_layout = QHBoxLayout(header_frame)
        
        title = QLabel("📚 Ders Listesi")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: white; background: none;")
        
        subtitle = QLabel(f"Toplam {len(self.courses_data)} ders")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 180); background: none;")
        
        header_left = QVBoxLayout()
        header_left.addWidget(title)
        header_left.addWidget(subtitle)
        
        header_layout.addLayout(header_left)
        header_layout.addStretch()
        
        main_layout.addWidget(header_frame)
        
        # Araç çubuğu
        toolbar_layout = QHBoxLayout()
        
        # Arama kutusu
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Ders ara...")
        self.search_edit.setFixedHeight(40)
        self.search_edit.setStyleSheet("""
            QLineEdit {
                padding: 10px;
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
                padding: 10px;
                border: 2px solid #e0e6ed;
                border-radius: 10px;
                font-size: 14px;
                background: white;
            }
        """)
        self.grade_filter.currentTextChanged.connect(self.filter_table)
        
        # Butonlar
        self.add_btn = QPushButton("➕ Yeni Ekle")
        self.edit_btn = QPushButton("✏️ Düzenle")
        self.delete_btn = QPushButton("🗑️ Sil")
        
        buttons = [self.add_btn, self.edit_btn, self.delete_btn]
        colors = ["#27ae60", "#f39c12", "#e74c3c"]
        
        for btn, color in zip(buttons, colors):
            btn.setFixedHeight(40)
            btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background: {color}dd;
                }}
            """)
        
        toolbar_layout.addWidget(self.search_edit)
        toolbar_layout.addWidget(self.grade_filter)
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.edit_btn)
        toolbar_layout.addWidget(self.delete_btn)
        
        main_layout.addLayout(toolbar_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Ders Kodu", "Ders Adı", "Sınıf", "Grup", "Öğrenci Sayısı", "Öğretim Görevlisi"])
        
        # Tablo stili
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #e0e6ed;
                border-radius: 10px;
                gridline-color: #f1f3f4;
                font-size: 12px;
            }
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #667eea, stop: 1 #764ba2);
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f1f3f4;
            }
            QTableWidget::item:selected {
                background: #667eea20;
            }
        """)
        
        # Tablo ayarları
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.table)
        
        # Bağlantılar
        self.add_btn.clicked.connect(self.add_course)
        self.edit_btn.clicked.connect(self.edit_course)
        self.delete_btn.clicked.connect(self.delete_course)
    
    def populate_table(self):
        self.table.setRowCount(len(self.courses_data))
        
        for row, course in enumerate(self.courses_data):
            self.table.setItem(row, 0, QTableWidgetItem(course['code']))
            self.table.setItem(row, 1, QTableWidgetItem(course['name']))
            self.table.setItem(row, 2, QTableWidgetItem(course['grade']))
            self.table.setItem(row, 3, QTableWidgetItem(str(course['group'])))
            self.table.setItem(row, 4, QTableWidgetItem(str(course['student_count'])))
            self.table.setItem(row, 5, QTableWidgetItem(course['instructor']))
    
    def filter_table(self):
        search_text = self.search_edit.text().lower()
        grade_filter = self.grade_filter.currentText()
        
        for row in range(self.table.rowCount()):
            show_row = True
            
            # Metin filtresi
            if search_text:
                text_match = False
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and search_text in item.text().lower():
                        text_match = True
                        break
                if not text_match:
                    show_row = False
            
            # Sınıf filtresi
            if grade_filter != "Tüm Sınıflar":
                grade_item = self.table.item(row, 2)
                if grade_item:
                    grade_number = grade_filter.split('.')[0]
                    if grade_item.text() != grade_number:
                        show_row = False
            
            self.table.setRowHidden(row, not show_row)
    
    def add_course(self):
        dialog = AddCourseDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_course_data()
            if data['code'].strip() and data['name'].strip():
                self.courses_data.append(data)
                self.populate_table()
                QMessageBox.information(self, "Başarılı", "Ders başarıyla eklendi!")
            else:
                QMessageBox.warning(self, "Uyarı", "Ders kodu ve adı alanları boş olamaz!")
    
    def edit_course(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            dialog = AddCourseDialog(self)
            dialog.setWindowTitle("Ders Düzenle")
            
            # Mevcut verileri doldur
            course = self.courses_data[current_row]
            dialog.code_edit.setText(course['code'])
            dialog.name_edit.setText(course['name'])
            dialog.grade_combo.setCurrentText(course['grade'])
            dialog.group_spin.setValue(course['group'])
            dialog.student_count_spin.setValue(course['student_count'])
            dialog.instructor_edit.setText(course['instructor'])
            
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_course_data()
                if data['code'].strip() and data['name'].strip():
                    self.courses_data[current_row] = data
                    self.populate_table()
                    QMessageBox.information(self, "Başarılı", "Ders başarıyla güncellendi!")
                else:
                    QMessageBox.warning(self, "Uyarı", "Ders kodu ve adı alanları boş olamaz!")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek istediğiniz dersi seçin!")
    
    def delete_course(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            course_name = self.courses_data[current_row]['name']
            reply = QMessageBox.question(self, "Silme Onayı", 
                                       f"{course_name} dersini silmek istediğinizden emin misiniz?",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                del self.courses_data[current_row]
                self.populate_table()
                QMessageBox.information(self, "Başarılı", "Ders başarıyla silindi!")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek istediğiniz dersi seçin!")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = CoursesPage()
    window.show()
    sys.exit(app.exec_())