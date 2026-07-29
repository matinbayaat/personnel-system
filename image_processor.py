import cv2
import numpy as np
from datetime import datetime

class ImageProcessor:
    def __init__(self):
        """پردازش و اصلاح تصویر برای بهبود کیفیت OCR"""
        pass
    
    def preprocess_for_ocr(self, image):
        """
        پیش‌پردازش تصویر برای بهبود دقت OCR
        
        مراحل:
        1. تبدیل به خاکستری
        2. افزایش کنتراست
        3. کاهش نویز
        4. آستانه‌گذاری تطبیقی
        5. بزرگنمایی
        """
        if image is None:
            raise ValueError("❌ تصویر ورودی خالی است")
        
        # 1. تبدیل به خاکستری
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 2. افزایش کنتراست با CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # 3. کاهش نویز با بیلترال فیلتر
        denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # 4. آستانه‌گذاری تطبیقی
        binary = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # 5. بزرگنمایی برای OCR بهتر
        scale_factor = 2.0
        width = int(binary.shape[1] * scale_factor)
        height = int(binary.shape[0] * scale_factor)
        scaled = cv2.resize(binary, (width, height), interpolation=cv2.INTER_CUBIC)
        
        # 6. مورفولوژی برای اتصال حروف
        kernel = np.ones((1, 1), np.uint8)
        morph = cv2.morphologyEx(scaled, cv2.MORPH_CLOSE, kernel)
        
        return morph
    
    def correct_perspective(self, image):
        """
        تصحیح پرسپکتیو کارت (اختیاری)
        """
        # این تابع برای تصحیح زاویه کارت استفاده می‌شود
        # در صورت نیاز می‌توانید پیاده‌سازی کنید
        return image
    
    def extract_text_region(self, image, region):
        """
        استخراج ناحیه مشخص از تصویر
        """
        x, y, w, h = region
        roi = image[y:y+h, x:x+w]
        return roi
    
    def deskew(self, image):
        """
        اصلاح کجی متن
        """
        coords = np.column_stack(np.where(image > 0))
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), 
                                   flags=cv2.INTER_CUBIC,
                                   borderMode=cv2.BORDER_REPLICATE)
            return rotated
        return image
    
    def save_processed_image(self, image, prefix='processed'):
        """ذخیره تصویر پردازش شده برای دیباگ"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'logs/{prefix}_{timestamp}.jpg'
        cv2.imwrite(filename, image)
        return filename

# تست ماژول
if __name__ == "__main__":
    processor = ImageProcessor()
    # تست با یک تصویر نمونه
    test_image = cv2.imread('test_images/sample.jpg')
    if test_image is not None:
        processed = processor.preprocess_for_ocr(test_image)
        cv2.imshow('Original', test_image)
        cv2.imshow('Processed', processed)
        cv2.waitKey(0)
        cv2.destroyAllWindows()