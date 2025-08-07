import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Read the CSV file
df = pd.read_csv('lang_data/Sort(language).csv')  # Replace with your actual file path

# Step 2: Verify the data
print("First few rows of the data:")
print(df.head())

# Step 3: Convert 'Size' to numeric if it's not already
df['Size'] = pd.to_numeric(df['Size'], errors='coerce')

# Extract 'Size' column and language columns
size_col = 'Size'
language_cols = df.columns[1:]  # Extract all columns except 'Size'

# Convert the language columns to numeric, if not already
df[language_cols] = df[language_cols].apply(pd.to_numeric, errors='coerce')

# Check the data types to ensure they are correct
print("\nData types:")
print(df.dtypes)

# Step 4: Drop rows where 'Size' is NaN (if any)
df = df.dropna(subset=[size_col])

# Step 5: Group by 'Size' and calculate the mean correctness for each language
average_correctness = df.groupby(size_col).mean()

# Ensure the index of average_correctness reflects the correct Size values
print("\nIndex of average_correctness:")
print(average_correctness.index)

# Step 6: Plot the averages
plt.figure(figsize=(14, 10))  # Increased figure size for better visibility

# Plot each language's average correctness
for language in average_correctness.columns:
    sns.lineplot(x=average_correctness.index, y=average_correctness[language], marker='o', label=language)

# Customize the plot with bigger fonts
plt.title('Average Correctness by Size for Each Language', fontsize=22, fontweight='bold')
plt.xlabel('Size', fontsize=18)
plt.ylabel('Average Correctness', fontsize=18)
plt.legend(title='Languages', fontsize=16, title_fontsize=18)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.grid(True)

# Save the plot to a PDF file
plt.savefig('lang_graph.pdf', format='pdf')

plt.show()
