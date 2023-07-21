from scheme_env import seval, translate  , builtins
import subprocess

import pathlib
import sys
right_program_path = pathlib.Path(__file__).resolve().parent
right_files = list(right_program_path.glob("tests/*.ss"))

racket_path = "racket"

# for simple one line
def main():
    for file in right_files:
        with open(file) as f:
            print(file)
            environ = (builtins, {})
            lines = f.readlines()
            for line in lines:
                if line.startswith("#") or line.startswith(";") or line.startswith("(require"):
                    continue
                s = translate(line)
                print(s)
                r1 = seval(s, environ)

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