import os
import re
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# 1. قراءة التوكن والـ ID من متغيرات البيئة (أو وضعهم مباشرة)
TOKEN = os.environ.get("TOKEN", "8813617570:AAE53Jh5NdKfvlcmR1OkFTokzBLgJKsogx0")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "5978710701"))

bot = telebot.TeleBot(TOKEN)
user_states = {}


# --- أزرار القوائم (Keyboard Helper Functions) ---


# القائمة الرئيسية
def get_main_menu_markup():
  markup = InlineKeyboardMarkup()
  btn_deposit = InlineKeyboardButton(
      "💳 مشكلة في الإيداع", callback_data="deposit_issue"
  )
  btn_withdraw = InlineKeyboardButton(
      "🏧 مشكلة في السحب", callback_data="withdraw_issue"
  )
  btn_admin = InlineKeyboardButton(
      "👨‍💼 تواصل مع الأدمن", callback_data="contact_admin"
  )

  markup.add(btn_deposit)
  markup.add(btn_withdraw)
  markup.add(btn_admin)
  return markup


# زر الرجوع أو إعادة التشغيل (Start)
def get_back_button_markup():
  markup = InlineKeyboardMarkup()
  # زر للرجوع خطوة أو للقائمة الرئيسية
  btn_back = InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")
  # زر Start لفتح البوت من أول وجديد
  btn_start = InlineKeyboardButton("🏠 القائمة الرئيسية (Start)", callback_data="start_over")
  
  markup.add(btn_back, btn_start)
  return markup


# --- المعالجات (Handlers) ---


# أمر /start الأساسي (عند كتابة /start في الشات)
@bot.message_handler(commands=["start"])
def send_welcome(message):
  user_states[message.chat.id] = None  # إعادة ضبط حالة المستخدم
  welcome_text = (
      f"أهلاً بك يا {message.from_user.first_name} في بوت الدعم الفني! 👋\n\n"
      "كيف يمكننا مساعدتك اليوم؟ يرجى اختيار المشكلة من الأزرار أدناه:"
  )
  bot.send_message(
      message.chat.id, welcome_text, reply_markup=get_main_menu_markup()
  )


# التعامل مع ضغطات الأزرار (Callback Queries)
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
  chat_id = call.message.chat.id
  message_id = call.message.message_id

  # 🏠 1. عند الضغط على زر "القائمة الرئيسية (Start)"
  if call.data == "start_over" or call.data == "main_menu":
    user_states[chat_id] = None  # إلغاء أية حالة إرسال رسالة للأدمن
    welcome_text = (
        f"أهلاً بك يا {call.from_user.first_name} من جديد! 👋\n\n"
        "كيف يمكننا مساعدتك اليوم؟ يرجى اختيار المشكلة من الأزرار أدناه:"
    )
    # تعديل نفس الرسالة لتظهر القائمة الرئيسية من جديد
    bot.edit_message_text(
        welcome_text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=get_main_menu_markup(),
    )
    bot.answer_callback_query(call.id, "تم العودة للقائمة الرئيسية 🏠")

  # 💳 2. مشكلة في الإيداع
  elif call.data == "deposit_issue":
    user_states[chat_id] = None
    response_text = (
        "📌 **حلول مشاكل الإيداع:**\n\n"
        "1. تأكد من إرسال المبلغ الدقيق المطلوب.\n"
        "2. تستغرق التأكيدات عادة من 5 إلى 15 دقيقة.\n"
        "3. في حال لم يصل الإيداع، تواصل مع الإدارة."
    )
    bot.edit_message_text(
        response_text,
        chat_id=chat_id,
        message_id=message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button_markup(),
    )
    bot.answer_callback_query(call.id)

  # 🏧 3. مشكلة في السحب
  elif call.data == "withdraw_issue":
    user_states[chat_id] = None
    response_text = (
        "📌 **حلول مشاكل السحب:**\n\n"
        "1. تأكد من صحة عنوان المحفظة أو الحساب.\n"
        "2. تتم معالجة طلبات السحب خلال 10 دقائق إلى ساعتين.\n"
        "3. إذا تجاوزت المدة، يمكنك مراسلة الإدارة."
    )
    bot.edit_message_text(
        response_text,
        chat_id=chat_id,
        message_id=message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button_markup(),
    )
    bot.answer_callback_query(call.id)

  # 👨‍💼 4. تواصل مع الأدمن
  elif call.data == "contact_admin":
    user_states[chat_id] = "waiting_for_admin_msg"
    response_text = (
        "✍️ **تفضل بكتابة رسالتك أو استفسارك الآن:**\n\n"
        "سيتم تحويل رسالتك مباشرة للإدارة وسنرد عليك بداخل البوت.\n\n"
        "*(للإلغاء والعودة اضغط على زر القائمة الرئيسية أدناه)*"
    )
    bot.edit_message_text(
        response_text,
        chat_id=chat_id,
        message_id=message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button_markup(),
    )
    bot.answer_callback_query(call.id)


