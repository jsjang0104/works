import json
import random
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'adjective.json'), 'r', encoding='utf-8') as f:
    ADJ_LIST = json.load(f)
with open(os.path.join(BASE_DIR, 'noun.json'), 'r', encoding='utf-8') as f:
    NOUN_LIST = json.load(f)

# ---------- 관사 변화표 ----------

ARTICLE = {
    'ein': {
        ('sg', 'masculine', 1): 'ein',    ('sg', 'masculine', 2): 'eines',  ('sg', 'masculine', 3): 'einem',  ('sg', 'masculine', 4): 'einen',
        ('sg', 'neutral',   1): 'ein',    ('sg', 'neutral',   2): 'eines',  ('sg', 'neutral',   3): 'einem',  ('sg', 'neutral',   4): 'ein',
        ('sg', 'feminine',  1): 'eine',   ('sg', 'feminine',  2): 'einer',  ('sg', 'feminine',  3): 'einer',  ('sg', 'feminine',  4): 'eine',
    },
    'dieser': {
        ('sg', 'masculine', 1): 'dieser', ('sg', 'masculine', 2): 'dieses', ('sg', 'masculine', 3): 'diesem', ('sg', 'masculine', 4): 'diesen',
        ('sg', 'neutral',   1): 'dieses', ('sg', 'neutral',   2): 'dieses', ('sg', 'neutral',   3): 'diesem', ('sg', 'neutral',   4): 'dieses',
        ('sg', 'feminine',  1): 'diese',  ('sg', 'feminine',  2): 'dieser', ('sg', 'feminine',  3): 'dieser', ('sg', 'feminine',  4): 'diese',
        ('pl', 'masculine', 1): 'diese',  ('pl', 'masculine', 2): 'dieser', ('pl', 'masculine', 3): 'diesen', ('pl', 'masculine', 4): 'diese',
        ('pl', 'neutral',   1): 'diese',  ('pl', 'neutral',   2): 'dieser', ('pl', 'neutral',   3): 'diesen', ('pl', 'neutral',   4): 'diese',
        ('pl', 'feminine',  1): 'diese',  ('pl', 'feminine',  2): 'dieser', ('pl', 'feminine',  3): 'diesen', ('pl', 'feminine',  4): 'diese',
    },
}

ARTICLE_KR = {'ein': '한', 'dieser': '이'}

# ---------- 형용사 어미 ----------

ADJ_WEAK = {  # der/dieser 뒤 약변화
    ('sg', 'masculine', 1): 'e',  ('sg', 'masculine', 2): 'en', ('sg', 'masculine', 3): 'en', ('sg', 'masculine', 4): 'en',
    ('sg', 'neutral',   1): 'e',  ('sg', 'neutral',   2): 'en', ('sg', 'neutral',   3): 'en', ('sg', 'neutral',   4): 'e',
    ('sg', 'feminine',  1): 'e',  ('sg', 'feminine',  2): 'en', ('sg', 'feminine',  3): 'en', ('sg', 'feminine',  4): 'e',
    ('pl', 'masculine', 1): 'en', ('pl', 'masculine', 2): 'en', ('pl', 'masculine', 3): 'en', ('pl', 'masculine', 4): 'en',
    ('pl', 'neutral',   1): 'en', ('pl', 'neutral',   2): 'en', ('pl', 'neutral',   3): 'en', ('pl', 'neutral',   4): 'en',
    ('pl', 'feminine',  1): 'en', ('pl', 'feminine',  2): 'en', ('pl', 'feminine',  3): 'en', ('pl', 'feminine',  4): 'en',
}

ADJ_MIXED = {  # ein 뒤 혼합변화
    ('sg', 'masculine', 1): 'er', ('sg', 'masculine', 2): 'en', ('sg', 'masculine', 3): 'en', ('sg', 'masculine', 4): 'en',
    ('sg', 'neutral',   1): 'es', ('sg', 'neutral',   2): 'en', ('sg', 'neutral',   3): 'en', ('sg', 'neutral',   4): 'es',
    ('sg', 'feminine',  1): 'e',  ('sg', 'feminine',  2): 'en', ('sg', 'feminine',  3): 'en', ('sg', 'feminine',  4): 'e',
}

