from itertools import permutations
from enum import Enum
from time import time_ns

class Variable:
    def __init__(self, available_options: list):
        self.domain = list(permutations(available_options))
        self.available_options = available_options
        self.value = None

    def reset(self):
        self.domain = list(permutations(self.available_options))
        self.value = None

class Orientation(Enum):
    RIGHT = 1
    LEFT = 2
    NEXT_TO = 3


def add_constraint(constraint_function: callable, constraints: dict, variable1: Variable, variable2: Variable = None):
    constraints[variable1].append(constraint_function)
    if (variable2 is not None and variable1 != variable2):
        constraints[variable2].append(constraint_function)


def equality_constraint(variable1: Variable, variable1_value: str, variable2: Variable, variable2_value: str):
    if (variable1.value is None or variable2.value is None):
        return True
    return variable1.value.index(variable1_value) == variable2.value.index(variable2_value)


def neighbourhood_constraint(orientation: Orientation, variable1: Variable, variable1_value: str,
                             variable2: Variable, variable2_value: str):
    if (variable1.value is None or variable2.value is None):
        return True
    if (orientation == Orientation.RIGHT):
        return variable1.value.index(variable1_value) - variable2.value.index(variable2_value) == 1
    if (orientation == Orientation.LEFT):
        return variable1.value.index(variable1_value) - variable2.value.index(variable2_value) == -1
    if (orientation == Orientation.NEXT_TO):
        return abs(variable1.value.index(variable1_value) - variable2.value.index(variable2_value)) == 1
    raise ValueError("Unknown orientation type")


def position_constraint(position: int, variable: Variable, variable_value: str):
    if (variable.value is None):
        return True
    return variable.value.index(variable_value) == position


def domains_not_empty(variables: list):
    for variable in variables:
        if (not variable.domain):
            return False
    return True


def backtracking(variables: list, constraints: dict):
    i = 0
    start = time_ns() // 1000000
    while i < len(variables):
        global iterations
        current_variable = variables[i]

        if (not current_variable.domain):
            if (i == 0):
                print("No solution to the puzzle")
                break
            current_variable.reset()
            i -= 1
        else:
            iterations += 1
            current_variable.value = current_variable.domain[0]
            del current_variable.domain[0]
            constraints_satisfied = True
            for constraint in constraints[current_variable]:
                if (not constraint()):
                    constraints_satisfied = False
                    break
            if (constraints_satisfied):
                i += 1
    for variable in variables:
        print(variable.value)
    
    print(f'\nTime of execution of backtracking algorithm: {time_ns() // 1000000 - start}ms')


def adjust_domains(variables: list, constraints: dict, current_variable: Variable):
    for variable in variables:
        if (variable == current_variable):
            continue
        new_domain = []
        variable_value = variable.value
        for option in variable.domain:
            variable.value = option
            constraints_satisfied = True
            for constraint in constraints[variable]:
                if (not constraint()):
                    constraints_satisfied = False
                    break
            if (constraints_satisfied):
                new_domain.append(option)
        variable.domain = new_domain
        variable.value = variable_value

def backtracking_with_forward_checking(variables: list, constraints: dict, i: int = 0):
    global iterations
    global start
    start = time_ns() / 1000000
    if (i == len(variables)):
        return True
    current_variable = variables[i]
    for value in current_variable.domain:
        iterations += 1
        current_variable.value = value
        constraints_satisfied = True
        for constraint in constraints[current_variable]:
            if (not constraint()):
                constraints_satisfied = False
                break
        domains = {}
        if (constraints_satisfied):
            for variable in variables[i+1:]:
                domain = []
                domains[variable] = variable.domain
                for val in variable.domain:
                    variable.value = val
                    constraints_satisfied = True
                    for constraint in constraints[variable]:
                        if (not constraint()):
                            constraints_satisfied = False
                            break
                    if (constraints_satisfied):
                        domain.append(val)
                    variable.value = None
                variable.domain = domain
            result = backtracking_with_forward_checking(variables, constraints, i + 1)
            if (result):
                return True
        current_variable.value = None
        for variable in domains:
            variable.domain = domains[variable]
    return False


