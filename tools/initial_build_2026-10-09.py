"""Normalize raw Wowhead extracts into one data.json for the spellbook app."""
import json, re, pathlib

RAW = pathlib.Path(__file__).parent / "raw"
OUT = pathlib.Path(__file__).parent / "data.json"

CLASSES = ["Warrior", "Paladin", "Hunter", "Rogue", "Priest", "Shaman", "Mage", "Warlock", "Druid"]
COLORS = {"Warrior": "#C79C6E", "Paladin": "#F58CBA", "Hunter": "#ABD473", "Rogue": "#FFF569", "Priest": "#FFFFFF",
          "Shaman": "#0070DE", "Mage": "#69CCF0", "Warlock": "#9482C9", "Druid": "#FF7D0A"}
TREE_ORDER = {"Warrior": ["Arms", "Fury", "Protection"], "Paladin": ["Holy", "Protection", "Retribution"],
              "Hunter": ["Beast Mastery", "Marksmanship", "Survival"], "Rogue": ["Assassination", "Combat", "Subtlety"],
              "Priest": ["Discipline", "Holy", "Shadow"], "Shaman": ["Elemental", "Enhancement", "Restoration"],
              "Mage": ["Arcane", "Fire", "Frost"], "Warlock": ["Affliction", "Demonology", "Destruction"],
              "Druid": ["Balance", "Feral", "Restoration"]}
HUNTER_PET = {"Great Stamina", "Natural Armor", "Arcane Resistance", "Fire Resistance", "Frost Resistance",
              "Nature Resistance", "Shadow Resistance", "Growl", "Thunderstomp"}
# costs I added from memory while transcribing; strip them so only Wowhead data remains
UNVERIFIED_COST = {"Warrior": {"Thunder Clap", "Demoralizing Shout", "Shield Block", "Whirlwind", "Challenging Shout"},
                   "Paladin": {"Seal of Righteousness", "Seal of the Crusader", "Seal of Fury"}}

