from scheme_subtitue import seval, translate , builtins
import subprocess

import pathlib
import sys
right_program_path = pathlib.Path(__file__).resolve().parent
right_files = list(right_program_path.glob("tests/*.ss"))

racket_path = "/Applications/Racket v8.5/bin/racket"


def main():
    for file in right_files:
        print(file)
        with open(file) as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("#") or line.startswith(";"):
                    continue
                r1 = seval(translate(line))

            print("r1 is ", r1)
            r2 = subprocess.check_output([racket_path, str(file)])
            r2 = r2.decode().strip("\n")
            if r2 == "#t":
                r2 = True
            elif r2 == "#f":
                r2 = False
            else:
                r2 = int(r2)
            print("r2 is ", r2)
            assert  r1 == r2


if __name__ == "__main__":
    main()