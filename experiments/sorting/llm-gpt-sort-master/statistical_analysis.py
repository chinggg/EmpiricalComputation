import pingouin as pg
import numpy as np
from scipy.stats import mannwhitneyu

with open('condition1.txt', 'r') as file:
    # Read all lines into a list
    name1 = file.readline()
    c1vals = file.read().splitlines()
with open('condition2.txt', 'r') as file:
    # Read all lines into a list
    name2 = file.readline()
    c2vals = file.read().splitlines()

print(name1, name2)
c1 = np.array(c1vals, dtype=int)
c2 = np.array(c2vals, dtype=int)
df = (pg.mwu(c1, c2, alternative='two-sided'))
print(df['p-val'] < 0.05)
print(df)
print(mannwhitneyu(c1, c2, method="auto"))
