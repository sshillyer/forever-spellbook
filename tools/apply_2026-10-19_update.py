import json,re
d=json.load(open('data/data.json'));u=json.load(open('data/pulls/2026-10-19-talents-racials.json'))
loose=lambda s:re.sub(r'[^a-z0-9%.]','',(s or '').lower())
TREE={'MageFire':'Fire','MageFrost':'Frost','MageArcane':'Arcane','WarriorArms':'Arms','WarriorProtection':'Protection','WarriorFury':'Fury',
 'RogueCombat':'Combat','RogueAssassination':'Assassination','RogueSubtlety':'Subtlety','PriestDiscipline':'Discipline','PriestHoly':'Holy','PriestShadow':'Shadow',
 'ShamanElementalCombat':'Elemental','ShamanRestoration':'Restoration','ShamanEnhancement':'Enhancement','DruidFeralCombat':'Feral','DruidRestoration':'Restoration','DruidBalance':'Balance',
 'WarlockDestruction':'Destruction','WarlockCurses':'Affliction','WarlockSummoning':'Demonology','HunterBeastMastery':'Beast Mastery','HunterSurvival':'Survival','HunterMarksmanship':'Marksmanship',
 'PaladinCombat':'Retribution','PaladinHoly':'Holy','PaladinProtection':'Protection'}
CLS={'Mage':'Mage','Warrior':'Warrior','Rogue':'Rogue','Priest':'Priest','Shaman':'Shaman','Druid':'Druid','Warlock':'Warlock','Hunter':'Hunter','Paladin':'Paladin'}
# cosmetic-only diffs: keep our cleaned text
KEEP_OLD={'Venom','Prayer of Mending','Feral Charge','Berserk','Shifting Power','Demonic Brand','Vindication','Improved Seal of Fury','Thick Hide'}
NEW_ACTIVE={'Arcane Wrath':{'sp':1326079,'c':'140 Mana','r':'30 yd range','ct':'3.5 sec cast','cd':'6 sec cooldown'},
            'Elemental Mastery':{'sp':16166,'ct':'Instant','cd':'3 min cooldown'}}
ACTIVE_FIX={'Lava Burst':{'c':'135 Mana'}}
FIXTEXT={'Divine Aegis':('(20 * 60)','1,200')}
changed_names=set()
for tid,tl in u['talents'].items():
    desc=u['trees'][tid]['description']; cname=next(c for c in CLS if desc.startswith(c)); tname=TREE[desc]
    C=d['classes'][cname]; tree=next(t for t in C['trees'] if t['name']==tname)
    oldby={x['name']:x for t in C['trees'] for x in t['talents']}
    out=[]
    for n in sorted(tl,key=lambda x:(x['row'],x['col'])):
        o=oldby.get(n['name'])
        dsc=n['d']
        if o and (loose(o['desc'])==loose(dsc) or n['name'] in KEEP_OLD): dsc=o['desc']
        elif o: changed_names.add((cname,n['name']))
        if n['name'] in FIXTEXT: dsc=dsc.replace(*FIXTEXT[n['name']])
        act=o['active'] if o else None
        if n['name'] in NEW_ACTIVE: act=NEW_ACTIVE[n['name']]
        if act and n['name'] in ACTIVE_FIX: act={**act,**ACTIVE_FIX[n['name']]}
        if o and o['active'] is None and n['name'] not in NEW_ACTIVE: act=None
        out.append({'id':n['id'],'name':n['name'],'icon':n['icon'],'row':n['row'],'col':n['col'],'max':n['max'],'desc':dsc,'req':n['req'],'level':10+n['row']*5,'active':act})
    tree['talents']=out
# relink abilities to talents by name; update single-rank talent abilities' text
for cname,C in d['classes'].items():
    byname={x['name']:(x,t['name']) for t in C['trees'] for x in t['talents']}
    keep=[]
    for a in C['abilities']:
        if a.get('talent'):
            hit=byname.get(a['name']) or next(((x,tn) for (x,tn) in byname.values() if x['id']==a['talent'] and a['name'].startswith(x['name'])),None)
            if not hit: print('drop ability (talent gone):',cname,a['name']); continue
            t,tn=hit; a['talent']=t['id']; a['tree']=tn
            if (cname,a['name']) in changed_names and len(a['levels'])<=1:
                a['desc']=t['desc']
                if t['active']:
                    for k,f in (('c','cost'),('r','range'),('ct','cast'),('cd','cd')):
                        if t['active'].get(k): a[f]=t['active'][k]
            if len(a['levels'])<=1: a['levels']=[t['level']]; a['learn']=t['level']
        keep.append(a)
    C['abilities']=keep
    # add new active talents without abilities
    have={a['name'] for a in C['abilities']}
    for t in [x for tr in C['trees'] for x in tr['talents']]:
        if t['name'] in NEW_ACTIVE and t['name'] not in have:
            act=t['active']
            C['abilities'].append({'name':t['name'],'icon':t['icon'],'spellId':act['sp'],'levels':[t['level']],'learn':t['level'],'desc':t['desc'],
              'cost':act.get('c'),'range':act.get('r'),'cast':act.get('ct'),'cd':act.get('cd'),'reqs':[],'changes':['introduced'],'talent':t['id'],
              'tree':next(tr['name'] for tr in C['trees'] if t in tr['talents']),'passive':False,'petTraining':False,'racial':False,
              'roles':['damage'] if t['name']=='Arcane Wrath' else ['burst']})
            print('added ability',cname,t['name'])
# racials
R=d['racials']
CID={'1':'Warrior','2':'Paladin','3':'Hunter','4':'Rogue','5':'Priest','7':'Shaman','8':'Mage','9':'Warlock','11':'Druid'}
byClass={}
for cid,races in u['racials'].items():
    byClass[CID[cid]]={r:list(ids) for r,ids in races.items()}
# Wowhead maps Paladin/Hunter/Shaman/Druid gnomes to the Energy Eureka; keep the mana version for those
for c,keepid in (('Paladin',1259823),('Shaman',1259823),('Druid',1259823),('Hunter',1259821)):
    byClass[c]['7']=[keepid if i==1259812 else i for i in byClass[c]['7']]
R['byClass']=byClass
for k,s in u['spells'].items():
    o=R['spells'].get(k,{})
    R['spells'][k]={'n':s['n'],'i':s['i'],'d':s['d'] if loose(s['d'])!=loose(o.get('d')) else o['d'],'cd':s['cd'] or None,'ct':s['ct'] or None}
R['spells']['20589'].setdefault('ct','Instant')
d['meta']['pulled']='2026-10-19'
json.dump(d,open('data/data.json','w'),indent=1,ensure_ascii=False)
print('changed talents:',len(changed_names))
