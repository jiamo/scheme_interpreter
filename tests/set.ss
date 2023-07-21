#lang racket
(begin (define x 1) (define f (lambda (y) (+ x y))) (set! x 2) (f 0))