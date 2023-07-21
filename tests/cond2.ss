#lang racket
(begin (define fib (lambda (n) (cond ((< n 2) n) (else (+ (fib (- n 1)) (fib (- n 2))))))) (fib 9))