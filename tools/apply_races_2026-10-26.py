"""Rebuild data.racials from the 2026-10-26 Wowhead race-page pull, then layer the
launch racial tuning pass on top (Wowhead news 383597).

Run from the repo root:  python3 tools/apply_races_2026-10-26.py
"""
import json
from collections import Counter

PULL = 'data/pulls/2026-10-26-races.json'
NEWS = 'https://www.wowhead.com/forever/news/racial-ability-tuning-pass-for-wow-forever-383597'

CLASS_BY_ID = {1: 'Warrior', 2: 'Paladin', 3: 'Hunter', 4: 'Rogue', 5: 'Priest',
               7: 'Shaman', 8: 'Mage', 9: 'Warlock', 11: 'Druid'}
NAMES = {}  # use Wowhead's names (High Order / Windshaper Skyborne)

ARTISAN = 'dwarf-artisans-precision'  # no Forever spell id published yet

# Tuning overlay: id -> fields to replace (None removes the trait)
OVERLAY = {
    # Human
    '20597': {'d': 'Increases your critical strike chance with all spells and attacks by 1%.'},
    '20598': {'d': 'Spirit increased by 10%.'},
    # Dwarf: Earth Fury out, Artisan's Precision in
    '1259719': None,
    # Tauren
    '1259918': {'d': 'Gain 2% increased movement speed every 5 sec spent moving, up to a maximum of 60% increase. '
                     'Taking damage or standing still will reduce this effect. Does not affect mounted speed.'},
    '20550': {'d': 'Total Health increased by 5%.'},
    # Orc: Savage out, Command back
    '20574': None,
    # Skyborne
    '1259710': {'d': 'Increases your spellcasting, melee, and ranged Haste by 2%.'},
    '1259705': {'d': 'Increases your Health and Mana regeneration by 50% for 15 sec. Cannot be used while Innervate is active, and Innervate replaces it as the stronger effect. '
                     'Using it at a Ley Line grants Attuned for 1 hour, raising the bonus to 100%. Attuned persists through death.'},
    '1259686': {'d': 'Increases your movement speed by 15% for 15 sec. Using it at an elemental convergence grants Charged for 1 hour, '
                     'raising the bonus to 30%. Charged persists through death.'},
    # Additions posted 2026-10-27 in the same thread
    '20572': {'cd': '2 min cooldown'},  # Orc Blood Fury (was 3 min)
    '20554': {'d': 'Increases your spellcasting and attack speed by 10% for 15 sec.'},  # Troll Berserking (was 10 sec)
    '1260189': {'d': 'Your spells and attacks have a 20% chance to drain Health from the target, up to 5% of your maximum Health. '
                     '15 sec internal cooldown.'},
    '1260201': {'d': 'Your spells and attacks have a 30% chance to drain Health from the target, up to 5% of your maximum Health. '
                     '15 sec internal cooldown.'},
}
# Skyborne clarification: Attuned and Charged are removed on entering a raid
OVERLAY['1259705']['d'] = OVERLAY['1259705']['d'].replace('persists through death.', 'persists through death and is removed on entering a raid.')
OVERLAY['1259686']['d'] = OVERLAY['1259686']['d'].replace('persists through death.', 'persists through death and is removed on entering a raid.')
ADD = {  # race -> [(after-which-id or None, id, spell)]
    '3': [('1259721', ARTISAN, {'n': "Artisan's Precision", 'i': 'ability_marksmanship',
                                'd': 'Increases hit chance with spells and attacks by 1%.'})],
    '2': [('20573', '20575', {'n': 'Command', 'i': 'ability_warrior_warcry',
                              'd': 'Damage dealt by Warlock and Hunter pets increased by 5%.'})],
}


def main():
    pull = json.load(open(PULL))
    data = json.load(open('data/data.json'))
    old = data['racials']

    spells = {}
    for sid, s in pull['spells'].items():
        if not s.get('n'):
            continue
        e = {'n': s['n'], 'i': s['i'], 'd': s['d']}
        if s.get('cd'):
            e['cd'] = s['cd']
        if s.get('ct'):  # passives have no cast time; the page keys "passive" off this
            e['ct'] = s['ct']
        spells[sid] = e

    races, faction, classes, by_class = {}, {}, {}, {c: {} for c in CLASS_BY_ID.values()}
    for rid, r in pull['races'].items():
        races[rid] = NAMES.get(rid, r['name'])
        faction[rid] = 'A' if r['side'] == 1 else 'H'
        classes[rid] = [CLASS_BY_ID[c] for c in sorted(r['classes']) if c in CLASS_BY_ID]
        dup = Counter(t['name'] for t in r['traits'])
        for cid, cname in CLASS_BY_ID.items():
            bit = 1 << (cid - 1)
            ids = []
            for t in r['traits']:
                # Class masks only matter for class-specific versions (Gnome, Undead).
                if dup[t['name']] > 1 and t['classes'] and not (t['classes'] & bit):
                    continue
                ids.append(str(t['id']))
            by_class[cname][rid] = ids

    # Apply the tuning overlay
    for sid, ch in OVERLAY.items():
        if ch is None:
            for cl in by_class.values():
                for rid in cl:
                    cl[rid] = [x for x in cl[rid] if x != sid]
            spells.pop(sid, None)
        else:
            spells[sid].update(ch)
            spells[sid]['tuned'] = 1
    for rid, adds in ADD.items():
        for after, sid, sp in adds:
            spells[sid] = {**sp, 'tuned': 1}
            for cl in by_class.values():
                lst = cl[rid]
                lst.insert(lst.index(after) + 1 if after in lst else len(lst), sid)

    # byRace = first playable class's list (fallback only)
    by_race = {rid: by_class[classes[rid][0]][rid] for rid in races}
    data['racials'] = {
        'races': races, 'faction': faction, 'classes': classes,
        'byRace': by_race, 'byClass': by_class, 'spells': spells,
        'pulled': pull['pulled'][:10], 'tuning': NEWS,
    }
    data['meta']['racialsPulled'] = pull['pulled'][:10]
    json.dump(data, open('data/data.json', 'w'), indent=1, ensure_ascii=False)
    gone = sorted(set(old['spells']) - set(spells))
    print('races', len(races), 'spells', len(spells), 'removed', gone)


if __name__ == '__main__':
    main()
