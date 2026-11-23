'use strict';
// Internal stdin/stdout adapter. Never print request headers or credentials.
const fs=require('node:fs');
(async()=>{const q=JSON.parse(fs.readFileSync(0,'utf8'));
const u=new URL(q.url);if(u.origin!=='https://api.fabric.microsoft.com'||u.username||u.password||u.hash)throw Error('Invalid public Fabric URL');
if(!/^Bearer \S+$/i.test(q.headers.Authorization) ||
    decodeURIComponent(u.pathname).split('/').some(s=>['coreapi','generatemwctokenv2'].includes(s.toLowerCase())))
    throw Error('Expected public Fabric bearer request');
const r=await fetch(q.url,{method:q.method,headers:q.headers,redirect:'error',signal:AbortSignal.timeout(60000),...(q.bodyBase64===null?{}:{body:Buffer.from(q.bodyBase64,'base64')})});
const bytes=Buffer.from(await r.arrayBuffer());if(bytes.length>64*1024*1024)throw Error('Response size limit');
const raw=bytes.toString('utf8'); let body,valid=false;try{body=raw?JSON.parse(raw):null;valid=!!raw;}catch{body={binaryBase64:bytes.toString('base64'),bytes:bytes.length,contentType:r.headers.get('content-type')}}
// JSON.parse would round bare native IDs. Return raw response text for the Python exact parser.
process.stdout.write('{"status":'+r.status+',"headers":'+JSON.stringify(Object.fromEntries(r.headers))+',"body":'+(valid?raw:JSON.stringify(body))+'}');
})().catch(()=>{process.stderr.write('HTTPS request failed\n');process.exitCode=1;});
