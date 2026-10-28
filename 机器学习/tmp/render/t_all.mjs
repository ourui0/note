import fs from 'node:fs';
const raw = fs.readFileSync('../../output/pdf/欧睿_241870008_作业一.tex','utf8');
const clean = raw.split('\n').map(l=>{let o='';for(let i=0;i<l.length;i++){if(l[i]==='\\'&&i+1<l.length){o+=l[i]+l[i+1];i++;continue}if(l[i]==='%')break;o+=l[i]}return o}).join('\n');
const body = clean.slice(clean.indexOf('\\begin{document}')+16, clean.lastIndexOf('\\end{document}'));
const re = /\\begin\s*\{tabular\}\s*\{([^}]*)\}\s*([\s\S]*?)\\end\s*\{tabular\}/g;
let m, i=0;
while ((m = re.exec(body))) {
  i++;
  const spec = m[1];
  const content = m[2];
  const suspicious = /begin\{|end\{/.test(content) || /ccc@|@\{/.test(content) || content.length > 400;
  console.log(`#${i} spec=${JSON.stringify(spec)} len=${content.length} ${suspicious?'  <-- SUSPICIOUS':''}`);
  if (suspicious) console.log('   head:', JSON.stringify(content.slice(0,160)));
}
