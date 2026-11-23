"""HTTPS transport, mutation journals, bounded LRO polling, explicit auth context.
No implicit endpoint discovery guesses. Supply metadata-resolved API roots.
"""
import urllib.request, urllib.error, urllib.parse, email.utils, datetime, time, os, base64, json, re, subprocess
from pathlib import Path
from .codec import load, loads, dumps, save, sha, definition_hash
from uuid import uuid4
class HttpError(RuntimeError):
    def __init__(self,status,body=None):
        self.status=status
        self.category="authentication" if status in (401,403) else "http-error"
        super().__init__("HTTP "+str(status))
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def retry_seconds(headers,default=2):
    s=headers.get('retry-after')
    if s is None: return default
    try: return max(0,int(s))
    except ValueError:
        try: return max(0,(email.utils.parsedate_to_datetime(s)-datetime.datetime.now(datetime.timezone.utc)).total_seconds())
        except (ValueError,TypeError): return default
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): return None
class Client:
    def __init__(self,base,token_env,allowed_hosts=None,journal=None,adapter=None,sleep=time.sleep):
        self.base=base.rstrip('/'); self.token_env=token_env
        host='api.fabric.microsoft.com'
        if self.base!='https://'+host+'/v1' or (allowed_hosts is not None and host not in allowed_hosts):
            raise ValueError('Expected the public Fabric API base https://api.fabric.microsoft.com/v1')
        self.journal=Path(journal or 'run'); self.journal.mkdir(parents=True,exist_ok=True)
        self.adapter=adapter or self._http; self.sleep=sleep
        self.check_url(base)
    def check_url(self,url):
        p=urllib.parse.urlsplit(url)
        if p.scheme!='https' or p.netloc!='api.fabric.microsoft.com' or p.fragment:
            raise ValueError('Unapproved HTTPS endpoint')
        if {'coreapi','generatemwctokenv2'} & set(urllib.parse.unquote(p.path).lower().split('/')):
            raise ValueError('Expected a public Fabric API endpoint')
        return url
    def _token(self):
        t=os.environ.get(self.token_env)
        if not t: raise ValueError('Set '+self.token_env+' in the process environment')
        # JWT expiration is only a preflight convenience, not signature verification.
        if t.count('.')==2:
            try: c=json.loads(base64.urlsafe_b64decode(t.split('.')[1]+'==='))
            except Exception: c={}
            if c.get('exp',float('inf'))<=time.time()+5: raise ValueError('AUTH_EXPIRED: renew environment credential and resume')
        return t
    def _http(self,method,url,headers,body):
        node=os.environ.get('FABRIC_PLAN_HTTP_NODE')
        if node:
            # Optional managed-Windows transport. Credentials travel over stdin, not argv/files.
            script=Path(__file__).resolve().parent.parent/'tools/http.cjs'
            request={'method':method,'url':url,'headers':headers,'bodyBase64':base64.b64encode(body).decode() if body is not None else None}
            r=subprocess.run([node,'--use-system-ca',str(script)],input=dumps(request),text=True,encoding='utf-8',capture_output=True,timeout=70)
            if r.returncode: raise RuntimeError('Node HTTPS transport failed')
            return loads(r.stdout)
        req=urllib.request.Request(url,data=body,headers=headers,method=method)
        try: r=urllib.request.build_opener(NoRedirect).open(req,timeout=60)
        except urllib.error.HTTPError as e: r=e
        with r:
            raw=r.read(64*1024*1024+1); typ=r.headers.get('Content-Type','')
            if len(raw)>64*1024*1024:raise ValueError('Response size limit')
            try: data=loads(raw.decode('utf-8')) if raw else None
            except (ValueError,UnicodeDecodeError): data={'binaryBase64':base64.b64encode(raw).decode(),'bytes':len(raw),'contentType':typ}
            return {'status':r.status,'headers':{k.lower():v for k,v in r.headers.items()},'body':data}
    def request(self,method,route,body=None,label=None,content_type='application/json',accept=None):
        method=method.upper()
        target = self.check_url(route if route.startswith('https://') else self.base+'/'+route.lstrip('/'))
        from .planning_integrity import guard_write
        guard_write(method,route,body)
        token=self._token()
        url=target
        if token in url: raise ValueError('Credential in URL')
        raw=body if isinstance(body,bytes) else None if body is None else dumps(body).encode()
        mutable=method not in ('GET','HEAD')
        if mutable and not label: raise ValueError('Mutation requires stable journal label')
        if label and not re.fullmatch(r'[a-zA-Z0-9_.-]+',label): raise ValueError('Unsafe journal label')
        intent={'method':method,'url':url,'contentType':content_type,'bodyHash':sha(raw) if raw is not None else None}
        ip=self.journal/(label+'.intent.json') if label else None
        rp=self.journal/(label+'.response.json') if label else None
        if ip and ip.exists():
            old=load(ip)
            if old['request']!=intent: raise ValueError('Journal label reused for different request')
            if rp.exists():
                result=load(rp)
                if result.get('sensitiveBodyOmitted'): raise RuntimeError('Credential response was deliberately not persisted; issue a new auth request label')
                if result['status']>=400: raise HttpError(result['status'],result.get('body'))
                return result
            raise RuntimeError('UNCERTAIN_SUBMISSION: reconcile server state before resubmitting '+label)
        headers={'Authorization':'Bearer '+token,'Content-Type':content_type}
        if accept is not None:
            if not isinstance(accept,str) or '\r' in accept or '\n' in accept:raise ValueError('Invalid Accept header')
            headers['Accept']=accept
        if ip: save(ip,{'request':intent,'submittedAt':now(),'state':'submitted'})
        for attempt in range(4):
            try: r=self.adapter(method,url,headers,raw)
            except Exception:
                if not mutable and attempt<3: self.sleep(2*(attempt+1)); continue
                raise RuntimeError('Request interrupted; mutation intent retained' if mutable else 'GET interrupted') from None
            r['headers']={k.lower():v for k,v in r.get('headers',{}).items()}
            if token in dumps(r): raise RuntimeError('Response contained credential; not journaled')
            if isinstance(r.get('body'),dict) and 'binaryBase64' in r['body'] and token.encode() in base64.b64decode(r['body']['binaryBase64'],validate=True):
                raise RuntimeError('Binary response contained credential; not journaled')
            # Retry reads only. Even a throttled write is explicit, resumable reconciliation.
            if not mutable and (r['status']==429 or r['status']>=500) and attempt<3:
                self.wait(retry_seconds(r['headers'])); continue
            clean={'status':r['status'],'headers':{k:v for k,v in r['headers'].items() if k in ('location','retry-after','x-ms-operation-id','etag','requestid','x-ms-request-id','content-type','content-range')},'body':r.get('body')}
            if rp:
                sensitive=False
                def redact(x):
                    nonlocal sensitive
                    if isinstance(x,dict):
                        result={}
                        for k,v in x.items():
                            if k.casefold() in ('token','access_token','accesstoken','originalaadtoken','refresh_token','refreshtoken','mwctoken','authorization','password','client_secret'):
                                result[k]='<not-persisted>'; sensitive=True
                            else: result[k]=redact(v)
                        return result
                    if isinstance(x,list): return [redact(v) for v in x]
                    return x
                persisted=redact(clean)
                if sensitive: persisted['sensitiveBodyOmitted']=True
                save(rp,persisted)
            if not 200<=r['status']<300: raise HttpError(r['status'],r.get('body'))
            return clean
    def wait(self,seconds):
        # Keep individual waits bounded for interactive progress/handoff.
        while seconds>0:
            delay=min(seconds,30); self.sleep(delay); seconds-=delay
    def finish(self,initial,label,max_polls=120,max_seconds=1800):
        if initial['status']!=202: return initial
        cp=self.journal/(label+'.operation.json')
        h=initial['headers']; loc=h.get('location')
        if not loc:
            op=h.get('x-ms-operation-id')
            if not op: raise ValueError('202 missing Location and operation ID')
            loc=self.base+'/operations/'+urllib.parse.quote(op,safe='')
        loc=urllib.parse.urljoin(self.base+'/',loc); self.check_url(loc)
        if cp.exists():
            state=load(cp)
            if state['location']!=loc: raise ValueError('Operation checkpoint mismatch')
        else: state={'location':loc,'phase':'poll','startedAt':now()}
        save(cp,state); start=time.monotonic(); delay=retry_seconds(h)
        for i in range(max_polls):
            if time.monotonic()-start+delay>max_seconds: raise TimeoutError('PENDING: resume same operation checkpoint')
            self.wait(delay); r=self.request('GET',loc)
            status=(r.get('body') or {}).get('status')
            save(cp,{**state,'lastStatus':status,'phase':'poll','lastPollAt':now()})
            if status in ('Failed','Canceled','Cancelled'): raise RuntimeError('Operation '+status)
            if status=='Succeeded':
                result_url=r['headers'].get('location')
                if not result_url or result_url.rstrip('/')==loc.rstrip('/'): result_url=loc.rstrip('/')+'/result'
                result_url=urllib.parse.urljoin(loc,result_url); self.check_url(result_url)
                result=self.request('GET',result_url)
                save(cp,{**state,'phase':'complete','resultUrl':result_url})
                return result
            # Some operation Location responses directly return the result.
            if r['status']==200 and status is None and isinstance(r.get('body'),dict) and ('definition' in r['body'] or 'id' in r['body']):
                save(cp,{**state,'phase':'complete'}); return r
            if r['headers'].get('location'):
                loc=urllib.parse.urljoin(loc,r['headers']['location']); self.check_url(loc)
            delay=retry_seconds(r['headers'])
        raise TimeoutError('PENDING: resume same operation checkpoint')
    def paged(self,route):
        values=[]; seen=set()
        while route:
            if route in seen: raise ValueError('Pagination loop')
            seen.add(route); r=self.request('GET',route)['body']; values.extend(r.get('value',[]))
            route=r.get('continuationUri')
            if not route and r.get('continuationToken'): raise ValueError('Continuation token requires endpoint-specific parameter adapter')
        return values
