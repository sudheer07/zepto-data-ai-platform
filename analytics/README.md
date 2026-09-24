
# Titanic Analytics and Machine Learning

## 1. Overview

This module analyzes the Titanic passenger dataset and builds
machine learning models for two tasks:

- Classification: Predict whether a passenger survived.
- Regression: Predict a passenger's fare.

The dataset contains 891 passenger records and 15 original columns.

## 2. Project Files

| File | Description |
|---|---|
| `titanic.csv` | Original Titanic dataset |
| `01_eda.ipynb` | Exploratory data analysis and visualizations |
| `02_modeling.ipynb` | Classification models, tuning and imbalance handling |
| `03_fare_regression.ipynb` | Fare prediction and residual analysis |
| `models/titanic_classifier.joblib` | Saved classification pipeline |

## 3. Setup and Execution

Activate the project's Python virtual environment.

Install the required packages:

```bash
python -m pip install pandas numpy matplotlib seaborn \
    scikit-learn imbalanced-learn jupyter ipykernel joblib
```

Open the `analytics` folder in VS Code and run the notebooks
in the following order:

1. `01_eda.ipynb`
2. `02_modeling.ipynb`
3. `03_fare_regression.ipynb`

Select the project's Python virtual environment as the notebook kernel.

## 4. Exploratory Data Analysis

The EDA notebook examines missing values, outliers, distributions,
correlations and survival patterns.

Key findings:

- The overall survival rate was approximately 38.25%.
- Female passengers had a substantially higher survival rate
  than male passengers.
- First-class passengers had a higher survival rate than
  second- and third-class passengers.
- Approximately 19.87% of age values were missing.
- The deck column had approximately 77.22% missing values.
- Fare was strongly right-skewed and contained high-value outliers.

The EDA includes univariate, bivariate and multivariate plots,
a correlation heatmap and a standardization demonstration.

## 5. Survival Classification

The classification target is `survived`.

Seven input features were used:

- `pclass`
- `sex`
- `age`
- `sibsp`
- `parch`
- `fare`
- `embarked`

The dataset was split into 80% training data and 20% test data
using stratified sampling.

Preprocessing was performed within scikit-learn pipelines:

- Median imputation for missing numerical values.
- Most-frequent imputation for missing categorical values.
- Standard scaling for numerical features.
- One-hot encoding for categorical features.

This approach prevents preprocessing information from leaking
from the test set into training.

### Classification results

| Model | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Original logistic regression | 0.8045 | 0.7931 | 0.6667 | 0.7244 |
| Decision tree | 0.7933 | 0.8636 | 0.5507 | 0.6726 |
| Original random forest | 0.8156 | 0.8750 | 0.6087 | 0.7179 |
| Class-weighted logistic regression | 0.8045 | 0.7297 | 0.7826 | 0.7552 |
| Tuned random forest | 0.8156 | 0.8462 | 0.6377 | 0.7273 |
| SMOTE logistic regression | 0.8101 | 0.7397 | 0.7826 | 0.7606 |

### Hyperparameter tuning

Random forest hyperparameters were selected using five-fold
cross-validation on the training set, with F1 as the scoring metric.

Selected parameters:

- Number of trees: 200
- Maximum depth: 6
- Maximum features: None

Best cross-validation F1: 0.7514.

### Class imbalance

A majority-class baseline achieved 61.45% accuracy but zero
recall and F1.

Class weighting and SMOTE both increased logistic regression
recall from 66.67% to 78.26%, with a reduction in precision.

SMOTE was applied within an imbalanced-learn pipeline to
prevent resampling leakage during cross-validation.

The simplified SMOTE approach operates after one-hot encoding,
which can produce fractional encoded categorical values.

## 6. Model Persistence and Inference

The trained class-weighted logistic regression pipeline was
saved using `joblib` at:

`models/titanic_classifier.joblib`

The saved pipeline includes numerical and categorical
preprocessing and the trained classifier.

The model was reloaded successfully, and its predictions
were verified to be identical to the original model.

A demonstration passenger with the following characteristics
was used to test inference:

- Second class
- Female
- Age 28
- No accompanying siblings, spouses, parents or children
- Fare: £25
- Embarked at Southampton

The reloaded model predicted survival (class 1), with an
estimated survival probability of 86.62%.

This demonstrates that the saved pipeline can make predictions
for new records without retraining.

## 7. Fare Regression

Multiple linear regression was used to predict passenger fares.

Input features:

- `pclass`
- `sex`
- `age`
- `sibsp`
- `parch`
- `embarked`

Missing values were imputed within the training pipeline.

### Regression test results

| Metric | Value |
|---|---:|
| MAE | 20.8094 |
| RMSE | 30.4731 |
| R² | 0.3999 |
| Adjusted R² | 0.3679 |

The model explained approximately 40% of the variation
in passenger fares in the test set.

Residual analysis revealed a non-random error pattern,
varying error spread and substantial underprediction
of some expensive tickets.

## 8. Limitations

- The dataset is relatively small and historical.
- Nearly 20% of passenger ages are missing.
- Classification performance depends on the decision threshold.
- Standard SMOTE after one-hot encoding can generate
  fractional categorical values.
- The regression model does not fully capture the skewed
  fare distribution or nonlinear relationships.
- Model performance on this historical dataset does not
  establish performance on unrelated populations.

## 9. Reproducibility

A fixed random seed of 42 was used for data splitting
and stochastic model training.

Preprocessing was included within machine learning
pipelines to avoid data leakage.

Hyperparameter tuning and SMOTE cross-validation were
performed using training data only.