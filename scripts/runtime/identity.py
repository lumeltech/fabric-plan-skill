"""Lossless native IDs. Seed-zero XXH3-64, translated from xxHash v0.8.3.

xxHash copyright (c) 2012-2023 Yann Collet. BSD 2-Clause:
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

Upstream: https://github.com/Cyan4973/xxHash/blob/v0.8.3/xxhash.h
Only hash the exact external key specified by the selected identity domain.
This implementation does not infer field IDs from labels or column order.
"""
import secrets, re
MASK=(1<<64)-1
P1=0x9e3779b185ebca87; P2=0xc2b2ae3d27d4eb4f; P3=0x165667b19e3779f9
P4=0x85ebca77c2b2ae63; P5=0x27d4eb2f165667c5
Q1=0x9e3779b1; Q2=0x85ebca77; Q3=0xc2b2ae3d
MX1=0x165667919e3779f9; MX2=0x9fb21c651e98df25
SECRET=bytes.fromhex('''
b8fe6c3923a44bbe7c01812cf721ad1c ded46de9839097db7240a4a4b7b3671f
cb79e64eccc0e578825ad07dccff7221 b8084674f743248ee03590e6813a264c
3c2852bb91c300cb88d0658b1b532ea3 71644897a20df94e3819ef46a9deacd8
a8fa763fe39c343ff9dcbbc7c70b4f1d 8a51e04bcdb45931c89f7ec9d9787364
eac5ac8334d3ebc3c581a0fffa1363eb 170ddd51b7f0da49d316552629d4689e
2b16be587d47a1fc8ff8b8d17ad031ce 45cb3a8f95160428afd7fbcabb4b407e''')
def read(b,p,n=8): return int.from_bytes(b[p:p+n],'little')
def fold(a,b):
    p=a*b
    return ((p&MASK)^(p>>64))&MASK
def rot(h,n): return ((h<<n)|(h>>(64-n)))&MASK
def av3(h):
    h &= MASK; h^=h>>37; h=h*MX1&MASK
    return h^(h>>32)
def av64(h):
    h &= MASK; h^=h>>33; h=h*P2&MASK; h^=h>>29; h=h*P3&MASK
    return h^(h>>32)
def xxh3(data):
    if isinstance(data,str): data=data.encode('utf-8')
    n=len(data); s=SECRET
    def mix(p,q): return fold(read(data,p)^read(s,q),read(data,p+8)^read(s,q+8))
    if n==0: return av64(read(s,56)^read(s,64))
    if n<=3: return av64(((data[0]<<16)|(data[n>>1]<<24)|data[-1]|(n<<8))^(read(s,0,4)^read(s,4,4)))
    if n<=8:
        h=((read(data,0,4)<<32)+read(data,n-4,4))^(read(s,8)^read(s,16))
        h^=rot(h,49)^rot(h,24); h=h*MX2&MASK; h^=(h>>35)+n; h=h*MX2&MASK
        return h^(h>>28)
    if n<=16:
        lo=read(data,0)^read(s,24)^read(s,32); hi=read(data,n-8)^read(s,40)^read(s,48)
        swap=int.from_bytes(lo.to_bytes(8,'little'),'big')
        return av3(n+swap+hi+fold(lo,hi))
    if n<=128:
        h=n*P1
        for i in range((n-1)//32,-1,-1): h+=mix(16*i,32*i)+mix(n-16*(i+1),32*i+16)
        return av3(h)
    if n<=240:
        h=n*P1+sum(mix(16*i,16*i) for i in range(8)); h=av3(h)
        tail=mix(n-16,119)
        for i in range(8,n//16): tail+=mix(16*i,16*(i-8)+3)
        return av3(h+tail)
    a=[Q3,P1,P2,P3,P4,Q2,P5,Q1]
    def stripe(p,q):
        for i in range(8):
            v=read(data,p+8*i); k=v^read(s,q+8*i)
            a[i^1]=(a[i^1]+v)&MASK; a[i]=(a[i]+(k&0xffffffff)*(k>>32))&MASK
    blocks=(n-1)//1024
    for block in range(blocks):
        for j in range(16): stripe(block*1024+j*64,j*8)
        for i in range(8): a[i]=((a[i]^(a[i]>>47)^read(s,128+8*i))*Q1)&MASK
    for j in range(((n-1)-blocks*1024)//64): stripe(blocks*1024+j*64,j*8)
    stripe(n-64,121)
    return av3(n*P1+sum(fold(a[2*i]^read(s,11+16*i),a[2*i+1]^read(s,19+16*i)) for i in range(4)))
def native_id(value):
    if not isinstance(value,str) or not re.fullmatch(r'0|[1-9][0-9]*',value) or int(value)>MASK:
        raise ValueError('Native Id must be a decimal u64 string')
    return value
AGGREGATION_ALIASES={'avg':'average','min':'minimum','max':'maximum'}
def product_aggregation(value):
    """The product's pivot aggregation name: avg, min and max become average, minimum and maximum."""
    return AGGREGATION_ALIASES.get(value,value) if isinstance(value,str) else value
def new_native_id(taken):
    """A random nonzero decimal u64 string that is not in ``taken``."""
    while True:
        value=str(secrets.randbits(64))
        if value!='0' and value not in taken: return value
class Registry:
    def __init__(self,entries=None): self.entries=dict(entries or {})
    def bind(self,key,value):
        value=native_id(value)
        if key in self.entries and self.entries[key]!=value: raise ValueError('Identity changed for '+key)
        if value in self.entries.values() and self.entries.get(key)!=value: raise ValueError('Identity collision: '+key)
        self.entries[key]=value; return value
    def custom(self,key):
        if key in self.entries: return self.entries[key]
        return self.bind(key,new_native_id(set(self.entries.values())))
    def semantic(self,external_key,column_type='Measure',aggregation=None):
        if not external_key: raise ValueError('Missing exact assignment key')
        if column_type!='Measure' and not aggregation: raise ValueError('Non-measure source needs explicit aggregation')
        prefix='' if column_type=='Measure' else product_aggregation(aggregation).upper()+'__'
        return self.bind('semantic:'+prefix+external_key,str(xxh3(prefix+external_key)))
