import pandas as pd
import json
from sklearn.model_selection import train_test_split, learning_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE
import numpy as np
import joblib
from datetime import datetime
import logging
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_json_data(file_path):
    """Loads dataset from a JSON file and converts it to a Pandas DataFrame."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df.columns = df.columns.str.strip()  # Remove any unexpected spaces in column names
        logging.info(f"Loaded dataset from JSON with {len(df)} samples.")
        logging.info(f"Columns in loaded data: {df.columns.tolist()}")
        return df
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
        exit()
    except json.JSONDecodeError:
        logging.error("Error decoding JSON file.")
        exit()

def plot_learning_curve(model, X, y):
    """Plots learning curve for the model, adjusting for small datasets."""
    n_splits = min(5, len(y))  # Ensure cv does not exceed available samples
    if n_splits < 2:
        logging.warning("Not enough data points to generate a learning curve.")
        return
    
    train_sizes, train_scores, valid_scores = learning_curve(model, X, y, cv=n_splits, scoring='accuracy')
    train_mean = np.mean(train_scores, axis=1)
    valid_mean = np.mean(valid_scores, axis=1)
    
    plt.figure()
    plt.plot(train_sizes, train_mean, label="Training Score")
    plt.plot(train_sizes, valid_mean, label="Validation Score")
    plt.xlabel("Training Set Size")
    plt.ylabel("Score")
    plt.title("Learning Curve")
    plt.legend()
    plt.show()

def plot_feature_importance(model, feature_names):
    """Plots feature importance from trained model."""
    importances = model.feature_importances_
    sorted_indices = np.argsort(importances)[::-1]
    
    plt.figure()
    sns.barplot(y=feature_names[sorted_indices], x=importances[sorted_indices])
    plt.xlabel("Importance")
    plt.ylabel("Features")
    plt.title("Feature Importance")
    plt.show()

if __name__ == "__main__":
    # Load dataset from JSON
    data = load_json_data("tree_root_feedback.json")
    
    target_col = "label"
    if target_col not in data.columns:
        logging.error(f"Target column '{target_col}' not found in dataset. Available columns: {data.columns.tolist()}")
        exit()
    
    X = data.drop(columns=[target_col])
    y = data[target_col]
    
    if len(y) < 2:
        logging.error("Not enough samples for training. At least 2 samples are required.")
        exit()

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

    # Train model
    logging.info("Training model...")
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    # Evaluate model
    logging.info("Evaluating model...")
    predictions = model.predict(X_test)
    print(classification_report(y_test, predictions))

    # Plot learning curve
    plot_learning_curve(model, X, y)

    # Plot feature importance
    plot_feature_importance(model, X.columns)