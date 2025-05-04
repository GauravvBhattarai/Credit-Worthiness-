#!/usr/bin/env python
# coding: utf-8

# In[5]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set styling
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("deep")

# Create dataframe with selected Canadian securities (2 per category)
data = {
    'Security': [
        # Government Securities (2)
        'Canada 2.25% Mar 2029',
        'Canada T-Bill Jun 2026',
        
        # Provincial Bonds (2)
        'Ontario 2.60% Jun 2027',
        'British Columbia 2.95% Dec 2028',
        
        # Bank Senior & Covered Bonds (2)
        'TD 3.25% Apr 2026',
        'RBC Covered 1.875% Jun 2026',
        
        # Corporate Securities (2)
        'BCE 3.50% Sep 2027',
        'Brookfield 3.80% Mar 2028',
        
        # Specialty Securities (2)
        'Green Ontario 2.65% Feb 2030',
        'Maple Bond - Toyota 2.35% Jul 2027'
    ],
    
    'Type': [
        'GoC Bond', 'T-Bill',
        'Provincial', 'Provincial',
        'Bank Senior', 'Covered Bond',
        'Corporate', 'Corporate',
        'Green Bond', 'Maple Bond'
    ],
    
    'Credit_Rating': [
        'AAA', 'AAA',
        'AA-', 'AAA',
        'AA-', 'AAA',
        'BBB+', 'A-',
        'AA-', 'A+'
    ],
    
    # Yield to maturity (%)
    'YTM': [
        3.12, 3.05,
        3.50, 3.35,
        3.70, 3.25,
        4.25, 4.30,
        3.60, 3.80
    ],
    
    # Spread over benchmark GoC (bps)
    'Spread': [
        0, 0,
        45, 25,
        60, 15,
        115, 120,
        55, 70
    ],
    
    # Duration (years)
    'Duration': [
        3.6, 1.2,
        2.3, 3.5,
        1.1, 1.2,
        2.5, 2.8,
        4.2, 2.3
    ],
    
    # Liquidity score (1-10 scale, higher is more liquid)
    'Liquidity': [
        10, 10,
        8, 7,
        8, 7,
        6, 5,
        6, 4
    ],
    
    # ESG score (0-100 scale)
    'ESG_Score': [
        80, 80,
        75, 90,
        72, 70,
        65, 78,
        95, 75
    ],
    
    # Default probability over investment horizon (%)
    'Default_Probability': [
        0.01, 0.01,
        0.15, 0.05,
        0.18, 0.08,
        1.20, 0.90,
        0.15, 0.35
    ]
}

df = pd.DataFrame(data)

# Calculate risk-adjusted return: (Spread/100) / Default_Probability
df['Risk_Adjusted_Return'] = (df['Spread']/100) / (df['Default_Probability'] + 0.05)  # Adding 0.05 to avoid division by near-zero

# Create attractiveness score (higher is better)
df['Attractiveness'] = (
    df['Risk_Adjusted_Return'] * 1.5 +    # Risk-adjusted return
    (df['ESG_Score'] / 100) * 1.2 +       # ESG component
    (df['Liquidity'] / 10) * 1.0 -        # Liquidity bonus
    (df['Duration'] / 10) * 0.2           # Small duration penalty
)

# Create recommendation categories
def categorize_attractiveness(score):
    if score >= 4.0:
        return "Highly Recommended"
    elif score >= 3.0:
        return "Recommended"
    elif score >= 2.0:
        return "Neutral"
    else:
        return "Underweight"

df['Recommendation'] = df['Attractiveness'].apply(categorize_attractiveness)

# Define colors for recommendation categories
categories = ["Underweight", "Neutral", "Recommended", "Highly Recommended"]
category_colors = {"Highly Recommended": "#1a9641", 
                  "Recommended": "#a6d96a", 
                  "Neutral": "#ffffbf", 
                  "Underweight": "#fdae61"}

# Define marker shapes for different security types
security_types = {
    'GoC Bond': 'o',       # circle
    'T-Bill': 's',         # square
    'Provincial': '^',     # triangle up
    'Bank Senior': 'D',    # diamond
    'Covered Bond': 'P',   # plus filled
    'Corporate': '*',      # star
    'Green Bond': 'h',     # hexagon
    'Maple Bond': 'd'      # thin diamond
}

# Create a simplified and compact figure
plt.figure(figsize=(10, 6))

# Plot each security type with its own marker
for sec_type, marker in security_types.items():
    subset = df[df['Type'] == sec_type]
    if not subset.empty:
        for category in categories:
            subsubset = subset[subset['Recommendation'] == category]
            if not subsubset.empty:
                plt.scatter(
                    subsubset['Duration'], 
                    subsubset['YTM'], 
                    s=subsubset['Liquidity']*30,
                    c=[category_colors[category]]*len(subsubset),
                    marker=marker,
                    alpha=0.8,
                    edgecolor='black',
                    linewidth=1
                )

# Add security labels with minimal information
for idx, row in df.iterrows():
    plt.annotate(
        row['Security'] + f" ({row['Credit_Rating']})", 
        (row['Duration']+0.1, row['YTM']+0.02),
        fontsize=8
    )

# Add yield curve line for reference
durations = np.array([0.5, 1, 2, 3, 5, 7])
# Approximate yield curve based on GoC benchmark rates
yields = np.array([2.95, 3.05, 3.10, 3.12, 3.18, 3.25])
plt.plot(durations, yields, 'k--', alpha=0.5, label='GoC Yield Curve')

# Customize plot
plt.title('Canada Opportunity Map (2025)', fontsize=12)
plt.xlabel('Duration (Years)', fontsize=10)
plt.ylabel('Yield to Maturity (%)', fontsize=10)
plt.grid(True, alpha=0.3)

# Create compact legend for security types
handles, labels = plt.gca().get_legend_handles_labels()
type_handles = []
type_labels = []

for sec_type, marker in security_types.items():
    if sec_type in df['Type'].values:  # Only include types that are present
        handle = plt.scatter([], [], marker=marker, color='gray', edgecolor='black', s=50)
        type_handles.append(handle)
        type_labels.append(sec_type)

# Add the legend outside the plot to save space
security_legend = plt.legend(
    handles=type_handles, 
    labels=type_labels, 
    title="Security Types", 
    loc='best',
    fontsize=8,
    frameon=True,
    bbox_to_anchor=(1.05, 1),
)

plt.xlim(0.5, 5)
plt.ylim(3.0, 4.5)
plt.tight_layout()

# Print investment recommendations rather than including in plot
print("\nKey Investment Recommendations:")
print("1. Green Ontario 2.65% Feb 2030: Best ESG profile with strong provincial credit")
print("2. British Columbia 2.95% Dec 2028: AAA provincial with attractive yield premium")
print("3. TD 3.25% Apr 2026: Strong risk-adjusted returns with excellent liquidity")
print("4. Brookfield 3.80% Mar 2028: Best corporate option with strong ESG credentials")
print("5. RBC Covered 1.875% Jun 2026: Safety with yield advantage over GoC")

# Sort by attractiveness score for analytical insight
print("\nTop Securities by Attractiveness Score:")
recommendations = df.sort_values('Attractiveness', ascending=False)[
    ['Security', 'Type', 'Credit_Rating', 'YTM', 'Spread', 'Attractiveness', 'Recommendation']
].reset_index(drop=True)
print(recommendations.to_string(index=False))

# Show plot
plt.show()

