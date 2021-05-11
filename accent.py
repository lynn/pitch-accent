# Drop this file next to me:
# https://raw.githubusercontent.com/javdejong/nhk-pronunciation/master/ACCDB_unicode.csv
# https://raw.githubusercontent.com/davidluzgouveia/kanji-data/master/kanji.json

from collections import defaultdict
from dataclasses import dataclass
from jaconv import alphabet2kata, hira2kata, kata2alphabet
from os import path
import csv
import itertools
import json
import re
import sys
import unicodedata

all_kana = re.compile('^[\u3040-\u30ff]+$')
all_katakana = re.compile('^[\u30a0-\u30ff]+$')

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

def unchoonpu(kana):
    last = None
    result = []
    for k in kana:
        if k == 'ー':
            is_u = last in 'ョュ' or kata2alphabet(last)[-1:] in 'ou'
            result.append('ウ' if is_u else 'イ')
        else:
            result.append(k)
        last = k
    return ''.join(result)

def normalize_reading(kana):
    kana = unchoonpu(kana)
    # Completely throw away voicedness info, to more-than-undo rendaku.
    kana = unicodedata.normalize('NFKD', kana)
    kana = kana.replace('ッ', 'ツ')
    kana = kana.replace('\N{combining katakana-hiragana voiced sound mark}', '')
    kana = kana.replace('\N{combining katakana-hiragana semi-voiced sound mark}', '')
    return kana

def predict_kango_readings(kanji):
    ons = (onyomi.get(k, [k]) for k in kanji)
    return (hira2kata(''.join(t)) for t in itertools.product(*(ons)))

kango_readings = defaultdict(list)
wago_readings = defaultdict(list)
with open('nhk-pronunciation/ACCDB_unicode.csv') as f:
    for row in csv.reader(f):
        kanji = row[6]
        kana = row[-4]
        accent = row[-1].zfill(len(kana))
        morae = to_morae(kana, accent)
        nr = normalize_reading(kana)
        prs = list(map(normalize_reading, predict_kango_readings(kanji)))
        has_kanji = not all_kana.match(kanji)

        if nr in prs and has_kanji:
            kango_readings[kanji].append(morae)
            # print('Kango:', kanji, kana)
        elif not all_katakana.match(kanji):
            wago_readings[kanji].append(morae)
            # print('Wago:', kanji, kana)

def show_morae(morae):
    kana = ''.join(x.kana for x in morae)
    return f'{kana}【{accent_number(morae)}】'

import random
for name, r in [('kango', kango_readings), ('wago', wago_readings)]:
    print(f"Random words I think are {name}:")
    for k, v in random.sample(list(r.items()), 10): print(k, show_morae(v[0]))
    print()

