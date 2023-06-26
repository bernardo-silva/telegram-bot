from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import PicklePersistence
from esperanto import esperanto
from enfs import enfs
from translate import translate
from mbway import mbway
import datetime
# from pydub import AudioSegment
import tempfile
# from urllib.request import urlopen
# import requests
import logging

logging.basicConfig(filename='bot_log.log', encoding='utf-8', level=logging.INFO)

def escape_chars(text):
    reserved_chars = '''?&|!{}[]()^~:\\"'+-.'''

    mapper = ['\\' + ele for ele in reserved_chars]
    result_mapping = str.maketrans(dict(zip(reserved_chars, mapper)))
    return text.translate(result_mapping)


# async def send_esperanto(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     data = esperanto()
#     month, day, year = data["date"].split("-")
#     date = "-".join([day, month, year])

#     message = f"""Esperanto Word of the Day ({date}):
# *{data["word"]}*
# Word type: {data["wordtype"]}
# Translation: *{data["translation"]}*
# Example phrase: {data["fnphrase"]}
# Example phrase translation: {data["enphrase"]}
# """
#     message = escape_chars(message)

#     wordmp3 = urlopen(data["wordsound"]).read()
#     with tempfile.NamedTemporaryFile(delete=True) as f:
#         f.write(wordmp3)
#         AudioSegment.from_mp3(f.name).export("word_audio.ogg", format="ogg")

#     phrasemp3 = urlopen(data["phrasesound"]).read()
#     with tempfile.NamedTemporaryFile(delete=True) as f:
#         f.write(phrasemp3)
#         AudioSegment.from_mp3(f.name).export("phrase_audio.ogg", format="ogg")

#     await context.bot.send_message(
#         chat_id=update.effective_chat.id, text=message, parse_mode='MarkdownV2')

#     with open("word_audio.ogg", "rb") as f:
#         await context.bot.send_voice(chat_id=update.effective_chat.id,
#                                      voice=f,
#                                      caption="Word pronounciation")

#     with open("phrase_audio.ogg", "rb") as f:
#         await context.bot.send_voice(chat_id=update.effective_chat.id,
#                                      voice=f,
#                                      caption="Phrase pronounciation",
#                                      filename="phrase")


async def send_enfs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = enfs()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def send_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    replied_to = update.message.reply_to_message
    if replied_to is None:
        update.message.reply_text("You have to reply to a message for me to translate",
                                  reply_to_message_id=update.message.message_id)
        return

    text = ""
    if replied_to.text is not None and replied_to.text:
        text = replied_to.text
    elif replied_to.caption is not None and replied_to.caption:
        text = replied_to.caption

    message = ""
    if text:
        if context.args:
            message = translate(text, context.args[0])
        else:
            message = translate(text)

    await replied_to.reply_text(message or "Invalid message",
                                reply_to_message_id=replied_to.message_id)


async def send_dadjoke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = f"Já chega, {update.message.from_user.first_name}"
    # message = requests.get("https://icanhazdadjoke.com/",
    # headers={"Accept": "text/plain"}).text
    #message = message.encode("ISO-8859-1").decode()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def send_mbway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = mbway(datetime.datetime.now())
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def setup_notify_mbway(update: Update, context:
                             ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    logging.info(f"Setting up notifications for {chat_id}")
    jobs_in_queue = context.job_queue.get_jobs_by_name(str(chat_id))
    logging.info(f"Jobs in queue: {jobs_in_queue}")

    if jobs_in_queue:
        message = "Notificações já ativadas."
        await context.bot.send_message(chat_id=chat_id, text=message)
        return


    t = datetime.time(0, 00, 10, 000000)
    job = context.job_queue.run_daily(send_mbway, t, chat_id=chat_id,
                                      days=tuple(range(7)), name=str(chat_id))

    context.user_data["jobs"]["mbway"].append(chat_id)

    message = "Notificações diárias de MbWay ativadas."
    await context.bot.send_message(chat_id=chat_id, text=message)

    logging.info(f"Job created: {job}")

def restore_jobs(context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("jobs") is None:
        context.user_data["jobs"] = {"mbway": []}
        return

    if context.user_data["jobs"].get("mbway") is None:
        context.user_data["jobs"]["mbway"] = []
        return

    for chat_id in context.user_data["jobs"]["mbway"]:
        t = datetime.time(0, 00, 10, 000000)
        job = context.job_queue.run_daily(send_mbway, t, chat_id=chat_id,
                                          days=tuple(range(7)), name=str(chat_id))
        logging.info(f"Job created: {job}")
    


def main():
    with open("token.txt", "r") as f:
        token = f.read().strip()
    
    persistence = PicklePersistence(filepath='bot_data')
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
