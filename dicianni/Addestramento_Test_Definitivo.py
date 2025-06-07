# %% [markdown]
# # Importazione dataset, pulizia dei dati, grafici

# %%
import pandas as pd
import numpy as np
import joblib

# %%
df = pd.read_csv(r'bird_migration_data.csv')

# %%
print(f"Il dataset ha {df.shape[0]} righe e {df.shape[1]} colonne.")

# %%
df.head()

# %%
print("Colonne del dataset:")
for col in df.columns:
    print(f"- {col}")

# %%
# Informazioni sul dataset (tipi di dati, valori non nulli...)
df.info()

# %%
print("\nPercentuale di valori NaN per colonna:")
nan_percentage = (df.isna().sum() / len(df) * 100).round(2)
print(nan_percentage[nan_percentage > 0])

# %%
# Rimozione della colonna Interrupted_Reason
df = df.drop(columns=['Interrupted_Reason'])
print(f"Colonna 'Interrupted_Reason' rimossa. Nuove dimensioni del dataset: {df.shape}")

# %%
# Visualizza i valori unici per ciascuna colonna categoriale
categorical_cols = df.select_dtypes(include=['object']).columns
categorical_cols = [col for col in categorical_cols if col != 'Bird_ID']

for col in categorical_cols:
    unique_values = df[col].unique()
    print(f"\n{col} ({len(unique_values)} valori unici):")
    for val in unique_values:
        count = df[col].value_counts()[val]
        percentage = (count / len(df)) * 100
        print(f"- {val}: {count} occorrenze ({percentage:.2f}%)")

# %%
df.describe()

# %% [markdown]
# # Logistic Regression

# %%
# Colonne da eliminare
columns_to_drop = [
    'Bird_ID',                   # Identificatore univoco
    'Recovery_Location_Known',   # Informazione post-migrazione
    'Recovery_Time_days',        # Informazione post-migrazione
    'Observation_Counts',        # Potenziale data leakage
    'Observation_Quality',       # Potenziale data leakage
    'Tagged_By',                 # Informazione amministrativa
    'Average_Speed_kmph',        # Derivabile (da distanza e durata)
    'Migration_End_Month',       # Potenziale data leakage
    'Tag_Type',                  # Metadata potenzialmente non rilevante
    'Tag_Weight_g',              # Metadata potenzialmente non rilevante
    'Signal_Strength_dB',        # Metadata, può introdurre rumore
    'Nesting_Success',           # Potenziale data leakage
    'Migration_Interrupted',     # Potenziale data leakage
    'Tracking_Quality',          # Metadata, può introdurre rumore
    'Tag_Battery_Level_%',       # Metadata, può introdurre rumore
    'Habitat',                   # Feature non rilevante
    'Migration_Reason',          # Feature non rilevante
    'End_Latitude',              # Informazione post-migrazione
    'End_Longitude'              # Informazione post-migrazione
]

# Separazione tra features e target
X = df.drop(columns=columns_to_drop + ['Migration_Success'])
y = df['Migration_Success']


# %%
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, RandomizedSearchCV, GridSearchCV, KFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, RobustScaler, OneHotEncoder, OrdinalEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from scipy.stats import randint
from tqdm.notebook import tqdm

# %%
# Riceve in input un dataframe e dà in output un dataframe
sklearn.set_config(transform_output='pandas')

# %%
# Identifica le colonne categoriche e numeriche
categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()

# %%
# Separazione dello scaler per gestire gli outlier
robust_cols = [
    'Flight_Distance_km',
    'Start_Latitude',
    'Start_Longitude',
    'Max_Altitude_m',
    'Min_Altitude_m',
    'Temperature_C',
    'Wind_Speed_kmph',
    'Humidity_%',
    'Pressure_hPa',
    'Visibility_km',
    'Rest_Stops',
    'Predator_Sightings',
    'Flock_Size'
    ]
standard_cols = [col for col in numerical_cols if col not in robust_cols]

# %%
# Costruzione del preprocessore
preprocessor = ColumnTransformer(
    transformers=[
        ('robust', RobustScaler(), robust_cols),
        ('standard', StandardScaler(), standard_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
    ],
    verbose_feature_names_out=False
)

# %%
# Pipeline con regressione logistica (Ridge = L2)
log_reg_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(
        penalty='l2',        # Ridge
        C=1.0,               # Inverso della regolarizzazione (basso = più regolarizzazione)
        solver='lbfgs',      # Ottimo per L2 + multiclasse
        max_iter=1000,
        random_state=42
    ))
])

# %%
# Definisce la k-fold cross-validation
k_fold = KFold(n_splits=5, shuffle=True, random_state=42)

# %%
# Esegue la cross-validation
cv_scores = cross_val_score(log_reg_pipeline, X, y, cv=k_fold, scoring='accuracy')

# %%
# Stampa i risultati della cross-validation
print(f"Cross-Validation Scores: {cv_scores}")
print(f"Mean CV Score: {cv_scores.mean():.4f}")
print(f"Standard Deviation: {cv_scores.std():.4f}")

# %%
# Divide i dati in train e test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# %%
# Addestra il modello sul set di training completo
log_reg_pipeline.fit(X_train, y_train)

# %%
# Fai previsioni sul test set
y_pred = log_reg_pipeline.predict(X_test)

# %%
# Valuta il modello
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.4f}")

# %%
# Estrae i coefficienti
coefficients = log_reg_pipeline.named_steps['classifier'].coef_[0]  # [0] perché è binaria
feature_names = log_reg_pipeline.named_steps['preprocessor'].get_feature_names_out()

# Crea DataFrame con valori assoluti dei coefficienti
importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': np.abs(coefficients)  # Valore assoluto per importanza
}).sort_values('importance', ascending=False)

print("Top 10 Features - Logistic Regression:")
print(importance_df.head(10))


joblib.dump(log_reg_pipeline, 'log_reg.joblib')