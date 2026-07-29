import cv2
import numpy as np
import os
from datetime import datetime

class CardDetector:
    def __init__(self, template_path='templates/card_template.jpg'):
        """
        کلاس تشخیص کارت با استفاده از Template Matching
        """
        self.template_path = template_path
        self.template = None
        self.load_template()
        
    def load_template(self):
        """بارگذاری تمپلیت کارت"""
        if os.path.exists(self.template_path):
            self.template = cv2.imread(self.template_path, 0)
            if self.template is not None:
                print(f"✅ تمپلیت با موفقیت بارگذاری شد: {self.template.shape}")
            else:
                raise ValueError("❌ خطا در بارگذاری تمپلیت")
        else:
            raise FileNotFoundError(f"❌ فایل تمپلیت پیدا نشد: {self.template_path}")
    
    def detect_card(self, image_path, threshold=0.7):
        """
        تشخیص کارت در تصویر با استفاده از Template Matching
        
        Args:
            image_path: مسیر تصویر ورودی
            threshold: آستانه تشخیص (0-1)
        
        Returns:
            موقعیت کارت در تصویر و تصویر برش‌خورده
        """
        # خواندن تصویر
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"❌ خطا در خواندن تصویر: {image_path}")
        
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # تطبیق الگو با چندین متد
        methods = [
            cv2.TM_CCOEFF_NORMED,
            cv2.TM_CCORR_NORMED,
            cv2.TM_SQDIFF_NORMED
        ]
        
        best_match = None
        best_score = -1
        best_method = None
        
        for method in methods:
            result = cv2.matchTemplate(gray_image, self.template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # برای TM_SQDIFF_NORMED مقدار کمتر بهتر است
            if method == cv2.TM_SQDIFF_NORMED:
                score = 1 - min_val
                location = min_loc
            else:
                score = max_val
                location = max_loc
            
            if score > best_score:
                best_score = score
                best_match = location
                best_method = method
        
        print(f"🔍 بهترین تطبیق: امتیاز={best_score:.3f}, متد={best_method}")
        
        if best_score >= threshold and best_match is not None:
            h, w = self.template.shape
            x, y = best_match
            
            # برش کارت از تصویر
            card_roi = image[y:y+h, x:x+w]
            
            # رسم مستطیل روی کارت
            result_image = image.copy()
            cv2.rectangle(result_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(result_image, f"Card Detected ({best_score:.2f})", 
                       (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            return {
                'card_image': card_roi,
                'result_image': result_image,
                'location': (x, y, w, h),
                'confidence': best_score
            }
        else:
            print(f"⚠️ کارت تشخیص داده نشد (امتیاز: {best_score:.3f})")
            return None
    
    def save_detected_card(self, card_data, output_path='detected_card.jpg'):
        """ذخیره تصویر کارت تشخیص داده شده"""
        if card_data and 'result_image' in card_data:
            cv2.imwrite(output_path, card_data['result_image'])
            print(f"✅ تصویر تشخیص کارت ذخیره شد: {output_path}")
            return output_path
        return None

# تست ماژول
if __name__ == "__main__":
    # ایجاد نمونه
    detector = CardDetector()
    
    # تست با یک تصویر نمونه
    test_image = 'test_images/sample_card.jpg'  # باید یک تصویر تست داشته باشید
    if os.path.exists(test_image):
        result = detector.detect_card(test_image)
        if result:
            detector.save_detected_card(result)
            cv2.imshow('Detected Card', result['card_image'])
            cv2.waitKey(0)
            cv2.destroyAllWindows()