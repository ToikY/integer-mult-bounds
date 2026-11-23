"""Exercise the installed period placement and two real decoder rejection paths."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import ceil
from pathlib import Path
import json
import subprocess
import sys

parser = ArgumentParser(description=__doc__)
parser.add_argument("runtime", type=Path)
parser.add_argument("signed_source", type=Path)
args = parser.parse_args()
runtime = args.runtime.resolve()
sys.path.insert(0, str(runtime))
from upstream import install
install()
from periodic import Job
from transport import axes
from typed_transport import NativeType, TypedPlan


def rejection(callback, expected):
    try:
        callback()
    except (ValueError, ArithmeticError) as e:
        assert str(e) == expected
        return str(e)
    raise AssertionError("invalid operation passed")


# Cross the period discontinuity. The production stage binds every row through
# this same selector. Each phase has exactly the prescribed number of axes.
period_results = []
for M, size in ((263772,258),(264192,258),(264196,258),(262144,193)):
    period = 4*ceil(Q(M,4*size))
    assert M%4==0 and 0 <= period*size-M < 4*size
    five = (period*size-M)//4
    assert period*size == M+4*five
    multiplicities=Counter()
    rows=[]
    for phase in range(period):
        observed=tuple(axes(M,size,period,phase))
        expected=tuple(u//5 if u<5*five else u-4*five
                       for u in (phase+i*period for i in range(size)))
        assert observed==expected and len(set(observed))==size
        assert all(0<=x<M for x in observed)
        multiplicities.update(observed)
        if phase in (0,1):
            rows.append(observed)
    assert rows[0] != rows[1]  # a wrong start phase changes the owned placement
    assert Counter(multiplicities.values())==Counter({1:M-five,5:five})
    period_results.append(dict(carrier=M, width=size, period=period, fivefold=five,
                               phase0=rows[0][:3], corrupted_phase1=rows[1][:3]))

types=(NativeType((2,), (1,1), 1),NativeType((2,2), (1,1,1,1), 90))
shares={(0,1,1,2):Q(1), (1,1,0,2):Q(1,180), (1,1,1,2):Q(179,180)}
placement=dict(n=384,types=types,cells=shares,t=Q(1),lower=10,upper=42,volume=450,
               ticks=8,rounds=32,scale_step=Q(2),padding=1)
plan=TypedPlan(**placement,delay_base=4)
same_clock=rejection(lambda: TypedPlan(**placement,delay_base=1),
                     "The carrier and the temporal base must support each real raw word")
same_delay=rejection(lambda: TypedPlan(**{**placement,"scale_step":Q(100)},delay_base=4),
                     "The child misses its return time")

class Machine:
    def native(self, jobs, columns):
        assert columns==2 and not jobs
        yield Job("retained-owner",(0,))

    def leaf(self, job):
        assert job.owner=="retained-owner"

opened=(0,7,2)
paid=(1,7,17,1,0)
returned=(2,7)
plan.decode((),0,0,Machine(),(opened,paid,returned))
missing=rejection(lambda: plan.decode((),0,0,Machine(),(opened,paid)),
                  "The last native owner did not return.")
# Re-enter at the pinned signed runtime, and reuse the signed dense-oracle
# checker solely to replay wrong-sign controls in both component widths.
checker=args.signed_source.resolve()/"check_stage_seam.py"
control = """import json,runpy,sys
path,runtime=sys.argv[1:]
sys.argv=[path,runtime]
verify=runpy.run_path(path)['verify_tape']
print(json.dumps([verify(1,[0,1],[2,1]),verify(2,[1,7],[3,1])]))"""
run=subprocess.run([sys.executable,"-IB","-c",control,str(checker),str(runtime)],check=True,capture_output=True,text=True)
signed=json.loads(run.stdout)
assert all(case["wrong_signed_return_rejected"] for case in signed)
print(json.dumps(dict(period=period_results, same_clock=same_clock, same_delay=same_delay,
                      omitted_native_close=missing,signed_controls=signed,
                      signed_checker_sha256=sha256(checker.read_bytes()).hexdigest()),indent=2))
