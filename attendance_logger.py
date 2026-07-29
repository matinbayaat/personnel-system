import json
import os
from datetime import datetime
import pandas as pd

class AttendanceLogger:
    def __init__(self, log_file='logs/attendance.json'):
        """
        ثبت و مدیریت ورود/خروج کارکنان
        """
        self.log_file = log_file
        self.attendance_data = []
        self.load_data()
        
    def load_data(self):
        """بارگذاری داده‌های قبلی"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.attendance_data = json.load(f)
                print(f"✅ {len(self.attendance_data)} رکورد بارگذاری شد")
            except:
                self.attendance_data = []
                print("⚠️ خطا در بارگذاری داده، شروع مجدد")
        else:
            self.attendance_data = []
            print("ℹ️ فایل لاگ جدید ایجاد می‌شود")
    
    def save_data(self):
        """ذخیره داده‌ها در فایل"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.attendance_data, f, ensure_ascii=False, indent=2)
        print(f"✅ {len(self.attendance_data)} رکورد ذخیره شد")
    
    def log_attendance(self, personnel_id, image_path=None, action='check_in'):
        """
        ثبت ورود یا خروج کارمند
        
        Args:
            personnel_id: شماره پرسنلی
            image_path: مسیر تصویر ثبت شده
            action: 'check_in' یا 'check_out'
        
        Returns:
            دیکشنری شامل اطلاعات ثبت شده
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime('%Y-%m-%d')
        time_str = timestamp.strftime('%H:%M:%S')
        
        # بررسی آخرین وضعیت کارمند
        last_record = self.get_last_record(personnel_id)
        
        # اگر ورود است و آخرین وضعیت هم ورود بوده، اجازه ندهید
        if action == 'check_in' and last_record and last_record['action'] == 'check_in':
            print(f"⚠️ کارمند {personnel_id} قبلاً امروز ورود ثبت کرده است")
            return None
        
        # اگر خروج است و آخرین وضعیت خروج بوده یا رکوردی وجود ندارد
        if action == 'check_out':
            if not last_record or last_record['action'] == 'check_out':
                print(f"⚠️ کارمند {personnel_id} امروز ورود ثبت نکرده است")
                return None
        
        # ثبت رکورد جدید
        record = {
            'personnel_id': personnel_id,
            'action': action,
            'date': date_str,
            'time': time_str,
            'timestamp': timestamp.isoformat(),
            'image_path': image_path
        }
        
        self.attendance_data.append(record)
        self.save_data()
        
        action_persian = "ورود" if action == 'check_in' else "خروج"
        print(f"✅ {action_persian} کارمند {personnel_id} در {time_str} ثبت شد")
        
        return record
    
    def get_last_record(self, personnel_id):
        """دریافت آخرین رکورد یک کارمند"""
        records = [r for r in self.attendance_data if r['personnel_id'] == personnel_id]
        if records:
            return records[-1]
        return None
    
    def get_today_records(self):
        """دریافت رکوردهای امروز"""
        today = datetime.now().strftime('%Y-%m-%d')
        return [r for r in self.attendance_data if r['date'] == today]
    
    def get_employee_today_status(self, personnel_id):
        """
        دریافت وضعیت امروز یک کارمند
        Returns: 'checked_in', 'checked_out', 'not_registered'
        """
        today_records = [r for r in self.get_today_records() 
                        if r['personnel_id'] == personnel_id]
        
        if not today_records:
            return 'not_registered'
        
        last_record = today_records[-1]
        return 'checked_in' if last_record['action'] == 'check_in' else 'checked_out'
    
    def generate_daily_summary(self):
        """تولید خلاصه روزانه"""
        today_records = self.get_today_records()
        
        if not today_records:
            return "📊 امروز هیچ رکوردی ثبت نشده است"
        
        summary = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_records': len(today_records),
            'check_ins': len([r for r in today_records if r['action'] == 'check_in']),
            'check_outs': len([r for r in today_records if r['action'] == 'check_out']),
            'unique_employees': len(set(r['personnel_id'] for r in today_records))
        }
        
        return summary

# تست ماژول
if __name__ == "__main__":
    logger = AttendanceLogger()
    
    # ثبت نمونه
    logger.log_attendance('12345', action='check_in')
    logger.log_attendance('12345', action='check_out')
    
    print("\n📊 خلاصه امروز:")
    print(logger.generate_daily_summary())