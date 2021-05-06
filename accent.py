# Drop this file next to me:
# https://raw.githubusercontent.com/javdejong/nhk-pronunciation/master/ACCDB_unicode.csv

import csv
from collections import defaultdict
from dataclasses import dataclass

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

readings = defaultdict(list)
with open('ACCDB_unicode.csv') as f:
    for row in csv.reader(f):
        kanji = row[6]
        kana = row[-4]
        accent = row[-1].zfill(len(kana))
        morae = to_morae(kana, accent)
        print(kanji, morae, accent_number(morae))
        readings[kanji].append(morae)

