#lang racket
; Metacircular evaluator
;
; In this file, we will implement the meta-circular evaluator as described
; in Section 4.1 of SICP.
;
; However, rather than literally following the book letter-for-letter, we
; will be making various changes and simplifications that allow us to
; make more incremental process.
;
; The evaluator consists of two core functions.
;
;    (seval ...)
;    (sapply ...)
;
; seval evaluates an expression and returns the result.
; sapply is used to apply a procedure to arguments.
;
; Big idea:  All of computation is expressed by combinations of eval and apply.
; Thus, these two procedures are what we'll work with.  

; Evaluates an expression
(define (seval exp environ)      ; DO NOT UNDER ANY CIRCUMSTANCE CALL "environ",  "env"
    (cond ((primitive? exp) exp)
          ((boolean? exp) exp)
          ((symbol? exp) (lookup-in-environment environ exp))
          ((quote? exp) exp)
          ; Special forms?
          ((begin? exp) (seval-begin exp environ))
          ((define? exp) (seval-define exp environ))    ; Code will be very similar to derivative example
          ((if? exp) (seval-if exp environ))
          ((and? exp) (seval-and exp environ))
          ((or? exp) (seval-or exp environ))
          ((cond? exp) (seval-cond exp environ))
          ((let? exp) (seval-let exp environ))
          ((lambda? exp) (seval-lambda exp environ))
          ((set!? exp) (seval-set! exp environ))
          ((while? exp) (seval-while exp environ))
          ;
          ; Is it a procedure??
          ((list? exp)
           (sapply exp environ))
          ((list? exp) (sapply exp environ))
          (else (error "Can't evaluate" exp)))
)

