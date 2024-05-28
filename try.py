import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import torch
import matplotlib.pyplot as plt

# Read data
data = pd.read_csv("final_data_prediction.csv")

# Map months to numbers and create Date column
month_map_reverse = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                     'July': 7, 'August': 8, 'September': 9, 'October': 10, 'Novermber': 11, 'December': 12}
data['Month'] = data['Month'].map(month_map_reverse)
data['Year'] = 2023
data['Date'] = pd.to_datetime(data['Month'].astype(str) + ' ' + data['Year'].astype(str), format='%m %Y')
data.set_index('Date', inplace=True)
data.drop(columns=['Unnamed: 0'], inplace=True)

# Select relevant columns
final_data = data[["Inventory", "Value", "code_p"]]

# Normalize data
scaler = MinMaxScaler()
final_data['Value'] = scaler.fit_transform(final_data[['Value']])
final_data['Inventory'] = scaler.fit_transform(final_data[['Inventory']])

# Function to create sequences
def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data[i:i + seq_length]
        y = data[i + 1:i + seq_length + 1]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

# Parameters
sequence_length = 3

# Initialize lists for train and test data
X_train, y_train, X_test, y_test = [], [], [], []

# Split data and create sequences for each product
for code_p, group in final_data.groupby('code_p'):
    group_values = group['Value'].values
    
    # Determine split index
    train_size = int(len(group_values) * 0.8)
    
    # Training data
    group_train = group_values[:train_size]
    X_tr, y_tr = create_sequences(group_train, sequence_length)
    X_train.append(X_tr)
    y_train.append(y_tr)
    
    # Testing data
    group_test = group_values[train_size - sequence_length:]  # include overlap
    X_te, y_te = create_sequences(group_test, sequence_length)
    X_test.append(X_te)
    y_test.append(y_te)

# Concatenate all data
X_train = np.concatenate(X_train)
y_train = np.concatenate(y_train)
X_test = np.concatenate(X_test)
y_test = np.concatenate(y_test)

# Convert to tensors
X_train = torch.FloatTensor(X_train).unsqueeze(2)  # Add a dimension for features
y_train = torch.FloatTensor(y_train)
X_test = torch.FloatTensor(X_test).unsqueeze(2)  # Add a dimension for features
y_test = torch.FloatTensor(y_test)

# Print shapes
print("Train shape:", X_train.shape, y_train.shape)
print("Test shape:", X_test.shape, y_test.shape)

# Function to print sample sequences
def print_samples(X, y, num_samples=5):
    for i in range(num_samples):
        print(f"Sample {i+1}:")
        print("X:", X[i].numpy().flatten())
        print("y:", y[i].numpy().flatten())
        print()

print("Training Samples:")
print_samples(X_train, y_train)

print("Testing Samples:")
print_samples(X_test, y_test)

# Function to check alignment
def check_alignment(X, y):
    for i in range(len(X)):
        if not np.array_equal(X[i, 1:, 0], y[i, :-1]):
            print(f"Misalignment at sample {i}: X_last = {X[i, -1, 0]}, y = {y[i]}")
            return
    print("All sequences are correctly aligned.")

print("Checking Training Data Alignment:")
check_alignment(X_train, y_train)

print("Checking Testing Data Alignment:")
check_alignment(X_test, y_test)

# Function to plot sequences
def plot_sequences(X, y, num_samples=5):
    for i in range(num_samples):
        plt.figure(figsize=(10, 2))
        plt.plot(range(len(X[i])), X[i].numpy().flatten(), label='X')
        plt.plot(range(1, len(y[i])+1), y[i].numpy(), label='y', linestyle='--')
        plt.title(f"Sample {i+1}")
        plt.xlabel("Time Step")
        plt.ylabel("Value")
        plt.legend()
        plt.show()

print("Visualizing Training Data:")
plot_sequences(X_train, y_train)

print("Visualizing Testing Data:")
plot_sequences(X_test, y_test)
