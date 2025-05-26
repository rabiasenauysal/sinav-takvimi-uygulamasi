import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import copy
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QFileDialog, QLineEdit, QVBoxLayout,
    QHBoxLayout, QFrame, QProgressBar, QGraphicsDropShadowEffect,
    QCheckBox, QSpinBox, QMessageBox, QTextEdit, QDateEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QDialog, QGridLayout,
    QScrollArea, QTabWidget, QGroupBox, QSplitter
)
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent, QColor, QPalette
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDate
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
import xlsxwriter
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

class ExamScheduler:
    """Geliştirilmiş sınav takvimi algoritması"""
    
    def __init__(self, start_date, end_date):
        # Sınıf bilgileri - Hackathon verilerinden
        self.classrooms = {
            'EZ003': 42, 'EZ004': 42, 'A107': 21, 'A108': 21, 'E106': 60,
            'EZ010': 55, 'EZ009': 55, 'EZ016': 60, 'E116': 50
        }
        
        # Kullanıcıdan alınan tarihler
        self.start_date = start_date
        self.end_date = end_date
        self.excluded_dates = [datetime(2025, 6, 21), datetime(2025, 6, 22)]  # ÖSYM günleri
        
        # Saat dilimleri - 2 saatlik bloklar
        self.weekday_slots = ['09:00-11:00', '11:00-13:00', '13:00-15:00', '15:00-17:00']
        self.weekend_slots = ['10:00-12:00', '12:00-14:00', '14:00-16:00']
        
        # Sabit sınav zamanları - İster dosyasından
        self.fixed_exams = {
            'İş Sağlığı ve Güvenliği I': {'day': 'Friday', 'time': '10:00-12:00', 'fixed': True},
            'İş Sağlığı ve Güvenliği II': {'day': 'Friday', 'time': '11:00-13:00', 'fixed': True},
            'Matematik-II': {'day': 'Monday', 'time': '15:00-17:00', 'fixed': True},
            'Matematik-1': {'day': 'Monday', 'time': '15:00-17:00', 'fixed': True},
            'Veri Madenciliğine Giriş': {'day': 'Thursday', 'time': '15:00-17:00', 'fixed': True},
            'Elektrik Devreleri': {'day': 'Wednesday', 'time': '11:00-13:00', 'fixed': True},
            'Fizik 1.': {'day': 'Tuesday', 'time': '15:30-17:30', 'fixed': True}  # Kendi programından
        }
        
        # Ortak ders programı - İster dosyasından
        self.common_exams = {
            '2025-06-12': {
                '13:00-15:45': {
                    'courses': ['Atatürk İlkeleri ve İnkılap Tarihi II', 'Yabancı Dil II (İngilizce)', 'Türk Dili II'],
                    'fixed': True
                },
                '10:00-13:00': {
                    'courses': ['Alan Dışı Seçmeli Ders (Grup 1)'],
                    'fixed': True
                }
            },
            '2025-06-13': {
                '13:30-15:00': {
                    'courses': ['Alan Dışı Seçmeli Ders (Grup 2)'],
                    'fixed': True
                }
            }
        }
        
        self.schedule = {}
        self.course_conflicts = defaultdict(set)  # Çakışma tespiti için
        
    def create_schedule(self, df, allow_weekend=False, max_parallel=4):
        """Ana scheduling algoritması - Çakışmasız"""
        try:
            # Veri ön işleme
            courses = self.preprocess_data(df)
            print(f"Toplam işlenecek ders: {len(courses)}")
            
            # Takvim günlerini oluştur
            available_days = self.generate_available_days(allow_weekend)
            print(f"Kullanılabilir gün sayısı: {len(available_days)}")
            
            # Ortak sınavları yerleştir
            self.place_common_exams(available_days)
            print("Ortak sınavlar yerleştirildi")
            
            # Sabit sınavları yerleştir
            self.place_fixed_exams(courses, available_days)
            print("Sabit sınavlar yerleştirildi")
            
            # Gruplu dersleri birlikte yerleştir
            grouped_courses = self.group_courses_by_name(courses)
            print(f"Gruplanan ders ailesi: {len(grouped_courses)}")
            
            # Kalan dersleri algoritma ile yerleştir
            success = self.solve_with_conflict_detection(grouped_courses, available_days, max_parallel)
            
            return success, self.schedule
            
        except Exception as e:
            print(f"Algoritma hatası: {str(e)}")
            return False, f"Algoritma hatası: {str(e)}"
    
    def group_courses_by_name(self, courses):
        """Aynı dersin farklı gruplarını birlikte ele al"""
        course_groups = defaultdict(list)
        
        for course in courses:
            if not self.is_exam_placed(course):
                # Ders adından grup bilgisini temizle
                base_name = course['name'].replace(' A GRUBU', '').replace(' B GRUBU', '').replace(' C GRUBU', '').replace(' D GRUBU', '')
                course_groups[base_name].append(course)
        
        # Tekli ve çoklu grupları ayır
        result = []
        for base_name, course_list in course_groups.items():
            if len(course_list) == 1:
                result.append(course_list[0])  # Tekli ders
            else:
                result.append(course_list)     # Grup dersi
        
        return result
    
    def solve_with_conflict_detection(self, grouped_courses, available_days, max_parallel):
        """Çakışma kontrolü ile çözüm"""
        placed_count = 0
        
        # Önceliğe göre sırala (büyük dersler önce)
        sorted_groups = sorted(grouped_courses, key=self.calculate_group_priority, reverse=True)
        
        for course_group in sorted_groups:
            if isinstance(course_group, list):
                # Grup dersi - aynı zaman farklı sınıflar
                if self.place_group_exams(course_group, available_days, max_parallel):
                    placed_count += len(course_group)
                    print(f"Grup yerleştirildi: {course_group[0]['name']} ({len(course_group)} grup)")
                else:
                    print(f"Grup yerleştirilemedi: {course_group[0]['name']}")
            else:
                # Tekli ders
                if self.place_single_exam(course_group, available_days, max_parallel):
                    placed_count += 1
                    print(f"Ders yerleştirildi: {course_group['name']}")
                else:
                    print(f"Ders yerleştirilemedi: {course_group['name']}")
        
        print(f"Toplam yerleştirilen: {placed_count}")
        return placed_count > 0
    
    def calculate_group_priority(self, course_group):
        """Grup önceliği hesapla"""
        if isinstance(course_group, list):
            total_students = sum(c['student_count'] for c in course_group)
            avg_level = sum(c['class_level'] for c in course_group) / len(course_group)
        else:
            total_students = course_group['student_count']
            avg_level = course_group['class_level']
        
        priority = total_students * 10 + (5 - avg_level) * 50
        if total_students > 120:
            priority += 1000
        return priority
    
    def place_group_exams(self, course_group, available_days, max_parallel):
        """Grup derslerini aynı zaman farklı sınıflara yerleştir"""
        total_students = sum(c['student_count'] for c in course_group)
        
        for day in available_days:
            for time_slot in day['slots']:
                if self.can_place_group_exam(course_group, day, time_slot, max_parallel):
                    # Sınıf ataması - grup başına farklı sınıf
                    classroom_assignments = self.assign_classrooms_for_groups(course_group, day, time_slot)
                    
                    if classroom_assignments:
                        date_str = day['date'].strftime('%Y-%m-%d')
                        if date_str not in self.schedule:
                            self.schedule[date_str] = {}
                        
                        # Her grup için ayrı giriş
                        for i, course in enumerate(course_group):
                            group_key = f"{time_slot}_GROUP_{i}"
                            self.schedule[date_str][group_key] = {
                                'course': course,
                                'classrooms': classroom_assignments[i],
                                'time_slot': time_slot,
                                'is_group': True,
                                'group_index': i,
                                'fixed': False
                            }
                        
                        return True
        return False
    
    def place_single_exam(self, course, available_days, max_parallel):
        """Tekli dersi yerleştir"""
        for day in available_days:
            for time_slot in day['slots']:
                if self.can_place_single_exam(course, day, time_slot, max_parallel):
                    classrooms = self.assign_classrooms_optimized(course['student_count'], day, time_slot)
                    
                    if classrooms:
                        date_str = day['date'].strftime('%Y-%m-%d')
                        if date_str not in self.schedule:
                            self.schedule[date_str] = {}
                        
                        self.schedule[date_str][time_slot] = {
                            'course': course,
                            'classrooms': classrooms,
                            'fixed': False
                        }
                        return True
        return False
    
    def can_place_group_exam(self, course_group, day, time_slot, max_parallel):
        """Grup dersi yerleştirme kontrolü"""
        date_str = day['date'].strftime('%Y-%m-%d')
        
        # 1. Zaman dilimi tamamen müsait mi?
        if self.is_time_slot_occupied(date_str, time_slot):
            return False
        
        # 2. Toplam salon kapasitesi yeterli mi?
        total_students = sum(c['student_count'] for c in course_group)
        available_capacity = self.get_available_classroom_capacity(date_str, time_slot)
        if available_capacity < total_students:
            return False
        
        # 3. Aynı sınıf kuralları
        for course in course_group:
            if self.violates_same_class_rule(course, date_str):
                return False
        
        # 4. Büyük ders kuralı
        if total_students > 120 and self.has_large_exam_same_day(date_str, 120):
            return False
        
        return True
    
    def can_place_single_exam(self, course, day, time_slot, max_parallel):
        """Tekli ders yerleştirme kontrolü"""
        date_str = day['date'].strftime('%Y-%m-%d')
        
        # 1. Zaman dilimi müsait mi?
        if self.is_time_slot_occupied(date_str, time_slot):
            return False
        
        # 2. Salon kapasitesi
        available_capacity = self.get_available_classroom_capacity(date_str, time_slot)
        if available_capacity < course['student_count']:
            return False
        
        # 3. Aynı sınıf kuralı
        if self.violates_same_class_rule(course, date_str):
            return False
        
        # 4. Büyük ders kuralı
        if course['student_count'] > 120 and self.has_large_exam_same_day(date_str, 120):
            return False
        
        # 5. Günlük paralel sınav limiti
        daily_exam_count = self.count_daily_exams(date_str)
        if daily_exam_count >= max_parallel:
            return False
        
        return True
    
    def is_time_slot_occupied(self, date_str, time_slot):
        """Zaman dilimi dolu mu?"""
        if date_str not in self.schedule:
            return False
        
        # Tam çakışma kontrolü
        for existing_slot in self.schedule[date_str]:
            if self.times_overlap(time_slot, self.extract_time_slot(existing_slot)):
                return True
        return False
    
    def extract_time_slot(self, slot_key):
        """Slot anahtarından zaman dilimini çıkar"""
        if '_GROUP_' in slot_key:
            return slot_key.split('_GROUP_')[0]
        return slot_key
    
    def times_overlap(self, time1, time2):
        """İki zaman dilimi çakışıyor mu? - Geliştirilmiş"""
        if time1 == time2:
            return True
        
        try:
            # Zaman dilimlerini parse et
            start1, end1 = time1.split('-')
            start2, end2 = time2.split('-')
            
            start1_min = self.time_to_minutes(start1)
            end1_min = self.time_to_minutes(end1)
            start2_min = self.time_to_minutes(start2)
            end2_min = self.time_to_minutes(end2)
            
            # Çakışma kontrolü
            return not (end1_min <= start2_min or end2_min <= start1_min)
        except:
            return time1 == time2
    
    def time_to_minutes(self, time_str):
        """Saat:dakika formatını dakikaya çevir"""
        hour, minute = map(int, time_str.split(':'))
        return hour * 60 + minute
    
    def violates_same_class_rule(self, course, date_str):
        """Aynı sınıf kuralı ihlali var mı?"""
        if date_str not in self.schedule:
            return False
        
        same_class_mandatory_count = 0
        for exam_info in self.schedule[date_str].values():
            existing_course = exam_info['course']
            if (existing_course.get('class_level') == course.get('class_level') and
                not exam_info.get('is_common', False)):
                # Zorunlu ders sayısını kontrol et
                if self.is_mandatory_course(existing_course):
                    same_class_mandatory_count += 1
        
        # Aynı sınıftan en fazla 1 zorunlu ders olabilir
        if self.is_mandatory_course(course) and same_class_mandatory_count >= 1:
            return True
        
        return False
    
    def is_mandatory_course(self, course):
        """Zorunlu ders mi? (Seçmeli değilse zorunlu)"""
        course_name = course.get('name', '').lower()
        return 'seçmeli' not in course_name and 'alan dışı' not in course_name
    
    def has_large_exam_same_day(self, date_str, threshold):
        """Aynı gün büyük ders var mı?"""
        if date_str not in self.schedule:
            return False
        
        for exam_info in self.schedule[date_str].values():
            if exam_info['course'].get('student_count', 0) > threshold:
                return True
        return False
    
    def count_daily_exams(self, date_str):
        """Günlük sınav sayısı"""
        if date_str not in self.schedule:
            return 0
        
        unique_times = set()
        for slot_key in self.schedule[date_str]:
            time_slot = self.extract_time_slot(slot_key)
            unique_times.add(time_slot)
        
        return len(unique_times)
    
    def get_available_classroom_capacity(self, date_str, time_slot):
        """Müsait sınıf kapasitesi"""
        occupied_classrooms = set()
        
        if date_str in self.schedule:
            for existing_slot, exam_info in self.schedule[date_str].items():
                existing_time = self.extract_time_slot(existing_slot)
                if self.times_overlap(time_slot, existing_time):
                    occupied_classrooms.update(exam_info['classrooms'])
        
        available_capacity = sum(
            capacity for classroom, capacity in self.classrooms.items()
            if classroom not in occupied_classrooms
        )
        
        return available_capacity
    
    def assign_classrooms_for_groups(self, course_group, day, time_slot):
        """Grup dersleri için sınıf ataması"""
        date_str = day['date'].strftime('%Y-%m-%d')
        occupied_classrooms = set()
        
        # Mevcut dolu sınıfları bul
        if date_str in self.schedule:
            for existing_slot, exam_info in self.schedule[date_str].items():
                existing_time = self.extract_time_slot(existing_slot)
                if self.times_overlap(time_slot, existing_time):
                    occupied_classrooms.update(exam_info['classrooms'])
        
        # Her grup için sınıf ata
        assignments = []
        available_classrooms = [(k, v) for k, v in self.classrooms.items() if k not in occupied_classrooms]
        available_classrooms.sort(key=lambda x: x[1], reverse=True)  # Büyük sınıflar önce
        
        classroom_index = 0
        for course in course_group:
            group_classrooms = []
            remaining_capacity = course['student_count']
            
            while remaining_capacity > 0 and classroom_index < len(available_classrooms):
                classroom, capacity = available_classrooms[classroom_index]
                group_classrooms.append(classroom)
                remaining_capacity -= capacity
                classroom_index += 1
            
            if remaining_capacity > 0:
                return None  # Yetersiz kapasite
            
            assignments.append(group_classrooms)
        
        return assignments
    
    def assign_classrooms_optimized(self, required_capacity, day, time_slot):
        """Optimized sınıf ataması"""
        date_str = day['date'].strftime('%Y-%m-%d')
        occupied_classrooms = set()
        
        # Mevcut dolu sınıfları bul
        if date_str in self.schedule:
            for existing_slot, exam_info in self.schedule[date_str].items():
                existing_time = self.extract_time_slot(existing_slot)
                if self.times_overlap(time_slot, existing_time):
                    occupied_classrooms.update(exam_info['classrooms'])
        
        # Müsait sınıfları büyükten küçüğe sırala
        available = [(k, v) for k, v in self.classrooms.items() if k not in occupied_classrooms]
        available.sort(key=lambda x: x[1], reverse=True)
        
        assigned = []
        remaining = required_capacity
        
        for classroom, capacity in available:
            if remaining <= 0:
                break
            assigned.append(classroom)
            remaining -= capacity
        
        return assigned if remaining <= 0 else None
    
    def preprocess_data(self, df):
        """Veri ön işleme - geliştirilmiş"""
        courses = []
        
        for _, row in df.iterrows():
            try:
                # Güvenli veri çıkarma
                class_level = 1
                if pd.notna(row.iloc[0]):
                    level_str = str(row.iloc[0]).strip()
                    if level_str.isdigit():
                        class_level = int(level_str)
                
                code = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
                
                group = 1
                if pd.notna(row.iloc[2]):
                    group_str = str(row.iloc[2]).strip()
                    if group_str.isdigit():
                        group = int(group_str)
                
                name = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ''
                
                student_count = 0
                if pd.notna(row.iloc[4]):
                    count_str = str(row.iloc[4]).strip()
                    if count_str.replace('.', '').isdigit():
                        student_count = int(float(count_str))
                
                instructor = str(row.iloc[5]).strip() if pd.notna(row.iloc[5]) else ''
                
                if name and student_count > 0:
                    courses.append({
                        'class_level': class_level,
                        'code': code,
                        'group': group,
                        'name': name,
                        'student_count': student_count,
                        'instructor': instructor,
                        'priority': self.calculate_priority(student_count, class_level)
                    })
                    
            except Exception as e:
                print(f"Satır işleme hatası: {e}")
                continue
        
        return courses
    
    def calculate_priority(self, student_count, class_level):
        """Ders önceliği hesapla"""
        priority = student_count * 10
        if student_count > 120:
            priority += 1000
        priority += (5 - class_level) * 50
        return priority
    
    def generate_available_days(self, allow_weekend):
        """Müsait günleri oluştur"""
        days = []
        current = self.start_date
        
        while current <= self.end_date:
            if current not in self.excluded_dates:
                if allow_weekend or current.weekday() < 5:
                    days.append({
                        'date': current,
                        'weekday': current.strftime('%A'),
                        'is_weekend': current.weekday() >= 5,
                        'slots': self.weekend_slots if current.weekday() >= 5 else self.weekday_slots
                    })
            current += timedelta(days=1)
        
        return days
    
    def place_fixed_exams(self, courses, available_days):
        """Sabit sınavları yerleştir"""
        for course in courses:
            if course['name'] in self.fixed_exams:
                fixed_info = self.fixed_exams[course['name']]
                
                # İlk uygun günü bul
                target_day = None
                for day in available_days:
                    if day['weekday'] == fixed_info['day']:
                        target_day = day
                        break
                
                if target_day:
                    classrooms = self.assign_classrooms_optimized(
                        course['student_count'], target_day, fixed_info['time']
                    )
                    
                    if classrooms:
                        date_str = target_day['date'].strftime('%Y-%m-%d')
                        if date_str not in self.schedule:
                            self.schedule[date_str] = {}
                        
                        self.schedule[date_str][fixed_info['time']] = {
                            'course': course,
                            'classrooms': classrooms,
                            'fixed': True
                        }
                        print(f"Sabit sınav yerleştirildi: {course['name']}")
    
    def place_common_exams(self, available_days):
        """Ortak sınavları yerleştir"""
        for date_str, time_slots in self.common_exams.items():
            if date_str not in self.schedule:
                self.schedule[date_str] = {}
            
            for time_slot, exam_info in time_slots.items():
                self.schedule[date_str][time_slot] = {
                    'course': {
                        'name': ' / '.join(exam_info['courses']), 
                        'student_count': 200,
                        'class_level': 0
                    },
                    'classrooms': ['E106', 'EZ003', 'EZ004'],
                    'is_common': True,
                    'fixed': exam_info['fixed']
                }
    
    def is_exam_placed(self, course):
        """Ders zaten yerleştirilmiş mi?"""
        for date_exams in self.schedule.values():
            for exam_info in date_exams.values():
                if exam_info['course'].get('name') == course.get('name'):
                    return True
        return False