# ---------- 의미 카테고리 ----------
# 카테고리: person, animal, food, place, object, body, nature, abstract

NOUN_CAT = {
    # 사람 (person)
    'Baby': 'person', 'Babysitter': 'person', 'Bekannte': 'person', 'Bruder': 'person',
    'Chef': 'person', 'Chefin': 'person', 'Ehefrau': 'person', 'Empfänger': 'person',
    'Erwachsene': 'person', 'Fan': 'person', 'Frau': 'person', 'Freund': 'person',
    'Freundin': 'person', 'Gast': 'person', 'Herr': 'person', 'Jugendliche': 'person',
    'Junge': 'person', 'Kind': 'person', 'Kollege': 'person', 'Kollegin': 'person',
    'Kunde': 'person', 'Kundin': 'person', 'Mädchen': 'person', 'Mann': 'person',
    'Mensch': 'person', 'Mitarbeiter': 'person', 'Mutter': 'person', 'Nachbar': 'person',
    'Nachbarin': 'person', 'Onkel': 'person', 'Partnerin': 'person', 'Person': 'person',
    'Rentner': 'person', 'Rentnerin': 'person', 'Schwester': 'person', 'Schülerin': 'person',
    'Student': 'person', 'Studentin': 'person', 'Tante': 'person', 'Tourist': 'person',
    'Touristin': 'person', 'Vater': 'person', 'Ärztin': 'person',
    # 동물 (animal)
    'Katze': 'animal', 'Pferd': 'animal', 'Tier': 'animal',
    # 음식/음료 (food)
    'Apfel': 'food', 'Banane': 'food', 'Birne': 'food', 'Bohne': 'food',
    'Brot': 'food', 'Brötchen': 'food', 'Butter': 'food', 'Ei': 'food',
    'Eis': 'food', 'Essen': 'food', 'Fisch': 'food', 'Fleisch': 'food',
    'Frühstück': 'food', 'Gemüse': 'food', 'Gericht': 'food', 'Getränk': 'food',
    'Hamburger': 'food', 'Hähnchen': 'food', 'Kaffee': 'food', 'Kakao': 'food',
    'Kartoffel': 'food', 'Käse': 'food', 'Kuchen': 'food', 'Marmelade': 'food',
    'Milch': 'food', 'Mineralwasser': 'food', 'Mittagessen': 'food', 'Nudel': 'food',
    'Obst': 'food', 'Öl': 'food', 'Orange': 'food', 'Pizza': 'food',
    'Reis': 'food', 'Saft': 'food', 'Salat': 'food', 'Salz': 'food',
    'Schokolade': 'food', 'Suppe': 'food', 'Tee': 'food', 'Tomate': 'food',
    'Torte': 'food', 'Wasser': 'food', 'Wein': 'food', 'Wurst': 'food',
    'Zitrone': 'food', 'Zucker': 'food',
    # 장소 (place)
    'Apotheke': 'place', 'Ausland': 'place', 'Autobahn': 'place', 'Bad': 'place',
    'Bäckerei': 'place', 'Bahnhof': 'place', 'Bahnsteig': 'place', 'Balkon': 'place',
    'Bank': 'place', 'Bibliothek': 'place', 'Büro': 'place', 'Café': 'place',
    'Cafeteria': 'place', 'Club': 'place', 'Disco': 'place', 'Doppelzimmer': 'place',
    'Dorf': 'place', 'Eingang': 'place', 'Flughafen': 'place', 'Garage': 'place',
    'Garten': 'place', 'Geschäft': 'place', 'Gleis': 'place', 'Halle': 'place',
    'Haltestelle': 'place', 'Haus': 'place', 'Hotel': 'place', 'Insel': 'place',
    'Keller': 'place', 'Kindergarten': 'place', 'Kino': 'place', 'Kiosk': 'place',
    'Kirche': 'place', 'Krankenhaus': 'place', 'Kreuzung': 'place', 'Küche': 'place',
    'Laden': 'place', 'Land': 'place', 'Markt': 'place', 'Marktplatz': 'place',
    'Messe': 'place', 'Park': 'place', 'Platz': 'place', 'Reisebüro': 'place',
    'Reinigung': 'place', 'Restaurant': 'place', 'Rezeption': 'place',
    'Schlafzimmer': 'place', 'Schloss': 'place', 'Schule': 'place',
    'Schwimmbad': 'place', 'Sehenswürdigkeit': 'place', 'Spielplatz': 'place',
    'Sportplatz': 'place', 'Stadt': 'place', 'Strand': 'place', 'Straße': 'place',
    'Supermarkt': 'place', 'Theater': 'place', 'Toilette': 'place',
    'Universität': 'place', 'Weg': 'place', 'Wohnung': 'place',
    'Wohnzimmer': 'place', 'Zimmer': 'place',
    # 사물 (object)
    'Ampel': 'object', 'Antwortbogen': 'object', 'Apparat': 'object', 'Aufzug': 'object',
    'Ausweis': 'object', 'Auto': 'object', 'Ball': 'object', 'Basketball': 'object',
    'Bett': 'object', 'Bild': 'object', 'Bleistift': 'object', 'Bluse': 'object',
    'Buch': 'object', 'Bus': 'object', 'CD': 'object', 'Comic': 'object',
    'Computer': 'object', 'Drucker': 'object', 'E-Book': 'object', 'Fahrkarte': 'object',
    'Fahrplan': 'object', 'Fahrrad': 'object', 'Fenster': 'object', 'Fernseher': 'object',
    'Flasche': 'object', 'Flugzeug': 'object', 'Foto': 'object', 'Fotoapparat': 'object',
    'Fußball': 'object', 'Gabel': 'object', 'Gepäck': 'object', 'Gerät': 'object',
    'Geschenk': 'object', 'Gitarre': 'object', 'Glas': 'object', 'Handy': 'object',
    'Heft': 'object', 'Heizung': 'object', 'Jacke': 'object', 'Kamera': 'object',
    'Karte': 'object', 'Kasse': 'object', 'Kette': 'object', 'Klavier': 'object',
    'Kleid': 'object', 'Kleidung': 'object', 'Koffer': 'object', 'Kosmetik': 'object',
    'Kreuz': 'object', 'Kugelschreiber': 'object', 'Kühlschrank': 'object',
    'Lampe': 'object', 'Laptop': 'object', 'Licht': 'object', 'Löffel': 'object',
    'Mantel': 'object', 'Maschine': 'object', 'Messer': 'object', 'Mobiltelefon': 'object',
    'Motorroller': 'object', 'Müll': 'object', 'Mütze': 'object', 'Ohrring': 'object',
    'Paket': 'object', 'Papier': 'object', 'Parfum': 'object', 'Pass': 'object',
    'Plakat': 'object', 'Poster': 'object', 'Postkarte': 'object', 'Produkt': 'object',
    'Prospekt': 'object', 'Pullover': 'object', 'Rad': 'object', 'Radiergummi': 'object',
    'Radio': 'object', 'Ring': 'object', 'Rock': 'object', 'Rucksack': 'object',
    'Sache': 'object', 'Schalter': 'object', 'Schere': 'object', 'Schiff': 'object',
    'Schild': 'object', 'Schirm': 'object', 'Schlüssel': 'object', 'Schuh': 'object',
    'Smartphone': 'object', 'Sofa': 'object', 'Stiefel': 'object',
    'Straßenbahn': 'object', 'T-Shirt': 'object', 'Tablet': 'object', 'Tafel': 'object',
    'Tasche': 'object', 'Tasse': 'object', 'Taxi': 'object', 'Teller': 'object',
    'Ticket': 'object', 'Tisch': 'object', 'Tuch': 'object', 'Tür': 'object',
    'U-Bahn': 'object', 'Uhr': 'object', 'Wagen': 'object', 'Wäsche': 'object',
    'Wörterbuch': 'object', 'Zeitschrift': 'object', 'Zeitung': 'object',
    'Zelt': 'object', 'Zettel': 'object', 'Zug': 'object',
    # 신체 (body)
    'Arm': 'body', 'Auge': 'body', 'Bauch': 'body', 'Bein': 'body',
    'Fuß': 'body', 'Haar': 'body', 'Hals': 'body', 'Kopf': 'body',
    'Rücken': 'body', 'Zahn': 'body',
    # 자연 (nature)
    'Baum': 'nature', 'Blume': 'nature', 'Fluss': 'nature', 'Pflanze': 'nature',
    'Regen': 'nature', 'Rose': 'nature', 'Schnee': 'nature', 'See': 'nature',
    'Sonne': 'nature', 'Wald': 'nature', 'Wetter': 'nature', 'Wolke': 'nature',
    # 나머지는 abstract (기본값)
}

