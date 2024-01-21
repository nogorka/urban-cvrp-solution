import pandas as pd

def generate_batch(input_csv, output_csv, n_samples):
    df = pd.read_csv(input_csv)
    random_points = df.sample(n=n_samples)
    random_points.to_csv(output_csv, index=False)
    print(f'Выбраны и сохранены {n_samples} точек в файл {output_csv}')

if __name__ == "__main__":
    input_csv = 'public/locations_data.csv'
    output_csv = 'public/example_10_points.csv'
    n_samples = 15
    generate_batch(input_csv, output_csv, n_samples)
