import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(new URL('..',import.meta.url).pathname);
const pkg=JSON.parse(fs.readFileSync(path.join(root,'package.json'),'utf8'));
const report=Object.keys(pkg.dependencies).map(name=>{
 const p=JSON.parse(fs.readFileSync(path.join(root,'node_modules',name,'package.json'),'utf8'));
 return {name,version:p.version,license:p.license||'See package license',repository:p.repository?.url||p.repository||null};
});
fs.writeFileSync(path.join(root,'DEPENDENCY_LICENSES.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
