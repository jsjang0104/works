"""Shuffle small vocabulary groups while keeping confusing words close together."""

import argparse
import random
import unicodedata
from difflib import SequenceMatcher

from vocabulary import WORD_FILE, load_vocabulary

# Explicit meaning/spelling groups take precedence over automatic spelling matches.
CONFUSABLE = [
    ['fordern', 'fördern', 'folgen'],
    ['Betrag', 'Beitrag', 'einen Beitrag zu etwas leisten', 'Rechnungsbetrag', 'Nettobetrag', 'Gesamtpreis', 'Einzelpreis'],
    ['Ansehen', 'ansehen', 'aussehen'],
    ['erfahren', 'erfassen', 'erhalten', 'erwerben'],
    ['gewähren', 'gewährleisten'],
    ['Reis', 'rein', 'reif'],
    ['Bär', 'Bauer'],
    ['Lob', 'loben', 'Leistung', 'leisten', 'leistungsfähig'],
    ['bewusst', 'unbewusst', 'Bewusstlosigkeit', 'Ohnmacht', 'zu sich kommen'],
    ['ungewöhnlich', 'unglaublich', 'seltsam'],
    ['gratis', 'kostenlos', 'Gebühr'],
    ['sich freuen', 'freuen', 'erfreuen', 'fröhlich', 'glücklich'],
    ['gelingen', 'glücken', 'scheitern', 'schiefgehen', 'bestehen', 'durchfallen'],
    ['Absage', 'Zusage', 'abweisen', 'annehmen', 'verneinen'],
    ['Anreise', 'Abreise', 'Abfahrt', 'losfahren', 'anfahren', 'eintreffen'],
    ['Dienstreise', 'Geschäftsreise', 'auf Geschäftsreise sein'],
    ['in den Keller fallen', 'in den Keller gehen', 'Rückgang', 'Aufstieg'],
    ['Kaufvertrag', 'von einem Vertrag zurücktreten', 'abschließen'],
    ['stornieren', 'Stornierung', 'Stornokosten', 'Fristablauf', 'fristgerecht', 'kurzfristig'],
    ['verlegen', 'verschieben', 'sich verzögern', 'Verzögerung'],
    ['verschicken', 'versenden', 'zuschicken', 'zusenden', 'Versand', 'Sendung'],
    ['Lieferung', 'Auslieferung', 'Lieferdatum', 'Zustelldatum', 'Zustelltag', 'Zustellort', 'Zusteller', 'Lieferschein'],
    ['Rabatt', 'Ermäßigung', 'Preisnachlass', 'Sonderaktion', 'Sparangebot'],
    ['Ausfuhr', 'Export-Firma', 'Freihandelsabkommen'],
    ['Gesetz', 'gesetzlich', 'Vorschrift', 'Straßenverkehrsordnung'],
    ['Haftung', 'Schuld an etwas haben', 'für etwas verantwortlich sein',
     'jemanden für etwas haftbar machen', 'jemanden für etwas verantwortlich machen', 'für etwas aufkommen'],
    ['Schaden', 'Schadenfall', 'Schadenersatz', 'Kfz-Haftpflichtversicherung', 'Fahrerschutzversicherung', 'Teilkasko', 'Vollkasko'],
    ['Banker', 'Bankangestellte', 'Bankeinzug', 'ein Konto eröffnen', 'IBAN'],
    ['erschöpft', 'kaputt', 'sich erholen', 'Auszeit'],
    ['Einsamkeit', 'Einsamkeitsgefühl', 'Altersarmut', 'Demenz'],
    ['entführen', 'einführen', 'ausführen', 'aufführen', 'durchführen', 'führen'],
    ['einnehmen', 'zu sich nehmen', 'schlucken', 'Pille', 'Tablette', 'Medikament'],
    ['Heilmittel', 'Heilpraktiker', 'therapeutisch', 'Herzchirurg'],
    ['Notdienst', 'Notfall', 'Notrufdienst'],
    ['Geldbeutel', 'Geldgeber', 'Geldstrafe'],
    ['Vertrauen', 'vertrauen', 'Selbstvertrauen', 'Glaubwürdigkeitsverlust'],
    ['Rente', 'in Rente gehen', 'Ruhestand', 'pensioniert'],
    ['Bewerbung', 'sich bewerben', 'Stellenausschreibung', 'Vorstellungsgespräch', 'Praktikumsplatz', 'Auswahlprozess'],
    ['Auszubildende', 'ausbilden', 'erwerbstätig', 'angestellt', 'Arbeitnehmer'],
    ['beschäftigen', 'kündigen', 'befördern', 'Beförderung'],
    ['Leiter', 'Abteilungsleiter', 'Vertriebsmanager', 'Assistent'],
    ['Vollzeit', 'Ganztagstätigkeit', 'Halbtagsgehalt', 'Elternzeit', 'Wiedereinstieg'],
    ['Handschrift', 'Druckschrift', 'Schriftsprache', 'Unterschrift'],
    ['sprechen', 'ansprechen', 'aussprechen', 'absprechen', 'versprechen', 'entsprechen'],
    ['etwas zur Sprache bringen', 'Besprechung', 'Konferenz', 'ein Interview führen'],
    ['nachschauen', 'nachbohren', 'nachdenken', 'nachvollziehen'],
    ['Ereignis', 'Ergebnis', 'Erlebnis', 'Erbrecht'],
    ['untersuchen', 'durchsuchen', 'forschen', 'Forschungssemester', 'wissenschaftlich'],
    ['schützen', 'Schutz', 'sichern', 'Sicherheitskraft'],
    ['überwachen', 'übernehmen', 'überraschen', 'verwundern'],
    ['verursachen', 'auslösen', 'Grund für etwas sein'],
    ['verbinden', 'Verbindung', 'Verbindung ist schlecht', 'Zugang'],
    ['Mangel an etwas', 'mangelhaft', 'knapp', 'gering', 'fehlen'],
    ['brauchen', 'bedürfen', 'erforderlich', 'notwendig'],
    ['bewaffnet', 'abwehren', 'Angreifer', 'angreifen', 'Anschlag', 'Attentat', 'Selbstmordattentäter'],
    ['Bande', 'Dieb', 'Drogengeld', 'Drogenkriminalität', 'beschlagnahmen'],
    ['Polizei', 'Polizist', 'Polizeistreife', 'fahnden nach etwas'],
    ['Staatsanwaltschaft', 'Landgericht', 'Urteil', 'verurteilen', 'Zeugenaussage'],
    ['Rechtsanwalt', 'Fachanwalt', 'Kanzlei', 'Rechtsberatung', 'Rechtslage', 'Recht haben', 'rechtfertigen'],
    ['Familienrecht', 'Medizinrecht', 'BGB'],
    ['Schloss', 'Schlüssel', 'Schlusslicht', 'schließen'],
    ['Boden', 'goldenen Boden haben', 'Grundlage', 'Grundstückseigentümer'],
    ['im Allgemeinen', 'im Einzelnen', 'insbesondere', 'namentlich', 'unter anderem', 'vor allem'],
    ['jede Menge', 'eine Unmenge', 'Menge', 'Menschenmenge', 'maßlos', 'übermäßig'],
    ['kinderleicht', 'federleicht', 'Gewicht', 'Schwere', 'Größe'],
    ['bläulich', 'weißlich', 'rötlich', 'Farbe', 'weich'],
    ['Fernseher', 'Fernsehen', 'Tablet', 'Betriebssystem', 'herunterladen', 'synchronisieren'],
    ['Taste', 'Knopfdruck', 'Lautstärke', 'steuern'],
    ['Geschäft', 'Geschäftsaufgabe', 'Branche', 'Branchentreffen', 'Unternehmen', 'Betreiber'],
    ['Handelskette', 'Supermarktkette', 'Filiale', 'Betriebsurlaub', 'Betriebsversammlung'],
    ['Ware', 'Produktlinie', 'Produktprobe', 'Neuveröffentlichung', 'auf den Markt bringen'],
    ['Werbung', 'Zeitungsanzeige', 'Zielgruppe', 'Marktforschung', 'Konsumverhalten'],
    ['Messe', 'Messegelände', 'Ausstellung', 'Vernissage', 'Kurator', 'Publikumsmagnet'],
    ['Tageskasse', 'Vorverkauf', 'Eintritt', 'ausgebucht sein', 'ausverkauft'],
    ['Kunst', 'Werk', 'Wert', 'Bild', 'Zerrbild'],
    ['Zeitgenosse', 'zeitgenössisch', 'aktuell', 'derzeitig'],
    ['Wappen', 'Wappentier'],
    ['Sturmböe', 'Unwetter', 'Gewitter', 'Hagel', 'Schauer', 'Dauerregen', 'Starkregen'],
    ['Höchstwert', 'Tiefstwert', 'Tief', 'Wettervorhersage', 'vorhersagen'],
    ['nachhaltig', 'klimaneutral', 'Klimawandel', 'Mehrweg', 'wiederverwendbar', 'Wegwerfbecher'],
    ['Obst', 'Gemüse', 'Fleisch', 'Korn', 'Linse', 'Beilage'],
    ['zubereiten', 'Teezubereitung', 'Wasserkocher', 'Küche', 'Bäckerei', 'Caterer'],
    ['in Mode sein', 'Kleid', 'Krawatte', 'Badekleidung', 'Tragekomfort'],
    ['Miete', 'Mieter', 'Wohnanlage', 'Wohnungsbesichtigung', 'Einzelzimmer', 'Meerblick'],
    ['Halter', 'Hundehalter', 'Hundehaufen', 'Hinterlassenschaft', 'anleinen', 'Tierhaltung'],
    ['Gotteshaus', 'Kirche', 'Moschee', 'Pastor', 'Totenmesse'],
    ['flüchten', 'Flüchtling', 'Geflüchtete', 'Migrant', 'Neubürger'],
    ['beherbergen', 'unterbringen', 'Hotelverpflegung'],
    ['wünschen', 'Wunsch', 'zu wünschen übrig lassen', 'zu diesem Zweck'],
    ['weiterverkaufen', 'käuflich', 'Kaufkraft'],
    ['wahr', 'wahrscheinlich', 'voraussichtlich', 'tatsächlich', 'in der Tat'],
    ['auf jeden Fall', 'in jedem Fall', 'unter Umständen', 'falls', 'wenn auch'],
    ['verfügbar', 'jemandem zur Verfügung stehen', 'bereitliegen', 'einsetzbar'],
    ['keineswegs', 'nimmer', 'absolut'],
    ['gierig', 'faul', 'willig', 'belastbar', 'anspruchslos', 'klaglos'],
    ['sensibel', 'gereizt sein', 'ärgerlich', 'sich über etwas ärgern', 'schlechter Laune sein'],
    ['gastfreundlich', 'Gastgeber', 'weltoffen', 'sympathisch'],
    ['Würde', 'Verantwortungsbewusstsein', 'Vereinbarkeit'],
    ['Entwicklung', 'Innovation', 'Investition', 'Finanzkrise'],
    ['verdienen', 'Verdienst', 'verdanken', 'entlohnen', 'Mindestlohn'],
    ['Antrag', 'Angabe', 'Ankündigung', 'Angebot', 'anbieten'],
    ['Aufmerksamkeit auf sich ziehen', 'Aufmerksamkeit erregen', 'beeindruckend', 'großartig'],
    ['Sprach', 'Sprache', 'auf Wiederhören', 'Telefonat', 'Anrufbeantworter'],
    ['Gleis', 'Bahn', 'Zug', 'Fahrradmitnahme', 'Bordrestaurant', 'umsteigen', 'Haltestelle'],
    ['Fußballspiel', 'Sportverein', 'Athlet', 'ein Tor schießen', 'Titel', 'knapp vorbeigehen'],
    ['sich anstrengen', 'mit aller Mühe', 'Einsatz zeigen', 'unter Einsatz von etwas'],
    ['verbergen', 'heimlich', 'unauffällig', 'hervortreten'],
    ['Anerkennung', 'Bezeichnung', 'Sammelbezeichnung'],
    ['in Kauf nehmen', 'hinnehmen', 'in Anspruch nehmen'],
    ['vereinbaren', 'Vereinbarung', 'festlegen', 'bestätigen'],
    ['entscheiden', 'sich entschließen', 'vorhaben', 'sich etwas vorbehalten'],
    ['verpassen', 'vergessen', 'erledigen', 'zustande bringen'],
    ['Lageplan', 'Orientierung', 'Richtung', 'Standort', 'vor Ort'],
    ['Bezug', 'Becher', 'Büromöbel', 'Kommode', 'Gardine', 'Fototapete'],
]


