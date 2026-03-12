
# Customer Dataset Descriptive Analysis Report

## Data Cleaning
- Missing values in numerical columns were imputed with the median; categorical columns with the mode.
- Outliers were capped: Age (18-100), Income (0-200,000), PurchaseAmount (0-5,000).
- Categorical values were standardized.

## Key Metrics (Train Set)
- **Age**: Mean = 45.12, Median = 43.00, Std = 17.47
- **Income**: Mean = 49998.79, Median = 48083.98, Std = 22651.99
- **PurchaseAmount**: Mean = 253.24, Median = 208.79, Std = 486.37

## Categorical Distributions
- **Gender**: {'Other': 47, 'Male': 37, 'Female': 16}
- **Country**: {'Other': 38, 'Usa': 17, 'Canada': 16, 'India': 16, 'Uk': 13}

## Visualizations
- Histograms: `train_hist_Age.png`, `train_hist_Income.png`, `train_hist_PurchaseAmount.png`
- Boxplots: `train_box_Age.png`, `train_box_Income.png`, `train_box_PurchaseAmount.png`
- Bar charts: `train_bar_Gender.png`, `train_bar_Country.png`

