from pathlib import Path
import json,csv,collections
P=Path(__file__).resolve().parent
common={r['repo'] for r in csv.DictReader((P/'previous_tables/repository_checks.csv').open(encoding='utf-8-sig')) if r['common']=='True'}
for cohort,files in [('original',['primary_and_wave1/extension','wave2_frozen_collection']),('new',['new_cohorts/wave'])]:
 rows=[json.loads(l) for f in files for l in (P/f/'context_evaluations.jsonl').read_text(encoding='utf8').splitlines()]
 exposed={r['repo'] for r in rows if r['old'] and (cohort=='new' or r['repo'] in common)}
 conflict=set();equal={}
 for repo in exposed:
  bots=[r for r in rows if r['repo']==repo and r['group']=='bot' and r['policy']=='official']
  if any(set(r['old'])-set(r['reviewers']) for r in bots):conflict.add(repo)
  equal[repo]=(sum(set(r['old'])==set(r['reviewers']) for r in bots),len(bots))
 for policy in ['official','openrewrite']:
  loss={r['repo'] for r in rows if r['repo'] in exposed and r['policy']==policy and r['old_missing']}
  assert loss==conflict
 print(cohort,len(exposed),len(conflict),equal if cohort=='new' else sorted(conflict))
 assert (len(exposed),len(conflict))==((24,5) if cohort=='original' else (2,0))
 if cohort=='new':assert sorted(equal.values())==[(5,5),(42,42)]
