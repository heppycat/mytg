import asyncio
import json
import logging
import urllib.parse
import urllib.request

from telethon import TelegramClient, events

from .base import Behavior

logger = logging.getLogger(__name__)

# Google Translate language codes, keyed by lowercase name.
# Aliases (farsi, mandarin, etc.) are listed after the canonical entries.
LANG_MAP: dict[str, str] = {
    "afrikaans": "af",
    "albanian": "sq",
    "amharic": "am",
    "arabic": "ar",
    "armenian": "hy",
    "azerbaijani": "az",
    "basque": "eu",
    "belarusian": "be",
    "bengali": "bn",
    "bosnian": "bs",
    "bulgarian": "bg",
    "catalan": "ca",
    "cebuano": "ceb",
    "chinese": "zh-CN",
    "chinese simplified": "zh-CN",
    "chinese traditional": "zh-TW",
    "corsican": "co",
    "croatian": "hr",
    "czech": "cs",
    "danish": "da",
    "dutch": "nl",
    "english": "en",
    "esperanto": "eo",
    "estonian": "et",
    "filipino": "tl",
    "finnish": "fi",
    "french": "fr",
    "frisian": "fy",
    "galician": "gl",
    "georgian": "ka",
    "german": "de",
    "greek": "el",
    "gujarati": "gu",
    "haitian creole": "ht",
    "hausa": "ha",
    "hawaiian": "haw",
    "hebrew": "he",
    "hindi": "hi",
    "hmong": "hmn",
    "hungarian": "hu",
    "icelandic": "is",
    "igbo": "ig",
    "indonesian": "id",
    "irish": "ga",
    "italian": "it",
    "japanese": "ja",
    "javanese": "jv",
    "kannada": "kn",
    "kazakh": "kk",
    "khmer": "km",
    "kinyarwanda": "rw",
    "korean": "ko",
    "kurdish": "ku",
    "kyrgyz": "ky",
    "lao": "lo",
    "latin": "la",
    "latvian": "lv",
    "lithuanian": "lt",
    "luxembourgish": "lb",
    "macedonian": "mk",
    "malagasy": "mg",
    "malay": "ms",
    "malayalam": "ml",
    "maltese": "mt",
    "maori": "mi",
    "marathi": "mr",
    "mongolian": "mn",
    "burmese": "my",
    "myanmar": "my",
    "nepali": "ne",
    "norwegian": "no",
    "nyanja": "ny",
    "odia": "or",
    "pashto": "ps",
    "persian": "fa",
    "polish": "pl",
    "portuguese": "pt",
    "punjabi": "pa",
    "romanian": "ro",
    "russian": "ru",
    "samoan": "sm",
    "scots gaelic": "gd",
    "serbian": "sr",
    "sesotho": "st",
    "shona": "sn",
    "sindhi": "sd",
    "sinhala": "si",
    "slovak": "sk",
    "slovenian": "sl",
    "somali": "so",
    "spanish": "es",
    "sundanese": "su",
    "swahili": "sw",
    "swedish": "sv",
    "tajik": "tg",
    "tamil": "ta",
    "tatar": "tt",
    "telugu": "te",
    "thai": "th",
    "turkish": "tr",
    "turkmen": "tk",
    "ukrainian": "uk",
    "urdu": "ur",
    "uyghur": "ug",
    "uzbek": "uz",
    "vietnamese": "vi",
    "welsh": "cy",
    "xhosa": "xh",
    "yiddish": "yi",
    "yoruba": "yo",
    "zulu": "zu",
    # aliases
    "farsi": "fa",
    "mandarin": "zh-CN",
    "tagalog": "tl",
    "bangla": "bn",
}

_CODE_TO_NAME: dict[str, str] = {}
for _name, _code in LANG_MAP.items():
    if _code not in _CODE_TO_NAME:
        _CODE_TO_NAME[_code] = _name.capitalize()


def _translate(text: str, target: str) -> tuple[str, str]:
    """Returns (translated_text, detected_source_lang_code)."""
    url = (
        "https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl=auto&tl={target}&dt=t&q={urllib.parse.quote(text)}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
    translated = "".join(part[0] for part in data[0] if part[0])
    detected = data[2] if len(data) > 2 else "unknown"
    return translated, detected


class TranslateBehavior(Behavior):
    def register(self, client: TelegramClient) -> None:
        @client.on(events.NewMessage(outgoing=True, pattern=r"^!tr\s+(.+)$"))
        async def handler(event: events.NewMessage.Event) -> None:
            lang_input = event.pattern_match.group(1).strip().lower()
            target_code = LANG_MAP.get(lang_input)

            if target_code is None:
                await event.edit(f"Unknown language '{lang_input}'.")
                return

            if not event.reply_to_msg_id:
                await event.edit("Reply to a message to translate it.")
                return

            replied = await event.get_reply_message()
            text = getattr(replied, "text", None) or getattr(replied, "message", None)

            if not text:
                await event.edit("No text to translate.")
                return

            try:
                translated, source_code = await asyncio.to_thread(_translate, text, target_code)
            except Exception as e:
                logger.error("Translation failed: %s", e)
                await event.edit("[Translation failed]")
                return

            target_name = _CODE_TO_NAME.get(target_code, target_code.upper())

            if source_code == target_code:
                await event.edit(f"[Already in {target_name}]")
                return

            source_name = _CODE_TO_NAME.get(source_code, source_code.upper())
            await event.edit(f"[{source_name} → {target_name}]\n{translated}")
