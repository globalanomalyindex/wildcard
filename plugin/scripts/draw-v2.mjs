#!/usr/bin/env node
import {drawV2,freshSeed} from '../lib/sampler-v2.mjs';
try{
  let seed,mode,json=false;
  const args=process.argv.slice(2);
  for(let i=0;i<args.length;i++){
    const arg=args[i];
    if(arg==='--json'){json=true;continue;}
    if(arg==='--seed'||arg==='--mode'){
      const value=args[++i];if(value===undefined||value==='')throw new Error(`${arg} requires a value`);
      if(arg==='--seed')seed=value;else mode=value;continue;
    }
    if(arg.startsWith('--seed=')){seed=arg.slice(7);continue;}
    if(arg.startsWith('--mode=')){mode=arg.slice(7);continue;}
    throw new Error(`unsupported argument ${arg}; custom corpus flags require explicit legacy-crc-v1 replay`);
  }
  if(process.env.WILDCARD_DOMAINS||process.env.WILDCARD_CONCEPTS)throw new Error('custom corpus environment overrides require explicit legacy-crc-v1 replay');
  if(seed===undefined)seed=freshSeed();
  const receipt=await drawV2(seed,mode===undefined?{}:{mode});
  if(json)console.log(JSON.stringify(receipt,null,2));
  else{
    console.log(`mode=${receipt.mode}\n${receipt.key}=${receipt.value}\nlens=${receipt.lens}`);
    console.error(`receipt=${JSON.stringify(receipt)}`);
  }
}catch(e){console.error(`draw.sh: ${e.message}`);process.exitCode=2;}
