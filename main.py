from solver import Solver
from sets import Set, OrderedSet

names = Set('names', ['anne', 'anja', 'anke'])
last_names = Set('last_names', ['becker', 'kramer', 'wolff'])
subjects = Set('subjects', ['software', 'algorythms', 'paradigms'])
grades = OrderedSet('grades', [1.7, 2.6, 3.8])

solver = Solver(names, last_names, subjects, grades)

# 1
solver.relate(names['anne'] == grades[2.6])
# 2
solver.relate(names['anja'] == subjects['algorythms'])
solver.relate(names['anja'](grades) < last_names['wolff'](grades))
# 3
solver.relate(names['anke'] != subjects['paradigms'])
# solver.relate((names['anke'] and last_names['kramer']) > grades[1.7])
solver.relate(names['anke'] > grades[1.7])
solver.relate(last_names['kramer'] > grades[1.7])
# </>
solver.relate(names['anke'] != last_names['kramer'])

result = solver.solve()