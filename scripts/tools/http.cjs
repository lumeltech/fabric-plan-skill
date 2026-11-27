'use strict';
// Internal stdin/stdout adapter. Never print request headers or credentials.
const fs=require('node:fs'),path=require('node:path');
const ORIGIN='https://api.fabric.microsoft.com';
// Same route list as scripts/runtime/transport.py, from one shared file.
const PUBLIC_ROUTE=new RegExp(JSON.parse(fs.readFileSync(path.join(__dirname,'..','runtime','public_routes.json'),'utf8')).pattern);
// Check the raw path from the request string: URL() would already have normalised dot segments.
function isPublicFabricUrl(url){
    let u;try{u=new URL(url);}catch{return false;}
    if(u.origin!==ORIGIN||u.username||u.password||u.hash||!url.startsWith(ORIGIN+'/'))return false;
    return PUBLIC_ROUTE.test(url.slice(ORIGIN.length).split('?')[0]);
}
async function main(){const q=JSON.parse(fs.readFileSync(0,'utf8'));
if(!isPublicFabricUrl(q.url)||!/^Bearer \S+$/i.test(q.headers.Authorization))
    throw Error('Expected public Fabric bearer request');
const r=await fetch(q.url,{method:q.method,headers:q.headers,redirect:'error',signal:AbortSignal.timeout(60000),...(q.bodyBase64===null?{}:{body:Buffer.from(q.bodyBase64,'base64')})});
const bytes=Buffer.from(await r.arrayBuffer());if(bytes.length>64*1024*1024)throw Error('Response size limit');
const raw=bytes.toString('utf8'); let body,valid=false;try{body=raw?JSON.parse(raw):null;valid=!!raw;}catch{body={binaryBase64:bytes.toString('base64'),bytes:bytes.length,contentType:r.headers.get('content-type')}}
// JSON.parse would round bare native IDs. Return raw response text for the Python exact parser.
process.stdout.write('{"status":'+r.status+',"headers":'+JSON.stringify(Object.fromEntries(r.headers))+',"body":'+(valid?raw:JSON.stringify(body))+'}');
}
module.exports={isPublicFabricUrl};
if(require.main===module)main().catch(()=>{process.stderr.write('HTTPS request failed\n');process.exitCode=1;});
