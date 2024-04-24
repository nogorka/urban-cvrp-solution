import pandas as pd
from preprocessing.input_preprocess import get_all_filenames

input_csv = '../public/median_result_algorithms/'
output_csv = '../public/compare_result_main.csv'

filenames = get_all_filenames(input_csv)
dataframes = []

for file in filenames:
    df = pd.read_csv(input_csv + file)
    df['Source_File'] = file
    dataframes.append(df)

combined_dataframe = pd.concat(dataframes, ignore_index=True)
combined_dataframe.to_csv(output_csv, index=False)
print(f'Done writing {output_csv}')
