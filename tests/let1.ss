#lang racket
(let ((x 3) (y 4)) (+ (let ((x (+ y 5))) (* x y)) x))