import streamlit as st
from optimization import CarbonOptimizer
from rl_agent import RLAgent
import os
import json

class CarbonOptimizerApp:
    def __init__(self):
        # Initialize the data
        self.actions = {
            "bike": {
                "name": "Bike instead of drive",
                "savings": 100,  # CO2 savings in kg
                "cost": 0,      # Cost in dollars
                "effort": 3     # Effort scale 1-5
            },
            "reduce_beef": {
                "name": "Replace beef with plant-based",
                "savings": 40,
                "cost": 0,
                "effort": 2
            },
            "led_bulbs": {
                "name": "Switch to LED bulbs",
                "savings": 50,
                "cost": 20,
                "effort": 1
            },
            "public_transport": {
                "name": "Use public transport",
                "savings": 80,
                "cost": 5,
                "effort": 4
            }
        }
        
        # Initialize optimizer and RL agent
        self.optimizer = CarbonOptimizer(self.actions)
        self.rl_agent = RLAgent(len(self.actions))
        
        # Load previous state if exists
        self.load_state()
        
    def load_state(self):
        if os.path.exists('data/q_table.json'):
            with open('data/q_table.json', 'r') as f:
                self.rl_agent.q_table = json.load(f)
                
    def save_state(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        with open('data/q_table.json', 'w') as f:
            json.dump(self.rl_agent.q_table, f)
            
    def run(self):
        st.title("Carbon Footprint Optimizer")
        
        # User inputs
        st.header("Your Preferences")
        budget = st.slider("Monthly budget ($)", 0, 100, 50)
        max_effort = st.slider("Maximum effort level (1-10)", 1, 10, 5)
        
        if st.button("Get Recommendations"):
            # Get optimized recommendations
            recommendations = self.optimizer.optimize(budget, max_effort)
            
            # Display recommendations
            st.header("Recommended Actions")
            total_savings = 0
            total_cost = 0
            total_effort = 0
            
            for action, count in recommendations.items():
                if count > 0:
                    action_data = self.actions[action]
                    savings = action_data["savings"] * count
                    cost = action_data["cost"] * count
                    effort = action_data["effort"] * count
                    
                    total_savings += savings
                    total_cost += cost
                    total_effort += effort
                    
                    st.write(f"🔸 {action_data['name']} (x{count})")
                    st.write(f"   - CO₂ savings: {savings} kg")
                    st.write(f"   - Cost: ${cost}")
                    st.write(f"   - Effort: {effort}/10")
                    st.write("---")
            
            st.success(f"""
            Total Impact:
            - CO₂ savings: {total_savings} kg
            - Cost: ${total_cost}
            - Effort: {total_effort}/10
            """)
            
            # Feedback section
            st.header("Your Feedback")
            st.write("Which actions would you be willing to take?")
            
            for action in recommendations:
                if recommendations[action] > 0:
                    if st.checkbox(self.actions[action]["name"]):
                        # Update RL agent
                        self.rl_agent.update(action, 1)  # Positive reward
                    else:
                        self.rl_agent.update(action, -0.5)  # Negative reward
            
            # Save updated state
            self.save_state()

if __name__ == "__main__":
    app = CarbonOptimizerApp()
    app.run() 