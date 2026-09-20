// GENERATED from plugin/lib/sampler-v2.mjs; do not edit.
import {CORPUS,CORPUS_SHA256} from './corpus-v2.js';

export const SAMPLER='sha256-counter-v2';
const encoder=new TextEncoder();
const DOMAIN=encoder.encode('wildcard/sampler/v2');
const WORD_SPACE=4294967296;
function freezeTree(value){
  if(value&&typeof value==='object'){Object.values(value).forEach(freezeTree);Object.freeze(value);}
  return value;
}
freezeTree(CORPUS);
let corpusVerification;
async function verifyCorpus(){
  if(!corpusVerification)corpusVerification=(async()=>{
    if(!globalThis.crypto?.subtle)throw new Error('SHA-256 requires Web Crypto; no fallback is available');
    const digest=await globalThis.crypto.subtle.digest('SHA-256',encoder.encode(JSON.stringify(CORPUS,null,2)+'\n'));
    const actual=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
    if(actual!==CORPUS_SHA256)throw new Error('bundled corpus hash does not match its declared digest');
  })();
  await corpusVerification;
}

export function validateSeed(seed){
  if(typeof seed!=='string'||seed.length===0)throw new TypeError('seed must be a nonempty string');
  if(seed.includes('\0'))throw new TypeError('seed must not contain NUL');
  for(let i=0;i<seed.length;i++){
    const c=seed.charCodeAt(i);
    if(c>=0xd800&&c<=0xdbff){const next=seed.charCodeAt(++i);if(!(next>=0xdc00&&next<=0xdfff))throw new TypeError('seed must contain Unicode scalar values');}
    else if(c>=0xdc00&&c<=0xdfff)throw new TypeError('seed must contain Unicode scalar values');
  }
  if(encoder.encode(seed).length>1024)throw new RangeError('seed exceeds 1024 UTF-8 bytes');
  return seed;
}

export function shellQuote(value){return `'${String(value).replaceAll("'",`'"'"'`)}'`;}

export function frameBytes(seed,purpose,counter=0n){
  const s=encoder.encode(validateSeed(seed));
  if(typeof purpose!=='string'||!/^[-a-z0-9]+$/.test(purpose)||purpose.length>128)throw new TypeError('purpose must be a bounded ASCII identifier');
  if(typeof counter!=='bigint'||counter<0n||counter>0xffffffffffffffffn)throw new RangeError('counter must be uint64');
  const p=encoder.encode(purpose),bytes=new Uint8Array(DOMAIN.length+4+s.length+4+p.length+8),view=new DataView(bytes.buffer);
  let at=0;bytes.set(DOMAIN,at);at+=DOMAIN.length;view.setUint32(at,s.length,false);at+=4;bytes.set(s,at);at+=s.length;
  view.setUint32(at,p.length,false);at+=4;bytes.set(p,at);at+=p.length;view.setBigUint64(at,counter,false);
  return bytes;
}

export function createWordStream(seed,purpose){
  validateSeed(seed);
  let counter=0n,words=[],cursor=0;
  return async()=>{
    if(cursor===words.length){
      if(!globalThis.crypto?.subtle)throw new Error('SHA-256 requires Web Crypto; no fallback is available');
      const digest=await globalThis.crypto.subtle.digest('SHA-256',frameBytes(seed,purpose,counter));
      counter++;const view=new DataView(digest);words=Array.from({length:8},(_,i)=>view.getUint32(i*4,false));cursor=0;
    }
    return words[cursor++];
  };
}

export async function uniformInt(n,nextWord,{maxAttempts=1000000}={}){
  if(!Number.isInteger(n)||n<1||n>WORD_SPACE)throw new RangeError('modulus must be an integer from 1 through 2^32');
  if(!Number.isInteger(maxAttempts)||maxAttempts<1)throw new RangeError('maxAttempts must be a positive integer');
  const limit=Math.floor(WORD_SPACE/n)*n;
  for(let i=0;i<maxAttempts;i++){
    const word=await nextWord();
    if(!Number.isInteger(word)||word<0||word>=WORD_SPACE)throw new Error('source returned an invalid uint32 word');
    if(word<limit)return word%n;
  }
  throw new Error('rejection sampling exhausted its attempt bound');
}

export function freshSeed(){
  if(!globalThis.crypto?.getRandomValues)throw new Error('OS entropy is unavailable; no fallback is available');
  const bytes=new Uint8Array(32);globalThis.crypto.getRandomValues(bytes);
  return Array.from(bytes,b=>b.toString(16).padStart(2,'0')).join('');
}

export async function drawV2(seed,{mode}={}){
  validateSeed(seed);
  await verifyCorpus();
  if(mode!==undefined&&mode!=='specialist'&&mode!=='concept')throw new TypeError('mode must be specialist or concept');
  const selectedMode=mode??((await uniformInt(2,createWordStream(seed,'mode')))===0?'specialist':'concept');
  const entries=CORPUS.pools[selectedMode];
  const index=await uniformInt(entries.length,createWordStream(seed,`${selectedMode}-index`));
  const lensIndex=await uniformInt(CORPUS.lenses.length,createWordStream(seed,'lens'));
  const entry=entries[index],lens=CORPUS.lenses[lensIndex];
  return {
    schemaVersion:2,sampler:SAMPLER,seedEncoding:'utf-8',seed,
    corpusVersion:CORPUS.corpusVersion,corpusSha256:CORPUS_SHA256,
    lensVersion:CORPUS.lensVersion,modePolicy:'equal-mode',modeForced:mode!==undefined,
    mode:selectedMode,key:selectedMode==='specialist'?'domain':'concept',
    entryId:entry.id,entryIndex:index,value:entry.value,lens,lensIndex,
  };
}

export async function replayV2(receipt){
  if(!receipt||receipt.sampler!==SAMPLER||receipt.schemaVersion!==2)throw new Error('unsupported receipt version');
  if(receipt.corpusSha256!==CORPUS_SHA256||receipt.corpusVersion!==CORPUS.corpusVersion)throw new Error('receipt corpus version/hash does not match the bundled snapshot');
  if(typeof receipt.modeForced!=='boolean')throw new Error('receipt modeForced must be boolean');
  const replay=await drawV2(receipt.seed,receipt.modeForced?{mode:receipt.mode}:{});
  for(const [key,value] of Object.entries(replay))if(receipt[key]!==value)throw new Error(`receipt mismatch: ${key}`);
  return replay;
}
