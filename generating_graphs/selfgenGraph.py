import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Read the CSV file
df = pd.read_csv('selfgen_data/Sort(selfgen).csv', skipinitialspace=True)  # Replace with your actual file path

# Step 2: Inspect the data to ensure it's read correctly
print("First few rows of the data:")
print(df.head())

print("\nColumns:")
print(df.columns)

print("\nData types:")
print(df.dtypes)

# Ensure 'Size' and 'Correctness' are in numeric format
df['Size'] = pd.to_numeric(df['Size'], errors='coerce')
df['Correctness'] = pd.to_numeric(df['Correctness'], errors='coerce')

# Drop rows with NaN values in 'Size' or 'Correctness'
df = df.dropna(subset=['Size', 'Correctness'])

# Step 3: Group by 'Size' and calculate the mean correctness
average_correctness = df.groupby('Size').mean()

# Step 4: Plot the averages
plt.figure(figsize=(14, 10))  # Increased figure size for better visibility

# Print the Correctness values for specific sizes
sizes_to_check = [20,30,40, 50,90,100]

for size in sizes_to_check:
    if size in average_correctness.index:
        print(f"Correctness for Size {size}: {average_correctness.loc[size, 'Correctness']}")
    else:
        print(f"Size {size} not found in the data.")


# Plot the average correctness
sns.lineplot(x=average_correctness.index, y=average_correctness['Correctness'], marker='o', label='Correctness')

# Customize the plot with bigger fonts
plt.title('Average Correctness by Size', fontsize=22, fontweight='bold')
plt.xlabel('Size', fontsize=18)
plt.ylabel('Average Correctness', fontsize=18)
plt.legend(fontsize=16, title_fontsize=18)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.grid(True)

# Save the plot to a PDF file
pdf_path = 'selfgen_correctness_by_size.pdf'
plt.savefig(pdf_path, format='pdf')

# Show the plot (optional)
plt.show()