# استقبال الرسائل
@bot.message_handler(
    func=lambda m: True, content_types=["text", "photo", "document"]
)
def handle_messages(message):
  user_id = message.chat.id

  # رد الأدمن على المستخدمين
  if user_id == ADMIN_ID and message.reply_to_message:
    try:
      original_text = (
          message.reply_to_message.text or message.reply_to_message.caption or ""
      )
      match = re.search(r"ID:\s*(\d+)", original_text)

      if match:
        target_user_id = int(match.group(1))

        if message.text:
          bot.send_message(
              target_user_id,
              f"👨‍💼 **رد من الإدارة:**\n\n{message.text}",
              parse_mode="Markdown",
          )
        elif message.photo:
          bot.send_photo(
              target_user_id,
              message.photo[-1].file_id,
              caption=(
                  f"👨‍💼 **رد من الإدارة:**\n\n"
                  f"{message.caption if message.caption else ''}"
              ),
          )

        bot.reply_to(message, "✅ تم إرسال ردك للمستخدم بنجاح.")
      else:
        bot.reply_to(
            message, "❌ لم نتمكن من التعرف على ID المستخدم في هذه الرسالة."
        )
    except Exception as e:
      bot.reply_to(message, f"❌ حدث خطأ أثناء إرسال الرد: {e}")
    return

  # رسالة المستخدم الموجهة للأدمن
  if user_states.get(user_id) == "waiting_for_admin_msg":
    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "لا يوجد"
    )
    user_name = message.from_user.first_name

    admin_msg_text = (
        f"📩 **رسالة جديدة من مستخدم:**\n\n"
        f"👤 **الاسم:** {user_name}\n"
        f"🏷 **المعرف:** {username}\n"
        f"🆔 **ID:** `{user_id}`\n\n"
        f"💬 **الرسالة:**\n{message.text if message.text else '(صورة/ملف)'}\n\n"
        f"👇 *للرد، قم بعمل (Reply / رد) على هذه الرسالة.*"
    )

    try:
      if message.text:
        bot.send_message(ADMIN_ID, admin_msg_text, parse_mode="Markdown")
      elif message.photo:
        bot.send_photo(
            ADMIN_ID,
            message.photo[-1].file_id,
            caption=admin_msg_text,
            parse_mode="Markdown",
        )

      bot.reply_to(
          message,
          "✅ **تم إرسال رسالتك بنجاح للإدارة!**\nسيصلك الرد هنا فور مراجعته.",
          reply_markup=get_main_menu_markup(),
      )
      user_states[user_id] = None
    except Exception as e:
      bot.reply_to(
          message, "❌ حدث خطأ أثناء إرسال رسالتك، يرجى المحاولة لاحقاً."
      )

  else:
    bot.reply_to(
        message,
        "يرجى اختيار إحدى الخدمات من القائمة أو الضغط على /start للبدء.",
        reply_markup=get_main_menu_markup(),
    )


# تشغيل البوت
bot.infinity_polling()