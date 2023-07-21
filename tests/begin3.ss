#lang racket
(begin (define f (lambda (x y) (g y x))) (define g (lambda (x y) (- x y))) (f 1 2))