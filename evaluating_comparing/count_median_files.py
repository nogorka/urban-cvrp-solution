from preprocessing.input_preprocess import get_all_filenames
import pandas as pd


def process_algorithm_data(input_file, output_file):
    df = pd.read_csv(input_file)

    metrics = ['Distance (km)', 'Execution Time (s)', 'Length Difference (km)', 'Resemble Rate (%)']
    df[metrics] = df[metrics].apply(pd.to_numeric, errors='coerce')

    median_values = df.groupby('Algorithm')[metrics].median()
    median_values.to_csv(output_file)


if __name__ == '__main__':
    config = {
        'input_csv': '../public/compare_result_routes/',
        'output_csv': '../public/median_result_algorithms/',
    }

    filenames = get_all_filenames(config['input_csv'])
    for file in filenames:
        # file = '10_ex_1.csv'

        input_csv = config['input_csv'] + file
        output_csv = config['output_csv'] + file

        process_algorithm_data(input_csv, output_csv)
        print(f'Done: {output_csv}')
