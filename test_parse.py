import os
import pandas as pd
from app.services.file_handler import parse_file

car_df = pd.DataFrame({'car': [1,2,3]})
car_df.to_csv('uploads/car.csv', index=False)

df = parse_file('uploads/car.csv')
print(df.columns)
