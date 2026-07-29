import cv2
import os
import sys
from datetime import datetime
import argparse

# اضافه کردن مسیر src به sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from card_detector import CardDetector
from image_processor import ImageProcessor
from ocr_reader import OCRReader
from attendance_logger import AttendanceLogger
from excel_reporter import ExcelReporter

class PersonnelSystem:
    def __init__(self):
        """سیستم اصلی ورود و خروج کارکنان"""
        print("=" * 50)
        print("🚀 سیستم ورود و خروج کارکنان")
        print("=" * 50)
        
        # راه‌اندازی ماژول‌ها
        self.detector = CardDetector()
        self.processor = ImageProcessor()
        self.ocr = OCRReader()
        self.logger = AttendanceLogger()
        self.reporter = ExcelReporter()
        
        print("✅ همه ماژول‌ها راه‌اندازی شدند\n")
    
    def process_image(self, image_path, action='check_in'):
        """
        پردازش کامل یک تصویر
        
        Args:
            image_path: مسیر تصویر
            action: 'check_in' یا 'check_out'
        
        Returns:
            نتیجه پردازش
        """
        print(f"\n📸 پردازش تصویر: {image_path}")
        print(f"🎯 عملیات: {'ورود' if action == 'check_in' else 'خروج'}")
        
        try:
            # 1. تشخیص کارت
            print("\n🔍 مرحله 1: تشخیص کارت...")
            card_result = self.detector.detect_card(image_path)
            
            if card_result is None:
                print("❌ کارت تشخیص داده نشد")
                return False
            
            print(f"✅ کارت با دقت {card_result['confidence']:.2f} تشخیص داده شد")
            
            # 2. پردازش تصویر کارت
            print("\n🖼️ مرحله 2: پردازش تصویر...")
            card_image = card_result['card_image']
            processed_image = self.processor.preprocess_for_ocr(card_image)
            
            # ذخیره تصویر پردازش شده برای دیباگ
            self.processor.save_processed_image(processed_image, 'processed')
            
            # 3. خواندن شماره پرسنلی
            print("\n📖 مرحله 3: خواندن شماره پرسنلی با OCR...")
            personnel_id = self.ocr.read_personnel_number(processed_image)
            
            if not personnel_id:
                print("❌ شماره پرسنلی خوانده نشد")
                return False
            
            print(f"✅ شماره پرسنلی: {personnel_id}")
            
            # 4. ثبت در سیستم
            print("\n📝 مرحله 4: ثبت در سیستم...")
            record = self.logger.log_attendance(personnel_id, image_path, action)
            
            if record:
                print(f"✅ ثبت با موفقیت انجام شد")
                print(f"   زمان: {record['time']}")
                print(f"   تاریخ: {record['date']}")
                return True
            else:
                print("❌ ثبت انجام نشد")
                return False
                
        except Exception as e:
            print(f"❌ خطا در پردازش: {e}")
            return False
    
    def process_video(self, camera_id=0):
        """
        پردازش ویدئو از دوربین
        """
        print("\n🎥 شروع پردازش ویدئو از دوربین...")
        print("ℹ️ برای ثبت ورود کلید 'I'، برای ثبت خروج کلید 'O'، برای خروج کلید 'Q' را فشار دهید")
        
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print("❌ خطا در باز کردن دوربین")
            return
        
        # ایجاد دایرکتوری برای تصاویر موقت
        os.makedirs('temp', exist_ok=True)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # نمایش تصویر
            display_frame = frame.copy()
            cv2.putText(display_frame, "Press I:CheckIn, O:CheckOut, Q:Quit", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Personnel System', display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('i') or key == ord('I'):
                # ثبت ورود
                temp_path = f"temp/checkin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(temp_path, frame)
                self.process_image(temp_path, 'check_in')
            elif key == ord('o') or key == ord('O'):
                # ثبت خروج
                temp_path = f"temp/checkout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(temp_path, frame)
                self.process_image(temp_path, 'check_out')
        
        cap.release()
        cv2.destroyAllWindows()
        print("✅ پردازش ویدئو متوقف شد")
    
    def generate_reports(self):
        """تولید گزارش‌ها"""
        print("\n📊 تولید گزارش‌ها...")
        
        # بارگذاری داده‌ها
        self.logger.load_data()
        data = self.logger.attendance_data
        
        if not data:
            print("⚠️ هیچ داده‌ای برای گزارش وجود ندارد")
            return
        
        # گزارش روزانه
        self.reporter.generate_daily_report(data)
        
        # گزارش هفتگی
        self.reporter.generate_weekly_report(data)
        
        # گزارش ماهانه
        self.reporter.generate_monthly_report(data)
        
        print("✅ تمام گزارش‌ها تولید شدند")
    
    def show_status(self):
        """نمایش وضعیت امروز"""
        print("\n📊 وضعیت امروز:")
        summary = self.logger.generate_daily_summary()
        if isinstance(summary, dict):
            print(f"   تاریخ: {summary['date']}")
            print(f"   تعداد کل ثبت‌ها: {summary['total_records']}")
            print(f"   ورود: {summary['check_ins']}")
            print(f"   خروج: {summary['check_outs']}")
            print(f"   کارمندان منحصر‌به‌فرد: {summary['unique_employees']}")
        else:
            print(summary)

def main():
    parser = argparse.ArgumentParser(description='سیستم ورود و خروج کارکنان')
    parser.add_argument('--image', help='مسیر تصویر برای پردازش')
    parser.add_argument('--action', choices=['check_in', 'check_out'], default='check_in',
                       help='نوع عملیات: check_in یا check_out')
    parser.add_argument('--video', action='store_true', help='اجرا با دوربین')
    parser.add_argument('--report', action='store_true', help='تولید گزارش‌ها')
    parser.add_argument('--status', action='store_true', help='نمایش وضعیت امروز')
    parser.add_argument('--camera', type=int, default=0, help='شناسه دوربین (پیش‌فرض: 0)')
    
    args = parser.parse_args()
    
    system = PersonnelSystem()
    
    if args.image:
        system.process_image(args.image, args.action)
    elif args.video:
        system.process_video(args.camera)
    elif args.report:
        system.generate_reports()
    elif args.status:
        system.show_status()
    else:
        # حالت تعاملی
        print("\n🔧 حالت تعاملی")
        print("1. پردازش تصویر")
        print("2. اجرا با دوربین")
        print("3. تولید گزارش‌ها")
        print("4. نمایش وضعیت امروز")
        print("5. خروج")
        
        choice = input("\nانتخاب شما (1-5): ")
        
        if choice == '1':
            image_path = input("مسیر تصویر: ")
            action = input("نوع عملیات (check_in/check_out): ")
            system.process_image(image_path, action)
        elif choice == '2':
            system.process_video(args.camera)
        elif choice == '3':
            system.generate_reports()
        elif choice == '4':
            system.show_status()
        else:
            print("خروج از برنامه")

if __name__ == "__main__":
    main()