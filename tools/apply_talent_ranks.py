import json,re
d=json.load(open('data/data.json'));RAW=json.load(open('data/pulls/2026-10-23-talent-ranks.json'));R=RAW['talents'];TREES=RAW['trees']
TREE={'MageFire':'Fire','MageFrost':'Frost','MageArcane':'Arcane','WarriorArms':'Arms','WarriorProtection':'Protection','WarriorFury':'Fury',
 'RogueCombat':'Combat','RogueAssassination':'Assassination','RogueSubtlety':'Subtlety','PriestDiscipline':'Discipline','PriestHoly':'Holy','PriestShadow':'Shadow',
 'ShamanElementalCombat':'Elemental','ShamanRestoration':'Restoration','ShamanEnhancement':'Enhancement','DruidFeralCombat':'Feral','DruidRestoration':'Restoration','DruidBalance':'Balance',
 'WarlockDestruction':'Destruction','WarlockCurses':'Affliction','WarlockSummoning':'Demonology','HunterBeastMastery':'Beast Mastery','HunterSurvival':'Survival','HunterMarksmanship':'Marksmanship',
 'PaladinCombat':'Retribution','PaladinHoly':'Holy','PaladinProtection':'Protection'}
OLD_TEXT={'Feral Charge','Berserk','Thick Hide'}
def clean(s,name):
    s=s.replace('(20 * 60)','1,200').replace('restore 0 Mana','restore Mana').replace('convert 0 Mana','convert Mana')
    s=re.sub(r' by \(\d+ /- \d+ \* \d+\),',',',s)
    s=re.sub(r'deal \(\(\(\(.*?\)\) Fire or Shadow damage based on the pet\.','deal bonus Fire or Shadow damage based on the pet (scales with Shadow spell power).',s)
    s=re.sub(r'heals them for \[.*?\] the next','heals them (scales with healing power) the next',s)
    s=re.sub(r'\[(\d+) \+ \(Frost spell power \* 0\.1\) \* \(1\)\]',r'\1 (+10% of Frost spell power)',s)
    s=re.sub(r'\[(\d+) / Ferocity: (\d+) / Unleashed Fury: (\d+) \+ \(Ranged Attack Power \* \(0\.(\d+)\)\)\]',lambda m:f'{m[1]} ({m[2]} with Ferocity, {m[3]} with Unleashed Fury) + {int(m[4])}% of Ranged Attack Power',s)
    m=re.search(r'Lasts longer per combo point: (1 point.*)$',s)
    if m: s=s[:m.start(1)]+' / '.join(re.findall(r'(\d+) sec',m.group(1)))+' sec.'
    return s.strip()
log=[]
for cname,C in d['classes'].items():
    oldby={x['name']:x for t in C['trees'] for x in t['talents']}
    for tree in C['trees']:
        tid=next(k for k,v in TREES.items() if v.startswith(cname) and TREE[v]==tree['name'])
        items=sorted([r|{'id':int(i)} for i,r in R.items() if r['tree']==tid],key=lambda r:(r['row'],r['col']))
        out=[]
        for r in items:
            o=oldby.get(r['name'])
            ranks=[clean(x,r['name']) for x in r['ranks']]
            if r['name'] in OLD_TEXT and o: ranks=[o['desc']]*len(ranks)
            t={'id':r['id'],'name':r['name'],'icon':r['icon'],'row':r['row'],'col':r['col'],'max':r['max'],'desc':ranks[-1],
               'req':r['req'],'level':10+r['row']*5,'active':o['active'] if o else None}
            if len(set(ranks))>1: t['ranks']=ranks
            out.append(t)
        tree['talents']=out
    # relink abilities
    byname={x['name']:(x,t['name']) for t in C['trees'] for x in t['talents']}
    keep=[]
    for a in C['abilities']:
        if a.get('talent'):
            hit=byname.get(a['name']) or next(((x,tn) for (x,tn) in byname.values() if x['id']==a['talent'] and a['name'].startswith(x['name'])),None)
            if not hit: log.append('dropped ability '+cname+' '+a['name']); continue
            a['talent']=hit[0]['id'];a['tree']=hit[1]
        keep.append(a)
    C['abilities']=keep
ib=next(a for a in d['classes']['Mage']['abilities'] if a['name']=='Ice Barrier')
t=next(x for tr in d['classes']['Mage']['trees'] for x in tr['talents'] if x['name']=='Ice Barrier')
ib['desc']=t['desc']
d['meta']['pulled']='2026-10-23'
json.dump(d,open('data/data.json','w'),indent=1,ensure_ascii=False)
print('\n'.join(log)); 
print(sum(1 for C in d['classes'].values() for tr in C['trees'] for x in tr['talents']),'talents;',sum(1 for C in d['classes'].values() for tr in C['trees'] for x in tr['talents'] if 'ranks' in x),'with per-rank text')
for n in ['Venom','Vindication','Demonic Brand','Prayer of Mending','Ice Barrier','Divine Aegis','Winter\'s Chill']:
    x=next(x for C in d['classes'].values() for tr in C['trees'] for x in tr['talents'] if x['name']==n); print(n,'|',x.get('ranks',[x['desc']])[0][:220])
