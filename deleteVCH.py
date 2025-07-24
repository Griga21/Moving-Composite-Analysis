import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
dt = pd.read_csv("D:\Diplom\DiplomPy\stepanalyzer\Algorithms\Result.csv")
plt.figure(figsize=(8, 6))
sns.catplot(data=dt, x='Day', y='Total Count Step', hue='Group', kind='box')
plt.show()
plt.figure(figsize=(8, 6))
sns.catplot(data=dt, x='Day', y='Average Max Angel', hue='Group', kind='box')
plt.show()

plt.figure(figsize=(8, 6))
sns.catplot(data=dt, x='Day', y='Average Min Angel', hue='Group', kind='box')
plt.show()

plt.figure(figsize=(8, 6))
sns.catplot(data=dt, x='Day', y='Average Step Duration (s)', hue='Group', kind='box')
plt.show()
plt.figure(figsize=(8, 6))
sns.catplot(data=dt, x='Day', y='Average height Step', hue='Group', kind='box')
plt.show()
