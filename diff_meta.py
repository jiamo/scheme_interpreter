
import subprocess
import pathlib
from util import decode
import sys
right_program_path = pathlib.Path(__file__).resolve().parent
right_files = list(right_program_path.glob("tests/*.ss"))
advance_tests = list(right_program_path.glob("advance_tests/*.ss"))
racket_path = "racket"

# for simple one line
def main():
    for file in right_files + advance_tests:
        with open(file) as f:
            print(file)
            r1 = subprocess.check_output([racket_path, "meta.ss", str(file)])
            r1 = decode(r1)
            print("r1 is ", r1)
            r2 = subprocess.check_output([racket_path, str(file)])
            r2 = decode(r2)
            print("r2 is ", r2)
            assert  r1 == r2


if __name__ == "__main__":
    main()