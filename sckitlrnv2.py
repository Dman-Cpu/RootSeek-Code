import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV, learning_curve, cross_val_score
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
from imblearn.over_sampling import SMOTE
import numpy as np
import joblib
from datetime import datetime
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import make_classification

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(file_path):
    """Loads dataset from a CSV file."""
    try:
        data = pd.read_csv(file_path, skip_blank_lines=True)
        logging.info(f"Loaded dataset with {len(data)} samples.")
        return data
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
        exit()
    except pd.errors.EmptyDataError:
        logging.error("The file is empty.")
        exit()

def validate_data(data, target_col):
    """Validates the dataset structure and types."""
    if target_col not in data.columns:
        logging.error(f"Target column '{target_col}' missing.")
        raise ValueError(f"Target column '{target_col}' is missing.")
    if not all(data.dtypes.apply(lambda x: x in [int, float])):
        logging.error("All columns must be numeric for this model.")
        raise TypeError("All columns must be numeric for this model.")
    logging.info("Data validation passed.")

def handle_missing_data(data):
    """Handles missing data using SimpleImputer."""
    logging.info("Checking for missing data...")
    imputer = SimpleImputer(strategy='mean')  # Use 'mean', 'median', or other strategies
    data[:] = imputer.fit_transform(data)
    logging.info("Missing data handled with mean imputation.")
    return pd.DataFrame(data, columns=data.columns)

def encode_categorical_columns(data):
    """Encodes categorical columns using OneHotEncoder."""
    from sklearn.preprocessing import OneHotEncoder
    categorical_cols = data.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        encoder = OneHotEncoder(drop='first', sparse=False)
        encoded = encoder.fit_transform(data[categorical_cols])
        encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(categorical_cols))
        data = data.drop(columns=categorical_cols).reset_index(drop=True)
        data = pd.concat([data, encoded_df], axis=1)
        logging.info(f"Encoded categorical columns: {categorical_cols}")
    return data

def balance_data(X, y):
    """Balances the dataset using SMOTE."""
    smote = SMOTE(random_state=42)
    X_balanced, y_balanced = smote.fit_resample(X, y)
    logging.info(f"Balanced dataset. Original size: {len(y)}, New size: {len(y_balanced)}")
    return X_balanced, y_balanced

def split_data(data, target_col, test_size=0.1, random_state=42):
    """Splits the dataset into training and testing sets dynamically."""
    if target_col not in data.columns:
        logging.error(f"Error: Target column '{target_col}' is missing.")
        exit()
    X = data.drop(columns=[target_col])  # Dynamically drop the target column
    y = data[target_col]
    return train_test_split(X, y, test_size=test_size, random_state=random_state)

def tune_hyperparameters_random(X_train, y_train):
    """Tunes hyperparameters of Random Forest using RandomizedSearchCV."""
    param_dist = {
        'n_estimators': [50, 100, 200, 300],
        'max_depth': [None, 10, 20, 30, 40],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'bootstrap': [True, False]
    }
    model = RandomForestClassifier(random_state=42)
    random_search = RandomizedSearchCV(
        estimator=model, 
        param_distributions=param_dist, 
        n_iter=20, 
        cv=3, 
        n_jobs=-1, 
        verbose=2, 
        random_state=42
    )
    random_search.fit(X_train, y_train)
    logging.info(f"Best Parameters from RandomizedSearchCV: {random_search.best_params_}")
    return random_search.best_estimator_

def plot_learning_curve(model, X, y):
    """Plots learning curve for the model."""
    train_sizes, train_scores, test_scores = learning_curve(model, X, y, cv=5, n_jobs=-1)
    train_scores_mean = train_scores.mean(axis=1)
    test_scores_mean = test_scores.mean(axis=1)
    plt.plot(train_sizes, train_scores_mean, label='Training Score')
    plt.plot(train_sizes, test_scores_mean, label='Validation Score')
    plt.xlabel('Training Set Size')
    plt.ylabel('Score')
    plt.legend()
    plt.title('Learning Curve')
    plt.show()

def save_model(model, file_name):
    """Saves the trained model to a file."""
    joblib.dump(model, file_name)
    logging.info(f"Model saved as {file_name}")

def generate_synthetic_data(samples=1000, features=20, classes=2):
    """Generates synthetic data for testing."""
    X, y = make_classification(n_samples=samples, n_features=features, n_classes=classes, random_state=42)
    data = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(features)])
    data["label"] = y
    logging.info(f"Synthetic data generated with {samples} samples.")
    return data

def evaluate_model(model, X_test, y_test):
    """Evaluates the model and logs detailed metrics."""
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    logging.info(f"Accuracy: {accuracy * 100:.2f}%")
    logging.info(f"Precision (weighted): {report['weighted avg']['precision']:.2f}")
    logging.info(f"Recall (weighted): {report['weighted avg']['recall']:.2f}")
    logging.info(f"F1-score (weighted): {report['weighted avg']['f1-score']:.2f}")

if __name__ == "__main__":
    # Generate synthetic data for testing
    data = generate_synthetic_data(samples=500, features=10, classes=2)
    target_col = "label"

    # Validate data
    try:
        validate_data(data, target_col)
    except (ValueError, TypeError) as e:
        logging.error(f"Data validation failed: {e}")
        exit()

    # Handle missing data
    data = handle_missing_data(data)

    # Encode categorical columns (if applicable)
    data = encode_categorical_columns(data)

    # Balance data
    X, y = balance_data(data.drop(columns=[target_col]), data[target_col])

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

    # Hyperparameter tuning and training
    logging.info("Tuning hyperparameters...")
    model = tune_hyperparameters_random(X_train, y_train)

    # Evaluate model
    logging.info("Evaluating model...")
    evaluate_model(model, X_test, y_test)

    # Plot learning curve
    logging.info("Plotting learning curve...")
    plot_learning_curve(model, X, y)

    # Save the model with a timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_model(model, f"tree_root_model_{timestamp}.pkl")
