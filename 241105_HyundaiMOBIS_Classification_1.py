# -*- coding: utf-8 -*-
"""Untitled3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1H3Sm-mET7VEnkAtEisqlhvkcML0TPHMn
"""

import streamlit as st
import zipfile
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import numpy as np

# Set filter configurations
FILTER_COLUMN = 'L/O'
FILTER_THRESHOLD = 0.4

def load_and_filter_csv(file):
    # Load CSV and filter rows
    df = pd.read_csv(file)
    df_filtered = df[df[FILTER_COLUMN] >= FILTER_THRESHOLD]
    # Select only NIR and VIS columns for classification
    return df_filtered[['NIR', 'VIS']]

def process_zip_file(zip_file):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        # Extract files
        zip_ref.extractall('temp_extracted')
        folders = [os.path.join('temp_extracted', folder) for folder in os.listdir('temp_extracted') if os.path.isdir(os.path.join('temp_extracted', folder))]

        # Prepare data and labels
        data, labels = [], []
        for folder in folders:
            files = os.listdir(folder)
            label = os.path.basename(folder)
            for file in files:
                filepath = os.path.join(folder, file)
                df_filtered = load_and_filter_csv(filepath)
                data.append(df_filtered.values)
                labels += [label] * len(df_filtered)

        # Convert lists to numpy arrays
        data = np.vstack(data)
        labels = np.array(labels)

        # Split into train and test sets
        train_data, test_data, train_labels, test_labels = train_test_split(data, labels, test_size=0.5, stratify=labels)
        return train_data, test_data, train_labels, test_labels

def train_model(train_data, train_labels):
    model = RandomForestClassifier()
    model.fit(train_data, train_labels)
    return model

def evaluate_model(model, test_data, test_labels):
    predictions = model.predict(test_data)
    return classification_report(test_labels, predictions, output_dict=True)

st.title("Laser Welding Data Classification")

# Step 1: Upload ZIP for Training
uploaded_zip = st.file_uploader("Upload ZIP File", type="zip")

if uploaded_zip:
    train_data, test_data, train_labels, test_labels = process_zip_file(uploaded_zip)
    model = train_model(train_data, train_labels)
    report = evaluate_model(model, test_data, test_labels)
    st.write("Model Evaluation Report:")
    st.json(report)

# Step 2: Upload Single CSV for Prediction
uploaded_csv = st.file_uploader("Upload CSV for Prediction", type="csv")

if uploaded_csv:
    new_data = load_and_filter_csv(uploaded_csv)
    prediction = model.predict(new_data)
    st.write(f"Predicted Category: {prediction[0]}")