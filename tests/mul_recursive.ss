#lang racket
(begin (define even (lambda (n) (cond ((= n 0) #t) ((= n 1) #f) (else  (odd (- n 1)))))) (define odd (lambda (n) (cond ((= n 0) #f) ((= n 1) #t) (else  (even (- n 1)))))) (even 41))