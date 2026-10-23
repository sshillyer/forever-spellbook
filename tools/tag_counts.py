import json,re
d=json.load(open('data/data.json'))
J=r'\b'
TAGS={
'Warrior':[['Rage','\\brage\\b'],['Crit','critical|\\bcrit\\b'],['Shield / Block','\\bshield|\\bblock'],['Stances','stance'],['Bleeds','\\brend\\b|deep wound|\\bbleed'],
  ['Two-Hand / Dual Wield','two-hand|dual wield|off hand|off-hand'],['Weapons','\\baxe|\\bsword|\\bmace|polearm|weapon'],['Control','\\bstun|\\bdaze|\\bslow|\\bfear|disarm|immobiliz|hamstring|intimidat'],
  ['Charge','\\bcharge|intercept'],['Execute','\\bexecute'],['Overpower','overpower'],['Threat','threat|taunt'],['Health','\\bhealth'],['Armor','\\barmor'],['Cooldowns','cooldown']],
'Paladin':[['Seals','\\bseals?\\b'],['Judgement','judgement'],['Holy damage','holy damage'],['Healing','\\bheal'],['Shield / Block','\\bshield|\\bblock'],['Blessings','blessing'],['Auras','\\baura'],
  ['Mana','\\bmana\\b'],['Crit','critical|\\bcrit\\b'],['Intellect','intellect|spell damage|spell power'],['Forbearance','forbearance'],['Undead / Demons','undead|demon'],
  ['Control','\\bstun|hammer of justice|repentance|incapacitat|\\bfear|\\bslow|\\bdaze'],['Threat','threat|taunt'],['Party','\\bparty|\\braid'],['Cooldowns','cooldown']],
'Rogue':[['Combo points','combo point'],['Energy','\\benergy'],['Stealth','stealth|vanish'],['Poisons','poison'],['Bleeds','\\bbleed|rupture|garrote|hemorrhage'],['Finishers','finishing move'],
  ['Crit','critical|\\bcrit\\b'],['Daggers','dagger'],['Weapons','dagger|\\bsword|\\bmace|\\baxe|\\bfist|off hand|dual wield'],['Control','\\bstun|gouge|\\bsap\\b|\\bblind|kidney|cheap shot|\\bdaze|incapacitat|\\bslow'],
  ['Dodge / Parry','\\bdodge|evasion|\\bparry'],['Threat','threat'],['Cooldowns','cooldown']],
'Priest':[['Shadow','shadow'],['Holy','\\bholy'],['Healing','\\bheal'],['Shields / Absorbs','\\bshield|absorb'],['Over time','over \\d+ sec|periodic'],['Mind Blast / Flay','mind blast|mind flay'],
  ['Smite / Holy Fire','\\bsmite|holy fire'],['Mana','\\bmana\\b'],['Spirit','\\bspirit'],['Crit','critical|\\bcrit\\b'],['Control','\\bfear|silence|psychic|\\bstun|horror|shackle|\\bslow|immobiliz'],
  ['Pushback','casting time|interrupt'],['Party','\\bparty|\\braid'],['Threat','threat'],['Cooldowns','cooldown']],
'Shaman':[['Totems','totem'],['Shocks','\\bshock'],['Lightning','lightning'],['Fire','\\bfire|flame|magma|lava'],['Frost','frost'],['Nature','nature'],['Healing','\\bheal'],
  ['Weapon / Melee','\\bweapon|windfury|flametongue|rockbiter|frostbrand|\\bmelee|stormstrike'],['Shields','\\bshield'],['Mana','\\bmana\\b'],['Crit','critical|\\bcrit\\b'],
  ['Pushback','casting time|interrupt'],['Party','\\bparty|\\braid'],['Cooldowns','cooldown']],
'Mage':[['Fire','\\bfire|flame|pyroblast|scorch|ignite|combustion'],['Frost','frost|\\bice\\b|cone of cold|blizzard'],['Arcane','arcane'],['Crit','critical|\\bcrit\\b'],['Hit','chance to hit|\\bhit chance'],
  ['Mana','\\bmana\\b'],['Frozen','frozen|freeze|frost nova|chill'],['Control','\\bslow|\\bdaze|\\bstun|polymorph|counterspell|immobiliz|silence'],['Arcane Missiles','missile'],
  ['Armor / Wards','\\barmor|\\bward|barrier|mana shield'],['Pushback','casting time|interrupt'],['Range','\\brange|radius'],['Cooldowns','cooldown']],
'Warlock':[['Curses','\\bcurse|\\bbane'],['Damage over time','over \\d+ sec|periodic|corruption|immolate|siphon'],['Shadow','shadow'],['Fire','\\bfire|immolate|incinerate|searing|conflagrate'],
  ['Demons','\\bdemon|\\bpet\\b|\\bimp\\b|voidwalker|succubus|incubus|felhunter|felguard'],['Soul Shards','soul shard'],['Drain / Life','\\bdrain|siphon|life tap|\\blife\\b'],['Health','\\bhealth'],['Mana','\\bmana\\b'],
  ['Crit','critical|\\bcrit\\b'],['Control','\\bfear|\\bhowl|death coil|banish|seduc|\\bstun|\\bslow|exhaust'],['Range','\\brange'],['Pushback','casting time|interrupt'],['Threat','threat'],['Cooldowns','cooldown']],
'Druid':[['Cat','\\bcat\\b'],['Bear','\\bbear\\b'],['Moonkin','moonkin'],['Forms / Shifting','\\bform\\b|shapeshift'],['Energy','\\benergy'],['Rage','\\brage\\b'],['Combo points','combo point'],
  ['Healing','\\bheal'],['Heal over time','rejuvenation|regrowth|lifebloom|wild growth|tranquility'],['Nature','nature|wrath|moonfire|insect swarm'],['Arcane','arcane|starfire|moonfire'],
  ['Crit','critical|\\bcrit\\b'],['Mana','\\bmana\\b'],['Control','\\broot|entangl|\\bbash|\\bstun|hibernate|cyclone|\\bdaze|\\bslow|immobiliz'],['Stealth','prowl|stealth'],['Armor','\\barmor'],
  ['Party','\\bparty|\\braid'],['Cooldowns','cooldown']],
}
out={}
for cls,tags in TAGS.items():
    C=d['classes'][cls];names={a['talent']:a['name'] for a in C['abilities'] if a.get('talent')}
    T=[(x['name'],(x['name']+' '+' '.join(x.get('ranks',[x['desc']]))+' '+names.get(x['id'],'')).lower()) for tr in C['trees'] for x in tr['talents']]
    keep=[]
    for l,r in tags:
        n=[nm for nm,s in T if re.search(r,s,re.I)]
        print(f'{cls:8} {l:18} {len(n):2}  {", ".join(n)[:110]}')
        if len(n)>=2: keep.append([l,r])
    out[cls]=keep
json.dump(out,open('tools/tags.json','w'),indent=1)
