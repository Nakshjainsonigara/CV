from pulp import LpMaximize, LpProblem, LpVariable

class CarbonOptimizer:
    def __init__(self, actions):
        self.actions = actions
        
    def optimize(self, budget, max_effort):
        # Initialize optimization problem
        model = LpProblem(name="carbon_optimization", sense=LpMaximize)
        
        # Decision variables
        x = {action: LpVariable(name=action, lowBound=0, cat='Integer') 
             for action in self.actions}
        
        # Objective function: Maximize CO2 savings
        model += sum(self.actions[action]["savings"] * x[action] 
                    for action in self.actions)
        
        # Constraints
        # Budget constraint
        model += sum(self.actions[action]["cost"] * x[action] 
                    for action in self.actions) <= budget
        
        # Effort constraint
        model += sum(self.actions[action]["effort"] * x[action] 
                    for action in self.actions) <= max_effort
        
        # Solve the optimization problem
        model.solve()
        
        # Get results
        results = {action: x[action].value() for action in self.actions}
        return results 