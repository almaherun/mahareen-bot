"""
الملف الرئيسي لتشغيل بوت أكاديمية الماهرون
يدعم كل من Polling و Webhook
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إعداد نظام السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_environment():
    """التحقق من متغيرات البيئة المطلوبة"""
    required_vars = ['TELEGRAM_BOT_TOKEN', 'GEMINI_API_KEYS']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ متغيرات البيئة المفقودة: {', '.join(missing_vars)}")
        return False
    
    logger.info("✅ جميع متغيرات البيئة متوفرة")
    return True

def main():
    """الدالة الرئيسية"""
    logger.info("🚀 بدء تشغيل بوت أكاديمية الماهرون...")
    
    # التحقق من متغيرات البيئة
    if not check_environment():
        sys.exit(1)
    
    # تحديد وضع التشغيل
    mode = os.getenv('BOT_MODE', 'polling').lower()
    
    try:
        if mode == 'webhook':
            logger.info("🌐 تشغيل البوت في وضع Webhook...")
            from webhook_bot import app
            port = int(os.environ.get('PORT', 8080))
            app.run(host='0.0.0.0', port=port, debug=False)
        else:
            logger.info("🔄 تشغيل البوت في وضع Polling...")
            from bot import MahareenBot
            bot = MahareenBot()
            bot.run()
            
    except KeyboardInterrupt:
        logger.info("⏹️ تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
