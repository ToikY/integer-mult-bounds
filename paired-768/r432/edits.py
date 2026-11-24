"""Exact source changes to the integral-fringe tariff and stage verifiers."""

RECEIPT = (
    ("ORDINARY_DEBIT = Q(1414404, 2**20)", "ORDINARY_DEBIT = Q(1414276, 2**20)"),
    ("CHILD_TARIFF = Q(2391, 1024)", "CHILD_TARIFF = Q(10981863, 4703998)"),
    ("def tape_factor(ambient, rate, lower, suffix=64):", "def tape_factor(ambient, rate, lower, suffix=64, *, endpoint=1):"),
    ("power_interval(1024 * ambient * lower, rate)[1]", "power_interval(1024 * ambient * lower, rate)[endpoint]"),
    ('''    ordinary_upper = tape_factor(134, BINARY_C, 4474, Q(186, 25)) * Q(255, 256) * CHILD_TARIFF
    ordinary_allowance = 2 * Q(power_interval(2, ORDINARY_DEBIT - 1)[0], UNIT)
    assert ordinary_upper < ordinary_allowance
    worst_child = Q(2390, 1024)
    rank_guard = 3**7  # N >= 9 and the quotient mean decreases with N.
    assert 21 * rank_guard + 3 <= worst_child * (9 * rank_guard - 1)
    assert all(height >= 4 for profile in (ENTRY, TERMINAL) for height in profile.rank_logs)
    child_ratio = worst_child / CHILD_TARIFF''',
     '''    ordinary_upper = tape_factor(134, BINARY_C, 4474, Q(186, 25)) * Q(255, 256) * CHILD_TARIFF
    allowed_lo, allowed_hi = (2 * Q(end, UNIT) for end in power_interval(2, ORDINARY_DEBIT - 1))
    old_tariff = Q(2391, 1024)
    old_lo = tape_factor(134, BINARY_C, 4474, Q(186, 25), endpoint=0) * Q(255, 256) * old_tariff
    old_hi = ordinary_upper * old_tariff / CHILD_TARIFF
    assert ordinary_upper < allowed_lo <= allowed_hi < old_lo
    assert old_hi < 2 * Q(power_interval(2, Q(1414404, 2**20) - 1)[0], UNIT)
    rank_guard = 3**7  # N >= 9 and the quotient mean decreases with N.
    worst_child = Q(21 * rank_guard + 3, 9 * rank_guard - 1)
    assert worst_child == Q(22965, 9841) < Q(2390, 1024)
    assert all(height >= 4 for profile in (ENTRY, TERMINAL) for height in profile.rank_logs)
    child_ratio = worst_child / CHILD_TARIFF'''),
    ("== (134145234, 208653)", "== (134139351, 208653)"),
    ('''    previous = Q(".003900857312000")
    gain = TERMINAL.kappa - previous
    assert TERMINAL.kappa == Q(".003900857312674")
    assert previous - older == Q(22107, 500000000000000)
    assert gain == Q(337, 500000000000000)''',
     '''    period = Q(".003900857312000")
    previous = Q(".003900857312674")
    gain = TERMINAL.kappa - previous
    assert TERMINAL.kappa == Q(".003900857313143")
    assert period - older == Q(22107, 500000000000000)
    assert previous - period == Q(337, 500000000000000)
    assert gain == Q(469, 1000000000000000)'''),
    ('''    assert previous - frozen_tariff == Q(857, 20000000000000)
    previous_positive = GAUSSIAN_C - Q(1039701, 2**23) / TERMINAL.complex_log - 5 * stop
    assert previous < previous_positive <= previous + Q(1, 10**15)
    positive_ceiling = GAUSSIAN_C - DEBIT / TERMINAL.complex_log - 5 * stop
    prior_booked = Q(late["ordinary_rates"][-2])
    last_height = TERMINAL.rank_logs[-1]
    ordinary_ceiling = min(
        TERMINAL.eta, (249 * (BINARY_C - ORDINARY_DEBIT / last_height) + prior_booked) / 250
    ) - 5 * stop
    assert previous_positive < TERMINAL.kappa < ordinary_ceiling < positive_ceiling
    assert ordinary_ceiling <= TERMINAL.kappa + Q(1, 10**15)''',
     '''    assert period - frozen_tariff == Q(857, 20000000000000)
    previous_positive = GAUSSIAN_C - Q(1039701, 2**23) / TERMINAL.complex_log - 5 * stop
    assert period < previous_positive <= period + Q(1, 10**15)
    positive_ceiling = GAUSSIAN_C - DEBIT / TERMINAL.complex_log - 5 * stop

    def guarded_ordinary(debit):
        booked = Q(0)
        for height in TERMINAL.rank_logs:
            upper = min(TERMINAL.eta, (249 * (BINARY_C - debit / height) + booked) / 250)
            booked = Q(int(upper * 10**21) - 1, 10**21)
        return upper - 5 * stop

    prior_ordinary = guarded_ordinary(Q(1414404, 2**20))
    assert previous < prior_ordinary <= previous + Q(1, 10**15)
    assert previous_positive < prior_ordinary < TERMINAL.kappa < positive_ceiling
    assert positive_ceiling < guarded_ordinary(ORDINARY_DEBIT)
    assert positive_ceiling <= TERMINAL.kappa + Q(1, 10**15)'''),
)

