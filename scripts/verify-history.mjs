// Read-only: compares frozen artifacts against the pinned source snapshot.
import {readFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve,dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
export const ROOT=resolve(dirname(fileURLToPath(import.meta.url)),'..');
export function verifyHistory(root=ROOT){
  const snapshot=JSON.parse(readFileSync(join(root,'research/audit-2026-09/history-manifest.json'),'utf8'));
  const changed=[];
  for(const entry of snapshot.files){
    const file=join(root,entry.path);
    if(!existsSync(file)){changed.push({path:entry.path,reason:'missing'});continue;}
    const actual=createHash('sha256').update(readFileSync(file)).digest('hex');
    if(actual!==entry.sha256)changed.push({path:entry.path,reason:'hash-mismatch',expected:entry.sha256,actual});
  }
  return {sourceCommit:snapshot.sourceCommit,checkedFiles:snapshot.files.length,unchanged:changed.length===0,changed};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const result=verifyHistory();console.log(JSON.stringify(result,null,2));if(!result.unchanged)process.exitCode=1;
}
