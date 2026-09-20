#!/usr/bin/env node
import {readFileSync,writeFileSync,statSync,realpathSync,mkdtempSync,renameSync,rmSync} from 'node:fs';
import {resolve,dirname,join} from 'node:path';
import {screenReason,parseConcepts,POLICY_VERSION} from '../lib/concept-policy.mjs';
const [action,input,log]=process.argv.slice(2);
let temporary;
try{
  if(!input)throw new Error('an input file is required');
  const rawPath=resolve(input),rawStat=statSync(rawPath);
  if(!rawStat.isFile())throw new Error('input must be a regular file');
  const text=readFileSync(rawPath,'utf8');
  if(action==='audit'){
    const records=parseConcepts(text,{min:Number(process.env.WILDCARD_MIN_CONCEPTS??150)});
    console.log(`audit OK: ${records.length} concepts, all tiers present, policy ${POLICY_VERSION}`);
  }else if(action==='screen'){
    if(!log)throw new Error('a rejection-log path is required');
    const logPath=resolve(log);
    if(rawPath===logPath)throw new Error('input and log must be different files');
    try{const target=statSync(logPath);if((target.dev===rawStat.dev&&target.ino===rawStat.ino)||realpathSync(logPath)===realpathSync(rawPath))throw new Error('input and log must be different files');if(!target.isFile())throw new Error('log must be a regular file');}catch(e){if(e.code!=='ENOENT')throw e;}
    const kept=[],rejected=[];let total=0;
    for(const raw of text.split(/\r?\n/u)){
      const line=raw.trim();if(!line||line.startsWith('#'))continue;total++;
      const reason=screenReason(raw);if(reason)rejected.push(`${reason}\t${line}`);else kept.push(line);
    }
    temporary=mkdtempSync(join(dirname(logPath),'.wildcard-screen-'));
    const staged=join(temporary,'rejections');writeFileSync(staged,rejected.length?rejected.join('\n')+'\n':'');renameSync(staged,logPath);
    if(kept.length)process.stdout.write(kept.join('\n')+'\n');
    console.error(`screen: ${total} candidates, ${kept.length} kept, ${rejected.length} rejected (policy ${POLICY_VERSION}; see ${logPath})`);
  }else throw new Error('expected screen or audit');
}catch(e){console.error(`concepts: ${e.message}`);process.exitCode=1;}finally{if(temporary)rmSync(temporary,{recursive:true,force:true});}
