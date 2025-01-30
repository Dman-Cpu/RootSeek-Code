import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load dataset
data = pd.read_csv("tree_root_data.csv", skip_blank_lines=True)
print(data.head())
print(f"Number of samples: {len(data)}")

# Check dataset
print(data.head())
print(data.shape)

# Handle missing data
if data.isnull().sum().sum() > 0:
    data = data.dropna()  # Option: data.fillna(0)

# Define features and target
if "label" not in data.columns:
    print("Error: 'label' column is missing. Add it or fix your dataset.")
    exit()

X = data[["distance", "temperature", "humidity"]]
y = data["label"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, train_size=0.9, random_state=42)

# Check dataset size
if len(X) == 0 or len(y) == 0:
    print("Error: Dataset is empty. Check your CSV file or data processing.")
    exit()

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Test model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy * 100:.2f}%")

# Save the model
joblib.dump(model, "tree_root_model.pkl")
print("Model saved as tree_root_model.pkl")

