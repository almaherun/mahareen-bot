"""
مدير Google Gemini API مع نظام تبديل تلقائي
"""

import os
import logging
import google.generativeai as genai
from typing import Optional

logger = logging.getLogger(__name__)

class GeminiManager:
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.current_index = int(os.getenv('CURRENT_API_INDEX', 0))
        self.model = None
        self._initialize_model()
    
    def _load_api_keys(self) -> list:
        """تحميل مفاتيح API من متغيرات البيئة"""
        keys_str = os.getenv('GEMINI_API_KEYS', '')
        if not keys_str:
            logger.error("❌ لم يتم العثور على مفاتيح Gemini API")
            return []
        
        keys = [key.strip() for key in keys_str.split(',') if key.strip()]
        logger.info(f"✅ تم تحميل {len(keys)} مفاتيح API")
        return keys
    
    def _initialize_model(self):
        """تهيئة نموذج Gemini"""
        if not self.api_keys:
            logger.error("❌ لا توجد مفاتيح API متاحة")
            return
        
        try:
            current_key = self.api_keys[self.current_index]
            genai.configure(api_key=current_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info(f"✅ تم تهيئة Gemini بالمفتاح رقم {self.current_index + 1}")
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة Gemini: {e}")
            self._try_next_key()
    
    def _try_next_key(self):
        """محاولة استخدام المفتاح التالي"""
        if len(self.api_keys) <= 1:
            logger.error("❌ لا توجد مفاتيح بديلة")
            return
        
        self.current_index = (self.current_index + 1) % len(self.api_keys)
        logger.info(f"🔄 التبديل إلى المفتاح رقم {self.current_index + 1}")
        
        try:
            current_key = self.api_keys[self.current_index]
            genai.configure(api_key=current_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("✅ تم التبديل بنجاح")
        except Exception as e:
            logger.error(f"❌ فشل التبديل: {e}")
            if self.current_index < len(self.api_keys) - 1:
                self._try_next_key()
    
    async def generate_response(self, prompt: str, context: str = "") -> Optional[str]:
        """توليد رد من Gemini"""
        if not self.model:
            return "❌ عذراً، الذكاء الاصطناعي غير متاح حال<|im_start|>"
        
        try:
            # إعداد السياق والتعليمات
            full_prompt = f"""
أنت مساعد ذكي لأكاديمية الماهرون لتعليم القرآن الكريم.

معلومات الأكاديمية:
{context}

تعليمات مهمة:
- أجب بالعربية فقط
- كن مفيد<|im_start|> ومهذباً
- ركز على معلومات الأكاديمية
- إذا لم تعرف الإجابة، وجه المستخدم للتواصل المباشر
- استخدم الإيموجي بشكل مناسب

سؤال المستخدم: {prompt}

الإجابة:
"""
            
            response = self.model.generate_content(full_prompt)
            
            if response and response.text:
                logger.info("✅ تم توليد رد من Gemini بنجاح")
                return response.text.strip()
            else:
                logger.warning("⚠️ رد فارغ من Gemini")
                return "عذراً، لم أتمكن من فهم سؤالك. يرجى إعادة صياغته."
                
        except Exception as e:
            logger.error(f"❌ خطأ في Gemini: {e}")
            
            # محاولة التبديل للمفتاح التالي
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                logger.info("🔄 انتهت حصة المفتاح الحالي، جاري التبديل...")
                self._try_next_key()
                
                # محاولة مرة أخرى مع المفتاح الجديد
                try:
                    response = self.model.generate_content(full_prompt)
                    if response and response.text:
                        return response.text.strip()
                except Exception as e2:
                    logger.error(f"❌ فشل مع المفتاح الجديد: {e2}")
            
            return "❌ عذراً، حدث خطأ في الذكاء الاصطناعي. يرجى المحاولة لاحق应用查看نا مباشرة."
    
    def get_current_key_info(self) -> dict:
        """الحصول على معلومات المفتاح الحالي"""
        return {
            "current_index": self.current_index,
            "total_keys": len(self.api_keys),
            "has_model": self.model is not None
        }
