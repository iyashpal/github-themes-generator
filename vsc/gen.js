// usage: node gen.js [srcDir=src] [outFile=vscode.json] [--upstream-only]
//   --upstream-only skips the tritanopia variants, so an unpatched upstream src can be built for comparison
const fs=require('fs'), path=require('path'), chroma=require('chroma-js');
const args=process.argv.slice(2), only=args.includes('--upstream-only'), pos=args.filter(a=>!a.startsWith('--'));
const SRC=path.resolve(__dirname, pos[0]||'src'), OUT=path.resolve(__dirname, pos[1]||'vscode.json');
const getTheme=require(SRC+'/theme'), getClassic=require(SRC+'/classic/theme'), {getColors}=require(SRC+'/colors');
const variants={'light-default':'light','light-high-contrast':'light_high_contrast','light-colorblind':'light_colorblind','light-tritanopia':'light_tritanopia',
 'dark-default':'dark','dark-high-contrast':'dark_high_contrast','dark-colorblind':'dark_colorblind','dark-tritanopia':'dark_tritanopia','dark-dimmed':'dark_dimmed'};
const flat=(o,p='',r={})=>{for(const[k,v]of Object.entries(o)){const kk=p?p+'.'+k:k; if(Array.isArray(v)) v.forEach((x,i)=>{ if(typeof x==='string'&&chroma.valid(x)) r[kk+'.'+i]=chroma(x).hex()}); else if(v&&typeof v==='object') flat(v,kk,r); else if(typeof v==='string'&&chroma.valid(v)) r[kk]=chroma(v).hex();} return r;};
const out={};
for(const[n,t]of Object.entries(variants)){ if(only&&t.includes('tritanopia')) continue; const th=getTheme({theme:t,name:n}); out[n]={colors:th.colors,tokenColors:th.tokenColors,primer:flat(getColors(t))}; }
for(const s of ['light','dark']){ const th=getClassic({style:s,name:s}); out[s]={colors:th.colors,tokenColors:th.tokenColors,primer:null}; }
fs.writeFileSync(OUT,JSON.stringify(out,null,1));
