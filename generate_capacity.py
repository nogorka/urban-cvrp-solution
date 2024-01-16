from sklearn.cluster import KMeans
import numpy as np
import pandas as pd


# Чтение данных из файла CSV
df = pd.read_csv('public/locations_data.csv')

X = np.array([
    [40.7128, -74.0060], # Parcel locker 1
    [34.0522, -118.2437], # Parcel locker 2
    [41.8781, -87.6298], # Parcel locker 3
    [37.7749, -122.4194], # Parcel locker 4
    [51.5074, -0.1278], # Parcel locker 5
])

# Use K-Means to cluster the parcel lockers into two groups
kmeans = KMeans(n_clusters=3).fit(X)

# Print the cluster assignments for each parcel locker
print(kmeans.labels_)
