# Logic Puzzle Solver
This engine can solve logic puzzles with 1:1 correspondances between discrete sets of equal size and unique elements.

# [Example](../example.py)

## Task
[taken from Question 1 of the [KIT University Computer Science Self Assessment Test](https://selbsttest.informatik.kit.edu/frontend/www/), translated from german]

The three friends Anne, Anja and Anke visit the courses software technic, algorythms and programming paradigms 
with varying degrees of success (1.7/2.6/3.8). (note: in Germany the grading system is from 1 (best) to 6 (worst))
They search for their results in a list under the names Becker, Kramer and Wolff.
1. Anne passed witha grade of 2.6
2. Anja took the course algorythms. She has a better grade than student Wolff
3. Anke did not take programming paradigms

## Step 0: Imports
```py
from solver import Model
from sets import Set, OrderedSet
```

## Step 1: Create the datasets
```py
names = Set('names', ['anne', 'anja', 'anke'])
last_names = Set('last_names', ['becker', 'kramer', 'wolff'])
subjects = Set('subjects', ['software', 'algorythms', 'paradigms'])
grades = OrderedSet('grades', [1.7, 2.6, 3.8])
```

## Step 2: Create the model
```py
model = Model(names, last_names, subjects, grades)
```

## Step 3: Create the relations
```py
# == 1 ==
# read: `the grade of anne is 2.6` / `the grade related to the name anne is 2.6`
model.relate(names['anne'](grades) == 2.6)
# which is the same as:
# model.relate(names['anne'] == grades[2.6])
# == 2 ==
model.relate(names['anja'] == subjects['algorythms'])
model.relate(names['anja'](grades) < last_names['wolff'](grades))
# == 3 ==
model.relate(names['anke'] != subjects['paradigms'])
model.relate((names['anke'] & last_names['kramer']) > grades[1.7])
# the `&` above is a short form for the 3 following relations:
# model.relate(names['anke'] > grades[1.7])
# model.relate(last_names['kramer'] > grades[1.7])
# model.relate(names['anke'] != last_names['kramer'])
```

## Step 4: Evaluate the relations
```py
solver = model.solver()
solution = solver.solve()

print(solution)
```

## Result
| names | last_names | subjects   | grades |
|-------|------------|------------|--------|
| anne  | kramer     | paradigms  | 2.6    |
| anja  | becker     | algorythms | 1.7    |
| anke  | wolff      | software   | 3.8    |