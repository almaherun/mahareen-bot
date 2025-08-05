"""
بوت تليجرام ذكي لأكاديمية الماهرون لتحفيظ القرآن الكريم
"""

import os
import logging
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from gemini_manager import GeminiManager
from academy_data import ACADEMY_INFO, PRICING_PLANS, CONTACT_INFO, PROGRAMS, EDUCATIONAL_PATHS

# تحميل متغيرات البيئة
load_dotenv()

# إعداد نظام السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MahareenBot:
    def __init__(self):
        self.gemini_manager = GeminiManager()
        self.user_sessions = {}  # لحفظ جلسات المستخدمين
        
    def create_main_menu(self) -> InlineKeyboardMarkup:
        """إنشاء القائمة الرئيسية"""
        keyboard = [
            [
                InlineKeyboardButton("📚 معلومات الأكاديمية", callback_data="academy_info"),
                InlineKeyboardButton("💠 البرامج التعليمية", callback_data="programs")
            ],
            [
                InlineKeyboardButton("🧭 المسارات المتوفرة", callback_data="paths"),
                InlineKeyboardButton("💵 أنظمة الاشتراك", callback_data="pricing")
            ],
            [
                InlineKeyboardButton("📞 التواصل والتسجيل", callback_data="contact"),
                InlineKeyboardButton("❓ اسأل الذكاء الاصطناعي", callback_data="ask_ai")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_programs_menu(self) -> InlineKeyboardMarkup:
        """إنشاء قائمة البرامج"""
        keyboard = [
            [InlineKeyboardButton("1️⃣ برنامج الحفظ الجماعي", callback_data="program_group")],
            [InlineKeyboardButton("2️⃣ برنامج الحفظ المكثف", callback_data="program_intensive")],
            [InlineKeyboardButton("3️⃣ برنامج الحفظ الفردي", callback_data="program_individual")],
            [InlineKeyboardButton("4️⃣ برنامج الحفظ والمراجعة", callback_data="program_review")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_paths_menu(self) -> InlineKeyboardMarkup:
        """إنشاء قائمة المسارات"""
        keyboard = [
            [InlineKeyboardButton("1️⃣ مسار القراءة والكتابة", callback_data="path_reading")],
            [InlineKeyboardButton("2️⃣ مسار الحفظ الجديد", callback_data="path_memorization")],
            [InlineKeyboardButton("3️⃣ مسار التثبيت (السرد)", callback_data="path_consolidation")],
            [InlineKeyboardButton("4️⃣ مسار الإجازات", callback_data="path_ijazah")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_back_menu(self) -> InlineKeyboardMarkup:
        """إنشاء قائمة العودة"""
        keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]]
        return InlineKeyboardMarkup(keyboard)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /start"""
        user = update.effective_user
        welcome_message = f"""
🌟 أهلاً وسهلاً بك {user.first_name} في أكاديمية الماهرون! 🌟

📚 نحن متخصصون في تعليم وتحفيظ القرآن الكريم لجميع الفئات العمرية

🤖 أنا مساعدك الذكي، يمكنني مساعدتك في:
✅ التعرف على برامج الأكاديمية
✅ معرفة أنظمة الاشتراك والأسعار
✅ الإجابة على استفساراتك
✅ مساعدتك في التسجيل

اختر ما تريد معرفته من القائمة أدناه:
        """
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=self.create_main_menu()
        )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار التفاعلية"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "main_menu":
            await query.edit_message_text(
                "🏠 القائمة الرئيسية:\nاختر ما تريد معرفته:",
                reply_markup=self.create_main_menu()
            )
            
        elif data == "academy_info":
            await query.edit_message_text(
                ACADEMY_INFO,
                reply_markup=self.create_back_menu()
            )
            
        elif data == "programs":
            await query.edit_message_text(
                "💠 البرامج التعليمية المتاحة:\nاختر البرنامج للتفاصيل:",
                reply_markup=self.create_programs_menu()
            )
            
        elif data == "paths":
            await query.edit_message_text(
                "🧭 المسارات التعليمية المتوفرة:\nاختر المسار للتفاصيل:",
                reply_markup=self.create_paths_menu()
            )
            
        elif data == "pricing":
            await query.edit_message_text(
                PRICING_PLANS,
                reply_markup=self.create_back_menu()
            )
            
        elif data == "contact":
            await query.edit_message_text(
                CONTACT_INFO,
                reply_markup=self.create_back_menu()
            )
            
        elif data == "ask_ai":
            self.user_sessions[query.from_user.id] = {"mode": "ai_chat"}
            await query.edit_message_text(
                "🤖 مرحباً! أنا الذكاء الاصطناعي لأكاديمية الماهرون\n\n"
                "يمكنك سؤالي عن أي شيء متعلق بالأكاديمية:\n"
                "• البرامج والمسارات\n"
                "• الأسعار والاشتراكات\n"
                "• طرق التسجيل\n"
                "• أي استفسار آخر\n\n"
                "اكتب سؤالك وسأجيبك فور<|im_start|>! 💬",
                reply_markup=self.create_back_menu()
            )

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل النصية"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # التحقق من وضع المحادثة مع الذكاء الاصطناعي
        if user_id in self.user_sessions and self.user_sessions[user_id].get("mode") == "ai_chat":
            await update.message.reply_text("🤖 جاري البحث عن الإجابة...")
            
            # توليد الرد من Gemini
            response = await self.gemini_manager.generate_response(
                message_text, 
                ACADEMY_INFO + "\n" + PRICING_PLANS + "\n" + CONTACT_INFO
            )
            
            await update.message.reply_text(
                response,
                reply_markup=self.create_back_menu()
            )
        else:
            # رد افتراضي للرسائل العادية
            await update.message.reply_text(
                "مرحباً! 👋\n\n"
                "لاستخدام البوت، اضغط /start أو اختر من القائمة أدناه:",
                reply_markup=self.create_main_menu()
            )

    def run(self):
        """تشغيل البوت"""
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            logger.error("❌ لم يتم العثور على TELEGRAM_BOT_TOKEN")
            return
        
        # إنشاء التطبيق
        application = Application.builder().token(token).build()
        
        # إضافة المعالجات
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CallbackQueryHandler(self.button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
        
        logger.info("🚀 بدء تشغيل بوت أكاديمية الماهرون...")
        
        # تشغيل البوت
        application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    bot = MahareenBot()
    bot.run()
