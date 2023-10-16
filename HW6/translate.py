import re

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ" + "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ".upper()
TRANSLATION = (
    "a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k",
    "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "ts",
    "ch", "sh", "sch", "", "y", "", "e", "yu", "ja", "je", "i", "ji", "g"
) + (
    "A", "B", "V", "G", "D", "E", "E", "J", "Z", "I", "J", "K",
    "L", "M", "N", "O", "P", "R", "S", "T", "U", "F", "H", "TS",
    "CH", "SH", "SCH", "", "Y", "", "E", "YU", "JA", "JE", "I", "JI", "G"
)

TRANS = dict(zip(CYRILLIC_SYMBOLS, TRANSLATION))

def normalize(name: str) -> str:
    t_name = name.translate(TRANS)
    t_name = re.sub(r'[^a-zA-Z0-9]', '_', t_name)  # This regex replaces all characters except letters and numbers
    return t_name
