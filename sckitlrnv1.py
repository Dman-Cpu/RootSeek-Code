import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.impute import SimpleImputer
import joblib
from datetime import datetime

def load_data(file_path):
    """Loads dataset from a CSV file."""
    try:
        data = pd.read_csv(file_path, skip_blank_lines=True)
        print(f"Loaded dataset with {len(data)} samples.")
        return data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        exit()
    except pd.errors.EmptyDataError:
        print("Error: The file is empty.")
        exit()

def handle_missing_data(data):
    """Handles missing data using SimpleImputer."""
    print("Checking for missing data...")
    imputer = SimpleImputer(strategy='mean')  # Use 'mean', 'median', or other strategies
    data[:] = imputer.fit_transform(data)
    print("Missing data handled with mean imputation.")
    return pd.DataFrame(data, columns=data.columns)

def split_data(data, target_col, test_size=0.1, random_state=42):
    """Splits the dataset into training and testing sets dynamically."""
    if target_col not in data.columns:
        print(f"Error: Target column '{target_col}' is missing.")
        exit()
    X = data.drop(columns=[target_col])  # Dynamically drop the target column
    y = data[target_col]
    return train_test_split(X, y, test_size=test_size, random_state=random_state)

def tune_hyperparameters(X_train, y_train):
    """Tunes hyperparameters of Random Forest using GridSearchCV."""
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'bootstrap': [True, False]
    }
    model = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=3, n_jobs=-1, verbose=2)
    grid_search.fit(X_train, y_train)
    print("Best Parameters:", grid_search.best_params_)
    return grid_search.best_estimator_

def evaluate_model(model, X_test, y_test):
    """Evaluates the model and prints metrics."""
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

def save_model(model, file_name):
    """Saves the trained model to a file."""
    joblib.dump(model, file_name)
    print(f"Model saved as {file_name}")

if __name__ == "__main__":
    # Load data
    file_path = "tree_root_data.csv"
    data = load_data(file_path)

    # Handle missing data
    data = handle_missing_data(data)

    # Define target column
    target_col = "label"

    # Split dataset
    X_train, X_test, y_train, y_test = split_data(data, target_col)

    # Hyperparameter tuning and training
    print("Tuning hyperparameters...")
    model = tune_hyperparameters(X_train, y_train)

    # Evaluate model
    print("Evaluating model...")
    evaluate_model(model, X_test, y_test)

    # Save the model with a timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_model(model, f"tree_root_model_{timestamp}.pkl")
