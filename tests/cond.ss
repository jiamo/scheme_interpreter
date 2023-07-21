#lang racket
(begin (define fact  (lambda (n) (cond ((= n 0) 1) (else (* n (fact (- n 1))))))) (fact 5))