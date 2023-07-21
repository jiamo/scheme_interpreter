#lang racket
(require dyoo-while-loop)
(define (fact n) 
    (define result 1) 
    (while (> n 0) (set! result (* result n)) (set! n (- n 1))) 
    result)
(fact 5)