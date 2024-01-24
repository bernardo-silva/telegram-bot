import datetime

# from urllib.request import urlopen
# import requests
import logging

# from pydub import AudioSegment

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, PicklePersistence

from enfs import enfs
from mbway import fetch_prize_table, mbway
from translate import translate

logging.basicConfig(filename="bot_log.log", encoding="utf-8", level=logging.INFO)


async def send_enfs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = enfs()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def send_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    replied_to = update.message.reply_to_message
    if replied_to is None:
        update.message.reply_text(
            "You have to reply to a message for me to translate",
            reply_to_message_id=update.message.message_id,
        )
        return

    text = ""
    if replied_to.text is not None and replied_to.text:
        text = replied_to.text
    elif replied_to.caption is not None and replied_to.caption:
        text = replied_to.caption
    # elif replied_to.question is not None and replied_to.question:
    # text = replied_to.question

    message = ""
    if text:
        if context.args:
            message = translate(text, context.args[0])
        else:
            message = translate(text)

    if "Hoje:" in text:
        message = f"{update.message.from_user.first_name}, outra vez?\n\n" + message

    await replied_to.reply_text(
        message or "Invalid message", reply_to_message_id=replied_to.message_id
    )


async def send_dadjoke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = f"Já chega, {update.message.from_user.first_name}"
    # message = requests.get("https://icanhazdadjoke.com/",
    # headers={"Accept": "text/plain"}).text
    # message = message.encode("ISO-8859-1").decode()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def send_mbway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = datetime.datetime.now()
    if context.args and context.args[0].lower() in ["amanhã", "amanha", "tomorrow"]:
        date += datetime.timedelta(days=1)
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)

    message = mbway(date)
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message, parse_mode="MarkdownV2"
    )


async def send_mbway_notification(context: ContextTypes.DEFAULT_TYPE):
    job = context.job

    message = ""
    try:
        fetch_prize_table()
    except Exception as e:
        message = "Erro a carregar tabela de prémios.\n"
        logging.error(f"Error fetching prize table: {e}")

    message += mbway(datetime.datetime.now())
    logging.info(f"Sending message to {job.chat_id}: {message}")
    await context.bot.send_message(chat_id=job.chat_id, text=message)


async def setup_notify_mbway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    logging.info(f"Setting up notifications for {chat_id}")
    jobs_in_queue = context.job_queue.get_jobs_by_name(str(chat_id))
    logging.info(f"Jobs in queue: {jobs_in_queue}")

    if jobs_in_queue:
        message = "Notificações já ativadas."
        await context.bot.send_message(chat_id=chat_id, text=message)
        return

    t = datetime.time(
        0, 00, 10, 000000, tzinfo=datetime.timezone(datetime.timedelta(hours=1))
    )
    job = context.job_queue.run_daily(
        send_mbway_notification,
        t,
        chat_id=chat_id,
        days=tuple(range(7)),
        name=str(chat_id),
    )

    context.bot_data["jobs"]["mbway"].append(chat_id)

    message = "Notificações diárias de MbWay ativadas."
    await context.bot.send_message(chat_id=chat_id, text=message)

    logging.info(f"Job created: {job}")


async def restore_jobs(context: ContextTypes.DEFAULT_TYPE):
    if context.bot_data.get("jobs") is None:
        context.bot_data["jobs"] = {"mbway": []}
        return

    if context.bot_data["jobs"].get("mbway") is None:
        context.bot_data["jobs"]["mbway"] = []
        return

    for chat_id in context.bot_data["jobs"]["mbway"]:
        t = datetime.time(
            0, 00, 10, 000000, tzinfo=datetime.timezone(datetime.timedelta(hours=1))
        )
        job = context.job_queue.run_daily(
            send_mbway_notification,
            t,
            chat_id=chat_id,
            days=tuple(range(7)),
            name=str(chat_id),
        )
        logging.info(f"Job created: {job} for chat {chat_id}")


def main():
    with open("token.txt", "r") as f:
        token = f.read().strip()

    persistence = PicklePersistence(filepath="bot_data")
    application = Application.builder().token(token).persistence(persistence).build()

    application.job_queue.run_once(restore_jobs, 0)

    # esperanto_handler = CommandHandler("esperanto", send_esperanto)
    # application.add_handler(esperanto_handler)

    enfs_handler = CommandHandler("enfs", send_enfs)
    application.add_handler(enfs_handler)

    translate_handler = CommandHandler("translate", send_translate)
    application.add_handler(translate_handler)

    dadjoke_handler = CommandHandler("dadjoke", send_dadjoke)
    application.add_handler(dadjoke_handler)

    mbway_handler = CommandHandler("mbway", send_mbway)
    application.add_handler(mbway_handler)

    mbway_notify_handler = CommandHandler("mbwaynotify", setup_notify_mbway)
    application.add_handler(mbway_notify_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
