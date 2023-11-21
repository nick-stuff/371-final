import pandas as pd
import numpy as np
import openpyxl
import random

from datetime import datetime, timedelta


np.random.seed(42)

data = {
    'Date': [datetime(2023, 1, 1) + timedelta(days=i) for i in range(100)],
    'Stock': [f'Stock_{i}' for i in range(100)],
    'Price': np.random.uniform(50, 200, 100).round(2),
    'Volume': np.random.randint(1000, 5000, 100),
    'Revenue': np.random.uniform(10000, 50000, 100).round(2)
}


df = pd.DataFrame(data)


excel_file = 'financial_data.csv'
df.to_csv(excel_file, index=False)

print(f"Financial data has been generated and saved to {excel_file}.")