'use strict';
// Optional maintenance only. Node 24: node --use-system-ca scripts/tools/refresh-schemas.cjs
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..','..','assets','schemas'),manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.json')));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function refs(v){if(Array.isArray(v))return v.flatMap(refs);if(v&&typeof v==='object')return Object.entries(v).flatMap(([k,x])=>k==='$ref'?[x]:refs(x));return [];}
(async()=>{const queue=manifest.schemas.map(s=>s.url),seen=new Set(),next=[];
while(queue.length){const url=queue.shift();if(seen.has(url))continue;seen.add(url);if(!url.startsWith('https://developer.microsoft.com/json-schemas/fabric/'))throw Error('Unapproved schema host');
try{const r=await fetch(url,{redirect:'error',signal:AbortSignal.timeout(30000)});if(!r.ok)throw Error('HTTP '+r.status);const bytes=Buffer.from(await r.arrayBuffer()),doc=JSON.parse(bytes),file=hash(url).slice(0,16)+'.json';fs.writeFileSync(path.join(root,file),bytes);next.push({url,file,status:'downloaded',sha256:hash(bytes)});for(const x of refs(doc)){const u=new URL(x,url);u.hash='';queue.push(u.href);}}
catch(e){next.push({url,status:'unavailable',reason:e.message});}}
fs.writeFileSync(path.join(root,'manifest.json'),JSON.stringify({retrievedAt:new Date().toISOString(),schemas:next},null,2));console.log(JSON.stringify({downloaded:next.filter(x=>x.status==='downloaded').length,unavailable:next.filter(x=>x.status!=='downloaded')}));})().catch(e=>{console.error(e.message);process.exitCode=1});
