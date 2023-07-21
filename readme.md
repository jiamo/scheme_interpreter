I take the course from https://www.dabeaz.com/sicp.html.  
The course go through the sicp book.  
I only put my implemention in this repo.  
If you are going to take the course. You may want to check it.  

## prepare
   export PATH="/Applications/Racket v8.5/bin/":$PATH
   raco pkg install while-loop

## run and compare different interpreter
    python diff.py
    python diff_substitue.py
    python diff_meta.py

## file infomation
   meta.rkt write the interpreter by racket  
   scheme_subtitue.py is using subtitue tech  
   scheme_env is using env  

## advance tests for only racket implement

## TODO
[x] python interpreter don't support multi args in define