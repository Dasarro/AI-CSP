import tkinter as tk
from math import hypot
from random import randrange
from time import time_ns
from statistics import stdev, mean

class Node:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.color = None
        self.domain = [0, 1, 2, 3]

    def distance(self, node: 'Node'):
        return hypot(node.x - self.x, node.y - self.y)

    def reset_node(self):
        self.domain = [0, 1, 2, 3]
        self.color = None

    def check_constraint(self, other: 'Node'):
        if (self.color is None or other.color is None):
            return True
        if (self.color == other.color):
            return False
        return True

    def __str__(self):
        return f'({self.x}, {self.y})'

    def __eq__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

class Path:
    def __init__(self, start_node: Node, end_node: Node):
        self.start_node = start_node
        self.end_node = end_node

    def intersect(self, path: 'Path'):
        A, B = self.start_node, self.end_node
        C, D = path.start_node, path.end_node

        if (A.x == B.x and C.x == D.x):
            if (A.x != C.x):
                return False
            min1 = min(A.y, B.y)
            max1 = max(A.y, B.y)

            min2 = min(C.y, D.y)
            max2 = max(C.y, D.y)

            minIntersection = max(min1, min2)
            maxIntersection = min(max1, max2)

            if (minIntersection < maxIntersection):
                return True
            else:
                return False

        try:
            a1 = (B.y - A.y) / (B.x - A.x)
            a2 = (D.y - C.y) / (D.x - C.x)

            b1 = A.y - a1 * A.x
            b2 = C.y - a2 * C.x

            if (a1 == a2 and b1 == b2):
                distance = A.distance(B) + C.distance(D)
                return not (A.distance(C) >= distance or A.distance(D) >= distance or
                            B.distance(C) >= distance or B.distance(D) >= distance)
        except ZeroDivisionError:
            pass

        dx0 = B.x - A.x
        dx1 = D.x - C.x
        dy0 = B.y - A.y
        dy1 = D.y - C.y

        p0 = dy1 * (D.x - A.x) - dx1 * (D.y - A.y)
        p1 = dy1 * (D.x - B.x) - dx1 * (D.y - B.y)
        p2 = dy0 * (B.x - C.x) - dx0 * (B.y - C.y)
        p3 = dy0 * (B.x - D.x) - dx0 * (B.y - D.y)

        return bool((p0 * p1 < 0) & (p2 * p3 < 0))

    def __str__(self):
        return f'[{self.start_node}, {self.end_node}]'

    def __eq__(self, other):
        if not isinstance(other, Path):
            return NotImplemented
        return self.start_node == other.start_node and self.end_node == other.end_node

