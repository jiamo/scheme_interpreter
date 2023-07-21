#lang racket
(begin (let ((x 1)) (define f (lambda (y) (+ x y))) (let ((x 2)) (f 0))))
;(let ((x 1)) (+ x 1 1))