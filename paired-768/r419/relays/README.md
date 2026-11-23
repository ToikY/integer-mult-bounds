# Exact forward and adjoint checks for four remaining chart relays

The checked input is the exact [#8094 peer head](https://github.com/CrocSwap/integer-mult-bounds/commit/c20a08dc0a79a989e3515068560d5da371c0a2a8). The checker reconstructs the predecessor word from the Round 411 inputs and independently compares the two words' literal paid edges. It verifies that the old and new words have identical endpoint and chart declarations, and that both predecessor legs use strictly nested chart subspaces. The archived chart lowerer produces the exact original two factors and the proposed direct factor.

| Replacement node | Old chart path | Original paid grades | Direct paid grade |
| --- | --- | --- | --- |
| 104489 | 412 → 798 → 922 | 2 + 3 | 5 |
| 104490 | 614 → 795 → 917 | 2 + 2 | 4 |
| 104491 | 392 → 1037 → 918 | 3 + 2 | 5 |
| 104492 | 411 → 1038 → 921 | 3 + 2 | 5 |

On each of the 512 nine-axis columns, the independent Gaussian dyadic verifier matches the direct operator to the original pair and to the canonical frame change. For the adjoint, the reference reverses the predecessor factor order and applies the adjoint to each leg. It also matches the reversed canonical frames. The phase control adds a quarter turn while leaving the Pauli tableau unchanged. The direction control uses forward Fourier inside the adjoint's reversed monomial wrappers. Both controls fail at column zero on all four cases.

The exact algebra replay exhausted four designated pairs in 4.32 seconds with exit 0. Together with the [Round 416 result](../../r416/signed/README.md), all five direct factors and their adjoints now have finite exact column evidence. The selected four replace eight paid chart entries by four with the same grade sum of 19. This is a count of literal local chart charges. Full typed calls, spectator movement, physical phase and ownership, installed scheduling and the comparative signed bound require separate verification.

## Replay

Use CPython 3.12 with assertions. Run from a clean public handoff checkout. Set `COMPOSED_CHECKOUT` to the exact #8094 checkout above. The check authenticates the Round 411 and 416 checkers, the public word, the relevant archive and its named source members, and the predecessor reconstruction inputs. The runner cap is 45 seconds.

```sh
package="$COMPOSED_CHECKOUT/research/p104-shortcut-word-eta-27bit-5stage"
python3.12 -IB paired-768/r419/relays/check.py \
  --word "$package/w5669_shortcut5.json.gz" \
  --archive "$package/peer8057.tar.gz" \
  --relay-root paired-768/r411/relay \
  --prior-signed-check paired-768/r416/signed/check.py > four-relays.json
cmp four-relays.json paired-768/r419/relays/RECEIPT.json
```

Credit floration for the exact composed shortcut word, Ali Romman for #8057 and its archived chart lowerer, and the retained Clifford/native review authors. This work reuses the earlier Round 411 provenance chain and Round 416 signed controls. OpenAI Codex assisted with the independent replay.
