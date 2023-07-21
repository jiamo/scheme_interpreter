#lang racket
(begin (define f (lambda (x y z) (+ x (* y z)))) (f 1 2 3))