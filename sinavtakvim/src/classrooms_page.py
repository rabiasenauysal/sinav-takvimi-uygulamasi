# classrooms_page.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit, QSpinBox,
    QHeaderView, QMessageBox, QDialog, QDialogButtonBox, QFormLayout,
    QFrame, QGraphicsDropShadowEffect, QComboBox
)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt

class AddClassroomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Sınıf Ekle")
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 10px;
            }
            QLabel {
                color: #2c3e50;
                font-weight: 600;
            }
            QLineEdit, QSpinBox {
                padding: 8px;
                border: 2px solid #e0e6ed;
                border-radius: 8px;
                font-size: 12px;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #667eea;
            }
        """)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        form_layout = QFormLayout()
        
        self.class_code_edit = QLineEdit()
        self.class_code_edit.setPlaceholderText("Örn: EZ001, A105")
        
        self.capacity_spin = QSpinBox()
        self.capacity_spin.setRange(1, 500)
        self.capacity_spin.setValue(30)
        
        form_layout.addRow("Sınıf Kodu:", self.class_code_edit)
        form_layout.addRow("Kapasite:", self.capacity_spin)
        
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
            'code': self.class_code_edit.text().strip(),
            'capacity': self.capacity_spin.value()
        }

class EditClassroomDialog(QDialog):
    def __init__(self, code, capacity, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sınıf Düzenle")
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 10px;
            }
            QLabel {
                color: #2c3e50;
                font-weight: 600;
            }
            QLineEdit, QSpinBox {
                padding: 8px;
                border: 2px solid #e0e6ed;
                border-radius: 8px;
                font-size: 12px;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #667eea;
            }
        """)
        self.setup_ui(code, capacity)
        
    def setup_ui(self, code, capacity):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        form_layout = QFormLayout()
        
        self.class_code_edit = QLineEdit(code)
        self.capacity_spin = QSpinBox()
        self.capacity_spin.setRange(1, 500)
        self.capacity_spin.setValue(capacity)
        
        form_layout.addRow("Sınıf Kodu:", self.class_code_edit)
        form_layout.addRow("Kapasite:", self.capacity_spin)
        
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
            'code': self.class_code_edit.text().strip(),
            'capacity': self.capacity_spin.value()
        }

class ClassroomsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sınıf Kapasiteleri Yönetimi")
        self.setGeometry(200, 200, 900, 600)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f8f9fa, stop: 1 #e9ecef);
            }
        """)
        
        # Başlangıç verileri (salon_kapasite_tablosu.xlsx'den)
        self.classrooms_data = [
            {'code': 'EZ003', 'capacity': 42},
            {'code': 'EZ004', 'capacity': 42},
            {'code': 'A107', 'capacity': 21},
            {'code': 'A108', 'capacity': 21},
            {'code': 'E106', 'capacity': 60},
            {'code': 'EZ010', 'capacity': 55},
            {'code': 'EZ009', 'capacity': 55},
            {'code': 'EZ016', 'capacity': 60},
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
        
        title = QLabel("🏛️ Sınıf Kapasiteleri Yönetimi")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: white; background: none;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Sınıf bilgilerini görüntüleyin, ekleyin ve düzenleyin")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 180); background: none;")
        subtitle.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        layout.addWidget(title_frame)
        
        # Arama ve buton alanı
        controls_layout = QHBoxLayout()
        
        # Arama
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Sınıf kodu ara...")
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
        
        # Butonlar
        self.add_btn = QPushButton("➕ Yeni Sınıf Ekle")
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
        controls_layout.addStretch()
        controls_layout.addWidget(self.add_btn)
        controls_layout.addWidget(self.edit_btn)
        controls_layout.addWidget(self.delete_btn)
        
        layout.addLayout(controls_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Sıra", "Sınıf Kodu", "Kapasite"])
        
        # Tablo stili
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: none;
                border-radius: 10px;
                gridline-color: #e0e6ed;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 12px;
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
                padding: 15px;
                font-weight: 600;
                font-size: 13px;
            }
        """)
        
        # Tablo ayarları
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(2, 120)
        
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
        self.add_btn.clicked.connect(self.add_classroom)
        self.edit_btn.clicked.connect(self.edit_classroom)
        self.delete_btn.clicked.connect(self.delete_classroom)
        
    def populate_table(self):
        self.table.setRowCount(len(self.classrooms_data))
        
        for row, classroom in enumerate(self.classrooms_data):
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(classroom['code']))
            self.table.setItem(row, 2, QTableWidgetItem(str(classroom['capacity'])))
            
            # Sıra numarası hizalama
            self.table.item(row, 0).setTextAlignment(Qt.AlignCenter)
            self.table.item(row, 2).setTextAlignment(Qt.AlignCenter)
    
    def filter_table(self):
        search_text = self.search_edit.text().lower()
        
        for row in range(self.table.rowCount()):
            code_item = self.table.item(row, 1)
            if code_item:
                should_show = search_text in code_item.text().lower()
                self.table.setRowHidden(row, not should_show)
    
    def add_classroom(self):
        dialog = AddClassroomDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if not data['code']:
                QMessageBox.warning(self, "Uyarı", "Sınıf kodu boş olamaz!")
                return
                
            # Aynı kodun olup olmadığını kontrol et
            for classroom in self.classrooms_data:
                if classroom['code'].upper() == data['code'].upper():
                    QMessageBox.warning(self, "Uyarı", "Bu sınıf kodu zaten mevcut!")
                    return
            
            self.classrooms_data.append({
                'code': data['code'].upper(),
                'capacity': data['capacity']
            })
            
            self.populate_table()
            QMessageBox.information(self, "Başarılı", "Yeni sınıf başarıyla eklendi!")
    
    def edit_classroom(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek istediğiniz sınıfı seçin!")
            return
        
        classroom = self.classrooms_data[current_row]
        dialog = EditClassroomDialog(classroom['code'], classroom['capacity'], self)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if not data['code']:
                QMessageBox.warning(self, "Uyarı", "Sınıf kodu boş olamaz!")
                return
            
            # Aynı kodun başka bir sınıfta olup olmadığını kontrol et
            for i, other_classroom in enumerate(self.classrooms_data):
                if i != current_row and other_classroom['code'].upper() == data['code'].upper():
                    QMessageBox.warning(self, "Uyarı", "Bu sınıf kodu başka bir sınıf tarafından kullanılıyor!")
                    return
            
            self.classrooms_data[current_row] = {
                'code': data['code'].upper(),
                'capacity': data['capacity']
            }
            
            self.populate_table()
            QMessageBox.information(self, "Başarılı", "Sınıf bilgileri başarıyla güncellendi!")
    
    def delete_classroom(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek istediğiniz sınıfı seçin!")
            return
        
        classroom = self.classrooms_data[current_row]
        reply = QMessageBox.question(
            self, "Onay", 
            f"'{classroom['code']}' sınıfını silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.classrooms_data[current_row]
            self.populate_table()
            QMessageBox.information(self, "Başarılı", "Sınıf başarıyla silindi!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClassroomsPage()
    window.show()
    sys.exit(app.exec_())