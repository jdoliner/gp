;;mapcar needs to be extended to work with macros

(defun mapcar-macro (lst)
	(cond
		((eq lst nil) nil)
		(T (let ((front (first lst)))
			(cons (safe-funtion front) (mapcar-macro (rest lst)))))))

;;remove duplicates rearranges the elements of the list in an undesirable way
(defun remove-dupes-helper (lst accum)
	(cond
		((eq lst nil) nil)
		((member (first lst) accum) (remove-dupes-helper (rest lst) accum))
		(T (cons (first lst) (remove-dupes-helper (rest lst) (cons (first lst) accum))))))

(defun remove-dupes (lst)
	(remove-dupes-helper lst nil))


;;these only seem to work for user created functions,
;;not so solid for builtins, more on those later
;;where also going to run into problems with variable numbers of arguments
;;these need to be passed symbols, not functions
(defun args (fsymbol)
	(first (rest (rest (first (first (rest (symbol-plist fsymbol)))))))
)

(defun body (fsymbol)
	(first (rest (rest (rest (first (first (rest (symbol-plist fsymbol))))))))
)

;;now we need versions of that are safe for mapping modifier lists
;;really this means that when they get nil, they return nil,
;;otherwise they behave as normal
(defun safe-args (fsymbol)
	(cond
		((eq None fsymbol) None) ;;this slot doesn't have a function
		(T (args fsymbol))))

(defun safe-body (fsymbol)
	(cond
		((eq None fsymbol) None) ;;this slot doesn't have a function
		(T (body fsymbol))))

;;insert an atom into a list at a given position
(defun insert-atom (insertion orig location)
	(cond
		((= location 1) (cons insertion (rest orig)))
		(T (cons (first orig) (insert-atom insertion (rest orig) (- location 1))))))

;;given two lists and a location (integer) replaces the element of that index
;;in the orig list with the insertion list
(defun insert-args (insertion orig location)
	(cond
		((= location 1) (append insertion (rest orig)) )
		(T (cons (first orig) (insert-args insertion (rest orig) (- location 1))))))

;;this function takes a list of insertions and an orig list, they must
;;be of the same length or we hit an error (add that shit later)
;;each element of insertions is either a list, or the symbol 'pass
;;if it's symbols they're spliced in, the old thing in that place, if 0
;;nothing happens

;;basically we need nil to do two things, represent a function that has no arguments
;;and represent the case where we want to just leave things blank so one of them need to change
;;we're going to change when we want to leave the spot blank since that makes more sense
;;we reserve the word none to represent no function.
;;This is quite a hack by having the symbol set to itself we bypass lazy evaluation alot
;;this really should be fine just don't use "None" for anything else
(setq None 'None)

(defun insert-lists (insertions original)
	(let ((front (pop insertions)))
	(cond
		((eq original nil) nil)
		((eq front None) (cons (pop original) (insert-lists insertions  original)))
		(T (append front (insert-lists insertions (rest original)))))))

;;insert-atoms
;;solidly a knock-off of insert-lists, the only difference is that it doesn't do any splicing
(defun insert-atoms (insertions original)
	(let ((front (pop insertions)))
	(cond
		((eq original nil) nil)
		((eq front None) (cons (pop original) (insert-atoms insertions original)))
		(T (cons front (insert-atoms insertions (rest original)))))))




;;this guy works!!! set something equal to it, then hit apply on that thing with args 
(defmacro copy-function (f)
		`(lambda ,(args f) ,(body f))
)

(defmacro make-function (args body)
	`(lambda ,args ,body))

(defmacro make-function2 (name args body)
	`(defun ,name ,args ,body)) 

(defmacro apply-f (f args)
	`(funcall ,f ,args))
;;safe-function creates a safe version of a function, safe in two regards, 
;;first it's variable names are gensyms so there is no risk of a collision when we compose the function
;;second its body is just a call to the function, so it's abstraction doesn't get violated.
(defun gensym-wrapper (arg)
	(cond
		((integerp arg) (gensym arg))
		(T (gensym))))

(defun gensym-args (f)
	(mapcar 'gensym-wrapper (args f)))

(defmacro gensym-body (f args)
	`(,f ,@args))  


;this guy works
(defmacro safe-function (f)
	(let ((arguments (gensym-args f))
	      (name (gentemp (symbol-name f))))
		`(make-function2 ,name ,arguments (,f ,@arguments))))

(defun make-comp-lis-safe (comp-lis)
	(cond
		((eq comp-lis nil) nil)
		(T (let ((front (safe-function-wrapper (first comp-lis))))
				(cons front (make-comp-lis-safe (rest comp-lis))))))) 


;;and this one actually works, it still fails on lambda functions for now, but that's less of a problem since it doesn't make lambda functions.
(defmacro compose-slot (newf f g slot)
	(let ((arguments (insert-args (args g) (args f) slot))
	     (body `(,f ,@(insert-atom (body g) (args f) slot))))
	`(make-function2 ,newf ,arguments ,body)))

(defun make-args (f comp-lis)
	(insert-lists (mapcar 'safe-args comp-lis) (args f)))

(defun make-body (f comp-lis)
	`(,f ,@(insert-atoms (mapcar 'safe-body comp-lis) (args f))))

;this chap works, and it is magnificent
(defmacro compose (newf f comp-lis) 
	(let* ((arguments (make-args f (symbol-value comp-lis)))
	       (body (make-body f (symbol-value comp-lis))))
	`(make-function2 ,newf ,arguments ,body)))

;well saints be praised this works too
(defmacro pinch (newf f pinch-list)
	(let* ((arguments (remove-dupes (symbol-value pinch-list)))
	       (body `(,f ,@(symbol-value pinch-list))))
	`(make-function2 ,newf ,arguments ,body)))

;;so it turns out that symbol-value is really key
;;who knew


;;some basic building blocks

(defun plus (x y)
  (+ x y))

(defun minus (x y)
  (- x y))

(defun mult (x y)
  (* x y))

(defun div (x y)
  (cond
    ((eq (coerce (eval y) 'float) 0.0) x)
    (T	(coerce (/ x y) 'float) ) ) )

(defun one ()
  1)

(setq a (list (safe-function one) (safe-function one)))
(compose two plus a)
