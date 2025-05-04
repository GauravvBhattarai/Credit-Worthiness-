#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns

# Set styling
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("deep")

# Define starting values based on current Canada metrics
current_year = 2025
forecast_years = 5
years = list(range(current_year, current_year + forecast_years + 1))

# Current metrics (as of 2025)
initial_metrics = {
    'GDP_Growth': 0.012,  # 1.2% base growth rate (WB)
    'Debt_to_GDP': 1.07,  # 107.49% initial debt-to-GDP ratio (IMF)
    'Unemployment': 0.067,  # 6.7% unemployment rate (Statistique Canada)
    'Bond_Yield_10Y': 0.034,  # 3.4% 10-year bond yield (BoC)
    'Credit_Rating': 'AA+'  # Current S&P rating
}

# Define scenarios with different parameters
scenarios = {
    'Baseline': {
        'GDP_Growth_Path': [0.018, 0.019, 0.017, 0.016, 0.017],  # Steady growth
        'Debt_Annual_Change': [0.01, 0.005, 0.0, -0.005, -0.01],  # Slow debt reduction
        'Unemployment_Path': [0.060, 0.059, 0.058, 0.058, 0.057],  # Gradual improvement
        'Bond_Yield_Change': [0.001, 0.0, -0.001, -0.001, 0.0],  # Stable yields
        'Color': 'blue'
    },
    'Optimistic': {
        'GDP_Growth_Path': [0.022, 0.024, 0.026, 0.025, 0.024],  # Strong growth
        'Debt_Annual_Change': [-0.01, -0.015, -0.02, -0.025, -0.03],  # Significant debt reduction
        'Unemployment_Path': [0.058, 0.055, 0.052, 0.050, 0.048],  # Substantial improvement
        'Bond_Yield_Change': [-0.002, -0.003, -0.003, -0.002, -0.001],  # Declining yields
        'Color': 'green'
    },
    'Pessimistic': {
        'GDP_Growth_Path': [0.01, 0.008, 0.005, 0.006, 0.007],  # Weak growth
        'Debt_Annual_Change': [0.02, 0.025, 0.03, 0.025, 0.02],  # Rising debt
        'Unemployment_Path': [0.063, 0.067, 0.070, 0.072, 0.070],  # Worsening unemployment
        'Bond_Yield_Change': [0.004, 0.005, 0.006, 0.004, 0.003],  # Rising yields
        'Color': 'red'
    }
}

# Function to calculate metrics for each scenario
def project_metrics(scenario_params):
    gdp_growth = [initial_metrics['GDP_Growth']] + scenario_params['GDP_Growth_Path']
    
    # Calculate debt-to-GDP progression
    debt_to_gdp = [initial_metrics['Debt_to_GDP']]
    for i in range(forecast_years):
        # Debt changes based on annual change parameter and is affected by GDP growth
        new_debt_ratio = debt_to_gdp[-1] + scenario_params['Debt_Annual_Change'][i]
        # GDP growth effect on debt ratio (growing GDP reduces the ratio)
        new_debt_ratio = new_debt_ratio / (1 + gdp_growth[i+1])
        debt_to_gdp.append(new_debt_ratio)
    
    # Unemployment path
    unemployment = [initial_metrics['Unemployment']] + scenario_params['Unemployment_Path']
    
    # Bond yield progression
    bond_yield = [initial_metrics['Bond_Yield_10Y']]
    for i in range(forecast_years):
        bond_yield.append(bond_yield[-1] + scenario_params['Bond_Yield_Change'][i])
    
    # Credit rating projection (simplified model)
    credit_ratings = []
    rating_scale = {'AAA': 1, 'AA+': 2, 'AA': 3, 'AA-': 4, 'A+': 5}
    reverse_scale = {v: k for k, v in rating_scale.items()}
    
    current_rating_value = rating_scale[initial_metrics['Credit_Rating']]
    
    for i in range(forecast_years + 1):
        # Simple model: If debt-to-GDP < 85% and unemployment < 5.5%, improve rating
        # If debt-to-GDP > 110% or unemployment > 7%, downgrade rating
        if i > 0:  # Skip first year which is current
            if debt_to_gdp[i] < 0.85 and unemployment[i] < 0.055:
                current_rating_value = max(1, current_rating_value - 1)  # Improve rating (lower number is better)
            elif debt_to_gdp[i] > 1.10 or unemployment[i] > 0.07:
                current_rating_value = min(5, current_rating_value + 1)  # Downgrade rating
        
        credit_ratings.append(reverse_scale[current_rating_value])
    
    return {
        'GDP_Growth': gdp_growth,
        'Debt_to_GDP': debt_to_gdp,
        'Unemployment': unemployment,
        'Bond_Yield': bond_yield,
        'Credit_Rating': credit_ratings
    }

