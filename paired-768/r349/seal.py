"""Bind the observed first failed coefficient to authenticated source and time receipts."""
import argparse
from decimal import Decimal
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import runpy

def read(p):
    return json.loads(p.read_bytes())

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    cli=argparse.ArgumentParser()
    for key in ('peer-application','binary','progress','timing','out'):
        cli.add_argument('--'+key,type=Path,required=True)
    a=cli.parse_args()
    solver=Path(__file__).with_name('price.py')
    assert digest(solver)=='9bc09f04d63985d62efa1df8112c48abfc7cc9d211952320c02146207dc5f492'
    assert digest(a.progress)=='eb5d98fcf6b3d7a9a601b6118c34f00771e96c4c1dbf42ccc64101eea0e1a446'
    assert read(a.timing)['exit_code']==1 and read(a.timing)['elapsed_seconds']<45
    mem=runpy.run_path(str(solver))
    pins=mem['PINS'].copy()
    pins['round348/accept.json']='35481cf9a929a3dd137a9e63134b7e97ee7c5408d4e675a3e8ad67b16d9a7b71'
    assert digest(a.binary)==pins['round347/BINARY.json'] and digest(a.peer_application)==pins['peer/APPLICATION.json']
    app=read(a.peer_application);old=read(a.binary)['peer_finite']
    progress=[json.loads(x) for x in a.progress.read_text().splitlines()]
    assert [v['j'] for v in progress if v['stage']=='coefficient-accepted']==list(range(8))
    assert [v['last_complete_height'] for v in progress if v['stage']=='tabulating-coefficients']==list(range(-1,129))
    last=progress[-1]
    assert last['stage']=='coefficient-exclusion' and last['j']==8
    bound=F(last['ratio']);eta=old['uniform']['eta']
    assert bound>F(eta['upper'])>F(last['capacity'])==F(eta['lower'])
    # Reconstruct the mean only: this packaging check does not evaluate another
    # parameter, price or coefficient. Retain three distinct positive charge terms.
    t=Decimal('0.996109884723406');weight=cumul=F(0)
    for k,n in app['binary_native']['paid_all'].items():
        (lo,hi),(_,log)=mem['directed'](int(k),t)
        weight+=n*lo;cumul+=n*hi*log
    raw=cumul/(weight*mem['directed'](15,t)[1][0])
    ratio=old['independent_directed_compiler']['ratio_intervals']
    split=2*(F(ratio[1][1])/F(ratio[0][0]))**768
    assert raw+split<F(3,4)
    output={'status':'EXCLUDED_FROZEN_BERNOULLI_COEFFICIENT_CERTIFICATE','scientific_gain':'0',
            'case':{'p':128,'h':1024,'q':'3/4','shift_upper':'7/20','ambient_lower':'21/10','slope_lower':'51/50'},
            'previous_complete_claim':'0.00389011519729','source_pins':pins,'member_pins':mem['MEMBERS'],
            'positive_raw_mean_upper':mem['bounded_print'](raw),'positive_split_uplift_upper':mem['bounded_print'](split),
            'additional_recursive_completion_upper':'0','completed_mean_upper':mem['bounded_print'](raw+split),
            'passed':['full directed price prior to source','attained minimum','complete paid mean','leading limit','ordinary base','all 129 polynomial rows','Newton orders 0 through 7'],
            'first_failure':last,'true_capacity_upper':eta['upper'],'unchecked_finite_differences':'9 through 128 inclusive; order 128 leading formula separately checked',
            'direct_function_violations_established':False,'literal_candidate_or_signed_replay':False,
            'checker_sha256':digest(solver),'progress_sha256':digest(a.progress)}
    mem['dump'](a.out,output)
    print(output['status'],output['completed_mean_upper'],'first order',last['j'])
if __name__=='__main__':
    main()