# ---------- role tagging ----------
ROLE_NAMES = {
    "interrupt": {"Kick", "Pummel", "Shield Bash", "Counterspell", "Earth Shock", "Silence", "Feral Charge (Bear)", "Feral Charge"},
    "stun": {"Hammer of Justice", "Kidney Shot", "Cheap Shot", "Bash", "Pounce", "Concussion Blow", "Intercept", "Intimidation",
             "War Stomp", "Holy Wrath", "Inferno"},
    "cc": {"Polymorph", "Polymorph: Cow", "Sap", "Blind", "Gouge", "Fear", "Howl of Terror", "Psychic Scream", "Intimidating Shout",
           "Hibernate", "Freezing Trap", "Scatter Shot", "Repentance", "Banish", "Shackle Undead", "Turn Undead", "Scare Beast",
           "Mind Control", "Death Coil", "Confounding Flash", "Seduction", "Entangling Roots"},
    "snare": {"Frost Nova", "Hamstring", "Wing Clip", "Concussive Shot", "Frost Shock", "Earthbind Totem", "Cone of Cold",
              "Frost Trap", "Piercing Howl", "Curse of Exhaustion", "Entangling Roots", "Mind Flay", "Frostbolt", "Chastise",
              "Nature's Grasp", "Blast Wave", "Frostfire Bolt", "Counterattack"},
    "taunt": {"Taunt", "Growl", "Mocking Blow", "Challenging Shout", "Challenging Roar", "Seal of Fury", "Stoneclaw Totem", "Distracting Shot"},
    "purge": {"Purge", "Dispel Magic", "Tranquilizing Shot", "Shield Slam"},
    "dispel": {"Cleanse", "Purify", "Remove Curse", "Remove Lesser Curse", "Cure Poison", "Abolish Poison", "Cure Disease",
               "Abolish Disease", "Dispel Magic", "Poison Cleansing Totem", "Disease Cleansing Totem", "Tremor Totem"},
    "defensive": {"Shield Wall", "Last Stand", "Divine Shield", "Divine Protection", "Ice Block", "Evasion", "Deterrence", "Barkskin",
                  "Ice Barrier", "Templar's Bulwark", "Frenzied Regeneration", "Retaliation", "Shield Block", "Holy Shield",
                  "Lay on Hands", "Mana Shield", "Shadow Ward", "Fire Ward", "Frost Ward", "Desperate Prayer", "Elune's Grace",
                  "Stoneform", "Will of the Forsaken", "Will to Survive", "Escape Artist", "Shatter Curse", "Voice of Truth",
                  "Power Word: Shield", "Ghostly Strike", "Berserker Rage", "Feedback"},
    "mobility": {"Blink", "Sprint", "Dash", "Disengage", "Charge", "Intercept", "Feral Charge", "Feral Charge (Bear)",
                 "Aspect of the Cheetah", "Aspect of the Pack", "Ghost Wolf", "Travel Form", "Strider Kick", "Blessing of Freedom",
                 "Walk on Air", "Skysight", "Aquatic Form"},
    "burst": {"Death Wish", "Recklessness", "Arcane Power", "Combustion", "Rapid Fire", "Bestial Wrath", "Adrenaline Rush",
              "Blade Flurry", "Cold Blood", "Power Infusion", "Rage of the Farseer", "Berserk", "Presence of Mind", "Inner Focus",
              "Divine Favor", "Nature's Swiftness", "Elune's Light", "Blood Fury", "Berserking", "Amplify Curse", "Tiger's Fury",
              "Sweeping Strikes", "Eureka!", "Preparation", "Cold Snap", "Premeditation", "Bloodrage", "Swift Judgement",
              "Shifting Power", "Evocation", "Innervate", "Mana Tide Totem"},
    "threat_drop": {"Feign Death", "Fade", "Feint", "Cower", "Vanish", "Shadowmeld", "Disengage", "Blessing of Salvation"},
    "debuff": {"Demoralizing Shout", "Demoralizing Roar", "Hunter's Mark", "Curse of Tongues", "Curse of Weakness",
               "Curse of Recklessness", "Curse of the Elements", "Scorpid Sting", "Viper Sting", "Hex of Weakness", "Faerie Fire",
               "Sunder Armor", "Expose Armor", "Thunder Clap", "Disarm"},
    "stealth": {"Stealth", "Prowl", "Shadowmeld"},
    "res": {"Resurrection", "Redemption", "Revive", "Ancestral Spirit", "Rebirth", "Create Soulstone", "Reincarnation",
            "Divine Intervention"},
    "pet": {"Call Pet", "Dismiss Pet", "Revive Pet", "Mend Pet", "Feed Pet", "Tame Beast", "Eyes of the Beast", "Beast Training",
            "Summon Imp", "Summon Voidwalker", "Summon Succubus", "Summon Incubus", "Summon Felhunter", "Health Funnel",
            "Demonic Sacrifice", "Soul Link", "Fel Domination", "Subjugate Demon", "Summon Hawk", "Intimidation", "Bestial Wrath"},
}
BUFF_RE = re.compile(r"for (1 hour|30 min|10 min|60 minutes)|Lasts (30|10) min|Aura\b|Blessing|Armor|Totem|Seal of|Shout|Form$", re.I)


def tag_roles(name, desc, passive):
    roles = [r for r, names in ROLE_NAMES.items() if name in names]
    d = desc or ""
    if not passive:
        if re.search(r"interrupts? (any )?spellcasting|interrupting (their|any)|Counters the enemy's spellcast", d) and "interrupt" not in roles:
            roles.append("interrupt")
        if re.match(r"(Heals?|Heal your|Instantly heals|A slow casting spell that heals|A powerful prayer that heals|Regenerates all)", d) and "heal" not in roles:
            roles.append("heal")
        if re.search(r"\b(Totem|Aura)$", name) or name.startswith(("Seal of", "Blessing", "Greater Blessing", "Aspect of", "Track ", "Sense ")) \
                or BUFF_RE.search(d) and not roles:
            if "buff" not in roles:
                roles.append("buff")
        if name in {"Auto Shot", "Multi-Shot", "Judgement", "Drain Life", "Siphon Life", "Slice and Dice"} and "damage" not in roles:
            roles.append("damage")
        if re.search(r"(damage|Damage)", d) and not set(roles) & {"heal", "buff", "pet", "res", "defensive"} and "damage" not in roles:
            roles.append("damage")
    if passive:
        roles = ["passive"]
    return roles or ["utility"]


def talent_level(row):
    return 10 + row * 5


