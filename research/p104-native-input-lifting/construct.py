"""Lift four existing helper inputs to native frames.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The source word is PR6314 by DreamingOfClouds with Claude Opus 5.5 assistance.
"""
from copy import deepcopy
import gzip
import json

from support import HERE, WORD, inputs, need

ENTRIES = {496: 595, 649: 597, 663: 105, 508: 1093}
OMIT = {
    85: ['ADD', 113, 649, '-1/2', 3],
    223: ['ADD', 194, 649, '-1/2', 3],
    228: ['ADD', 187, 649, '-1/2', 3],
    239: ['ADD', 205, 649, '-1/2', 3],
    591: ['ADD', 138, 663, '1/2', 3],
    595: ['ADD', 120, 663, '-1/2', 3],
    687: ['ADD', 178, 663, '-1/2', 3],
    793: ['ADD', 192, 663, '1/2', 3],
    1090: ['ADD', 157, 508, '1/2', 3],
    4368: ['ADD', 220, 496, '1/2', 3],
}
EDITS = {
    8289: (['MOVE', 639, 3, 1027, False],
           [['ADD', 639, 643, '-2', 3], ['MOVE', 639, 3, 1027, False]]),
    8315: (['MOVE', 643, 3, 1027, False],
           [['MOVE', 643, 3, 595, False], ['ADD', 643, 496, '-1/2', 595],
            ['MOVE', 643, 595, 1027, False], ['ADD', 639, 643, '2', 1027]]),
    9029: (['MOVE', 496, 3, 595, False], []),
    9105: (['MOVE', 198, 3, 597, False],
           [['MOVE', 198, 3, 597, False], ['ADD', 198, 649, '1', 597]]),
    9210: (['MOVE', 663, 3, 1051, False],
           [['MOVE', 179, 3, 105, False], ['ADD', 179, 663, '1/2', 105],
            ['MOVE', 665, 3, 1051, False], ['MOVE', 663, 105, 1051, False],
            ['ADD', 665, 663, '-1', 1051]]),
    9212: (['MOVE', 665, 3, 1051, False], []),
    9227: (['MOVE', 631, 3, 118, False],
           [['ADD', 631, 635, '-2', 3], ['MOVE', 631, 3, 118, False]]),
    9229: (['MOVE', 649, 3, 120, False],
           [['MOVE', 648, 3, 120, False], ['MOVE', 649, 597, 120, False],
            ['ADD', 648, 649, '-1', 120]]),
    9245: (['MOVE', 635, 3, 118, False],
           [['MOVE', 635, 3, 1093, False], ['ADD', 635, 508, '-1/2', 1093],
            ['MOVE', 635, 1093, 118, False], ['ADD', 631, 635, '2', 118]]),
    9284: (['MOVE', 648, 3, 120, False], []),
    9304: (['MOVE', 179, 3, 105, False], []),
    9867: (['MOVE', 508, 3, 733, False], [['MOVE', 508, 1093, 733, False]]),
}
RESTORE = [['ADD', 639, 496, '1', 127], ['ADD', 643, 496, '1/2', 127],
           ['ADD', 648, 649, '1', 127], ['ADD', 665, 663, '1', 127],
           ['ADD', 631, 508, '1', 127], ['ADD', 635, 508, '1/2', 127]]


def construct(source):
    need(len(source['frames']) == 1093 and len(source['program']) == 17445,
         'Exact source dimensions')
    word = deepcopy(source)
    word['frames'].append([30, 42, 384])
    for role, frame in ENTRIES.items():
        need(source['initial'][role] == 3 and source['final'][role] == 127,
             'Full helper target before the lift')
        word['initial'][role] = frame
    initial_uses = {i: e for i, e in enumerate(source['program'])
                    if e[0] in ('ADD', 'COPY', 'SCALE') and e[-1] == 3 and
                    (e[1] in ENTRIES or e[0] in ('ADD', 'COPY') and e[2] in ENTRIES)}
    need(initial_uses == OMIT, 'Every use of a lifted input in the initial chart')
    program = []
    for i, event in enumerate(source['program']):
        if i in OMIT:
            need(event == OMIT[i], 'Exact omitted preparation event')
        elif i in EDITS:
            before, after = EDITS[i]
            need(event == before, 'Exact native edit at source event ' + str(i))
            program.extend(deepcopy(after))
        else:
            program.append(deepcopy(event))
    program.extend(deepcopy(RESTORE))
    word['program'] = program
    need(len(program) == 17452, 'Exact event count')
    return word


def payload(word):
    return (json.dumps(word, sort_keys=True, separators=(',', ':')) + '\n').encode()


if __name__ == '__main__':
    source = json.loads(gzip.decompress(inputs()[WORD]))
    (HERE / 'WORD.json.gz').write_bytes(gzip.compress(payload(construct(source)), mtime=0))
