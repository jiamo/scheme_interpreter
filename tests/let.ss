#lang racket
(begin (let ((x 1)) (define f (lambda (y) (+ x y))) (let ((x 2)) (f 0))))