# 형용사 호환 카테고리 (None = 모든 카테고리 허용)
ADJ_COMPAT = {
    # 사람/동물 전용 (성격, 감정, 행동)
    'freundlich': ['person', 'animal'],
    'nett':       ['person', 'animal'],
    'sympathisch':['person', 'animal'],
    'lustig':     ['person', 'animal'],
    'traurig':    ['person', 'animal'],
    'glücklich':  ['person', 'animal'],
    'müde':       ['person', 'animal'],
    'jung':       ['person', 'animal'],
    'klug':       ['person', 'animal'],
    'dumm':       ['person', 'animal'],
    'blöd':       ['person', 'animal'],
    'verrückt':   ['person', 'animal'],
    'faul':       ['person', 'animal'],
    'nervös':     ['person', 'animal'],
    'einsam':     ['person', 'animal'],
    'froh':       ['person', 'animal'],
    'lieb':       ['person', 'animal'],
    'aktiv':      ['person', 'animal'],
    'fleißig':    ['person'],
    'dankbar':    ['person'],
    'ehrlich':    ['person'],
    'sportlich':  ['person'],
    'streng':     ['person'],
    'herzlich':   ['person'],
    'einverstanden': ['person'],
    'freiwillig':    ['person'],
    'bösen':      ['person'],
    # 사람/동물 전용 (외모/신체)
    'blond':      ['person', 'animal'],
    'schwanger':  ['person'],
    'männlich':   ['person', 'animal'],
    'gesund':     ['person', 'animal', 'food'],
    'krank':      ['person', 'animal'],
    'schwach':    ['person', 'animal'],
    # 맛/식감 (음식 전용)
    'sauer':      ['food'],
    'scharf':     ['food', 'object'],   # 매운 / 날카로운
    'süß':        ['food', 'person', 'animal'],  # 달콤한 / 귀여운
    'frisch':     ['food', 'nature', 'object'],
    # 온도 (비추상 한정)
    'warm':  ['food', 'object', 'place', 'nature', 'body'],
    'kalt':  ['food', 'object', 'place', 'nature', 'body'],
    'heiß':  ['food', 'object', 'place', 'nature', 'body'],
    'kühl':  ['food', 'object', 'place', 'nature', 'body'],
    # 색깔 (추상 제외)
    'rot':    ['person', 'animal', 'food', 'place', 'object', 'body', 'nature'],
    'blau':   ['person', 'animal', 'food', 'place', 'object', 'body', 'nature'],
    'grün':   ['person', 'animal', 'food', 'place', 'object', 'body', 'nature'],
    'gelb':   ['person', 'animal', 'food', 'place', 'object', 'body', 'nature'],
    'grau':   ['person', 'animal', 'food', 'place', 'object', 'body', 'nature'],
    'braun':  ['person', 'animal', 'food', 'place', 'object', 'body', 'nature'],
    'schwarz':['person', 'animal', 'food', 'place', 'object', 'body', 'nature'],
    'weiß':   ['person', 'animal', 'food', 'place', 'object', 'body', 'nature'],
    'bunt':   ['person', 'animal', 'food', 'place', 'object', 'body', 'nature'],
    'hell':   ['person', 'animal', 'place', 'object', 'nature'],
    'dunkel': ['person', 'animal', 'place', 'object', 'nature'],
    'sonnig': ['place', 'nature'],
    'neblig': ['place', 'nature'],
    # 물리적 상태 (사물/장소 한정)
    'kaputt':      ['object'],
    'nass':        ['object', 'person', 'animal', 'nature'],
    'hart':        ['object', 'food'],
    'elektrisch':  ['object'],
    'elektronisch':['object'],
    'automatisch': ['object'],
    'bequem':      ['object', 'place'],
    'besetzt':     ['place', 'object'],
    'sauber':      ['object', 'place', 'person', 'animal'],
    'schmutzig':   ['object', 'place', 'person', 'animal'],
    'offen':       ['place', 'object'],
    # 가격/가치 (구매 가능한 것 한정)
    'teuer':    ['object', 'food', 'place'],
    'billig':   ['object', 'food', 'place'],
    'günstig':  ['object', 'food', 'place'],
    'preiswert':['object', 'food', 'place'],
    'kostenlos':['object', 'abstract', 'place'],
    # 나머지 형용사는 모든 카테고리 허용 (None)
}