class Map:
    def __init__(self, square_size: int):
        self.graph = {}
        self.paths = []
        self.square_size = square_size

    def random_graph(self, nodes_count: int):
        if (self.square_size ** 2 < nodes_count):
            raise ValueError(f"{nodes_count} nodes will not fit in {self.square_size}x{self.square_size} square.")
        self.graph = {}
        for _ in range(nodes_count):
            while True:
                x = randrange(0, self.square_size)
                y = randrange(0, self.square_size)
                new_node = Node(x, y)
                if (new_node not in self.graph):
                    self.graph[Node(x, y)] = []
                    break
        paths = []
        nothing_changed = 0
        while (nothing_changed < len(self.graph)):
            for base_node in self.graph:
                distances = {}
                for node in self.graph:
                    if (node == base_node):
                        continue
                    is_already_connected = False
                    for connected_node in self.graph[base_node]:
                        if (connected_node == node):
                            is_already_connected = True
                            break
                    if (is_already_connected):
                        continue
                    distances[node] = node.distance(base_node)
                sorted_distances = sorted(distances.items(), key=lambda item: item[1])
                for node, _ in sorted_distances:
                    current_path = Path(base_node, node)
                    is_intersecting = False
                    for path in paths:
                        if (current_path.intersect(path)):
                            is_intersecting = True
                            break
                    if (is_intersecting):
                        continue
                    paths.append(current_path)
                    self.graph[base_node].append(node)
                    self.graph[node].append(base_node)
                    nothing_changed = 0
                    break
                nothing_changed += 1
        self.paths = paths

    @staticmethod
    def domains_not_empty(variables: list):
        for variable in variables:
            if (not variable.domain):
                return False
        return True

    def reset_map_state(self):
        for variable in self.graph:
            variable.reset_node()

    def color_backtracking(self):
        i = 0
        t = 0
        backtracks = 0
        iterations = 0
        start = time_ns() // 1000000
        variables = list(self.graph)
        while i < len(self.graph):
            current_variable = variables[i]

            if ((time_ns() // 1000000 - start) // 5000 > t):
                print(f'{int(time_ns() // 1000000 - start)}ms', f'{iterations} iterations')
                t += 1

            if (not current_variable.domain):
                if (i == 0):
                    # print("Graph cannot be colored")
                    return None, None
                current_variable.reset_node()
                i -= 1
                backtracks += 1
            else:
                iterations += 1
                current_variable.color = current_variable.domain[0]
                current_variable.domain = current_variable.domain[1:]
                constraints_satisfied = True
                for variable in self.graph[current_variable]:
                    if (not variable.check_constraint(current_variable)):
                        constraints_satisfied = False
                        break
                if (constraints_satisfied):
                    i += 1
        return (time_ns() // 1000000 - start), iterations

    def color_backtracking_with_forward_checking(self):
        i = 0
        t = 0
        iterations = 0
        backtracks = 0
        start = time_ns() // 1000000
        variables = list(self.graph)
        historical_domains = {}
        for variable in variables:
            historical_domains[variable] = [variable.domain.copy()]
        while i < len(variables):
            current_variable = variables[i]

            if ((time_ns() // 1000000 - start) // 5000 > t):
                print(f'{int(time_ns() // 1000000 - start)}ms', f'{iterations} iterations')
                t += 1

            if (not Map.domains_not_empty(variables[i:])):
                if (i == 0):
                    # print("Graph cannot be colored")
                    return None, None
                for j, variable in enumerate(variables):
                    historical_domains[variable].pop()
                    if (j >= i):
                        variable.domain = historical_domains[variable][-1].copy()
                        variable.color = None
                i -= 1
                backtracks += 1
            else:
                iterations += 1
                current_variable.color = current_variable.domain[0]
                current_variable.domain = current_variable.domain[1:]
                constraints_satisfied = True
                for variable in self.graph[current_variable]:
                    if (current_variable.color in variable.domain and variables.index(variable) > variables.index(current_variable)):
                        variable.domain.remove(current_variable.color)
                    if (not variable.check_constraint(current_variable)):
                        constraints_satisfied = False
                for variable in variables:
                    historical_domains[variable].append(variable.domain.copy())
                if (constraints_satisfied):
                    i += 1
        return (time_ns() // 1000000 - start), iterations
                

    def draw(self):
        window = tk.Tk()
        window.title("Map coloring")
        width = height = 600
        ratio = width / self.square_size
        width += ratio
        height += ratio

        colors = ['orange red', 'green yellow', 'deep sky blue', 'plum1']

        canvas = tk.Canvas(window, bg='#C4C4C4', height=height, width=width)
        for path in self.paths:
            canvas.create_line((path.start_node.x + 1) * ratio, (path.start_node.y + 1) * ratio, 
                               (path.end_node.x + 1) * ratio, (path.end_node.y + 1) * ratio, 
                               fill='black', width=2)
        for node in self.graph:
            color = colors[node.color] if node.color is not None else 'snow'
            canvas.create_oval((node.x + 1) * ratio + 7, (node.y + 1) * ratio + 7,
                               (node.x + 1) * ratio - 7, (node.y + 1) * ratio - 7,
                               fill=color, outline=color)
            
        canvas.pack()
        
        window.protocol('WM_DELETE_WINDOW', exit)
        window.mainloop()


def test(nodes: int):
    map = Map(50)
    iterations_backtrack2 = []
    time_backtrack2 = []
    iterations_forward2 = []
    time_forward2 = []
    failed_attempts = 0

    while len(iterations_backtrack2) < 10:
        map.random_graph(nodes)
        time_backtrack, iterations_backtrack = map.color_backtracking()
        map.reset_map_state()
        time_forward, iterations_forward = map.color_backtracking_with_forward_checking()
        if (time_forward is None):
            failed_attempts += 1
            continue
        iterations_backtrack2.append(iterations_backtrack)
        iterations_forward2.append(iterations_forward)
        time_backtrack2.append(time_backtrack)
        time_forward2.append(time_forward)

    print(f"{nodes} nodes test")
    print("Min time and iterations backtrack: ", min(time_backtrack2), min(iterations_backtrack2))
    print("Max time and iterations backtrack: ", max(time_backtrack2), max(iterations_backtrack2))
    print("Average time and iterations backtrack: ", mean(time_backtrack2), mean(iterations_backtrack2))
    print("Standard deviation time and iterations backtrack: ", stdev(time_backtrack2), stdev(iterations_backtrack2))
    print()
    print("Min time and iterations forward: ", min(time_forward2), min(iterations_forward2))
    print("Max time and iterations forward: ", max(time_forward2), max(iterations_forward2))
    print("Average time and iterations forward: ", mean(time_forward2), mean(iterations_forward2))
    print("Standard deviation time and iterations forward: ", stdev(time_forward2), stdev(iterations_forward2))
    print(f"Percent of success: {(10 / (failed_attempts + 10)) * 100}%")

    map.draw()

                    
# test(25)
map = Map(50)
map.random_graph(25)
map.color_backtracking_with_forward_checking()
map.draw()
