"""
بوت تليجرام مع Webhook للنشر على Railway
"""

import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot import MahareenBot

# إعداد نظام السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إنشاء تطبيق Flask
app = Flask(__name__)

# إنشاء البوت
bot_instance = MahareenBot()

# إنشاء التطبيق
application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

# إضافة المعالجات
application.add_handler(CommandHandler("start", bot_instance.start_command))
application.add_handler(CallbackQueryHandler(bot_instance.button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_instance.message_handler))

@app.route('/')
def index():
    return "🤖 بوت أكاديمية الماهرون يعمل بنجاح!"

@app.route('/webhook', methods=['POST'])
async def webhook():
    """معالج Webhook"""
    try:
        # الحصول على البيانات من Telegram
        json_data = request.get_json()
        
        # إنشاء Update object
        update = Update.de_json(json_data, application.bot)
        
        # معالجة التحديث
        await application.process_update(update)
        
        return "OK"
    except Exception as e:
        logger.error(f"خطأ في معالجة Webhook: {e}")
        return "Error", 500

@app.route('/set_webhook')
async def set_webhook():
    """تعيين Webhook URL"""
    try:
        webhook_url = f"https://{request.host}/webhook"
        await application.bot.set_webhook(webhook_url)
        return f"✅ تم تعيين Webhook: {webhook_url}"
    except Exception as e:
        logger.error(f"خطأ في تعيين Webhook: {e}")
        return f"❌ خطأ في تعيين Webhook: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
