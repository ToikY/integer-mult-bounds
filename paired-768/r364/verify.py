"""Verify immutable blocks, their sequenced disjoint union, and both nesting rank obstructions."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from functools import lru_cache
import gzip,json,sys,subprocess,time
def need(x,m):
    if not x:raise ValueError(m)
def dig(p):return sha256(p.read_bytes()).hexdigest()
def rank(rows):
    echelon={}
    for row in rows:
        a=list(map(F,row))
        for j,v in sorted(echelon.items()):
            x=a[j]
            if x:a=[u-x*y for u,y in zip(a,v)]
        i=next((j for j,x in enumerate(a) if x),None)
        if i is not None:echelon[i]=[u/a[i] for u in a]
    return len(echelon)
def check(a):
    need(dig(a.base/'result.json')=='40634f32710849f1693d5e691c7c9c192ee2f2dedda8f642f17f592e4aa4f5b9','sealed first block')
    need(dig(a.word)=='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326','source compressed #8027')
    w=json.loads(gzip.decompress(a.word.read_bytes()));f=w['frames']
    x,y=[json.loads((q/'result.json').read_bytes()) for q in (a.base,a.follow)]
    for n in ('triggers.json','profiles.json'):
        need(dig(a.base/n)==dig(a.follow/n),'frozen '+n)
    need(x['ranked']==y['ranked'] and x['tested']==128 and y['tested']==69 and y['unresolved_ranked']==0,'same ranked family and complementary counts')
    seq=x['geometry_obstructions']+y['geometry_obstructions']
    need([id for id,_ in seq]==x['ranked'] and len(set(map(tuple,x['ranked'])))==197,'no gaps, overlap or reordered cases')
    @lru_cache(None)
    def checks(l,h):
        lo,hi=f[str(l)],f[str(h)]
        r=rank(lo['B']+hi['B']);s=rank(lo['A']+hi['A'])
        need(r>hi['dim'] and s>8-lo['dim'],'two exact rank obstructions')
        return r,s
    pairs=Counter();rows=[]
    for triple,(productive,i,lo,hi,(j,k,dot)) in seq:
        A,D,B=triple;x0,y0=(w['start'][i],w['final'][i]) if productive else w['program'][i][2:]
        actual=sorted((B if z in (A,D) else z for z in (x0,y0)),key=lambda z:f[str(z)]['dim'])
        need(actual==[lo,hi],'trace exact chart edge from named source')
        nonzero=sum(F(r)*F(s) for r,s in zip(f[str(lo)]['B'][j],f[str(hi)]['A'][k]))
        need(nonzero==F(dot) and nonzero,'rational separator')
        r,s=checks(lo,hi);pairs[productive]+=1;rows.append([triple,i,lo,hi,r,s,str(nonzero)])
    # The pair of signed quadratic norms is always strictly positive, so setting its exact
    # row product to zero destroys this certificate on the named first boundary.
    wrong=F(0);need(wrong!=F(seq[0][1][-1][-1]),'zeroed separator rejected')
    result=dict(source=dig(a.word),first_block=dig(a.base/'result.json'),second_block=dig(a.follow/'result.json'),ranked=197,first=128,second=69,unvisited=0,distinct_rank_pairs=checks.cache_info().currsize,first_unvisited_363=x['ranked'][128],final=x['ranked'][-1],separating_paid=sum(not q for (q,_,_,_,_) in (s for _,s in seq)),separating_productive=sum(q for (q,_,_,_,_) in (s for _,s in seq)),zeroed_separator_rejected=True,independent_union_ranks_and_products=rows)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
if __name__=='__main__':
    p=ArgumentParser()
    for n in ('base','follow','word','out'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--child',action='store_true');a=p.parse_args()
    if a.child:check(a)
    else:
        t=time.monotonic();z=subprocess.run([sys.executable,'-IB',__file__,'--child',*sys.argv[1:]],timeout=15);print('exit',z.returncode,'seconds',time.monotonic()-t);raise SystemExit(z.returncode)
