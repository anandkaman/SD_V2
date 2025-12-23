import re
import unicodedata
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate


# -------------------------------
# Core transliterator (v2 - STABLE)
# -------------------------------

# IAST consonant → ASCII-friendly mapping
IAST_CONSONANT_MAP = str.maketrans({
    "ś": "sh",
    "ṣ": "sh",
    "ṭ": "t",
    "ḍ": "d",
    "ṇ": "n",
    "ṅ": "ng",
    "ñ": "ny",
    "ḻ": "l",
})


def kannada_to_english(text: str) -> str:
    """
    Kannada → human-readable ASCII (Roman Kannada style).

    Pipeline:
      1) Kannada → IAST (library)
      2) Consonant mapping (ś/ṣ/ṭ/ḍ/ṇ/ṅ/ñ/ḻ → sh/t/d/n/ng/ny/l)
      3) Anusvāra stabilization (ṃ → class nasal)
      4) Word-level pass (no trailing-a hacks)
      5) Strip diacritics (NFKD + drop combining marks)
      6) Whitespace cleanup

    NOTE:
    - Does NOT modify English or numbers
    - Safe for mixed Kannada + English text
    """
    if not text or not isinstance(text, str):
        return text

    # 1️ Kannada → IAST
    iast = transliterate(text, sanscript.KANNADA, sanscript.IAST)

    # 2️ Consonant normalization
    iast = iast.translate(IAST_CONSONANT_MAP)

    # 3️ Minimal anusvāra stabilization
    iast = re.sub(r'ṃ(?=[kg])', 'ng', iast)   # velars
    iast = re.sub(r'ṃ(?=[cj])', 'ny', iast)   # palatals
    iast = re.sub(r'ṃ(?=[ṭḍ])', 'n', iast)    # retroflex
    iast = re.sub(r'ṃ(?=[td])', 'n', iast)    # dentals
    iast = re.sub(r'ṃ(?=[pb])', 'm', iast)    # labials
    iast = iast.replace('ṃ', 'm')             # fallback

    # 4️ Word-level pass (kept explicit for future hooks)
    fixed_iast = " ".join(iast.split())

    # 5️ Remove diacritics → ASCII
    ascii_text = unicodedata.normalize("NFKD", fixed_iast)
    ascii_text = "".join(c for c in ascii_text if not unicodedata.combining(c))

    # 6️ Clean spacing
    ascii_text = re.sub(r'\s+', ' ', ascii_text).strip()

    return ascii_text


# -------------------------------
# Optional display formatter
# -------------------------------

def format_for_display(text: str) -> str:
    """
    Optional UI-level formatter.
    Not used in DB pipeline unless explicitly called.
    """
    if not text or not isinstance(text, str):
        return text
    return text.title()


def transliterate_json_fields(data):
    """
    Recursively transliterate all string values in a nested dict/list from Kannada → Roman.
    """
    if isinstance(data, dict):
        return {k: transliterate_json_fields(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [transliterate_json_fields(item) for item in data]
    elif isinstance(data, str):
        return kannada_to_english(data)
    else:
        return data