(define (quote? exp) (and (pair? exp) (eq? (car exp) 'quote)))

(define (primitive? exp)
  (number? exp))

(define (define? exp)
  (and (pair? exp) (eq? (car exp) 'define)))

;; suppport (define (f x) (+ x 1))
(define (define-name exp)
  (if (pair? (cadr exp))
   (caadr exp)
   (cadr exp)))

(define (define-value exp)
  (cond
    ((pair? (cadr exp))
      ;(display `(lambda ,(cdadr exp) ,@(cddr exp)))
      `(lambda ,(cdadr exp) ,@(cddr exp)))
    (else (caddr exp))))

(define (seval-define exp environ)
  (let ((value (seval (define-value exp) environ))
        (name (define-name exp)))
    (define-in-environment environ name value )))

(define (begin? exp)
  (and (pair? exp) (eq? (car exp) 'begin)))
(define (begin-exps exp) (cdr exp))

;; eval all but return last

(define (seval-begin exp environ)
  (seval-many (begin-exps exp) environ))

(define (seval-many exp environ)
  (cond
    ((null? (cdr exp)) (seval (car exp) environ))
    (else (seval (car exp) environ)
          (seval-many (cdr exp) environ))))
;; eval all exp but return the last exp
;; the seval-many is the same as my 

(define (while? exp) (and (pair? exp) (eq? (car exp) 'while)))
(define (while-predicate exp) (cadr exp))
(define (while-expressions exp) (cddr exp))
(define (seval-while exp environ)
  (cond ((seval (while-predicate exp) environ)
         (seval-many (while-expressions exp) environ)
         (seval-while exp environ))))

(define (if? exp) (and (pair? exp) (eq? (car exp) 'if)))
(define (if-test exp) (cadr exp))
(define (if-then-expr exp) (caddr exp))
(define (if-else-expr exp) (cadddr exp))


(define (cond? exp)
  (and (pair? exp)
       (eq? 'cond (car exp))))

(define (cond-body exp) (cdr exp))
(define (cond-branchs exp) (cdr exp))
(define (cond-branch-test exp) (car exp))
(define (cond-branch-body exp) (cdr exp))

(define (cond-test-eval exp environ)
  (or (eq? 'else exp)
      (seval exp environ)))

(define (seval-cond-branchs exp environ)
  (define (iter exp environ)
    (let ((branch (car exp)))
      (if (cond-test-eval (cond-branch-test branch) environ)
          (seval-many (cond-branch-body branch) environ)
          (iter (cdr exp) environ))))
  (iter exp environ))

(define (seval-cond exp environ)
  (seval-cond-branchs (cond-branchs exp) environ))

(define (and? exp) (and (pair? exp) (eq? (car exp) 'and)))
(define (and-exprs exp) (cdr exp))
(define (seval-and exp environ)
  (define (eval-true exprs)
    (cond ((null? exprs) #t)
          ((null? (cdr exprs)) (seval (car exprs) environ))
          ((seval (car exprs) environ) (eval-true (cdr exprs)))
          (else #f)))
  (eval-true (and-exprs exp)))

(define (or? exp) (and (pair? exp) (eq? (car exp) 'or)))
(define (or-exprs exp) (cdr exp))
(define (seval-or exp environ)
  (define (eval-false exprs)
    (cond ((null? exprs) #t)
          ((null? (cdr exprs)) (seval (car exprs) environ))
          ((not (seval (car exprs) environ)) (eval-false (cdr exprs)))
          (else #t)))
  (eval-false (or-exprs exp)))

(define (set!? exp) (and (pair? exp) (eq? (car exp) 'set!)))
(define (set!-name exp) (cadr exp))
(define (set!-value exp) (caddr exp))
(define (seval-set! exp environ)
  (set-in-environment! environ (set!-name exp) (seval (set!-value exp) environ)))


(define (lambda? exp) (and (pair? exp) (eq? (car exp) 'lambda)))
(define (lambda-args exp) (cadr exp))
(define (lambda-body exp) (cddr exp)) ;; lambda can have multi exp

(define (make-lambda argnames body environ)
  ;(display argnames)
  (lambda args
    (let ((new-environ (make-new-environment environ)))
      (define (update-args-in-new-environ names vals)
        (cond ((or (null? names) (null? vals)) null)
              (else (define-in-environment new-environ (car names) (car vals))
                    (update-args-in-new-environ (cdr names) (cdr vals)))))
      (update-args-in-new-environ argnames args)

      (seval-many body new-environ))))

; return not produce return


;(define (seval-lambda exp environ)
;  (make-lambda (lambda-args exp) (lambda-body exp) environ))

(define (make-closure exp environ)
  (list 'closure exp environ))

(define (seval-lambda exp environ)
  (make-closure exp environ))

(define (closure-env exp)
  (caddr exp))
(define (closure-lambda exp)
  (cadr exp))

(define (seval-closure exp args environ)
  (let ((new-env (make-new-environment (closure-env exp))))
    (begin
      (define-multi-in-environment new-env
        (lambda-args (closure-lambda exp)) args)
      (seval-many (lambda-body (closure-lambda exp)) new-env))))


;; not god at such ` and ,@ 
(define (let? exp) (and (pair? exp) (eq? (car exp) 'let)))
(define (let-names exp)
  ;(display exp)
  (map car (cadr exp)))
(define (let-values exp)
  (map cadr (cadr exp)))
(define (let-expressions exp)
  (cddr exp))
(define (seval-let-use-begin exp environ)
   (let ((names (let-names exp))
         (values (map (lambda (arg) (seval arg environ)) (let-values exp)))
         (expressions (let-expressions exp))
         (new-env (make-new-environment environ)))
     (define-multi-in-environment new-env names values)
     (seval `(begin ,@expressions) new-env)))

(define (seval-let-use-lambda exp environ)
  
   (let ((names (let-names exp))
         (values (map (lambda (arg) (seval arg environ)) (let-values exp)))
         (expressions (let-expressions exp)))
     ;(display `((lambda ,names (begin ,@expressions)) ,@values))
     (seval `((lambda ,names (begin ,@expressions)) ,@values) environ)))
;using let and 


(define (seval-let exp environ)
  ;;(seval-let-use-lambda exp environ)
  (seval-let-use-begin exp environ)
  )     

(define (seval-if exp environ)
  (if (seval (if-test exp) environ)
      (seval (if-then-expr exp) environ)
      (seval (if-else-expr exp) environ)))

; Executes a procedure
(define (sapply exp environ)
    (let ((proc (seval (car exp) environ))
          (args (map (lambda (arg) (seval arg environ)) (cdr exp))))
      (cond
        ((procedure? proc) (apply proc args))
        ((eq? (car proc) 'closure) (seval-closure proc args environ))
            ;(else (apply proc args))
            )))

; Initial steps:
;  1. The environment.   Use racket hash table.  (See chapter 2, "The box")
;  2. Builtin operators (+, -, *, /)
;  3. Executing the builtin operators.

; ------ The Environment.
; One big idea in SICP is the idea of making abstraction layers.   This means that you "wishfully think" some features into
; existence related to environments.  What do you want to do with the environment?
;
; Inside the procedures, you can make the environment whatever you want.  Use a Racket hash table. Use something else.
; Other code will only use these high-level procedures.

(define (make-new-environment parent)
  ;(make-hash)    ; Racket feature
  (cons (make-hash) parent))



(define (define-in-environment environ name value)
  ;(hash-set!  environ name value)   ; Racket feature (hashes)
  (hash-set!  (car environ) name value)
  )

;;(define (lookup-in-environment environ name)
;;  (hash-ref environ name))
(define (lookup-in-environment environ name)
  (cond ((null? environ) (error "Name not found -- " name))
        ((hash-has-key? (car environ) name) (hash-ref (car environ) name))
        (else (lookup-in-environment (cdr environ) name))))

(define (update-in-environment! environ name value)
  (cond ((null? environ) null)
        ((hash-has-key? (car environ) name) (hash-set! (car environ) name value))
        (else (update-in-environment! (cdr environ) name value))))

(define (set-in-environment! environ name value)
  (if (hash-has-key? (car environ) name)
      (hash-set! (car environ) name value)
      (set-in-environment! (cdr environ) name value)))

(define (define-multi-in-environment environ namelist varlist)
  (for ((name namelist)
        (var varlist))
    (define-in-environment environ name var)))

; ------ Builtin operations
; Write a procedure that installs built-in operations into an environment
(define (install-builtins environ)
  (define-multi-in-environment environ
    '(+ - * / = < > >= <= display displayln #t)
     (list + - * / = < > >= <= display displayln #t))
;  (define-in-environment environ '+ +)
;  (define-in-environment environ '- -)
;  ; Add more definitions ... yes, I could probably do something more sophisticated than repeatedly calling define-in-environment.
;  ; Or, I could just cut/paste it and get on with writing the rest of the project.  I choose the latter.
;  (define-in-environment environ '* *)
;  (define-in-environment environ '/ /)
;  (define-in-environment environ '= =)
;  (define-in-environment environ '< <)
;  (define-in-environment environ '> >)
;  (define-in-environment environ '<= <=)
;  (define-in-environment environ '>= >=)
  )

; Create the global environ
(define environ (make-new-environment null))
(install-builtins environ)


(define r3
  (lambda (exp)
    (seval exp environ)))
;;(seval 42 environ)

;;(define filename (car (current-command-line-arguments)))

;(define file-content 
;  (file->string filename))

;(seval file-content)

(define (ignore-#lang str)
  (if (or (string-prefix? str "#lang") (string-prefix? str ";") (string-prefix? str "(require"))
        'ignore
        (with-input-from-string str read)))

(define (strings->sexps strings)
  (filter
    (lambda (x) (not (eq? x 'ignore)))
    (map ignore-#lang strings)))


(define args (current-command-line-arguments))
(define filename (vector-ref args 0))

;; at now for simple. I can only parse one line sexp
(define lst (file->lines filename))


(define sexps (strings->sexps lst))
(define wrapped-sexps (cons 'begin sexps))
(r3 wrapped-sexps)

