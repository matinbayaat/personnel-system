import pandas as pd
from datetime import datetime, timedelta
import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

class ExcelReporter:
    def __init__(self, report_dir='reports'):
        """
        تولید گزارش‌های اکسل از داده‌های حضور و غیاب
        """
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)
        
    def generate_daily_report(self, attendance_data, date=None):
        """
        تولید گزارش روزانه
        
        Args:
            attendance_data: لیست رکوردهای حضور و غیاب
            date: تاریخ مورد نظر (پیش‌فرض امروز)
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # فیلتر کردن داده‌های تاریخ مورد نظر
        daily_data = [r for r in attendance_data if r['date'] == date]
        
        if not daily_data:
            print(f"⚠️ هیچ داده‌ای برای تاریخ {date} وجود ندارد")
            return None
        
        # تبدیل به دیتافریم
        df = pd.DataFrame(daily_data)
        
        # ایجاد جدول خلاصه برای هر کارمند
        summary = []
        employees = df['personnel_id'].unique()
        
        for emp_id in employees:
            emp_records = df[df['personnel_id'] == emp_id]
            check_ins = emp_records[emp_records['action'] == 'check_in']
            check_outs = emp_records[emp_records['action'] == 'check_out']
            
            # محاسبه ساعت کاری (اگر ورود و خروج ثبت شده باشد)
            work_hours = 0
            if len(check_ins) > 0 and len(check_outs) > 0:
                # ساده‌ترین حالت: اولین ورود و آخرین خروج
                first_in = check_ins.iloc[0]['time']
                last_out = check_outs.iloc[-1]['time']
                
                # محاسبه اختلاف زمان
                in_time = datetime.strptime(first_in, '%H:%M:%S')
                out_time = datetime.strptime(last_out, '%H:%M:%S')
                work_hours = (out_time - in_time).seconds / 3600
            
            summary.append({
                'شماره پرسنلی': emp_id,
                'تعداد ورود': len(check_ins),
                'تعداد خروج': len(check_outs),
                'ساعت کاری (ساعت)': round(work_hours, 2),
                'وضعیت': 'حاضر' if len(check_ins) > 0 else 'غایب'
            })
        
        summary_df = pd.DataFrame(summary)
        
        # ایجاد فایل اکسل
        filename = f"{self.report_dir}/daily_report_{date}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # برگه خلاصه
            summary_df.to_excel(writer, sheet_name='خلاصه روزانه', index=False)
            
            # برگه جزئیات
            df.to_excel(writer, sheet_name='جزئیات', index=False)
            
            # برگه آمار
            stats = {
                'کل کارمندان': len(employees),
                'حاضرین': len(summary_df[summary_df['وضعیت'] == 'حاضر']),
                'غایبین': len(summary_df[summary_df['وضعیت'] == 'غایب']),
                'تعداد کل ثبت‌ها': len(daily_data)
            }
            stats_df = pd.DataFrame([stats])
            stats_df.to_excel(writer, sheet_name='آمار', index=False)
        
        print(f"✅ گزارش روزانه در {filename} ذخیره شد")
        return filename
    
    def generate_weekly_report(self, attendance_data, end_date=None):
        """
        تولید گزارش هفتگی
        """
        if end_date is None:
            end_date = datetime.now()
        
        start_date = end_date - timedelta(days=7)
        
        # فیلتر کردن داده‌های هفته
        weekly_data = []
        for record in attendance_data:
            record_date = datetime.strptime(record['date'], '%Y-%m-%d')
            if start_date <= record_date <= end_date:
                weekly_data.append(record)
        
        if not weekly_data:
            print("⚠️ هیچ داده‌ای برای هفته جاری وجود ندارد")
            return None
        
        df = pd.DataFrame(weekly_data)
        filename = f"{self.report_dir}/weekly_report_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # جزئیات
            df.to_excel(writer, sheet_name='جزئیات هفتگی', index=False)
            
            # خلاصه روزانه
            daily_summary = df.groupby(['date', 'personnel_id']).agg({
                'action': lambda x: list(x)
            }).reset_index()
            daily_summary.to_excel(writer, sheet_name='خلاصه روزانه', index=False)
        
        print(f"✅ گزارش هفتگی در {filename} ذخیره شد")
        return filename
    
    def generate_monthly_report(self, attendance_data, year=None, month=None):
        """
        تولید گزارش ماهانه
        """
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        # فیلتر کردن داده‌های ماه
        monthly_data = []
        for record in attendance_data:
            record_date = datetime.strptime(record['date'], '%Y-%m-%d')
            if record_date.year == year and record_date.month == month:
                monthly_data.append(record)
        
        if not monthly_data:
            print(f"⚠️ هیچ داده‌ای برای ماه {month}/{year} وجود ندارد")
            return None
        
        df = pd.DataFrame(monthly_data)
        filename = f"{self.report_dir}/monthly_report_{year}_{month:02d}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # جزئیات
            df.to_excel(writer, sheet_name='جزئیات ماهانه', index=False)
            
            # خلاصه روزانه
            daily_agg = df.groupby('date').agg({
                'personnel_id': 'nunique',
                'action': 'count'
            }).reset_index()
            daily_agg.columns = ['تاریخ', 'تعداد کارمندان', 'تعداد ثبت‌ها']
            daily_agg.to_excel(writer, sheet_name='خلاصه روزانه', index=False)
            
            # خلاصه کارمندان
            employee_agg = df.groupby('personnel_id').agg({
                'action': 'count',
                'date': 'nunique'
            }).reset_index()
            employee_agg.columns = ['شماره پرسنلی', 'تعداد حضور', 'تعداد روزهای حضور']
            employee_agg.to_excel(writer, sheet_name='خلاصه کارمندان', index=False)
        
        print(f"✅ گزارش ماهانه در {filename} ذخیره شد")
        return filename

# تست ماژول
if __name__ == "__main__":
    # نمونه داده برای تست
    sample_data = [
        {'personnel_id': '12345', 'action': 'check_in', 'date': '2026-01-29', 'time': '08:30:00'},
        {'personnel_id': '12345', 'action': 'check_out', 'date': '2026-01-29', 'time': '17:30:00'},
        {'personnel_id': '67890', 'action': 'check_in', 'date': '2026-01-29', 'time': '09:00:00'},
    ]
    
    reporter = ExcelReporter()
    reporter.generate_daily_report(sample_data)