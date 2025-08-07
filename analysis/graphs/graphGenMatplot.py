import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

# Read the CSV files into DataFrames
dfSort = pd.read_csv('csv_data/Sort 1-15-25.csv')
dfSortSearch = pd.read_csv('csv_data/Sorted Search.csv')
dfUnsortSearch = pd.read_csv('csv_data/Unsorted Search.csv')
dfssp = pd.read_csv('csv_data/SSP.csv')
dfSubstr = pd.read_csv('csv_data/Longest Palindromic Substring.csv')

# Function to add exponential line of best fit
def add_exp_fit(x, y, ax, label):
    valid = y > 0
    x_valid = x[valid]
    y_valid = y[valid]
    log_y = np.log(y_valid)
    coeffs = np.polyfit(x_valid, log_y, 1)
    fit_y = np.exp(coeffs[1]) * np.exp(coeffs[0] * x_valid)
    ax.plot(x_valid, fit_y, label=f'{label} Fit', linestyle='--')
    return coeffs

# Replace zeros with NaN after Size 15 in 'Inverse Multiplication'
def replace_zeros_after_size(x, y, threshold):
    y_filtered = y.copy()
    y_filtered[(x > threshold) & (y == 0)] = np.nan
    return y_filtered

def clean_numeric_column(column):
    return pd.to_numeric(column, errors='coerce')
dfSort['Inverse Multiplication'] = clean_numeric_column(dfSort['Inverse Multiplication'])

# Sorting
x00 = dfSort['Size']
y00 = dfSort['Average Timing']
y01 = dfSort['Average Correctness']
y02 = dfSort['Inverse Multiplication']

# Print Average Correctness for specific sizes
sizes_to_check = [10,20, 25, 30, 35, 40, 45, 50, 100]

# Create a DataFrame for easy lookup
df_sort_correctness = pd.DataFrame({'Size': x00, 'Average Correctness': y01})

# Iterate through the sizes to check
for size in sizes_to_check:
    match = df_sort_correctness[df_sort_correctness['Size'] == size]
    if not match.empty:
        print(f"Average Correctness for Size {size}: {match['Average Correctness'].values[0]}")
    else:
        print(f"Size {size} not found in the Sorting data.")


# Sorted Search
x10 = dfSortSearch['Size']
y10 = dfSortSearch['Average Timing']
y11 = dfSortSearch['Average Correctness']
y12 = replace_zeros_after_size(x10, dfSortSearch['Inverse Multiplication'], 15)

# Unsorted Search
x20 = dfUnsortSearch['Size']
y20 = dfUnsortSearch['Average Timing']
y21 = dfUnsortSearch['Average Correctness']
y22 = replace_zeros_after_size(x20, dfUnsortSearch['Inverse Multiplication'], 15)

# SSP
x30 = dfssp['Size']
y30 = dfssp['Average Timing']
y31 = dfssp['Average Correctness']
y32 = replace_zeros_after_size(x30, dfssp['Inverse Multiplication'], 15)

# Substring
dfSubstr['Inverse Multiplication'] = clean_numeric_column(dfSubstr['Inverse Multiplication'])

x40 = dfSubstr['Size']
y40 = dfSubstr['Average Timing']
y41 = dfSubstr['Average Correctness']
y42 = replace_zeros_after_size(x40, dfSubstr['Inverse Multiplication'], 15)

# Adjusted subplot matrix: (4 rows, 5 columns)
fig, axes = plt.subplots(4, 5, figsize=(18, 12))  # Increased height for the new row

# Timing
sns.lineplot(x=x00, y=y00, ax=axes[0, 0], marker='o')
sns.lineplot(x=x10, y=y10, ax=axes[0, 1], marker='o')
sns.lineplot(x=x20, y=y20, ax=axes[0, 2], marker='o')
sns.lineplot(x=x30, y=y30, ax=axes[0, 3], marker='o')
sns.lineplot(x=x40, y=y40, ax=axes[0, 4], marker='o')

# Correctness
sns.lineplot(x=x00, y=y01, ax=axes[1, 0], marker='o')
sns.lineplot(x=x10, y=y11, ax=axes[1, 1], marker='o')
sns.lineplot(x=x20, y=y21, ax=axes[1, 2], marker='o')
sns.lineplot(x=x30, y=y31, ax=axes[1, 3], marker='o')
sns.lineplot(x=x40, y=y41, ax=axes[1, 4], marker='o')

# Inverse Multiplication
sns.lineplot(x=x00, y=y02, ax=axes[2, 0], marker='o')
sns.lineplot(x=x10, y=y12, ax=axes[2, 1], marker='o')
sns.lineplot(x=x20, y=y22, ax=axes[2, 2], marker='o')
sns.lineplot(x=x30, y=y32, ax=axes[2, 3], marker='o')
sns.lineplot(x=x40, y=y42, ax=axes[2, 4], marker='o')

# Process data for Selfgen Sort
df_selfgen = pd.read_csv('selfgen_data/Sort(selfgen).csv', skipinitialspace=True)

# Ensure 'Size' and 'Correctness' are numeric and drop invalid rows
df_selfgen['Size'] = pd.to_numeric(df_selfgen['Size'], errors='coerce')
df_selfgen['Correctness'] = pd.to_numeric(df_selfgen['Correctness'], errors='coerce')
df_selfgen = df_selfgen.dropna(subset=['Size', 'Correctness'])

# Calculate mean correctness grouped by size
average_correctness_selfgen = df_selfgen.groupby('Size').mean()

# Add new graph for "Sort(selfgen)"
sns.lineplot(
    x=average_correctness_selfgen.index,
    y=average_correctness_selfgen['Correctness'],
    ax=axes[3, 0],
    marker='o'
)
axes[3, 0].set_ylabel("Selfgen Sort\nAverage Correctness")
axes[3, 0].set_xlabel("Size")
axes[3, 0].grid(True)

# Remove unused subplots in the new row
for i in range(1, 5):
    axes[3, i].axis('off')  # Turn off the axes for empty plots

# Adjust y-axes for better visualization
for i in range(5):
    axes[0, i].set_ylim(bottom=0)  # Timing plots (first row)
    axes[1, i].set_ylim(0, 1)  # Correctness plots (second row)
    axes[2, i].set_ylim(bottom=0)  # Inverse Multiplication plots (third row)


# Adjust y-axes for Timing plots (first row)
axes[0, 1].set_ylim(0, 1)  # Sorted Search Timing
axes[0, 2].set_ylim(0, 1)  # Unsorted Search Timing
axes[0, 4].set_ylim(0, 1)  # Substring Timing

# Set column titles
axes[0, 0].set_title('Sorting')
axes[0, 1].set_title('Sorted Search')
axes[0, 2].set_title('Unsorted Search')
axes[0, 3].set_title('SSP')
axes[0, 4].set_title('Substring')

# Update y-axis labels
for i in range(5):
    axes[0, i].set_ylabel("Time (seconds)")
    axes[1, i].set_ylabel("Average Correctness")
    axes[2, i].set_ylabel("Time to First Correct Solution")

# Display the plot
plt.tight_layout()
fig.savefig('comparison_plots_final.pdf', format='pdf')
plt.show()
