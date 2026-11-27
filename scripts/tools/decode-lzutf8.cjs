'use strict';
// Vendored MIT lzutf8 0.6.3. No network, dynamic imports, or user-code evaluation.
const fs=require('node:fs'),lz=require('../vendor/lzutf8/lzutf8.js');
const input=fs.readFileSync(0,'utf8').trim();
if(input.length>1024*1024 || !/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(input))throw Error('Invalid/bounded Base64 input');
const output=lz.decompress(input,{inputEncoding:'Base64'});
if(Buffer.byteLength(output,'utf8')>32*1024*1024)throw Error('Decompressed payload limit');
// Do not parse/stringify here: preserve all original numeric literals for Python.
process.stdout.write(output);