def get_noun_cat(noun):
    return NOUN_CAT.get(noun['sg.1'], 'abstract')


def compatible_adjs(noun_cat):
    result = [
        entry for entry in ADJ_LIST
        if ADJ_COMPAT.get(next(iter(entry))) is None
        or noun_cat in ADJ_COMPAT[next(iter(entry))]
    ]
    return result or ADJ_LIST


def adj_stem(word):
    if word == 'hoch':
        return 'hoh'
    if word.endswith('el'):
        return word[:-2] + 'l'
    if word.endswith('er') and word[-3] in 'aeiouäöü':
        return word[:-2] + 'r'
    if word.endswith('e'):
        return word[:-1]
    return word


def decline_adj(word, art_type, num, gender, case):
    stem = adj_stem(word)
    table = ADJ_WEAK if art_type in ('der', 'dieser') else ADJ_MIXED
    return stem + table[(num, gender, case)]


def has_batchim(text):
    for ch in reversed(text):
        if '가' <= ch <= '힣':
            return (ord(ch) - 0xAC00) % 28 != 0
    return False


def kr_suffix(case, noun_kr):
    if case == 1:
        return '이' if has_batchim(noun_kr) else '가'
    if case == 2:
        return '의'
    if case == 3:
        return '에게'
    if case == 4:
        return '을' if has_batchim(noun_kr) else '를'


