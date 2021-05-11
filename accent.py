# Drop this file next to me:
# https://raw.githubusercontent.com/javdejong/nhk-pronunciation/master/ACCDB_unicode.csv
# https://raw.githubusercontent.com/davidluzgouveia/kanji-data/master/kanji.json

from collections import defaultdict
from dataclasses import dataclass
from jaconv import hira2kata
from os import path
import csv
import itertools
import json
import sys
import unicodedata

if not path.exists('kanji-data/kanji.json'):
    sys.exit('Run `git submodule update --init` first.')

with open('kanji-data/kanji.json') as f:
    onyomi = {k: v['readings_on'] for k, v in json.load(f).items()}

@dataclass
class Mora:
    '''A pitched mora, like キョ0.'''
    kana: str
    pitch: str  # '0' low, '1' high, '2' nucleus
    def __repr__(self):
        return self.kana + self.pitch

def to_morae(kana, accent):
    '''Turn ("キョーイク", "00111") into [キョ0, ー1, イ1, ク1].'''
    assert len(kana) == len(accent)
    morae = []
    maccent = []
    for k, a in zip(kana, accent):
        if k in 'ャョュァェィォゥ':
            morae[-1] += k
            maccent[-1] += a
        elif k not in '・':
            morae.append([k])
            maccent.append([a])
    return [Mora(''.join(k), max(a)) for k, a in zip(morae, maccent)]

def accent_number(morae):
    '''Return 0 for heiban, 1 for atamadaka, etc.'''
    return 1 + ''.join(m.pitch for m in morae).find('2')

def normalize_reading(kana):
    return unicodedata.normalize('NFC', kana).translate({
        'ッ': 'ツ',
        '\N{combining katakana-hiragana voiced sound mark}': '',
        '\N{combining katakana-hiragana semi-voiced sound mark}': '',
    })

def predict_kango_readings(kanji):
    ons = (onyomi.get(k, []) for k in kanji)
    return (hira2kata(''.join(t)) for t in itertools.product(*(ons)))

readings = defaultdict(list)
with open('nhk-pronunciation/ACCDB_unicode.csv') as f:
    for row in csv.reader(f):
        kanji = row[6]
        kana = row[-4]
        accent = row[-1].zfill(len(kana))
        morae = to_morae(kana, accent)
        # print(kanji, morae, accent_number(morae))
        if normalize_reading(kana) in map(normalize_reading, predict_kango_readings(kanji)):
            print('Kango:', kanji, kana)
        readings[kanji].append(morae)

