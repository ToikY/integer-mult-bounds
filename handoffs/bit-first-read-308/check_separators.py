"""Replay each promised distinguishing input as scalar bits, without linear elimination."""
import gzip
import hashlib
import json
from pathlib import Path
import sys

word_path, result_path = map(Path,sys.argv[1:])
data=word_path.read_bytes()
assert hashlib.sha256(data).hexdigest()=="d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9"
word=json.loads(gzip.decompress(data))
receipt=json.loads(result_path.read_bytes())
cases=receipt["cases"]
assert len(cases)==32 and len({c["first"] for c in cases})==32
assert {c["clock"] for c in cases}==set(receipt["frozen"])
assert not (set(receipt["unvisited"]) & set(receipt["frozen"]))
assert sorted(receipt["frozen"]+receipt["unvisited"])==sorted(i for i,e in enumerate(word["program"]) if e[0]=="MOVE")
at={c["first"]:(i,c) for i,c in enumerate(cases)}
seeds=[int(c["separating_input"],16) for c in cases]
public=word["public"]
value=[sum(((s>>a)&1)<<i for i,s in enumerate(seeds)) for a in range(public)]+[0]*word["owned_fields"]
initial=value[:public]
chart=word["start"][:]+[None]*word["owned_fields"]
seen=0
for clock,(op,a,*rest) in enumerate(word["program"]):
    if clock in at:
        i,c=at[clock]
        assert word["program"][c["clock"]]==["MOVE",c["owner"],c["src"],c["dst"]]
        assert op=="ADD" and rest==[c["owner"],c["dst"]]
        assert chart[rest[0]]==chart[a]==c["dst"]
        assert (value[rest[0]]>>i)&1
        others=[j for j,s in enumerate(chart) if s==chart[a] and j!=rest[0]]
        assert len(others)==c["stock_count"]
        assert not any((value[j]>>i)&1 for j in others)
        seen+=1
    if op=="INIT":
        assert chart[a] is None
        chart[a],value[a]=rest[0],0
    elif op=="CLEAR":
        assert chart[a]==rest[0]
        chart[a],value[a]=None,0
    elif op=="ADD":
        b,ch=rest
        assert chart[a]==chart[b]==ch
        value[a]^=value[b]
    elif op=="MOVE":
        assert chart[a]==rest[0]
        chart[a]=rest[1]
    elif op=="SWAP":
        b,=rest
        value[a],value[b]=value[b],value[a]
        chart[a],chart[b]=chart[b],chart[a]
    else:
        raise ValueError(op)
expected=initial[:]
for role in range(111):
    expected[111+role]^=initial[role]
assert seen==32 and value[:public]==expected and chart[:public]==word["final"]
assert all(c is None for c in chart[public:])
print("PASS: 32 first-read collisions on the exact word; all 680 public endpoints and private retirements checked on those inputs")
