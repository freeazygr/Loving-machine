
import pandas as pd
import joblib

MODEL_PATH = 'relationship_model.joblib'

loaded_model = joblib.load(MODEL_PATH)
feature_cols = ['Gender', 'Income', 'Children', 'Age', 'Attractiveness']


def pred(gender, income, children, age, attractiveness):

    new_data = pd.DataFrame([[gender, income, children, age, attractiveness]], columns=feature_cols)
    prediction = loaded_model.predict(new_data)
    return round(prediction[0])

