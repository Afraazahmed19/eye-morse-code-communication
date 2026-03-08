# utils.py
MORSE_CODE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z',
   
}


def decode_morse_sequence(letter_list):
    """letter_list: ['.-','...'] -> decode to string. Unknown -> '?'"""
    out = ''
    for seq in letter_list:
        out += MORSE_CODE_DICT.get(seq, '?')
    return out


def morse_letters_to_text(words_list):
    """words_list: list of lists e.g. [['...','---','...'], ['.--','.']] -> 'SOS WE'"""
    words = []
    for letters in words_list:
        words.append(decode_morse_sequence(letters))
    return ' '.join(words)
