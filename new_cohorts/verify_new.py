"""Offline, from the extracted supplement: python new_cohorts/verify_new.py"""
from pathlib import Path
import json,sys,csv
N=Path(__file__).resolve().parent
runtime=N.parent/'wave2_frozen_collection/runtime'
if not runtime.exists():runtime=N/'wave/runtime'
sys.path.insert(0,str(runtime))
import run_controls as c
from platform_matching import activate
activate()
def get(p):return json.loads(p.read_text(encoding='utf-8-sig'))
b=[];a=[]
for f in sorted((N/'B').glob('repo*.json')):
 r=get(f);root=N/'B_inputs'/f"case{r['index']:02d}"
 old,new=[c.active(root/x)[1] for x in ('base','head')]
 for p in r['records']:
  o=set();n=set()
  for previous,path in p['paths']:
   o.update(c.nominated(old,previous or path));n.update(c.nominated(new,path))
  adj={x for x in n-o if x.lower()!='@'+p['author'].lower()}
  assert [sorted(x) for x in (o,n,n-o,adj)]==[p[k] for k in ('old','new','raw','adjusted')]
  b.append((bool(n-o),bool(adj),bool(p['requests'])))
assert [len(b),*[sum(x[i] for x in b) for i in range(3)]]==[25,7,2,9]
for l in (N/'wave/context_evaluations.jsonl').read_text(encoding='utf8').splitlines():
 v=json.loads(l);case='case%02d'%v['index'];src=N/'wave/replay/external'/case
 root={'official':src/'official','actual':src/'head','keep_old':src/'base','openrewrite':N/'wave/openrewrite/outputs'/case}[v['policy']]
 path=v['context']['path'];o=c.nominated(c.active(src/'base')[1],path);g=c.nominated(c.active(root)[1],path)
 assert sorted(g)==v['got'] and sorted(o)==v['old'] and sorted(o-g)==v['old_missing']
 a.append(v)
assert len(a)==4*197 and len({x['repo'] for x in a})==13
print('Verified 25 PR-level set comparisons and 788 context-policy rows from saved configuration files.')