def arrange(cards, seed=None):
    groups = [[i] for i in range(len(cards))]
    owner = list(range(len(cards)))

    def merge(a, b):
        a, b = owner[a], owner[b]
        if a == b or len(groups[a]) + len(groups[b]) > 8:
            return
        groups[a].extend(groups[b])
        for index in groups[b]:
            owner[index] = a
        groups[b] = []

    lookup = {}
    for i, card in enumerate(cards):
        if card['term'] in lookup:
            merge(lookup[card['term']], i)
        else:
            lookup[card['term']] = i
    for terms in CONFUSABLE:
        indices = [lookup[term] for term in terms if term in lookup]
        for i in indices[1:]:
            merge(indices[0], i)
    normalized = [unicodedata.normalize('NFKD', c['term']).casefold() for c in cards]
    # Only match ungrouped items, avoiding huge components of shared prefixes.
    for i, left in enumerate(normalized):
        if len(groups[owner[i]]) > 1 or len(left) < 5:
            continue
        best, score = None, .81
        for j in range(i + 1, len(cards)):
            if len(groups[owner[j]]) > 1:
                continue
            right = normalized[j]
            if abs(len(left) - len(right)) > 3:
                continue
            ratio = SequenceMatcher(None, left, right).ratio()
            if ratio > score:
                best, score = j, ratio
        if best is not None:
            merge(i, best)
    blocks = [sorted(group) for group in groups if group]
    random.Random(seed).shuffle(blocks)
    return [cards[index] for block in blocks for index in block]


def format_vocabulary(cards):
    lines = []
    for card in cards:
        fields = [card['term'], card['meaning'], card['sentence']]
        if card.get('sentence_translation'):
            fields.append(card['sentence_translation'])
        lines.append(' | '.join(fields) + '\n')
    return ''.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int)
    args = parser.parse_args()
    cards = arrange(load_vocabulary(), args.seed)
    WORD_FILE.write_text(format_vocabulary(cards), encoding='utf-8')
    print(f'{len(cards)}개 항목을 유사 어휘 그룹 단위로 섞었습니다.')
