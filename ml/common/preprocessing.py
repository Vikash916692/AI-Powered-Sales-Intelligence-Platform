"""
Leakage-free, robust preprocessor for tabular features in Phase 3 ML.
Supports median/mean imputation, Robust/Standard scaling, and categorical encoding.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, RobustScaler, StandardScaler


class RobustPreprocessor(BaseEstimator, TransformerMixin):
    """
    Robust preprocessor handling numerical scaling, imputation, and categorical encoding without leakage.
    """

    def __init__(
        self,
        numeric_features: list[str] | None = None,
        categorical_features: list[str] | None = None,
        scaler_type: str = "robust",
        numeric_impute_strategy: str = "median",
    ):
        self.numeric_features = numeric_features or []
        self.categorical_features = categorical_features or []
        self.scaler_type = scaler_type
        self.numeric_impute_strategy = numeric_impute_strategy

        self.num_imputer = SimpleImputer(strategy=self.numeric_impute_strategy)
        self.scaler = RobustScaler() if scaler_type == "robust" else StandardScaler()
        self.cat_encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.is_fitted = False

    def fit(self, X: pd.DataFrame, y=None):
        if self.numeric_features:
            num_data = X[self.numeric_features]
            self.num_imputer.fit(num_data)
            num_imputed = self.num_imputer.transform(num_data)
            self.scaler.fit(num_imputed)

        if self.categorical_features:
            cat_data = X[self.categorical_features].fillna("missing").astype(str)
            self.cat_encoder.fit(cat_data)

        self.is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("RobustPreprocessor must be fitted before transform.")

        arrays = []
        if self.numeric_features:
            num_data = X[self.numeric_features]
            num_imputed = self.num_imputer.transform(num_data)
            num_scaled = self.scaler.transform(num_imputed)
            arrays.append(num_scaled)

        if self.categorical_features:
            cat_data = X[self.categorical_features].fillna("missing").astype(str)
            cat_encoded = self.cat_encoder.transform(cat_data)
            arrays.append(cat_encoded)

        if not arrays:
            return np.empty((len(X), 0))

        return np.hstack(arrays)

    def fit_transform(self, X: pd.DataFrame, y=None, **fit_params) -> np.ndarray:
        return self.fit(X, y).transform(X)
