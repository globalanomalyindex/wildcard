// One finite lexical policy shared by acquisition screening and final validation.
// These inherited exclusions are editorial rules, not a semantic safety guarantee.
export const POLICY_VERSION='concept-screen-v1';
export const TIERS=['everyday','natural','scientific','abstract'];
export const FACETS=['chemistry','craft','earth','energy','life','light','math','matter','mind','physics','signal','society','sound','structure','time'];
const names=/violence|war|weapon|gun|rifle|missile|bomb|nuclear|massacre|genocide|terror|murder|assassinat|suicide|self-harm|rape|sexual|porn|nud(e|ity)|slur|nazi|hitler|holocaust|slavery|lynch|abortion|election|president|senator|parliament|communis|fascis|jihad|crusade|caliph|prophet|messiah|christ|allah|buddha|disease|cancer|tumor|pandemic|overdose|cartel|cocaine|heroin|gambl|casino/i;
const person=/\b(born|footballer|politician|singer|actor|actress|rapper|king|queen|emperor|dictator|pope|saint|president|sir|dame)\b/i;
const ip=/\b(inc|corp|llc|ltd|trademark|franchise|brand|disney|marvel|pixar|nintendo|pokemon|mcdonald|coca-cola)\b|star wars/i;
export const normalizeLabel=s=>s.normalize('NFC').trim().replace(/\s+/gu,' ').toLowerCase();
export function screenReason(title){
  if(/[\u0000-\u001f\u007f]/u.test(title))return 'control';
  const s=title.trim();if(!s)return 'empty';if(s.includes('|'))return 'pipe';
  if(/\(disambiguation\)|^list of|^index of|^outline of|^history of/i.test(s))return 'meta';
  if([...s].length>50)return 'toolong';if(names.test(s))return 'names';if(person.test(s))return 'person';if(ip.test(s))return 'ip';return null;
}
export function parseConcepts(text,{min=150}={}){
  if(!Number.isInteger(min)||min<1)throw new Error('minimum concept count must be a positive integer');
  const records=[],errors=[],seen=new Set(),tiers=new Set();
  for(const [offset,line]of text.split(/\r?\n/u).entries()){
    if(!line.trim()||line.trimStart().startsWith('#'))continue;
    const n=offset+1,fields=line.split(' | ');
    if(fields.length!==3){errors.push(`line ${n}: expected 3 fields`);continue;}
    const [value,tier,facet]=fields.map(s=>s.trim()),reason=screenReason(fields[0]);
    if(reason)errors.push(`line ${n}: ${reason} rule rejects ${value}`);
    if(/[\u0000-\u001f\u007f]/u.test(line))errors.push(`line ${n}: control character`);
    const normalized=normalizeLabel(value);if(seen.has(normalized))errors.push(`line ${n}: normalized duplicate ${value}`);seen.add(normalized);
    if(!TIERS.includes(tier))errors.push(`line ${n}: bad tier ${tier}`);else tiers.add(tier);
    if(!FACETS.includes(facet))errors.push(`line ${n}: invalid or empty facet ${facet}`);
    records.push({value,tier,facet,sourceLine:n});
  }
  if(records.length<min)errors.push(`too few concepts: ${records.length} < ${min}`);
  for(const tier of TIERS)if(!tiers.has(tier))errors.push(`missing tier: ${tier}`);
  if(errors.length)throw new Error(errors.join('\n'));
  return records;
}
