import sys
sys.path.append('..')
from lps import Set, OrderedSet, Model

# === Task ===
# [taken from Question 2 of the KIT computer science self assessment test, translated into english (https://selbsttest.informatik.kit.edu/frontend/www/)]
# Three programmers (Meyer, Scmitz, Müller) are developing a new software system. Each programmer works on a different component (algorythms, user interface, database).
# The programmers work in different departments (A, B, C). The components have different deadlines (December 2013, January 2014, May 2014).
#
# 1. In department A the algorythms are developed. This department has less time than at least one other department.
# 2. Department C has to finish its work til January.
# 3. Neither department C nor porgrammer Schmitz work with databases.
# 4. Programmer Müller has to be finished in May.

# === Step 1: Create the datasets ===
programmers = Set('programmers', ['meyer', 'schmitz', 'mueller'])
components = Set('components', ['algorythms', 'ui', 'database'])
departments = Set('departments', ['a', 'b', 'c'])
# Using fractions to mock dates which are orderable.
# Creating an object which is comparable or using datetime would also have worked.
deadlines = OrderedSet('deadlines', [2013.12, 2014.1, 2014.5])

# === Step 2: Create the model ===
model = Model(programmers, components, departments, deadlines)

# === Step 3: Create the relations ===
# == 1 ==
model.relate(departments['a'] == components['algorythms'])
# cannot be last deadline since at least one other department has to be finished afterwards
model.relate(departments['a'] < deadlines[2014.5])
# == 2 ==
model.relate(departments['c'] == deadlines[2014.1])
# == 3 ==
model.relate((departments['b'] & programmers['schmitz']) != components['database'])
# == 3 ==
model.relate(programmers['mueller'] == deadlines[2014.5])

# === Step 4: Evaluate the relations ===
solver = model.solver()

# a `ValueError` is thrown if there are not enough constraints to solve the model fully
# or the model ran for too few iterations (unlikey for small models).
# Check whether oyur input text allows you to deduce another formal statement whcih you didnt notice before.
# If there is a sttement error, aka no element from a set satisfies the conditions,
# a `ArithemeticError` is thrown. This should be due to an input error by the user.
try:
    solution = solver.solve()
    print(solution)
except ValueError:
    print(solver)

# | programmers | components | departments | deadlines |
# |-------------|------------|-------------|-----------|
# | meyer       | database   | c           | 2014.1    |
# | schmitz     | algorythms | a           | 2013.12   |
# | mueller     | ui         | b           | 2014.5    |