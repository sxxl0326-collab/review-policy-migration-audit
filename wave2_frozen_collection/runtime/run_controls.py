import pathlib,sys,json,os,subprocess,hashlib,shutil,time,textwrap,ctypes
R=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(R/'vendor'))
from codeowners import CodeOwners
import yaml
if os.name=='nt':
    k=ctypes.windll.kernel32;k.GetCurrentProcess.restype=ctypes.c_void_p;k.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_ulong];k.GetPriorityClass.argtypes=[ctypes.c_void_p];assert k.SetPriorityClass(k.GetCurrentProcess(),0x40);assert k.GetPriorityClass(k.GetCurrentProcess())==0x40
O=R/'results';O.mkdir(exist_ok=True)
PRIORITY=('.github/CODEOWNERS','CODEOWNERS','docs/CODEOWNERS')
BASH=pathlib.Path(os.environ.get('BASH','bash'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def active(root):
    for n in PRIORITY:
        if (root/n).exists():return n,(root/n).read_text(encoding='utf-8-sig')
    return None,''
def nominated(text,path):
    # Reject syntax where this parser differs from documented GitHub support.
    for ln in text.splitlines():
        if not ln.strip() or ln.lstrip().startswith('#'):continue
        pattern=ln.split()[0]
        if '[' in pattern or pattern.startswith('!'):raise ValueError('unsupported GitHub pattern: '+pattern)
    return {x[1] for x in CodeOwners(text).of(path.lstrip('/'))}
def extract_python():
    raw=yaml.safe_load((R/'sources/sync-dependabot-reviewers.yml').read_text(encoding='utf-8'))
    run=next(s['run'] for s in raw['jobs']['sync-reviewers']['steps'] if s.get('id')=='sync')
    lines=run.splitlines();start=next(i for i,x in enumerate(lines) if x.startswith('python3 <<'))+1;end=next(i for i in range(start,len(lines)) if lines[i]=='EOF')
    code='\n'.join(lines[start:end])+'\n';p=R/'sources/extracted_official_step.py';p.write_text(code,encoding='utf-8')
    save(R/'sources/extraction_manifest.json',{'workflow_sha256':sha(R/'sources/sync-dependabot-reviewers.yml'),'extracted_sha256':sha(p),'change':'YAML block extraction only; no executable Python code changed; workflow PR-creation step excluded'})
    return p
def fixture(root,config,owners):
    class Dumper(yaml.SafeDumper):
        def increase_indent(self,flow=False,indentless=False):return super().increase_indent(flow,False)
    root.mkdir(parents=True,exist_ok=True);(root/'.github').mkdir(exist_ok=True)
    (root/'.github/dependabot.yml').write_text(yaml.dump(config,Dumper=Dumper,sort_keys=False),encoding='utf-8')
    for name,value in owners.items():
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value,encoding='utf-8')
def run_official(root,kind,python_step):
    env={k:v for k,v in os.environ.items() if k.upper() in ('PATH','SYSTEMROOT','WINDIR','COMSPEC','PATHEXT')}
    temp=root/'tmp';temp.mkdir(exist_ok=True);env.update(GITHUB_OUTPUT=str(root/'github_output.txt'),TMP=str(temp),TEMP=str(temp),TMPDIR=str(temp).replace('\\','/'),PYTHONIOENCODING='utf-8',PYTHONUTF8='1')
    command=[str(BASH),'--noprofile','--norc',str(R/'sources/migrate-dependabot-reviewers.sh').replace('\\','/')] if kind=='official_bash' else [sys.executable,str(python_step)]
    begin=time.perf_counter()
    try:
        p=subprocess.run(command,cwd=root,env=env,stdin=subprocess.DEVNULL,capture_output=True,timeout=30)
        result={'exit_code':p.returncode,'elapsed_seconds':time.perf_counter()-begin}
        (root/'stdout.txt').write_bytes(p.stdout);(root/'stderr.txt').write_bytes(p.stderr)
    except subprocess.TimeoutExpired:
        result={'exit_code':None,'timed_out':True,'elapsed_seconds':time.perf_counter()-begin}
    name,txt=active(root);result.update(active_codeowners=name,codeowners=txt)
    return result
def update(eco='npm',directory='/',reviewers=('review-team',),branch=None):
    d={'package-ecosystem':eco,'directory':directory,'schedule':{'interval':'weekly'},'reviewers':list(reviewers)}
    if branch:d['target-branch']=branch
    return d
def context(path,actor='human',entry=None,branch='main'):
    return {'path':path,'actor':actor,'entry':entry,'branch':branch}
def specs():
    a=update();b=update(reviewers=('release-team',),branch='stable');pi=update('pip',reviewers=('python-team',));uv=update('uv',reviewers=('uv-team',))
    return [
      {'name':'basic_actor_scope','updates':[a],'owners':{},'contexts':[context('package.json','dependabot',0),context('package.json'),context('README.md')]},
      {'name':'existing_manifest_owner','updates':[a],'owners':{'.github/CODEOWNERS':'/package.json @app-team\n'},'contexts':[context('package.json','dependabot',0),context('package.json'),context('README.md')]},
      {'name':'multiple_codeowners_locations','updates':[a],'owners':{'CODEOWNERS':'/package.json @root-team\n','.github/CODEOWNERS':'/package.json @active-team\n'},'contexts':[context('package.json','dependabot',0),context('package.json'),context('README.md')]},
      {'name':'two_target_branches','updates':[a,b],'owners':{},'contexts':[context('package.json','dependabot',0,'main'),context('package.json','dependabot',1,'stable'),context('package.json')]},
      {'name':'shared_pyproject_ecosystems','updates':[pi,uv],'owners':{},'contexts':[context('pyproject.toml','dependabot',0),context('pyproject.toml','dependabot',1),context('pyproject.toml'),context('README.md')]},
      {'name':'already_equivalent_control','updates':[a],'owners':{'.github/CODEOWNERS':'/package.json @review-team\n'},'contexts':[context('package.json','dependabot',0),context('package.json'),context('README.md')]},
    ]
def expected(text,entries,c):
    out=nominated(text,c['path'])
    if c['actor']=='dependabot' and c['entry'] is not None:
        out|={r if r.startswith('@') else '@'+r for r in entries[c['entry']].get('reviewers',[])}
    return out
def compare(got,want):return {'exact':got==want,'missing':sorted(want-got),'extra':sorted(got-want),'got':sorted(got),'expected':sorted(want)}
def evaluate_contexts(oldtext,entries,contexts,outputs):
    wants=[expected(oldtext,entries,c) for c in contexts];union={}
    for c,w in zip(contexts,wants):union.setdefault((c['path'],c['branch']),set()).update(w)
    rows=[]
    for c,w in zip(contexts,wants):
        comparisons={'no_migration':compare(nominated(oldtext,c['path']),w),'conservative_path_reference':compare(union[c['path'],c['branch']],w),'context_aware_reference':compare(w,w)}
        for name,rec in outputs.items():
            if rec['exit_code']!=0:comparisons[name]={'implementation_failed':True,'exit_code':rec['exit_code']}
            else:comparisons[name]=compare(nominated(rec['codeowners'],c['path']),w)
        rows.append({'context':c,'comparisons':comparisons})
    witnesses=[]
    for i,c in enumerate(contexts):
        for j in range(i):
            other=contexts[j]
            if (c['path'],c['branch'])==(other['path'],other['branch']) and wants[i]!=wants[j]:witnesses.append({'context_indices':[j,i],'path':c['path'],'branch':c['branch'],'set1':sorted(wants[j]),'set2':sorted(wants[i])})
    return rows,witnesses
def main():
    before={p.name:sha(p) for p in (R/'sources').glob('*') if p.is_file()};step=extract_python();results=[];begin=time.perf_counter()
    # Independent parser behaviour sanity checks, including official file precedence.
    assert nominated('/package.json @first\n/package.json @last\n','package.json')=={'@last'}
    assert nominated('/.github/workflows/*.yml @ci\n','.github/workflows/build.yml')=={'@ci'}
    assert not nominated('/package.json @root\n','sub/package.json')
    for spec in specs():
        root=R/'fixtures'/spec['name'];original=root/'original';fixture(original,{'version':2,'updates':spec['updates']},spec['owners']);_,old=active(original)
        outputs={}
        for kind in ('official_bash','official_python'):
            dest=root/kind;fixture(dest,{'version':2,'updates':spec['updates']},spec['owners']);outputs[kind]=run_official(dest,kind,step)
        rows,witnesses=evaluate_contexts(old,spec['updates'],spec['contexts'],outputs)
        results.append({'specification':spec,'baseline_execution':outputs,'rows':rows,'same_path_scope_witnesses':witnesses})
    for name,h in before.items():assert sha(R/'sources'/name)==h
    summary={'specifications':len(results),'contexts':sum(len(x['rows']) for x in results),'scope_witness_cases':sum(bool(x['same_path_scope_witnesses']) for x in results),
       'elapsed_seconds':time.perf_counter()-begin,'api_calls_paid':0,'gpu_calls':0,'official_sources_unchanged':True,'results':results}
    save(O/'controlled_summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='results'},ensure_ascii=True))
if __name__=='__main__':main()
