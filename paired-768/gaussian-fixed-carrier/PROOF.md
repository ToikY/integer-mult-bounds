# Independent check of the fixed-carrier Gaussian price

SYLforge’s #8052 at `baaec65bf8e4c7e92be110a00d5b06522177931f` supplies the literal Gaussian and K7 words, caller, allocator and extended install. The extended profile uses binary rank exponents 60,000 and 960,000, Gaussian rank exponent 20,000,000 and stop denominator 10^18. The edit raises the installed Gaussian parameter from 2092819/2^29 to 1071523491/2^38 with those same sizes. The stage caps and input geometry in the extended receipts agree. The proposed κ is 19490860671/5000000000000 = 0.0038981721342. [Pinned predecessor](https://github.com/CrocSwap/integer-mult-bounds/tree/baaec65bf8e4c7e92be110a00d5b06522177931f/research/p104-k7-retimed-binary)

The old parameter with the same carrier and finite reserve imposes the strict upper endpoint C_old − 39/(256H) − 5/D = 1596691063349607327/409600000000000000000. The old reported κ passes and the proposed κ fails that bound. The proposed κ passes the corresponding new upper endpoint 817505948794129810799/209715200000000000000000. The exact gain over the old fixed-carrier upper endpoint is 242818712673/409600000000000000000. The gain over the old reported κ of 0.003898171 is 5671/5000000000000, exactly (5671/194908550)%, approximately +0.00002909569641762765%.

Independent census rebuilds all 105,216 productive and 564,144 paid ranks from the pinned Gaussian word, including 2,016 half-rank paid ports. It encloses each powered rank using 82-digit correctly rounded Decimal logarithms and exponentials, enclosing every result by its adjacent representable values and summing the resulting intervals as exact rationals. The lower Gaussian raw margin remains positive, changing from about 0.010745417209498417 to about 0.005373820796549829. The allocator's original dyadic power arithmetic then reconstructs both exact transport manifests. Forty-five of the 54 rational fractions differ. The 54 allowed edges agree, the rank-448 to rank-1,032 edge retains fraction 1, and the maximum numerator or denominator length remains 256 bits. Both manifests retain the declared 512-bit cap, downstream rank decrease and independent split floor.

The first band [32768,32770] has a different literal epoch boundary. Its new normalized mass exceeds the prior mass by more than 2^−96 even when the old upper and new lower come from the allocator's coarse 256-bit intervals. The same separation is reconstructed by the independent Decimal engine. Tightening to the production grid gives nested bounds because every inverse-power multiplier is positive, square root and multiplication are monotone, and rounding outward on a finer dyadic grid cannot widen the enclosing interval. The production volume 2^120000000 makes the change in the integer ceiling greater than one. The root's external placement geometry is determined by the same H and integer rank pair. Direct reconstruction at production H finds period 1,620, initial tickets (0,324,648) and first physically aligned SWAP (1,324,1). This checks an actual decoded placement while distinguishing it from the changed epoch multiplicity.

The two scripts independently check the raw price, resource receipt, supported arithmetic fractions, one physical root placement and one allocator boundary. The complete package runner owns signed action, storage and restoration across the full suite. The five inherited all-size obligations are native_all_columns, owned_erasure_and_restoration, compiler_transfer, precision_and_tape_services, and analytic_recovery. OpenAI Codex assisted preparation and replay.

Use CPython 3.12 from this folder. Fetch exact peer Git commit `baaec65bf8e4c7e92be110a00d5b06522177931f` into a clean checkout, set `PEER_CHECKOUT` to that root and use fresh output locations. The official bootstrap authenticates the archived dependency closure. Genuinely off-platform production payloads remain governed by the inherited assumptions.

```sh
python3.12 -IB prepare.py --peer "$PEER_CHECKOUT" --output fresh-candidate
OLD_PACKAGE="$PEER_CHECKOUT/research/p104-k7-retimed-binary"
CANDIDATE_PACKAGE="fresh-candidate/research/p104-k7-retimed-binary"
```

```sh
python3.12 -IB audit.py --old "$OLD_PACKAGE" --candidate "$CANDIDATE_PACKAGE" --out fresh-audit.json
python3.12 -IB boundary.py --transport "$OLD_PACKAGE/transport.py" --out fresh-boundary.json
```

The independent gate passed in 3.642092 seconds under its 45-second cap. The separate boundary replay took less than one second. The candidate inventory receipt was 3d85ccaf415b33702951ceb14b78fa1f7f0964ba3f201bf07b9e8a6e96882220. The two output SHA-256 digests are e3635f1834016e02304f130887c2618b21cf01d99e1ef7f1649a70a687bbb667 and 64665f6c828fb73d8654caa1e14363d70fbd09ff86df542042a4f71e0623a757. The first digest incorporates the serialized candidate receipt.
