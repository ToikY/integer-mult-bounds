"""Bind an already calculated R345 receipt to a fresh signed consumer, with R344 control."""
from argparse import ArgumentParser
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path

def read(path,hash_value=None):
    raw=path.read_bytes(); actual=sha256(raw).hexdigest()
    if hash_value and hash_value!=actual:raise ValueError(path.name+' fingerprint mismatch')
    return json.loads(raw),actual

def bind(root,component):
    rec,rec_hash=read(root/'receipt.json')
    expected=rec['output_sha256']
    app,_=read(root/'APPLICATION.json',expected['APPLICATION.json'])
    audit,_=read(root/'AUDIT.json',expected['AUDIT.json'])
    key='adapter/binary/FINITE.json'; finite,_=read(root/key,expected[key]);outer=audit['outer']
    def check(ok,why):
        if not ok:raise ValueError(why)
    check(rec['status']=='PASS_CONDITIONAL_ON_SUPPLIED_CAP','signed status')
    check(F(rec['cap'])==F(app['binary_ordinary'])==F(outer['pinned_binary_cap'])==F(finite['ordinary_admitted'])==F(component['cap']),'ordinary billing')
    check(F(rec['claim'])==F(outer['claim'])==F(app['application']['claim'])==F(component['candidate_grid_claim']),'published claim')
    check(F(rec['tested'])==F(outer['finite_compiler']['tested'])==F(component['candidate_tested']),'signed tested point')
    check(finite['word_sha256']==app['binary_word']=='d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d','binary word')
    check(app['word_sha256']=='7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48','rational word')
    check(outer['outer_checks']['strict_count']==54 and outer['outer_checks']['functional_count']==4,'outer gate count')
    check({'low_cap_rejected','extra_rank_1_charge_rejected'}.issubset(rec['controls']),'underpriced controls')
    check(rec['independent_orientations']['checked_coefficients_each_way']==1661521,'signed coefficient census')
    return {'cap':rec['cap'],'claim':rec['claim'],'tested':rec['tested'],'output_sha256':expected,'orientations':rec['independent_orientations'],'checks':outer['outer_checks'],'controls':rec['controls'],'premises':rec['premises']}

def main():
    p=ArgumentParser()
    for arg in ('component','consumer','old','old-consumer','out'):p.add_argument('--'+arg,type=Path,required=True)
    a=p.parse_args()
    new,h=read(a.component,'25c71dab6c8c1fbc6f7aeda9f23ecb2c9da108a6938f22edfeaafa967bc03417')
    old,oh=read(a.old,'1fd90f20d38e5368a98deef7efe4bce880f95b6da8078d4aa37e78921173f1ac')
    prev=bind(a.old_consumer,old);cur=bind(a.consumer,new)
    if prev['orientations']!=cur['orientations'] or prev['premises']!=cur['premises']:
        raise ValueError('signed scope or transfer changed')
    if not ([new['cells'][u]['left'] for u in ('5/6','11/12','23/24','1')]==['3/4','5/6','11/12','23/24']):
        raise ValueError('adjacent top-rank cells')
    for cell in new['cells'].values():
        if sorted(map(int,cell['rows']))!=list(range(32)) or len(cell['tail'])!=17:
            raise ValueError('full prefix/tail coverage')
    peer=F('0.00387992804346')
    out={'peer_gain_percent':str(100*(F(cur['claim'])-peer)/peer),'new_component_sha256':h,'old_component_sha256':oh,'signed':cur,'known_good':prev,'comparison':new['absolute_gain']}
    with a.out.open('x') as stream:json.dump(out,stream,indent=2);stream.write('\n')
    print('PASS independent signed bind',cur['cap'],cur['claim'],cur['tested'])
if __name__=='__main__':main()
