'use strict';
const fs=require('node:fs'),lz=require('../vendor/lzutf8/lzutf8.js');
const input=fs.readFileSync(0,'utf8');
if(Buffer.byteLength(input,'utf8')>32*1024*1024)throw Error('Input size limit');
// Compress raw text, preserving exact decimal/u64 literals. No JSON round trip.
process.stdout.write(lz.compress(input,{outputEncoding:'Base64'}));