if (__name__ == '__main__'):
    house_color = Variable(['red', 'green', 'ivory', 'yellow', 'blue'])
    nationality = Variable(['Englishman', 'Spaniard', 'Ukrainian', 'Norwegian', 'Japanese'])
    pets = Variable(['dog', 'snails', 'fox', 'horse', 'zebra'])
    drinks = Variable(['coffee', 'tea', 'milk', 'orange juice', 'water'])
    cigarettes = Variable(['Old Golds', 'Kools', 'Chesterfields', 'Lucky Strikes', 'Parliaments'])

    variables = []
    variables.extend([house_color, nationality, pets, drinks, cigarettes])

    constraints = {}
    constraints[house_color] = []
    constraints[nationality] = []
    constraints[pets] = []
    constraints[drinks] = []
    constraints[cigarettes] = []

    # 1. There are five houses.
    # 2. The Englishman lives in the red house.
    add_constraint(lambda: equality_constraint(nationality, 'Englishman', house_color, 'red'),
                   constraints, nationality, house_color)

    # 3. The Spaniard owns the dog.
    add_constraint(lambda: equality_constraint(nationality, 'Spaniard', pets, 'dog'),
                   constraints, nationality, pets)

    # 4. Coffee is drunk in the green house.
    add_constraint(lambda: equality_constraint(drinks, 'coffee', house_color, 'green'),
                   constraints, drinks, house_color)

    # 5. The Ukrainian drinks tea.
    add_constraint(lambda: equality_constraint(nationality, 'Ukrainian', drinks, 'tea'),
                   constraints, nationality, drinks)

    # 6. The green house is immediately to the right of the ivory house.
    add_constraint(lambda: neighbourhood_constraint(Orientation.RIGHT, house_color, 'green', house_color, 'ivory'),
                   constraints, house_color, house_color)

    # 7. The Old Gold smoker owns snails.
    add_constraint(lambda: equality_constraint(cigarettes, 'Old Golds', pets, 'snails'),
                   constraints, cigarettes, pets)

    # 8. Kools are smoked in the yellow house.
    add_constraint(lambda: equality_constraint(cigarettes, 'Kools', house_color, 'yellow'),
                   constraints, cigarettes, house_color)

    # 9. Milk is drunk in the middle house.
    add_constraint(lambda: position_constraint(2, drinks, 'milk'),
                   constraints, drinks)

    # 10. The Norwegian lives in the first house.
    add_constraint(lambda: position_constraint(0, nationality, 'Norwegian'),
                   constraints, nationality)

    # 11. The man who smokes Chesterfields lives in the house next to the man with the fox.
    add_constraint(lambda: neighbourhood_constraint(Orientation.NEXT_TO, cigarettes, 'Chesterfields', pets, 'fox'),
                   constraints, cigarettes, pets)

    # 12. Kools are smoked in the house next to the house where the horse is kept.
    add_constraint(lambda: neighbourhood_constraint(Orientation.NEXT_TO, cigarettes, 'Kools', pets, 'horse'),
                   constraints, cigarettes, pets)

    # 13. The Lucky Strike smoker drinks orange juice.
    add_constraint(lambda: equality_constraint(cigarettes, 'Lucky Strikes', drinks, 'orange juice'),
                   constraints, cigarettes, drinks)

    # 14. The Japanese smokes Parliaments.
    add_constraint(lambda: equality_constraint(nationality, 'Japanese', cigarettes, 'Parliaments'),
                   constraints, nationality, cigarettes)

    # 15. The Norwegian lives next to the blue house.
    add_constraint(lambda: neighbourhood_constraint(Orientation.NEXT_TO, nationality, 'Norwegian', house_color, 'blue'),
                   constraints, nationality, house_color)

    global iterations
    iterations = 0
    global start

    # backtracking(variables, constraints)
    # for variable in variables:
    #         print(variable.value)
    # print(f'Iterations: {iterations}')

    if (backtracking_with_forward_checking(variables, constraints)):
        for variable in variables:
            print(variable.value)
    print(f'Iterations: {iterations}')
    print(f'\nTime of execution of backtracking FC algorithm: {time_ns() // 1000000 - start}ms')
