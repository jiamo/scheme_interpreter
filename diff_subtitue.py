from scheme_subtitue import seval, translate , builtins
from util import decode
import subprocess
import pathlib
import sys
import scheme_subtitue

right_program_path = pathlib.Path(__file__).resolve().parent
right_files = list(right_program_path.glob("tests/*.ss"))

racket_path = "racket"


def main():
    for file in right_files:
        print(file)
        # need clean....
        scheme_subtitue.clean_env()
        with open(file) as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("#") or line.startswith(";") or line.startswith("(require"):
                    continue
                r1 = seval(translate(line))

            print("r1 is ", r1)
            r2 = subprocess.check_output([racket_path, str(file)])
            r2 = decode(r2)
            print("r2 is ", r2)
            assert  r1 == r2


if __name__ == "__main__":
    main()