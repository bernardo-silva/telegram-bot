from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from esperanto import esperanto
from enfs import enfs
from translate import translate
from pydub import AudioSegment
import tempfile
from urllib.request import urlopen


def escape_chars(text):
    reserved_chars = '''?&|!{}[]()^~:\\"'+-.'''

    mapper = ['\\' + ele for ele in reserved_chars]
    result_mapping = str.maketrans(dict(zip(reserved_chars, mapper)))
    return text.translate(result_mapping)


def send_esperanto(update: Update, context: CallbackContext):
    data = esperanto()
    month, day, year = data["date"].split("-")
    date = "-".join([day, month, year])

    message = f"""Esperanto Word of the Day ({date}): 
*{data["word"]}*
Word type: {data["wordtype"]}
Translation: *{data["translation"]}*
Example phrase: {data["fnphrase"]}
Example phrase translation: {data["enphrase"]}
"""
    message = escape_chars(message)

    wordmp3 = urlopen(data["wordsound"]).read()
    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.write(wordmp3)
        AudioSegment.from_mp3(f.name).export("word_audio.ogg", format="ogg")

    phrasemp3 = urlopen(data["phrasesound"]).read()
    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.write(phrasemp3)
        AudioSegment.from_mp3(f.name).export("phrase_audio.ogg", format="ogg")

    context.bot.send_message(
        chat_id=update.effective_chat.id, text=message, parse_mode='MarkdownV2')

    with open("word_audio.ogg", "rb") as f:
        context.bot.send_voice(chat_id=update.effective_chat.id,
                               voice=f,
                               caption="Word pronounciation")

    with open("phrase_audio.ogg", "rb") as f:
        context.bot.send_voice(chat_id=update.effective_chat.id,
                               voice=f,
                               caption="Phrase pronounciation",
                               filename="phrase")


def send_enfs(update: Update, context: CallbackContext):
    message = enfs()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def send_translate(update: Update, context: CallbackContext):
    replied_to = update.message.reply_to_message
    if replied_to is None:
        update.message.reply_text("You have to reply to a message for me to translate",
                                  reply_to_message_id=update.message.message_id)
        return
    if context.args:
        message = translate(replied_to.text, context.args[0])
    else:
        message = translate(replied_to.text)

    replied_to.reply_text(message, reply_to_message_id=replied_to.message_id)


def main():
    with open("token.txt", "r") as f:
        token = f.read().strip()

    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    esperanto_handler = CommandHandler("esperanto", send_esperanto)
    dispatcher.add_handler(esperanto_handler)

    enfs_handler = CommandHandler("enfs", send_enfs)
    dispatcher.add_handler(enfs_handler)

    translate_handler = CommandHandler("translate", send_translate)
    dispatcher.add_handler(translate_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
