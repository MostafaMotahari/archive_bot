from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import BotUser, Statistics
from database.engine import engine


@Client.on_message(filters.private & (filters.regex("^/start$") | filters.regex("^↩️ بازگشت به منوی قبل$")))
def start_message(client: Client, message: Message):
    with Session(engine) as session:
        if not session.scalar(select(BotUser).where(BotUser.user_id == message.from_user.id)):
            bot_user = BotUser(user_id=message.from_user.id)
            session.add(bot_user)

            bot_statistics: Statistics = session.scalar(select(Statistics).where(Statistics.id == 1))
            bot_statistics.users_count += 1
            session.commit()

    if message.text == "/start":
        client.send_message(
            message.chat.id,
            "سلام 🖐\n"
            "من پسر موسیول ام.\n"
            "میتونی آرشیو جزوات درسی و تمام رفرنس های ترم رو از من بگیری😄\n"
            "رشتت رو انتخاب کن و فایل های آپلود شده رو دریافت کن ✅\n\n"
            "❗️نکته: دوستان حواستون باشه، همه ی این منابع فقط و فقط با کمک شما رشد پیدا میکنن و کامل میشن. پس اگه جزوه ای دارید که فکر میکنید میتونه برای بقیه مفید باشه، از طریق دکمه ی ارسال جزوه اونو برامون ارسال کنید تا در اختیار همه قرار بگیره. بیاید به رشد فرهنگ اوپن سورس تو جامعه کمک کنیم❤️\n\n"
            "بزن بریم ....\n",
            reply_markup=ReplyKeyboardMarkup(
                [
                    [KeyboardButton("📖 لیست رشته ها 📖")],
                    [KeyboardButton("📓ارسال جزوه📓")]
                ],
                resize_keyboard=True
            )
        )
    else:
        client.send_message(
            message.chat.id,
            "◀️ به منوی اصلی بازگشتید:",
            reply_markup=ReplyKeyboardMarkup(
                [
                    [KeyboardButton("📖 لیست رشته ها 📖")],
                    [KeyboardButton("📓ارسال جزوه📓")]
                ],
                resize_keyboard=True
            )
        )



@Client.on_message(filters.private & filters.regex("^📓ارسال جزوه📓$"))
def send_doc_help_text(client: Client, message: Message):
    message.reply_text(
        "📓فلسفه اپن سورس میگه که \"دسترسی به منابع باید برای همه آزاد باشه در عین حالی که خود افراد به رشد و تکاملش کمک میکنن.\"\n\n"
        "خیلی ممنون از اینکه قصد داری جزوه ای که در اختیار داری رو اینجا قرار بدی دوستات هم بتونن استفاده کنن ❤️\n\n"
        "👇 برای فرستادن جزوه اینطوری عمل کن:\n"
        "1️⃣ اول جزوه ات رو همینجا در قالب یه فایل pdf یا rar یا zip و... بفرست.\n"
        "2️⃣ حالا کافیه روی جزوه ریپلای کنی و دستور /send_doc رو بفرستی (توی منوی سمت چپ هم هست).\n\n"
        "☑️ تمام! جزوه ات برای ما ارسال شد و توی آرشیو قرار میگیره. دَمِدَم گرم 🫶"
    )
