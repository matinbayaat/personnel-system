import pytesseract
import cv2
import re
from datetime import datetime

class OCRReader:
    def __init__(self, tesseract_path=None):
        """
        خواننده OCR برای استخراج شماره پرسنلی
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # تنظیمات OCR برای اعداد
        self.config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
        
    def read_personnel_number(self, image):
        """
        خواندن شماره پرسنلی از تصویر کارت
        
        Returns:
            شماره پرسنلی استخراج شده یا None
        """
        if image is None:
            raise ValueError("❌ تصویر ورودی خالی است")
        
        try:
            # تصویر را به خاکستری تبدیل کنید اگر رنگی است
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # افزایش اندازه برای دقت بهتر
            scale = 3.0
            width = int(gray.shape[1] * scale)
            height = int(gray.shape[0] * scale)
            resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)
            
            # اعمال فیلتر برای کاهش نویز
            denoised = cv2.bilateralFilter(resized, 9, 75, 75)
            
            # آستانه‌گذاری
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # چندین بار OCR با تنظیمات مختلف
            results = []
            
            # PSM 6: بلوک متن واحد
            config1 = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
            text1 = pytesseract.image_to_string(thresh, config=config1)
            results.append(text1.strip())
            
            # PSM 7: خط واحد
            config2 = '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
            text2 = pytesseract.image_to_string(thresh, config=config2)
            results.append(text2.strip())
            
            # PSM 8: کلمه واحد
            config3 = '--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789'
            text3 = pytesseract.image_to_string(thresh, config=config3)
            results.append(text3.strip())
            
            # استخراج اعداد از هر نتیجه
            numbers = []
            for text in results:
                # فقط اعداد را استخراج کنید
                digits = re.sub(r'\D', '', text)
                if digits:
                    numbers.append(digits)
            
            # بهترین نتیجه را انتخاب کنید (طولانی‌ترین عدد معتبر)
            if numbers:
                # اولویت با اعدادی که 5-8 رقم هستند (شماره پرسنلی معمولی)
                valid_numbers = [n for n in numbers if 5 <= len(n) <= 8]
                if valid_numbers:
                    best = max(valid_numbers, key=len)
                    print(f"✅ شماره پرسنلی خوانده شد: {best}")
                    return best
                else:
                    # اگر عدد معتبر پیدا نشد، اولین عدد را برگردانید
                    best = max(numbers, key=len)
                    print(f"⚠️ شماره پرسنلی احتمالی: {best}")
                    return best
            
            print("❌ هیچ شماره پرسنلی خوانده نشد")
            return None
            
        except Exception as e:
            print(f"❌ خطا در OCR: {e}")
            return None
    
    def extract_id_from_multiple_regions(self, image, regions):
        """
        استخراج شماره از چندین ناحیه مختلف (برای کارت‌های با فرمت‌های مختلف)
        """
        for i, region in enumerate(regions):
            roi = image[region[1]:region[1]+region[3], region[0]:region[0]+region[2]]
            if roi.size > 0:
                number = self.read_personnel_number(roi)
                if number:
                    print(f"✅ شماره از ناحیه {i+1} استخراج شد: {number}")
                    return number
        return None
    
    def save_ocr_result(self, image, number, output_path='ocr_result.jpg'):
        """ذخیره تصویر با نتیجه OCR"""
        result_img = image.copy()
        cv2.putText(result_img, f"ID: {number}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imwrite(output_path, result_img)
        return output_path

# تست ماژول
if __name__ == "__main__":
    reader = OCRReader()
    # تست با یک تصویر نمونه
    test_image = cv2.imread('test_images/card_roi.jpg')
    if test_image is not None:
        number = reader.read_personnel_number(test_image)
        print(f"شماره پرسنلی: {number}")