INDEPENDENT = (
    ('''    print("PASS_SHARPER_CHILD_TARIFF", 4474, "1414404/1048576", str(candidate_ratio))''',
     '''    print("PASS_SHARPER_CHILD_TARIFF", 4474, "1414404/1048576", str(candidate_ratio))

    # The quotient mean decreases in x=3**(N-2) and N>=9. Charge its
    # exact endpoint while retaining the preceding geometric contraction.
    x = 3**7
    exact_mean = Q(21*x + 3, 9*x - 1)
    tariff = exact_mean / candidate_ratio
    assert exact_mean == Q(22965, 9841) < child_mean
    assert tariff == Q(10981863, 4703998) < candidate_tariff
    assert exact_mean / tariff == candidate_ratio
    _, new_hi = bounds(4474, Q(186, 25), tariff)
    allowed_lo, allowed_hi = (2 * p for p in powers(2, Q(1414276, 2**20) - 1))
    assert new_hi < allowed_lo <= allowed_hi < candidate_lo
    print("PASS_EXACT_K7_CHILD_TARIFF", str(tariff), "353569/262144", str(candidate_ratio))'''),
    ('''    assert TERMINAL.kappa - Q(".003900857267786") == Q(5611, 125000000000000)
    assert TERMINAL.kappa - Q(".003900857312000") == Q(337, 500000000000000)''',
     '''    assert TERMINAL.kappa - Q(".003900857267786") == Q(45357, 1000000000000000)
    assert TERMINAL.kappa - Q(".003900857312000") == Q(1143, 1000000000000000)
    assert TERMINAL.kappa - Q(".003900857312674") == Q(469, 1000000000000000)'''),
)

SEAM = (
    ('''    ORDINARY=Q(1414404,2**20)  # tariff 2391/1024, same floor and fringe''',
     '''    FRINGE_ORDINARY=Q(1414404,2**20)  # predecessor tariff 2391/1024
    FRINGE_KAPPA=Q(".003900857312674")
    ORDINARY=Q(1414276,2**20)  # exact child mean, same floor and fringe'''),
    ('assert TERMINAL.kappa==Q(".003900857312674")', 'assert TERMINAL.kappa==Q(".003900857313143")'),
    ("assert gaussian_upper(TERMINAL.complex_log)>ordinary_upper(ranks)>paid",
     "assert ordinary_upper(ranks)>gaussian_upper(TERMINAL.complex_log)>paid"),
    ('''    assert TERMINAL.kappa+GRID>=ordinary_upper(ranks)-5*STOP''',
     '''    fringe_crossing=ordinary_upper(ranks,FRINGE_ORDINARY)-5*STOP
    assert FRINGE_KAPPA<fringe_crossing<=FRINGE_KAPPA+GRID
    assert fringe_crossing<TERMINAL.kappa
    assert TERMINAL.kappa+GRID>=gaussian_upper(TERMINAL.complex_log)-5*STOP'''),
    ('''        rejected(lambda:require_funding(ranks,TERMINAL.complex_log,kappa=TERMINAL.kappa+GRID),
                 "next-displayed-kappa-at-fixed-five-stage-profile"),''',
     '''        rejected(lambda:require_funding(ranks,TERMINAL.complex_log,debit=FRINGE_ORDINARY),
                 "predecessor-ordinary-debit-at-new-rate"),
        rejected(lambda:require_funding(ranks,TERMINAL.complex_log,kappa=TERMINAL.kappa+GRID),
                 "next-displayed-kappa-at-fixed-gaussian-height"),'''),
)

EDITS = {
    "receipt.py": RECEIPT,
    "independent_price.py": INDEPENDENT,
    "check_stage_seam.py": SEAM,
}