# Calculate projections for each scenario
projections = {name: project_metrics(params) for name, params in scenarios.items()}

# Create visualization of the scenarios
fig, axs = plt.subplots(2, 2, figsize=(15, 12))
plt.subplots_adjust(hspace=0.3)

# Format as percentage
def percentage_formatter(x, pos):
    return f'{x*100:.1f}%'

formatter = FuncFormatter(percentage_formatter)

# Plot GDP Growth
for scenario, metrics in projections.items():
    axs[0, 0].plot(years, metrics['GDP_Growth'], marker='o', label=scenario, color=scenarios[scenario]['Color'])
axs[0, 0].set_title('GDP Growth Projection', fontsize=14)
axs[0, 0].set_ylabel('Annual Growth Rate')
axs[0, 0].yaxis.set_major_formatter(formatter)
axs[0, 0].legend()
axs[0, 0].grid(True)

# Plot Debt-to-GDP
for scenario, metrics in projections.items():
    axs[0, 1].plot(years, metrics['Debt_to_GDP'], marker='o', label=scenario, color=scenarios[scenario]['Color'])
axs[0, 1].set_title('Debt-to-GDP Ratio Projection', fontsize=14)
axs[0, 1].set_ylabel('Ratio')
axs[0, 1].yaxis.set_major_formatter(formatter)
axs[0, 1].legend()
axs[0, 1].grid(True)

# Plot Unemployment
for scenario, metrics in projections.items():
    axs[1, 0].plot(years, metrics['Unemployment'], marker='o', label=scenario, color=scenarios[scenario]['Color'])
axs[1, 0].set_title('Unemployment Rate Projection', fontsize=14)
axs[1, 0].set_ylabel('Rate')
axs[1, 0].yaxis.set_major_formatter(formatter)
axs[1, 0].legend()
axs[1, 0].grid(True)

# Plot Bond Yields
for scenario, metrics in projections.items():
    axs[1, 1].plot(years, metrics['Bond_Yield'], marker='o', label=scenario, color=scenarios[scenario]['Color'])
axs[1, 1].set_title('10-Year Bond Yield Projection', fontsize=14)
axs[1, 1].set_ylabel('Yield')
axs[1, 1].yaxis.set_major_formatter(formatter)
axs[1, 1].legend()
axs[1, 1].grid(True)

plt.suptitle('Canada Economic Scenarios Analysis (2025-2030)', fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.95])

# Create a table to show the credit rating projections
rating_data = []
for scenario in projections:
    row = [scenario] + projections[scenario]['Credit_Rating']
    rating_data.append(row)

rating_df = pd.DataFrame(rating_data, columns=['Scenario'] + [f'{year}' for year in years])
print("Credit Rating Projections by Scenario:")
print(rating_df.to_string(index=False))

# Calculate investment return scenarios
def calculate_investment_returns(scenario):
    returns = []
    bond_yields = projections[scenario]['Bond_Yield']
    
    # Simple model: Annual return = yield + capital appreciation from yield changes
    for i in range(len(bond_yields)-1):
        # Base return is the yield
        base_return = bond_yields[i]
        # Price effect: bond prices rise when yields fall (roughly -7x duration for 10Y)
        duration_effect = -7 * (bond_yields[i+1] - bond_yields[i])
        total_return = base_return + duration_effect
        returns.append(total_return)
    
    return returns

# Calculate cumulative returns for each scenario
cumulative_returns = {}
for scenario in projections:
    annual_returns = calculate_investment_returns(scenario)
    cumulative = [1.0]  # Start with $1
    for ret in annual_returns:
        cumulative.append(cumulative[-1] * (1 + ret))
    cumulative_returns[scenario] = cumulative

# Plot the investment returns
plt.figure(figsize=(10, 6))
for scenario in cumulative_returns:
    plt.plot(years, cumulative_returns[scenario], marker='o', 
             label=f"{scenario} (End Value: ${cumulative_returns[scenario][-1]:.2f})",
             color=scenarios[scenario]['Color'])

plt.title('Projected Cumulative Returns on £1 Investment in Canadian 10Y Bonds', fontsize=14)
plt.ylabel('Value of £1 Investment')
plt.xlabel('Year')
plt.grid(True)
plt.legend()
plt.tight_layout()

# Create a summary of recommendations
print("\nInvestment Recommendations Based on Scenarios:")
print("Baseline Scenario: Maintain moderate allocation to Canadian government bonds")
print("Optimistic Scenario: Increase allocation to Canadian corporate bonds and equities")
print("Pessimistic Scenario: Reduce exposure to Canadian debt, focus on short-duration instruments")

# Display all plots
plt.show()