class ScheduleTableWidget(QWidget):
    """PDF benzeri sınav takvimi tablosu"""
    
    def __init__(self, schedule_data):
        super().__init__()
        self.schedule_data = schedule_data
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Başlık
        title = QLabel("📅 SINAV TAKVİMİ - YBÜ BİLGİSAYAR MÜHENDİSLİĞİ")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 10px; background: #2c3e50; color: white; border-radius: 8px;")
        layout.addWidget(title)
        
        # Tablo
        self.table = QTableWidget()
        self.populate_table()
        layout.addWidget(self.table)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("✏️ Düzenle")
        self.edit_btn.clicked.connect(self.edit_selected_exam)
        btn_layout.addWidget(self.edit_btn)
        
        self.export_excel_btn = QPushButton("📊 Excel Çıktı")
        self.export_excel_btn.clicked.connect(self.export_to_excel)
        btn_layout.addWidget(self.export_excel_btn)
        
        self.export_pdf_btn = QPushButton("📄 PDF Çıktı")
        self.export_pdf_btn.clicked.connect(self.export_to_pdf)
        btn_layout.addWidget(self.export_pdf_btn)
        
        layout.addLayout(btn_layout)
        
    def populate_table(self):
        """Tabloyu doldur"""
        if not self.schedule_data:
            return
        
        # Tarih ve saat listelerini oluştur
        dates = sorted(self.schedule_data.keys())
        all_times = set()
        
        for date_exams in self.schedule_data.values():
            for time_key in date_exams.keys():
                time_slot = self.extract_time_slot(time_key)
                all_times.add(time_slot)
        
        times = sorted(list(all_times))
        
        # Tablo boyutları
        self.table.setRowCount(len(times))
        self.table.setColumnCount(len(dates) + 1)
        
        # Başlıklar
        headers = ['SAAT'] + [self.format_date_header(date) for date in dates]
        self.table.setHorizontalHeaderLabels(headers)
        
        # Satır başlıkları (saatler)
        for i, time_slot in enumerate(times):
            self.table.setVerticalHeaderItem(i, QTableWidgetItem(time_slot))
        
        # Hücreleri doldur
        for i, time_slot in enumerate(times):
            # Saat sütunu
            time_item = QTableWidgetItem(time_slot)
            time_item.setTextAlignment(Qt.AlignCenter)
            time_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.table.setItem(i, 0, time_item)
            
            for j, date in enumerate(dates):
                col_index = j + 1
                exam_info = self.find_exam_at_time(date, time_slot)
                
                if exam_info:
                    item = self.create_exam_item(exam_info, date, time_slot)
                else:
                    item = QTableWidgetItem("")
                
                self.table.setItem(i, col_index, item)
        
        # Tablo görünümü
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        
    def extract_time_slot(self, slot_key):
        """Slot anahtarından zaman dilimini çıkar"""
        if '_GROUP_' in slot_key:
            return slot_key.split('_GROUP_')[0]
        return slot_key
    
    def format_date_header(self, date_str):
        """Tarih başlığını formatla"""
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        day_names = {
            'Monday': 'PAZARTESİ', 'Tuesday': 'SALI', 'Wednesday': 'ÇARŞAMBA',
            'Thursday': 'PERŞEMBE', 'Friday': 'CUMA', 'Saturday': 'CUMARTESİ', 'Sunday': 'PAZAR'
        }
        day_name = day_names.get(date_obj.strftime('%A'), '')
        return f"{date_obj.strftime('%d/%m/%Y')}\n{day_name}"
    
    def find_exam_at_time(self, date, time_slot):
        """Belirtilen zamandaki sınavı bul"""
        if date not in self.schedule_data:
            return None
        
        # Grup sınavlarını birleştir
        group_exams = []
        single_exam = None
        
        for slot_key, exam_info in self.schedule_data[date].items():
            exam_time = self.extract_time_slot(slot_key)
            if exam_time == time_slot:
                if '_GROUP_' in slot_key:
                    group_exams.append(exam_info)
                else:
                    single_exam = exam_info
        
        if group_exams:
            return {'type': 'group', 'exams': group_exams}
        elif single_exam:
            return {'type': 'single', 'exam': single_exam}
        
        return None
    
    def create_exam_item(self, exam_info, date, time_slot):
        """Sınav hücresi oluştur"""
        if exam_info['type'] == 'group':
            # Grup sınavları
            content = ""
            classrooms = []
            is_fixed = False
            
            for exam in exam_info['exams']:
                course = exam['course']
                content += f"📚 {course['name']}\n"
                content += f"👥 {course['student_count']} öğrenci\n"
                content += f"🏛️ {', '.join(exam['classrooms'])}\n\n"
                classrooms.extend(exam['classrooms'])
                if exam.get('fixed', False):
                    is_fixed = True
        else:
            # Tekli sınav
            exam = exam_info['exam']
            course = exam['course']
            content = f"📚 {course['name']}\n"
            content += f"👥 {course['student_count']} öğrenci\n"
            content += f"🏛️ {', '.join(exam['classrooms'])}"
            is_fixed = exam.get('fixed', False)
        
        item = QTableWidgetItem(content.strip())
        item.setData(Qt.UserRole, {'date': date, 'time': time_slot, 'exam_info': exam_info})
        
        # Renklendirme
        if is_fixed:
            item.setBackground(QColor(255, 200, 200))  # Kırmızımsı - değiştirilemez
            item.setToolTip("🔒 Bu sınav sabit - değiştirilemez")
        else:
            item.setBackground(QColor(200, 255, 200))  # Yeşilimsi - değiştirilebilir
            item.setToolTip("✏️ Bu sınavı düzenleyebilirsiniz")
        
        item.setFont(QFont("Arial", 9))
        return item
    
    def edit_selected_exam(self):
        """Seçili sınavı düzenle"""
        current_item = self.table.currentItem()
        if not current_item:
            QMessageBox.information(self, "Bilgi", "Lütfen düzenlemek istediğiniz sınavı seçin.")
            return
        
        exam_data = current_item.data(Qt.UserRole)
        if not exam_data:
            QMessageBox.information(self, "Bilgi", "Bu hücre boş.")
            return
        
        # Sabit sınav kontrolü
        exam_info = exam_data['exam_info']
        if exam_info['type'] == 'single' and exam_info['exam'].get('fixed', False):
            QMessageBox.warning(self, "Uyarı", "Bu sınav sabit olarak belirlenmiş - değiştirilemez!")
            return
        elif exam_info['type'] == 'group':
            for exam in exam_info['exams']:
                if exam.get('fixed', False):
                    QMessageBox.warning(self, "Uyarı", "Bu grup sınavında sabit dersler var - değiştirilemez!")
                    return
        
        # Düzenleme dialogu aç
        dialog = ExamEditDialog(exam_data, self.schedule_data)
        if dialog.exec_() == QDialog.Accepted:
            new_date, new_time = dialog.get_new_schedule()
            if new_date and new_time:
                self.move_exam(exam_data, new_date, new_time)
                self.populate_table()  # Tabloyu yenile
    
    def move_exam(self, exam_data, new_date, new_time):
        """Sınavı taşı"""
        old_date = exam_data['date']
        old_time = exam_data['time']
        
        # Eski konumdan kaldır
        if old_date in self.schedule_data:
            keys_to_remove = []
            for slot_key in self.schedule_data[old_date]:
                if self.extract_time_slot(slot_key) == old_time:
                    keys_to_remove.append(slot_key)
            
            for key in keys_to_remove:
                del self.schedule_data[old_date][key]
        
        # Yeni konuma ekle
        if new_date not in self.schedule_data:
            self.schedule_data[new_date] = {}
        
        exam_info = exam_data['exam_info']
        if exam_info['type'] == 'group':
            for i, exam in enumerate(exam_info['exams']):
                group_key = f"{new_time}_GROUP_{i}"
                self.schedule_data[new_date][group_key] = exam
        else:
            self.schedule_data[new_date][new_time] = exam_info['exam']
    
    def export_to_excel(self):
        """Excel dosyasına aktar"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Excel Dosyası Kaydet", "sinav_takvimi.xlsx", "Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                # Pandas DataFrame oluştur
                dates = sorted(self.schedule_data.keys())
                all_times = set()
                
                for date_exams in self.schedule_data.values():
                    for time_key in date_exams.keys():
                        time_slot = self.extract_time_slot(time_key)
                        all_times.add(time_slot)
                
                times = sorted(list(all_times))
                
                # DataFrame için veri hazırla
                data = []
                for time_slot in times:
                    row = {'SAAT': time_slot}
                    for date in dates:
                        date_formatted = self.format_date_header(date).replace('\n', ' ')
                        exam_info = self.find_exam_at_time(date, time_slot)
                        
                        if exam_info:
                            if exam_info['type'] == 'group':
                                content = ""
                                for exam in exam_info['exams']:
                                    course = exam['course']
                                    content += f"{course['name']} ({course['student_count']} öğr.) "
                            else:
                                course = exam_info['exam']['course']
                                content = f"{course['name']} ({course['student_count']} öğr.)"
                            row[date_formatted] = content
                        else:
                            row[date_formatted] = ""
                    
                    data.append(row)
                
                df = pd.DataFrame(data)
                df.to_excel(file_path, index=False)
                
                QMessageBox.information(self, "Başarılı", f"Excel dosyası kaydedildi:\n{file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Excel dosyası kaydedilemedi:\n{str(e)}")
    
    def export_to_pdf(self):
        """PDF dosyasına aktar"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "PDF Dosyası Kaydet", "sinav_takvimi.pdf", "PDF Files (*.pdf)"
        )
        
        if file_path:
            try:
                doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))
                elements = []
                
                # Başlık
                styles = getSampleStyleSheet()
                title = Paragraph("SINAV TAKVİMİ - YBÜ BİLGİSAYAR MÜHENDİSLİĞİ", styles['Title'])
                elements.append(title)
                elements.append(Spacer(1, 20))
                
                # Tablo verisi hazırla
                dates = sorted(self.schedule_data.keys())
                all_times = set()
                
                for date_exams in self.schedule_data.values():
                    for time_key in date_exams.keys():
                        time_slot = self.extract_time_slot(time_key)
                        all_times.add(time_slot)
                
                times = sorted(list(all_times))
                
                # Tablo başlıkları
                headers = ['SAAT'] + [self.format_date_header(date).replace('\n', ' ') for date in dates]
                table_data = [headers]
                
                # Tablo satırları
                for time_slot in times:
                    row = [time_slot]
                    for date in dates:
                        exam_info = self.find_exam_at_time(date, time_slot)
                        
                        if exam_info:
                            if exam_info['type'] == 'group':
                                content = ""
                                for exam in exam_info['exams']:
                                    course = exam['course']
                                    content += f"{course['name']}\n({course['student_count']} öğr.)\n"
                            else:
                                course = exam_info['exam']['course']
                                content = f"{course['name']}\n({course['student_count']} öğr.)"
                            row.append(Paragraph(content, styles['Normal']))
                        else:
                            row.append("")
                    
                    table_data.append(row)
                
                # Tablo oluştur
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                
                elements.append(table)
                doc.build(elements)
                
                QMessageBox.information(self, "Başarılı", f"PDF dosyası kaydedildi:\n{file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"PDF dosyası kaydedilemedi:\n{str(e)}")

class ExamEditDialog(QDialog):
    """Sınav düzenleme dialogu"""
    
    def __init__(self, exam_data, schedule_data):
        super().__init__()
        self.exam_data = exam_data
        self.schedule_data = schedule_data
        self.new_date = None
        self.new_time = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Sınav Zamanını Değiştir")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Mevcut bilgi
        info_group = QGroupBox("Mevcut Sınav Bilgisi")
        info_layout = QVBoxLayout(info_group)
        
        current_info = f"📅 Tarih: {self.exam_data['date']}\n"
        current_info += f"🕒 Saat: {self.exam_data['time']}\n\n"
        
        exam_info = self.exam_data['exam_info']
        if exam_info['type'] == 'group':
            current_info += "👥 Grup Sınavları:\n"
            for exam in exam_info['exams']:
                course = exam['course']
                current_info += f"  • {course['name']} ({course['student_count']} öğr.)\n"
        else:
            course = exam_info['exam']['course']
            current_info += f"📚 {course['name']} ({course['student_count']} öğr.)"
        
        info_label = QLabel(current_info)
        info_layout.addWidget(info_label)
        layout.addWidget(info_group)
        
        # Alternatif zamanlar
        alternatives_group = QGroupBox("Alternatif Zamanlar")
        alternatives_layout = QVBoxLayout(alternatives_group)
        
        self.alternatives_list = QComboBox()
        self.populate_alternatives()
        alternatives_layout.addWidget(self.alternatives_list)
        
        layout.addWidget(alternatives_group)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        self.ok_btn = QPushButton("✅ Değiştir")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("❌ İptal")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def populate_alternatives(self):
        """Alternatif zamanları listele"""
        alternatives = []
        
        # Tüm tarihleri ve saatleri kontrol et
        all_dates = set(self.schedule_data.keys())
        all_times = set()
        
        for date_exams in self.schedule_data.values():
            for time_key in date_exams.keys():
                time_slot = self.extract_time_slot(time_key)
                all_times.add(time_slot)
        
        # Ek tarihler de ekle (boş günler için)
        start_date = datetime(2025, 6, 11)
        end_date = datetime(2025, 6, 23)
        current = start_date
        while current <= end_date:
            if current.weekday() < 5:  # Hafta içi
                date_str = current.strftime('%Y-%m-%d')
                all_dates.add(date_str)
            current += timedelta(days=1)
        
        # Standard saat dilimlerini ekle
        standard_times = ['09:00-11:00', '11:00-13:00', '13:00-15:00', '15:00-17:00']
        all_times.update(standard_times)
        
        for date in sorted(all_dates):
            for time_slot in sorted(all_times):
                if self.is_slot_available(date, time_slot):
                    date_obj = datetime.strptime(date, '%Y-%m-%d')
                    day_name = date_obj.strftime('%A')
                    day_names = {
                        'Monday': 'Pazartesi', 'Tuesday': 'Salı', 'Wednesday': 'Çarşamba',
                        'Thursday': 'Perşembe', 'Friday': 'Cuma', 'Saturday': 'Cumartesi'
                    }
                    day_tr = day_names.get(day_name, day_name)
                    
                    display_text = f"{date} ({day_tr}) - {time_slot}"
                    alternatives.append((display_text, date, time_slot))
        
        if alternatives:
            for display_text, date, time_slot in alternatives:
                self.alternatives_list.addItem(display_text, (date, time_slot))
        else:
            self.alternatives_list.addItem("❌ Uygun alternatif bulunamadı", None)
            self.ok_btn.setEnabled(False)
    
    def extract_time_slot(self, slot_key):
        """Slot anahtarından zaman dilimini çıkar"""
        if '_GROUP_' in slot_key:
            return slot_key.split('_GROUP_')[0]
        return slot_key
    
    def is_slot_available(self, date, time_slot):
        """Slot müsait mi?"""
        # Mevcut sınav konumu ise müsait sayılır
        if date == self.exam_data['date'] and time_slot == self.exam_data['time']:
            return True
        
        # Slot dolu mu kontrol et
        if date in self.schedule_data:
            for existing_slot in self.schedule_data[date]:
                existing_time = self.extract_time_slot(existing_slot)
                if existing_time == time_slot:
                    return False
        
        return True
    
    def get_new_schedule(self):
        """Seçilen yeni zamanı döndür"""
        selected_data = self.alternatives_list.currentData()
        if selected_data:
            return selected_data
        return None, None

class FileProcessor(QThread):
    """Dosya işleme thread'i"""
    progress_updated = pyqtSignal(int)
    processing_finished = pyqtSignal(bool, str, dict)
    
    def __init__(self, file_path, start_date, end_date, allow_weekend, max_parallel):
        super().__init__()
        self.file_path = file_path
        self.start_date = start_date
        self.end_date = end_date
        self.allow_weekend = allow_weekend
        self.max_parallel = max_parallel
        
    def run(self):
        try:
            self.progress_updated.emit(10)
            
            if not os.path.exists(self.file_path):
                self.processing_finished.emit(False, "Dosya bulunamadı!", {})
                return
            
            # Excel dosyasını oku
            self.progress_updated.emit(20)
            df = pd.read_excel(self.file_path)
            
            if df.empty:
                self.processing_finished.emit(False, "Excel dosyası boş!", {})
                return
            
            self.progress_updated.emit(40)
            
            # Sınav takvimi algoritmasını çalıştır
            scheduler = ExamScheduler(self.start_date, self.end_date)
            self.progress_updated.emit(60)
            
            success, result = scheduler.create_schedule(
                df, self.allow_weekend, self.max_parallel
            )
            
            self.progress_updated.emit(90)
            
            if success:
                self.progress_updated.emit(100)
                total_courses = len(df)
                scheduled_courses = sum(len(day_exams) for day_exams in result.values())
                message = f"Başarıyla oluşturuldu!\n"
                message += f"Toplam {total_courses} ders işlendi\n"
                message += f"{scheduled_courses} sınav yerleştirildi\n"
                message += f"Takvim {len(result)} gün içeriyor"
                self.processing_finished.emit(True, message, result)
            else:
                self.processing_finished.emit(False, f"Algoritma hatası: {result}", {})
                
        except Exception as e:
            self.processing_finished.emit(False, f"İşlem hatası: {str(e)}", {})

class DragDropArea(QFrame):
    """Sürükle bırak alanı"""
    file_dropped = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFixedHeight(180)
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                border: 3px dashed #bdc3c7;
                border-radius: 12px;
                background: rgba(248, 249, 250, 0.5);
            }
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        lbl = QLabel("📁 Excel (*.xlsx, *.xls)\nSürükle-Bırak veya \"Dosya Seç\"")
        lbl.setFont(QFont("Segoe UI", 12))
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color: #2c3e50;")
        layout.addWidget(lbl)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() and len(event.mimeData().urls()) == 1:
            path = event.mimeData().urls()[0].toLocalFile()
            if path.lower().endswith(('.xlsx', '.xls')):
                event.acceptProposedAction()
                self.setStyleSheet(self.styleSheet().replace("#bdc3c7", "#667eea"))
                
    def dragLeaveEvent(self, event):
        self.setStyleSheet(self.styleSheet().replace("#667eea", "#bdc3c7"))
        
    def dropEvent(self, event: QDropEvent):
        path = event.mimeData().urls()[0].toLocalFile()
        self.file_dropped.emit(path)
        self.setStyleSheet(self.styleSheet().replace("#667eea", "#bdc3c7"))

class ModernUploadPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SınavTakvim Pro – Gelişmiş Sınav Programı Oluşturucu")
        self.setGeometry(200, 150, 1400, 900)
        self.setMinimumSize(1200, 800)
        self.selected_file = ""
        self.schedule_result = {}
        
        self.setStyleSheet("""
            QWidget { background: qlineargradient(
                x1:0,y1:0,x2:1,y2:1,
                stop:0 #f8f9fa, stop:1 #e9ecef);
            }
        """)
        
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(40, 30, 40, 30)
        main.setSpacing(20)
        
        # Header: Geri Butonu
        hdr = QHBoxLayout()
        self.back_btn = QPushButton("← Ana Menü")
        self.back_btn.setFixedSize(120, 40)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background:white; color:#6c757d;
                border:2px solid #dee2e6; border-radius:8px;
            }
            QPushButton:hover { color:#667eea; border-color:#667eea; }
        """)
        hdr.addWidget(self.back_btn)
        hdr.addStretch()
        main.addLayout(hdr)
        
        # Content card
        card = QFrame()
        card.setStyleSheet("QFrame{background:white; border-radius:15px;}")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25); shadow.setYOffset(5)
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(20)
        
        # Başlık
        title = QLabel("🎯 Gelişmiş Sınav Takvimi Oluşturucu")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        
        sub = QLabel("Çakışmasız • Düzenlenebilir • Excel/PDF Çıktı")
        sub.setFont(QFont("Segoe UI", 12))
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)
        card_layout.addWidget(sub)
        
        # Tarih seçimi
        date_group = QGroupBox("📅 Sınav Dönemi")
        date_layout = QHBoxLayout(date_group)
        
        date_layout.addWidget(QLabel("Başlangıç:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate(2025, 6, 11))
        self.start_date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.start_date_edit)
        
        date_layout.addWidget(QLabel("Bitiş:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate(2025, 6, 23))
        self.end_date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.end_date_edit)
        
        date_layout.addStretch()
        card_layout.addWidget(date_group)
        
        # Drag & Drop alanı
        self.drop_area = DragDropArea()
        card_layout.addWidget(self.drop_area)
        
        # Dosya yol input + buton
        row = QHBoxLayout()
        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        self.file_input.setPlaceholderText("Ders bazlı öğrenci sayısı Excel dosyası...")
        self.file_input.setFixedHeight(40)
        row.addWidget(self.file_input)
        self.browse_btn = QPushButton("Dosya Seç")
        self.browse_btn.setFixedSize(120, 40)
        row.addWidget(self.browse_btn)
        card_layout.addLayout(row)
        
        # İlerleme çubuğu ve durum etiketi
        self.progress = QProgressBar()
        self.progress.setFixedHeight(8)
        self.progress.hide()
        card_layout.addWidget(self.progress)
        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setWordWrap(True)
        card_layout.addWidget(self.status)
        
        # Algoritma ayarları
        settings_frame = QFrame()
        settings_frame.setStyleSheet("QFrame { background: #f8f9fa; border-radius: 8px; padding: 15px; }")
        settings_layout = QVBoxLayout(settings_frame)
        
        settings_title = QLabel("⚙️ Algoritma Parametreleri")
        settings_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        settings_layout.addWidget(settings_title)
        
        settings_row1 = QHBoxLayout()
        self.chk_weekend = QCheckBox("Hafta sonu dahil et (ÖSYM sınavları hariç)")
        self.chk_weekend.setChecked(False)
        settings_row1.addWidget(self.chk_weekend)
        settings_row1.addStretch()
        
        settings_row2 = QHBoxLayout()
        lbl_parallel = QLabel("Günlük maksimum paralel sınav:")
        settings_row2.addWidget(lbl_parallel)
        self.spin_parallel = QSpinBox()
        self.spin_parallel.setRange(1, 8)
        self.spin_parallel.setValue(4)
        self.spin_parallel.setSuffix(" sınav")
        settings_row2.addWidget(self.spin_parallel)
        settings_row2.addStretch()
        
        settings_layout.addLayout(settings_row1)
        settings_layout.addLayout(settings_row2)
        card_layout.addWidget(settings_frame)
        
        # İşlem başlat butonu
        self.start_btn = QPushButton("🚀 Çakışmasız Sınav Takvimi Oluştur")
        self.start_btn.setFixedHeight(50)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0,y1:0,x2:1,y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color:white; border:none; border-radius:12px;
                font-size:14px; font-weight:600;
            }
            QPushButton:hover { background: qlineargradient(
                x1:0,y1:0,x2:1,y2:0,
                stop:0 #7c94f4, stop:1 #8b5fbf);
            }
        """)
        card_layout.addWidget(self.start_btn)
        
        # Sonuçları göster butonu
        self.show_results_btn = QPushButton("📋 Dinamik Takvimi Görüntüle")
        self.show_results_btn.setFixedHeight(45)
        self.show_results_btn.setStyleSheet("""
            QPushButton {
                background: #28a745; color:white; border:none; border-radius:8px;
                font-size:13px; font-weight:600;
            }
            QPushButton:hover { background: #218838; }
        """)
        self.show_results_btn.hide()
        card_layout.addWidget(self.show_results_btn)
        
        main.addWidget(card)
        
    def connect_signals(self):
        self.back_btn.clicked.connect(self.close)
        self.browse_btn.clicked.connect(self.on_browse)
        self.drop_area.file_dropped.connect(self.set_file)
        self.start_btn.clicked.connect(self.on_start)
        self.show_results_btn.clicked.connect(self.show_schedule_results)
        
    def on_browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Excel Dosyası Seç", "", "Excel Files (*.xlsx *.xls)"
        )
        if path:
            self.set_file(path)
        
    def set_file(self, path):
        self.selected_file = path
        self.file_input.setText(path)
        self.status.clear()
        self.show_results_btn.hide()
        
    def on_start(self):
        if not self.selected_file:
            self.status.setText("❌ Lütfen önce Excel dosyasını seçin.")
            return
        
        # Tarih kontrolü
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        
        if start_date >= end_date:
            self.status.setText("❌ Başlangıç tarihi bitiş tarihinden küçük olmalı!")
            return
            
        # Thread ile algoritma işlemini başlat
        self.progress.show()
        self.progress.setValue(0)
        self.status.setText("🔄 Çakışmasız algoritma çalışıyor...")
        self.start_btn.setEnabled(False)
        
        # datetime objeleri oluştur
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.min.time())
        
        self.worker = FileProcessor(
            self.selected_file,
            start_datetime,
            end_datetime,
            allow_weekend=self.chk_weekend.isChecked(),
            max_parallel=self.spin_parallel.value()
        )
        self.worker.progress_updated.connect(self.progress.setValue)
        self.worker.processing_finished.connect(self.on_finished)
        self.worker.start()
        
    def on_finished(self, success: bool, msg: str, schedule: dict):
        self.start_btn.setEnabled(True)
        
        if success:
            self.status.setText(f"✅ {msg}")
            self.progress.setValue(100)
            self.schedule_result = schedule
            self.show_results_btn.show()
        else:
            self.status.setText(f"❌ {msg}")
            self.progress.hide()
            self.schedule_result = {}
    
    def show_schedule_results(self):
        """Dinamik takvimi göster"""
        if not self.schedule_result:
            QMessageBox.warning(self, "Sonuç Yok", "Henüz bir takvim oluşturulmadı!")
            return
        
        # Dinamik tablo penceresini oluştur
        self.result_window = ScheduleTableWidget(self.schedule_result)
        self.result_window.setWindowTitle("Dinamik Sınav Takvimi - Düzenlenebilir")
        self.result_window.show()
        self.result_window.raise_()
        self.result_window.activateWindow()

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = ModernUploadPage()
    window.show()
    sys.exit(app.exec_())