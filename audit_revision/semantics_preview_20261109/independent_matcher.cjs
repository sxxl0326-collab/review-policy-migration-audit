// Separate matcher implementation: frozen node-ignore, explicit case sensitivity.
// Does not load the Python CodeOwners engine or its regular expressions.
const fs=require('fs');
const ignore=require(process.argv[3]);
const cases=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const output=[];
for(const c of cases){
 if(c.category==='unsupported_syntax')continue;
 let result=[];
 for(const raw of c.evaluated_text.split(/\r?\n/)){
  const line=raw.split('#',1)[0].trim();if(!line)continue;
  const m=line.match(/^((?:\\.|[^\s])+)(?:\s+(.*))?$/);
  if(!m)throw new Error('Unsupported lexical input: '+line);
  const pattern=m[1],owners=(m[2]||'').split(/\s+/).filter(Boolean);
  if(ignore({ignorecase:false}).add(pattern).ignores(c.path))result=owners;
 }
 result=[...new Set(result)].sort();
 output.push({name:c.name,expected:c.expected,actual:result,passed:JSON.stringify(result)===JSON.stringify(c.expected)});
}
process.stdout.write(JSON.stringify({implementation:'Separate wrapper around frozen node-ignore with ignorecase:false; explicit CODEOWNERS last-match loop',independent_of_Python_CodeOwners:true,cases:output.length,passed:output.filter(x=>x.passed).length,results:output},null,2));