def plan_operation(client,workspace,kind,plan_id=None,definition=None,name=None,label='plan',baseline_hash=None):
    base='/workspaces/'+urllib.parse.quote(workspace,safe='')+'/plans'
    if kind in ('create','create-blank'):
        if not name or (kind=='create' and not definition): raise ValueError('Name and full definition required')
        body={'displayName':name}; route=base
        if kind=='create': body['definition']=definition.get('definition',definition)
    elif kind in ('export','update'):
        if not plan_id: raise ValueError('planId required')
        if kind=='update':
            if not baseline_hash: raise ValueError('Update requires the reviewed definition hash')
            # Journal replay can only resume the identical submission; a new one needs a fresh read.
            if not (client.journal/(label+'.intent.json')).exists():
                fresh=plan_operation(client,workspace,'export',plan_id,label=label+'-baseline-'+uuid4().hex)
                if definition_hash(fresh['body'])!=baseline_hash:
                    raise ValueError('Destination changed since reviewed baseline')
        route=base+'/'+urllib.parse.quote(plan_id,safe='')+('/getDefinition' if kind=='export' else '/updateDefinition')
        body={} if kind=='export' else {'definition':definition.get('definition',definition)}
    else: raise ValueError('Unknown Plan operation')
    return client.finish(client.request('POST',route,body,label=label),label)
