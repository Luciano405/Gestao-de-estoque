import time
import itertools
from collections import namedtuple
from queue import PriorityQueue

Node = namedtuple("Node", ["level", "value", "weight", "bound", "x_vector"])

class BranchAndBoundSolver:


    def __init__(self, df, capacity, time_limit=None, max_nodes=None):
       
        
        items = df.copy().reset_index(drop=True)
        
        items["ratio"] = items["Lucro Estimado"] / (items["Volume (m³)"] + 1e-9)
        items = items.sort_values(by="ratio", ascending=False).reset_index(drop=True)

        self.items = items
        self.W = float(capacity)
        self.n = len(items)
        self.weights = items["Volume (m³)"].tolist()
        self.values = items["Lucro Estimado"].tolist()

        
        self.best_value = 0.0
        self.best_x = [0] * self.n

        
        self.expanded_nodes = 0
        self.pruned_nodes = 0
        self.feasible_solutions = 0
        self.max_depth = 0
        self.nodes_per_level = {}

        
        self.time_limit = None if (time_limit is None) else float(time_limit)
        self.max_nodes = None if (max_nodes is None) else int(max_nodes)

        
        self._counter = itertools.count()

    def _calculate_bound(self, node: Node) -> float:
     
        if node.weight >= self.W:
            return 0.0
        bound = node.value
        current_weight = node.weight
        j = node.level + 1
        
        while j < self.n and current_weight + self.weights[j] <= self.W:
            current_weight += self.weights[j]
            bound += self.values[j]
            j += 1
        
        if j < self.n:
            remaining = self.W - current_weight
            bound += self.values[j] * (remaining / (self.weights[j] + 1e-9))
        return bound

    def _greedy_primal(self):
       
        value = 0.0
        weight = 0.0
        x = [0] * self.n
        for i in range(self.n):
            if weight + self.weights[i] <= self.W:
                weight += self.weights[i]
                value += self.values[i]
                x[i] = 1
        return value, x

    def solve(self):
        
        start_time = time.time()

        
        primal_val, primal_x = self._greedy_primal()
        self.best_value = primal_val
        self.best_x = primal_x
        self.feasible_solutions = 1

        
        PQ = PriorityQueue()
        root_x = [0] * self.n
        root_bound = self._calculate_bound(Node(-1, 0.0, 0.0, 0.0, root_x))
        root = Node(-1, 0.0, 0.0, root_bound, root_x)
        PQ.put((-root.bound, next(self._counter), root))

        while not PQ.empty():
            
            if self.time_limit is not None and (time.time() - start_time) >= self.time_limit:
                break
            if self.max_nodes is not None and self.expanded_nodes >= self.max_nodes:
                break

            negb, _, u = PQ.get()
            
            if u.bound <= self.best_value:
                self.pruned_nodes += 1
                continue

            i = u.level + 1
            if i >= self.n:

                continue

           
            w_in = u.weight + self.weights[i]
            v_in = u.value + self.values[i]
            x_in = u.x_vector[:]
            x_in[i] = 1

            if w_in <= self.W:
                bound_in = self._calculate_bound(Node(i, v_in, w_in, 0.0, x_in))
                node_in = Node(i, v_in, w_in, bound_in, x_in)

                if i == self.n - 1:
                    
                    self.feasible_solutions += 1
                    if v_in > self.best_value:
                        self.best_value = v_in
                        self.best_x = x_in[:]
                elif bound_in > self.best_value:
                    PQ.put((-bound_in, next(self._counter), node_in))
                else:
                    self.pruned_nodes += 1
            else:
                
                self.pruned_nodes += 1

           
            x_ex = u.x_vector[:]
            x_ex[i] = 0
            bound_ex = self._calculate_bound(Node(i, u.value, u.weight, 0.0, x_ex))
            node_ex = Node(i, u.value, u.weight, bound_ex, x_ex)

            if i == self.n - 1:
                self.feasible_solutions += 1
                if u.value > self.best_value:
                    self.best_value = u.value
                    self.best_x = u.x_vector[:]
            elif bound_ex > self.best_value:
                PQ.put((-bound_ex, next(self._counter), node_ex))
            else:
                self.pruned_nodes += 1

            
            self.expanded_nodes += 1
            self.max_depth = max(self.max_depth, i)
            self.nodes_per_level[i] = self.nodes_per_level.get(i, 0) + 1

        end_time = time.time()
        metrics = {
            "Tempo Total (s)": end_time - start_time,
            "Nós Expandidos": self.expanded_nodes,
            "Nós Podados": self.pruned_nodes,
            "Soluções Viáveis": self.feasible_solutions,
            "Profundidade Máxima": self.max_depth,
            "Nodes per Level": self.nodes_per_level
        }

        return self.best_value, self.best_x, metrics



def solve_knapsack_with_bnb(df, capacity, time_limit=None, max_nodes=None):
    solver = BranchAndBoundSolver(df, capacity, time_limit=time_limit, max_nodes=max_nodes)
    return solver.solve()

