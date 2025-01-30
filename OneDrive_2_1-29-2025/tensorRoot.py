import pandas as pd
from keras import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split

# Load dataset
data = pd.read_csv("/Users/gabrielsalgado/Downloads/tree_root/tree_root_data.csv")
X = data[["distance", "temperature", "humidity"]]
y = data["label"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build model
model = Sequential([
    Dense(64, activation="relu", input_shape=(X_train.shape[1],)),
    Dense(32, activation="relu"),
    Dense(1, activation="sigmoid")
])

model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

# Train model
model.fit(X_train, y_train, epochs=20, batch_size=8, validation_data=(X_test, y_test))

# Test model
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Accuracy: {accuracy * 100:.2f}%")

# Save model
model.save("/Users/gabrielsalgado/Downloads/tree_root/tree_root_model.keras")
