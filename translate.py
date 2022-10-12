from deep_translator import GoogleTranslator
from deep_translator.exceptions import LanguageNotSupportedException


def translate(text, target="english"):
    try:
        translator = GoogleTranslator(source="auto", target=target)
    except LanguageNotSupportedException:
        return "Invalid target language"

    return translator.translate(text)

