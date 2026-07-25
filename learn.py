
import logging
import joblib
import pandas as pd
from sklearn.linear_model import PoissonRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

DATA_PATH = 'Online_Dating_Behavior_Dataset.csv'
MODEL_PATH = 'relationship_model.joblib'
TARGET_COL = 'Matches'


def main():
    logging.info("Загрузка данных...")
    df = pd.read_csv(DATA_PATH)

    df_new = df.copy()
    df_new = df_new.dropna(subset=[TARGET_COL])

    # PoissonRegressor требует, чтобы целевая переменная была >= 0
    df_new = df_new[df_new[TARGET_COL] >= 0]

    if 'PurchasedVIP' in df_new.columns:
        df_new = df_new.drop(columns=['PurchasedVIP'])

    y = df_new[TARGET_COL]
    X = df_new

    # 1. Явно разделяем признаки по их математическому смыслу
    numeric_features = ['Income', 'Children', 'Age', 'Attractiveness']
    categorical_features = ['Gender'] # Бинарный признак (обычно 0 или 1)

    # 2. Правила для числовых колонок (заполняем пропуски медианой + масштабируем)
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    # 3. Правила для бинарного пола (только заполняем пропуски самым частым значением)
    # Масштабировать нули и единицы через StandardScaler математически бессмысленно
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent'))
    ])

    # 4. Диспетчер колонок: направляет признаки в нужные трансформеры
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='drop' # Игнорируем всё остальное
    )

    # 5. Собираем финальную трубу с Пуассоновской регрессией
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', PoissonRegressor(max_iter=1000))
    ])

    # Разбиваем данные
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    logging.info("Обучение модели (PoissonRegressor)...")
    pipeline.fit(X_train, y_train)

    logging.info("Оценка модели...")
    y_pred = pipeline.predict(X_test)

    # Для бизнеса MAE (Mean Absolute Error) понятнее, чем MSE.
    # Она показывает, на сколько штук матчей в среднем ошибается модель.
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    logging.info(f'MAE на тесте: {mae:.2f} матчей')
    logging.info(f'R2 на тесте: {r2:.4f}')

    joblib.dump(pipeline, MODEL_PATH)
    logging.info(f'Пайплайн сохранен в {MODEL_PATH}')

if __name__ == '__main__':
    main()
