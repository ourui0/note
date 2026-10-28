import fs from 'node:fs';
const clean = fs.readFileSync('../../output/pdf/欧睿_241870008_作业一.tex','utf8')
  .split('\n').map(l=>{let o='';for(let i=0;i<l.length;i++){if(l[i]==='\\'&&i+1<l.length){o+=l[i]+l[i+1];i++;continue}if(l[i]==='%')break;o+=l[i]}return o}).join('\n');
const body = clean.slice(clean.indexOf('\\begin{document}')+16, clean.lastIndexOf('\\end{document}'));
const envStart = body.indexOf('\\begin{center}');
console.log('center at', envStart);
// emulate the CURRENT takeEnv: first indexOf of \end{center}
const tag='\\begin{center}', endTag='\\end{center}';
const firstEnd = body.indexOf(endTag, envStart+tag.length);
console.log('first \\end{center} at', firstEnd, '-> inner length', firstEnd-(envStart+tag.length));
console.log('INNER =', JSON.stringify(body.slice(envStart+tag.length, firstEnd)));
console.log('REMAINDER starts =', JSON.stringify(body.slice(firstEnd+endTag.length, firstEnd+endTag.length+90)));
