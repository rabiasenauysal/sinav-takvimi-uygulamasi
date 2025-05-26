# instructors_page.py
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QLineEdit, QComboBox, QMessageBox,
    QDialog, QFormLayout, QDialogButtonBox, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtCore import Qt

class AddInstructorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Öğretim Görevlisi Ekle")
        self.setFixedSize(400, 300)
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
        title = QLabel("Yeni Öğretim Görevlisi")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Form alanları
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setStyleSheet("""
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
        
        self.title_combo = QComboBox()
        self.title_combo.addItems([
            "Öğr. Gör.", "Dr. Öğr. Üyesi", "Doç. Dr.", "Prof. Dr."
        ])
        self.title_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #e0e6ed;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        
        self.email_edit = QLineEdit()
        self.email_edit.setStyleSheet(self.name_edit.styleSheet())
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setStyleSheet(self.name_edit.styleSheet())
        
        form_layout.addRow("Ad Soyad:", self.name_edit)
        form_layout.addRow("Ünvan:", self.title_combo)
        form_layout.addRow("E-posta:", self.email_edit)
        form_layout.addRow("Telefon:", self.phone_edit)
        
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
    
    def get_instructor_data(self):
        return {
            'name': self.name_edit.text(),
            'title': self.title_combo.currentText(),
            'email': self.email_edit.text(),
            'phone': self.phone_edit.text()
        }

class InstructorsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Öğretim Görevlileri")
        self.setGeometry(150, 150, 1000, 700)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f8f9fa, stop: 1 #e9ecef);
            }
        """)
        
        # Başlangıç verileri - PDF'den çıkarılan bilgiler
        self.instructors_data = [
            {"name": "Başak KUZUCUOĞLU", "title": "Öğr. Gör.", "email": "", "phone": ""},
            {"name": "Halil İbrahim COŞAR", "title": "Dr. Öğr. Üyesi", "email": "", "phone": ""},
            {"name": "Mehmet BAKIR", "title": "Prof. Dr.", "email": "", "phone": ""},
            {"name": "Çağrı ARISOY", "title": "Dr. Öğr. Üyesi", "email": "", "phone": ""},
            {"name": "Ahmet Sertol KÖKSAL", "title": "Dr. Öğr. Üyesi", "email": "", "phone": ""},
            {"name": "Esra DEMİRCİ ELMALI", "title": "Öğr. Gör.", "email": "", "phone": ""},
            {"name": "Tarık AKAN", "title": "Dr. Öğr. Üyesi", "email": "", "phone": ""},
            {"name": "Ümüt TEMİZER", "title": "Prof. Dr.", "email": "", "phone": ""},
            {"name": "Yusuf PANDIR", "title": "Prof. Dr.", "email": "", "phone": ""},
            {"name": "Hüseyin KAMACI", "title": "Doç. Dr.", "email": "", "phone": ""},
            {"name": "Akın UYAR", "title": "Öğr. Gör.", "email": "", "phone": ""},
            {"name": "Emel EGEMEN", "title": "Öğr. Gör.", "email": "", "phone": ""},
            {"name": "Volkan ASLAN", "title": "Doç. Dr.", "email": "", "phone": ""},
            {"name": "Gökalp ÇINARER", "title": "Dr. Öğr. Üyesi", "email": "", "phone": ""},
            {"name": "Demet TAYLAN", "title": "Dr. Öğr. Üyesi", "email": "", "phone": ""},
            {"name": "Mehmet KARABULUT", "title": "Dr. Öğr. Üyesi", "email": "", "phone": ""},
            {"name": "Hasan ULUTAŞ", "title": "Dr. Öğr. Üyesi", "email": "", "phone": ""},
            {"name": "Muhammet Emin ŞAHİN", "title": "Doç. Dr.", "email": "", "phone": ""},
            {"name": "Kazım KILIÇ", "title": "Öğr. Gör.", "email": "", "phone": ""}
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
        
        title = QLabel("👨‍🏫 Öğretim Görevlileri")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: white; background: none;")
        
        subtitle = QLabel(f"Toplam {len(self.instructors_data)} öğretim görevlisi")
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
        self.search_edit.setPlaceholderText("Öğretim görevlisi ara...")
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
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.edit_btn)
        toolbar_layout.addWidget(self.delete_btn)
        
        main_layout.addLayout(toolbar_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Ad Soyad", "Ünvan", "E-posta", "Telefon"])
        
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
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.table)
        
        # Bağlantılar
        self.add_btn.clicked.connect(self.add_instructor)
        self.edit_btn.clicked.connect(self.edit_instructor)
        self.delete_btn.clicked.connect(self.delete_instructor)
    
    def populate_table(self):
        self.table.setRowCount(len(self.instructors_data))
        
        for row, instructor in enumerate(self.instructors_data):
            self.table.setItem(row, 0, QTableWidgetItem(instructor['name']))
            self.table.setItem(row, 1, QTableWidgetItem(instructor['title']))
            self.table.setItem(row, 2, QTableWidgetItem(instructor['email']))
            self.table.setItem(row, 3, QTableWidgetItem(instructor['phone']))
    
    def filter_table(self):
        search_text = self.search_edit.text().lower()
        
        for row in range(self.table.rowCount()):
            show_row = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.table.setRowHidden(row, not show_row)
    
    def add_instructor(self):
        dialog = AddInstructorDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_instructor_data()
            if data['name'].strip():
                self.instructors_data.append(data)
                self.populate_table()
                QMessageBox.information(self, "Başarılı", "Öğretim görevlisi başarıyla eklendi!")
            else:
                QMessageBox.warning(self, "Uyarı", "Ad Soyad alanı boş olamaz!")
    
    def edit_instructor(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            dialog = AddInstructorDialog(self)
            dialog.setWindowTitle("Öğretim Görevlisi Düzenle")
            
            # Mevcut verileri doldur
            instructor = self.instructors_data[current_row]
            dialog.name_edit.setText(instructor['name'])
            dialog.title_combo.setCurrentText(instructor['title'])
            dialog.email_edit.setText(instructor['email'])
            dialog.phone_edit.setText(instructor['phone'])
            
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_instructor_data()
                if data['name'].strip():
                    self.instructors_data[current_row] = data
                    self.populate_table()
                    QMessageBox.information(self, "Başarılı", "Öğretim görevlisi başarıyla güncellendi!")
                else:
                    QMessageBox.warning(self, "Uyarı", "Ad Soyad alanı boş olamaz!")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek istediğiniz öğretim görevlisini seçin!")
    
    def delete_instructor(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            instructor_name = self.instructors_data[current_row]['name']
            reply = QMessageBox.question(self, "Silme Onayı", 
                                       f"{instructor_name} isimli öğretim görevlisini silmek istediğinizden emin misiniz?",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                del self.instructors_data[current_row]
                self.populate_table()
                QMessageBox.information(self, "Başarılı", "Öğretim görevlisi başarıyla silindi!")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek istediğiniz öğretim görevlisini seçin!")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = InstructorsPage()
    window.show()
    sys.exit(app.exec_())