def generate_phrase() -> dict:
    """한국어-독일어 명사구 쌍 생성. {'korean', 'german', 'hint'} 반환."""
    art_type = random.choice(['ein', 'dieser'])
    case = random.randint(1, 4)

    for _ in range(30):
        noun = random.choice(NOUN_LIST)
        gender = noun['gender']
        tag = noun.get('tag', '')
        noun_kr = noun['KR']

        if '/' in gender:
            gender = random.choice(gender.split('/')).strip()

        singular_only = '단수전용' in tag
        num = 'sg' if (art_type == 'ein' or singular_only) else random.choice(['sg', 'pl'])

        noun_de = noun.get(f'{num}.{case}', '')
        if noun_de and noun_de != '-':
            break

    noun_cat  = get_noun_cat(noun)
    adj_entry = random.choice(compatible_adjs(noun_cat))
    adj_de, adj_kr = next(iter(adj_entry.items()))

    article_de   = ARTICLE[art_type].get((num, gender, case), '?')
    adj_declined = decline_adj(adj_de, art_type, num, gender, case)

    plural_kr    = '들' if num == 'pl' else ''
    full_noun_kr = noun_kr + plural_kr

    return {
        'korean': f"{ARTICLE_KR[art_type]} {adj_kr} {full_noun_kr}{kr_suffix(case, full_noun_kr)}",
        'german': f"{article_de} {adj_declined} {noun_de}",
        'hint':   [f"{art_type}-", f"{adj_de}-", noun['sg.1']],
    }


def main():
    phrase = generate_phrase()
    print(phrase['korean'])
    print(phrase['german'])


if __name__ == '__main__':
    main()