def build():
    rac = json.loads((RAW / "racials.json").read_text())
    ct_patch = json.loads((RAW / "ct_patch.json").read_text())
    out = {"classes": {}, "racials": rac, "meta": {
        "source": "Wowhead WoW Forever (talent calculator data + spell tooltips)",
        "pulled": "2026-10-09", "note": "Beta data; Blizzard is still tuning. Rank 1 of talent spells comes from the talent."}}
    for cls in CLASSES:
        raw = json.loads((RAW / f"{cls}.json").read_text())
        trees = sorted(raw["t"], key=lambda t: TREE_ORDER[cls].index(t["n"]))
        talent_by_name = {}
        talents_out = []
        for tree in trees:
            tl = []
            for t in tree["tl"]:
                a = t.get("a")
                if a and str(a.get("sp")) in ct_patch and not a.get("ct"):
                    a["ct"] = ct_patch[str(a["sp"])]
                entry = {"id": t["id"], "name": t["n"], "icon": t["i"], "row": t["r"], "col": t["c"], "max": t["m"],
                         "desc": t["d"], "req": t.get("q", []), "level": talent_level(t["r"]), "active": a}
                tl.append(entry)
                talent_by_name[t["n"]] = (tree["n"], entry)
            talents_out.append({"name": tree["n"], "role": ["Tank", "Healer", "Damage"][tree["role"]], "talents": tl})

        abilities = []
        seen = set()
        for a in raw["a"]:
            name = a["n"]
            if a.get("hidden"):
                continue
            if name in UNVERIFIED_COST.get(cls, set()):
                a.pop("c", None)
            if not a.get("ct") and str(a["id"]) in ct_patch:
                a["ct"] = ct_patch[str(a["id"])]
            tal = a.get("tal")
            tree_name = None
            if name in talent_by_name:
                tree_name, te = talent_by_name[name]
                tal = te["id"]
            levels = sorted(set(a["lv"]))
            learn = levels[0]
            if tal:
                learn = min(learn, talent_by_name[name][1]["level"]) if name in talent_by_name else learn
            passive = not (a.get("c") or a.get("ct") or a.get("cd"))
            is_pet = cls == "Hunter" and name in HUNTER_PET
            ab = {"name": name, "icon": a["i"], "spellId": a["id"], "levels": levels, "learn": learn, "desc": a.get("d", ""),
                  "cost": a.get("c"), "range": a.get("r"), "cast": a.get("ct"), "cd": a.get("cd"), "reqs": a.get("rq", []),
                  "changes": a.get("ch", []), "talent": tal, "tree": tree_name, "passive": passive,
                  "petTraining": is_pet, "racial": bool(a.get("race"))}
            ab["roles"] = ["pet"] if is_pet else tag_roles(name, ab["desc"], passive)
            abilities.append(ab)
            seen.add(name)
        # active talents that have no trainer ranks
        for tree in talents_out:
            for t in tree["talents"]:
                if t["active"] and t["name"] not in seen:
                    a = t["active"]
                    ab = {"name": t["name"], "icon": t["icon"], "spellId": a.get("sp"), "levels": [t["level"]], "learn": t["level"],
                          "desc": t["desc"], "cost": a.get("c"), "range": a.get("r"), "cast": a.get("ct"), "cd": a.get("cd"),
                          "reqs": a.get("rq", []), "changes": [], "talent": t["id"], "tree": tree["name"], "passive": False,
                          "petTraining": False, "racial": False}
                    ab["roles"] = tag_roles(t["name"], t["desc"], False)
                    abilities.append(ab)
                    seen.add(t["name"])
        abilities.sort(key=lambda x: (x["learn"], x["name"]))
        out["classes"][cls] = {"color": COLORS[cls], "trees": talents_out, "abilities": abilities}
    OUT.write_text(json.dumps(out, separators=(",", ":")))
    return out


if __name__ == "__main__":
    d = build()
    for c, v in d["classes"].items():
        ab = v["abilities"]
        print(f"{c:8} abilities={len(ab):3} talent-gated={sum(1 for a in ab if a['talent']):2} passive={sum(a['passive'] for a in ab):2}"
              f" talents={[len(t['talents']) for t in v['trees']]}")
    print("bytes", pathlib.Path(OUT).stat().st_size)
