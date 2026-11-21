"""Independent all-clock membership count on the literal forward and adjoint tapes."""
from collections import defaultdict, Counter
from hashlib import sha256
from itertools import combinations
import json,runpy,sys
from time import monotonic
from pathlib import Path

def main():
    package,source,output=map(Path,sys.argv[1:]);begin=monotonic()
    checker=package/'crosscheck.py';assert sha256(checker.read_bytes()).hexdigest()=='9af8f306b040dd0725e1c4dbee2403e65fa8cd4c48adc83827afe16b70f40632'
    independent=runpy.run_path(str(checker));engine=package/'sources/binary_operator.py'
    assert sha256(engine.read_bytes()).hexdigest()==independent['ENGINE']
    op=runpy.run_path(str(engine));word=op['load_json'](package/'sources/WORD.json.gz',op['WORD_GZIP'],True)
    assert op['canonical_hash'](word)==op['WORD']
    atlas=op['Atlas'](word['frames'])
    owners=range(222,word['public']);start,end=word['start'],word['final']
    ranks=[atlas.grade(a,b) for a,b in zip(start,end)]
    pairs=[]
    for i,j in combinations(owners,2):
        lo,hi=sorted((atlas.grade(start[i],end[j]),atlas.grade(start[j],end[i])))
        if lo>min(ranks[i],ranks[j]) and lo+hi==ranks[i]+ranks[j]:pairs.append((i,j))
    data=json.loads(source.read_bytes())
    assert len(pairs)==3112 and sha256(json.dumps(pairs,separators=(',',':')).encode()).hexdigest()==data['pair_digest']
    assert data['status']=='exhausted' and data['cursor'] is None and data['witness'] is None
    replays=[]
    for rev in (False,True):
        tape=op['run_tape'](word,atlas,rev)
        assert tape.output==op['expected_operator'](rev) and tape.dirty==3554
        valid=defaultdict(list)
        for c in sorted(atlas.body):
            if monotonic()-begin>20:raise ValueError(('verification capped',rev,c))
            _,q=independent['quotient']([v.row for v in tape.stock[c]],owners)
            for i,j in pairs:
                if q[i]==q[j]:valid[i,j].append(c)
        hist=dict(Counter(len(valid[pair]) for pair in pairs))
        expected=data['orientations'][int(rev)]
        assert not any(n>=2 for n in hist)
        assert expected['reverse']==rev and expected['trials']==[]
        assert expected['readable']==[[i,j,valid[i,j]] for i,j in pairs if valid[i,j]]
        assert hist=={int(k):v for k,v in expected['read_count_histogram'].items()}
        replays.append(dict(reverse=rev,counts=hist,public=len(tape.output),dirty=tape.dirty))
    assert sum(independent['quotient'](rows,[0,1])[1][0]==independent['quotient'](rows,[0,1])[1][1] for rows in [[3],[1,2],[]])==2
    out=dict(status='verified',replays=replays,individual_chart_tests=len(pairs)*len(atlas.body)*2,seconds=monotonic()-begin)
    output.write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
