"""Two distinct paid charts can add a helper transposition if both pre-store its parity."""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import gzip,json,runpy
from time import monotonic

PINS={'verify.py':'3d1f0686ec51e450c0b291c099d346b7a7620957aacaf12cf2d3b85d69a6af4d',
      'EXPECTED.json':'93b2464b4fe4ce2edf672c9b7c7fa703c89b3799cec2819597baf6eac99021e3',
      'sources/WORD.json.gz':'d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9',
      'sources/bit_native.py':'4368c62a5d42f81189d6776b8dba8c85a311b6a199b816244b545c6bb7d3dc1e'}
class Span:
    def __init__(self,rows=()):
        self.rows={}
        for v,tag in rows:self.add(v,tag)
    def add(self,v,tag):
        while v:
            p=v.bit_length()-1
            if p not in self.rows:self.rows[p]=(v,tag);return
            x,y=self.rows[p];v^=x;tag^=y
    def solve(self,v):
        tag=0
        while v:
            p=v.bit_length()-1
            if p not in self.rows:return None
            x,y=self.rows[p];v^=x;tag^=y
        return tag

def first_read(events,target):
    s=Span()
    for p,tag,v in sorted(events):
        s.add(v,1<<tag)
        solution=s.solve(target)
        if solution is not None:return p,solution
    raise ValueError('missing all-clock read')

def main():
    ap=ArgumentParser();ap.add_argument('package',type=Path);ap.add_argument('out',type=Path);args=ap.parse_args()
    t=monotonic()
    for p,h in PINS.items():assert sha256((args.package/p).read_bytes()).hexdigest()==h
    cfg=runpy.run_path(str(args.package/'verify.py'));g=runpy.run_path(str(args.package/'sources/bit_native.py'))
    w=json.loads(gzip.decompress((args.package/'sources/WORD.json.gz').read_bytes()))
    assert g['digest'](w)==cfg['WORD']
    pairs=cfg['improving_pairs'](w);expected=json.loads((args.package/'EXPECTED.json').read_bytes())
    assert len(pairs)==3112 and sha256(json.dumps(pairs,separators=(',',':')).encode()).hexdigest()==expected['pair_sha256']
    S,F,M,R,T=g['extract'](w);order=sorted(M,key=T.get);adj=g['basis'](S,M,R,order);val={i:1<<i for i in S}
    for k in order:val[k]=g['combine'](R[k],val)
    owners=sorted({i for pair in pairs for i in pair})
    result=dict(pins=PINS,pair_digest=expected['pair_sha256'],orientations=[],witness=None)
    def save(status,cursor):
        result.update(status=status,cursor=cursor,seconds=monotonic()-t);args.out.write_text(json.dumps(result,indent=2)+'\n');print(status,[o['read_count_histogram'] for o in result['orientations']],result['witness'],result['seconds'])
    for rev in (False,True):
        read,send=defaultdict(list),defaultdict(list)
        st,fn=(F,S) if rev else (S,F)
        for h in S:
            read[st[h]].append((-1,h,1<<h));send[fn[h]].append((len(M),h,1<<h))
        for pos,k in enumerate(reversed(order) if rev else order):
            a,b=M[k][::-1] if rev else M[k]
            read[b].append((pos,k,adj[k] if rev else val[k]));send[a].append((pos,k,val[k] if rev else adj[k]))
        charts=defaultdict(list)
        for c in sorted(map(int,w['frames'])):
            if monotonic()-t>60:save('capped',['all',rev,c]);return
            rk,sig=cfg['residues']([v for _,_,v in read[c]],owners)
            for i,j in pairs:
                if sig[i]==sig[j]:charts[i,j].append(c)
        rec=dict(reverse=rev,read_count_histogram=dict(Counter(len(charts[p]) for p in pairs)),readable=[[i,j,charts[i,j]] for i,j in pairs if charts[i,j]],trials=[])
        result['orientations'].append(rec)
        for i,j in pairs:
            target=(1<<i)^(1<<j)
            if len(charts[i,j])<2:continue
            first={c:first_read(read[c],target) for c in charts[i,j]}
            for a,b in combinations(charts[i,j],2):
                if monotonic()-t>60:save('capped',['chronology',rev,i,j,a,b]);return
                cut=max(first[a][0],first[b][0])
                s=Span((v,1<<tag) for c in (a,b) for pos,tag,v in send[c] if pos>cut)
                sol=s.solve(target);rec['trials'].append([i,j,a,b,cut,sol is not None])
                if sol is None:continue
                result['witness']=dict(reverse=rev,owners=[i,j],charts=[a,b],cut=cut,first={str(c):[first[c][0],list(g['indices'](first[c][1]))] for c in (a,b)},injections=list(g['indices'](sol)))
                save('hit',None);return
    save('exhausted',None)
if __name__=='__main__':main()
