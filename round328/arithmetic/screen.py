"""Exact changed-slab supplier arithmetic. The source supplies the signed inventories."""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import signal
from time import monotonic

INPUT = 'BIT-451.json'
PIN = '538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749'
C = Q('.003879928046148')
H = 1_202_400_000_000_000
V, U, W = 451, Q(13,50), Q(17,50)
K, OLD_K = 10**200 * 11**251, 11**451
FLOOR, AMBIENT = 16**451, 134**451
THETA, P, E, D = Q(17,20), 53, Q(2660,H), Q(1,10**13)
GRID = 10**22


def power(n, exponent):
    """Enclose rational powers with correctly rounded ln and exp, then exact integers."""
    if n == 1:
        return Q(1), Q(1)
    assert n > 0 and exponent > 0
    l = Decimal(n).ln()
    x = (l.next_minus() * exponent.numerator).next_minus()
    y = (l.next_plus() * exponent.numerator).next_plus()
    a = (x / exponent.denominator).next_minus().exp().next_minus()
    b = (y / exponent.denominator).next_plus().exp().next_plus()
    return Q(a), Q(b)


def moment(bins, exponent):
    terms = [(power(int(i), exponent), n) for i,n in bins.items()]
    return tuple(sum((v[j]*n for v,n in terms),Q(0)) for j in (0,1))


def upper_tick(x):
    return Q(-((-x.numerator*GRID)//x.denominator), GRID)


def ceiling(a,b):
    return (a+b-1)//b


def calc(source_path):
    data=source_path.read_bytes()
    if sha256(data).hexdigest()!=PIN:
        raise ValueError('supplier inventory pin mismatch')
    base=json.loads(data)
    paid,target=(base['native'][k] for k in ('paid','targets'))
    assert sum(paid.values()) == 107460 and sum(target.values())==20706
    t=1-C
    target_lb=moment(target,t)[0]
    alpha=upper_tick(moment(paid,t)[1]/target_lb)
    gamma=upper_tick(moment(paid,t+U)[1]/(power(11,U)[0]*target_lb))
    lam=upper_tick(power(16,W)[1]*moment(target,t-W)[1]/target_lb)
    assert all(Q(0)<x<1 for x in (alpha,gamma,lam))
    caps=base['separation']['caps']
    assert [alpha,gamma,lam] == [Q(caps[k]) for k in ('alpha','gamma','lambda')]
    # K/11^451=(10/11)^200, and 200U=52. Only the paid tail changes.
    base_part=1/(1+V*(1-alpha))
    uplift=2*gamma**V*Q(11,10)**52
    debit=lam**V
    surplus=1-base_part-uplift-debit
    assert surplus>Q('4.5074e-13')
    lower_surplus=Q((surplus.numerator*10**30)//surplus.denominator,10**30)
    assert 0 < E < Q(base['uniform']['uniform_loss']) and H*E==2660
    assert H == base['uniform']['H']
    eta_lo=t/power(134,V*C)[1]
    assert K**20<FLOOR**17 and 4*K**20<=AMBIENT**17
    assert THETA**P<eta_lo and power(134,V*C)[1]<2**P
    assert THETA**(P-1)>=t/power(134,V*C)[0]  # P-1 fails
    assert (H+1)**P<2**2660 and (H+1)*E>2*P
    assert Q(64,2**52)<D/4 and 2**int(H*D)>=1+D/2
    covered=C-E-D
    old_covered=Q(base['cover_and_stock']['covered'])
    assert covered-old_covered==Q(173,601200000000000)
    previous=Q(base['cover_and_stock']['seed'])
    stages=[]
    rho=Q(1,250)
    for _ in range(7):
        envelope=(1-rho)*covered+rho*previous
        admitted=Q((envelope*10**20).__floor__()-1,10**20)
        assert previous<admitted<envelope<covered<rho<1-envelope
        stages.append(dict(previous=str(previous),envelope=str(envelope),admitted=str(admitted)))
        previous=admitted
    assert previous>old_covered and previous<Q(base['raw_crossing'][0])
    w=base['partition']['witness']
    assert w['first_label']==[4,2569,1402] and w['tail_label']==[91,-1,0]
    assert w['first_grade']==4 and w['tail_grade']==14 and w['tail_factors']==450
    r=4*14**450
    old_count,new_count=(ceiling(r,k) for k in (OLD_K,K))
    assert old_count==int(w['all11_calls']) and new_count>old_count
    return dict(status='PASS_CHANGED_SLAB_ARITHMETIC_ONLY',source_sha256={INPUT:PIN},
                cap_seconds=60,cutoff='10^200*11^251',factor_count=V,
                theta=str(THETA),log_power=P,horizon=H,uniform_loss=str(E),
                unchanged_cover_loss=str(D),unchanged_raw_crossing=base['raw_crossing'],
                physical_label_witness=dict(first=w['first_label'],tail=w['tail_label'],tail_count=450,
                        rank='4*14^450',old_calls=str(old_count),new_calls=str(new_count)),
                caps=dict(alpha=str(alpha),gamma_original=str(gamma),lambda_original=str(lam)),
                paid_tail_multiplier=str(Q(11,10)**52),
                strict_complete_tensor_surplus_lower=str(lower_surplus),
                theta_and_shifted_log_tests=True,previous_log_power_rejected=True,
                covered=str(covered),old_covered=str(old_covered),covered_increase=str(covered-old_covered),
                stages=stages,ordinary_admitted=str(previous),old_ordinary=base['cover_and_stock']['ordinary_admitted'],
                bound_above_old_covered=True,ordinary_below_old_raw_lower=True,
                open=['full product and per-adapter, fixed-template accounting for increased calls',
                      '451-fold stock, compiler, precision, ownership and seed transfer on changed template',
                      'complete 48-call rational consumer and signed outer audit'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_root',type=Path)
    parser.add_argument('out',type=Path)
    args=parser.parse_args()
    start=monotonic()
    signal.alarm(60)
    with localcontext() as ctx:
        ctx.prec=90
        result=calc(args.source_root/INPUT)
    signal.alarm(0)
    result['elapsed_seconds']=monotonic()-start
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'], result['ordinary_admitted'], result['elapsed_seconds'])


if __name__=='__main__':
    main()
