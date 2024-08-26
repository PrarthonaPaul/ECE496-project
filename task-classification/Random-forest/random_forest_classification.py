import pandas as pd
import re
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import numpy as np

def preprocess_text(text):
    text = re.sub(r'\W', ' ', text)  # Remove all special characters
    text = re.sub(r'\s+', ' ', text)  # Remove all multiple spaces
    text = text.lower()  # Convert to lowercase
    return text

# Load dataset
splits = {'train': 'data/train-00000-of-00001.parquet', 'test': 'data/test-00000-of-00001.parquet', 'val_iron': 'data/val_iron-00000-of-00001.parquet', 'val_neg': 'data/val_neg-00000-of-00001.parquet'}
df_train = pd.read_parquet("hf://datasets/jakeazcona/short-text-labeled-emotion-classification/" + splits["train"])
df_test = pd.read_parquet("hf://datasets/jakeazcona/short-text-labeled-emotion-classification/" + splits["test"])


# Preprocess the data
df_train['sample'] = df_train['sample'].apply(preprocess_text)
df_test['sample'] = df_test['sample'].apply(preprocess_text)

# Encode the labels
label_encoder = LabelEncoder()
df_train['label'] = label_encoder.fit_transform(df_train['label'])
df_test['label'] = label_encoder.transform(df_test['label'])


# Vectorize the text data
vectorizer = TfidfVectorizer(max_features=5000)
X_train = vectorizer.fit_transform(df_train['sample']).toarray()
y_train = df_train['label']

X_test = vectorizer.transform(df_test['sample']).toarray()
y_test = df_test['label']

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate on the training data (just for the sake of demonstration)
y_train_pred = model.predict(X_train)
print("Training Set Evaluation:")
print(classification_report(y_train, y_train_pred))

# Evaluate on test data 
y_test_pred = model.predict(X_test)
print("Test Set Evaluation:")
print(classification_report(y_test, y_test_pred))

# Calculate correct and incorrect classifications
labels = np.unique(y_test)
correct_classifications = {label: 0 for label in labels}
incorrect_classifications = {label: 0 for label in labels}

for true, pred in zip(y_test, y_test_pred):
    if true == pred:
        correct_classifications[true] += 1
    else:
        incorrect_classifications[true] += 1

# Create the table
table_data = {
    'Label': labels,
    'Correct Classifications': [correct_classifications[label] for label in labels],
    'Incorrect Classifications': [incorrect_classifications[label] for label in labels],
    'Total Data Points (Train)': [len(y_train) for _ in labels],
    'Total Data Points (Test)': [len(y_test) for _ in labels]
}

result_df = pd.DataFrame(table_data)
print(result_df)


# Save classification reports to text files
with open('training_classification_report.txt', 'w') as file:
    file.write(classification_report(y_train, y_train_pred))

with open('test_classification_report.txt', 'w') as file:
    file.write(classification_report(y_test, y_test_pred))

print("Classification reports saved to training_classification_report.txt and test_classification_report.txt")
