'''
Failed attempt to use GGPLOT
'''


import pandas as pd
from plotnine import ggplot, aes, geom_line, facet_grid, labs
import glob

# Load data from multiple CSV files
file_paths = glob.glob('csv_data/*.csv')  # Adjust the path accordingly

# Function to clean and read each CSV file
def load_and_clean(file_path):
    df = pd.read_csv(file_path)
    df = df[['Average Correctness', 'Average Timing', 'Inverse Multiplication']]  # Select relevant columns
    df = df.apply(pd.to_numeric, errors='coerce')  # Convert to numeric, coerce errors to NaN
    df['source'] = file_path.split('/')[-1]  # Add source column for CSV file name
    df = df.dropna()  # Drop rows with NaN values
    df.reset_index(inplace=True)  # Create an index for x-axis
    return df

# Read and clean each CSV file into a DataFrame
dfs = [load_and_clean(file_path) for file_path in file_paths]

# Concatenate all DataFrames into a single DataFrame
df_combined = pd.concat(dfs, ignore_index=True)

# Melt the DataFrame to long-form for facet_grid
df_melted = pd.melt(df_combined, id_vars=['source', 'index'], var_name='measurement', value_name='value')

# Create the plot with facet_grid
plot = (ggplot(df_melted, aes(x='index', y='value', group='source', color='source')) 
        + geom_line()
        + facet_grid('source~measurement', scales='free_y')  # Free y scales for each facet
        + labs(x='Index', y='Value', color='CSV File')
       )

print(plot)
