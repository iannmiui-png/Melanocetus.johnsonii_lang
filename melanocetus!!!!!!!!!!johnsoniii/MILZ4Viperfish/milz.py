import sys
import random
from typing import Optional

UPPER_INTERVALS = [
    (0, 1, 'A'), (1, 2, 'B'), (2, 3, 'C'), (3, 4, 'D'),
    (4, 5, 'E'), (5, 6, 'F'), (6, 7, 'G'), (7, 8, 'H'),
    (8, 9, 'I'), (9, 10, 'J'), (10, 11, 'K'), (11, 12, 'L'),
    (12, 13, 'M'), (13, 14, 'N'), (14, 15, 'O'), (15, 16, 'P'),
    (16, 17, 'Q'), (17, 18, 'R'), (18, 19, 'S'), (19, 20, 'T'),
    (20, 21, 'U'), (21, 22, 'V'), (22, 23, 'W'), (23, 24, 'X'),
    (24, 25, 'Y'), (25, 26, 'Z'),
]

LOWER_INTERVALS = [
    (26, 27, 'a'), (27, 28, 'b'), (28, 29, 'c'), (29, 30, 'd'),
    (30, 31, 'e'), (31, 32, 'f'), (32, 33, 'g'), (33, 34, 'h'),
    (34, 35, 'i'), (35, 36, 'j'), (36, 37, 'k'), (37, 38, 'l'),
    (38, 39, 'm'), (39, 40, 'n'), (40, 41, 'o'), (41, 42, 'p'),
    (42, 43, 'q'), (43, 44, 'r'), (44, 45, 's'), (45, 46, 't'),
    (46, 47, 'u'), (47, 48, 'v'), (48, 49, 'w'), (49, 50, 'x'),
    (50, 51, 'y'), (51, 999999, 'z'),
]

INTERVALS = UPPER_INTERVALS + LOWER_INTERVALS

def num_to_char(n: float) -> Optional[str]:
    for lo, hi, ch in INTERVALS:
        if lo <= n < hi:
            return ch
    return None

def zeta_f(n: float) -> str:
    if n >= 51:
        return "{51Zinfinity}"
    ch = num_to_char(n)
    return ch if ch is not None else "_"

class MilzMachine:
    def __init__(self):
        self.A0 = 0.0
        self.A1 = 0.0
        self.A2 = 0.0
        self.output = []

    def cmd_M(self):
        ch = num_to_char(self.A0)
        if ch is None:
            ch = zeta_f(self.A0)
        self.output.append(ch)

    def cmd_no(self):
        self.A1 = self.A0

    def cmd_ii(self):
        self.A1 = self.A1 * self.A1

    def cmd_hash_bang(self):
        self.output.append(" ")
        self.A1 = 2.0
        self.A0 = self.A1
        self.cmd_M()

    def cmd_jJ(self):
        self.A2 = self.A2 * 3.14159 + 1.0
        self.A0 = 5.0
        if self.output and self.output[-1] == 'e':
            self.output[-1] = "{51Zinfinity}"

    def cmd_y_dot(self):
        if self.output and self.output[-1] == 'z':
            self.output[-1] = "."

    def cmd_star_v(self):
        self.A0 = float(random.randint(0, 51))
        if self.A0 == 5:
            self.A0 = 47.5
        if self.A0 == 2:
            self.A0 = 47.0

    def run_tokens(self, tokens):
        for tok in tokens:
            if tok == 'M':
                self.cmd_M()
            elif tok == 'no':
                self.cmd_no()
            elif tok == 'ii':
                self.cmd_ii()
            elif tok == '#!':
                self.cmd_hash_bang()
            elif tok == 'jJ':
                self.cmd_jJ()
            elif tok == 'y.':
                self.cmd_y_dot()
            elif tok == '*v':
                self.cmd_star_v()

    def get_output(self):
        return "".join(self.output)

TOKEN_SPECS = ["*v", "jJ", "y.", "#!", "no", "ii", "M"]

def tokenize(program):
    tokens = []
    i = 0
    while i < len(program):
        matched = False
        for spec in TOKEN_SPECS:
            if program.startswith(spec, i):
                tokens.append(spec)
                i += len(spec)
                matched = True
                break
        if not matched:
            i += 1
    return tokens

def strip_bespoke_prefix(src):
    prefix = "PLEASE MILZ DO"
    idx = src.find(prefix)
    if idx == -1:
        return src
    return src[idx + len(prefix):].lstrip()

def run_milz_source(src):
    core = strip_bespoke_prefix(src)
    tokens = tokenize(core)
    vm = MilzMachine()
    vm.run_tokens(tokens)
    return vm.get_output()

def main():
    if len(sys.argv) < 2:
        print("Usage: python MILZ.py \"PLEASE MILZ DO *vnoMiiii\"")
        return
    src = " ".join(sys.argv[1:])
    print(run_milz_source(src))

if __name__ == "__main__":
    main()
