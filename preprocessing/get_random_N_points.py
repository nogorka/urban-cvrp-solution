import pandas as pd


def generate_batch(input_csv, output_csv, n_samples):
    df = pd.read_csv(input_csv)  #[:200]
    random_points = df.sample(n=n_samples)
    random_points.to_csv(output_csv, index=False)
    print(f'Выбраны и сохранены {n_samples} точек в файл {output_csv}')


if __name__ == "__main__":
    n_samples = 50
    input_csv = '../public/locations_data.csv'
    output_csv = f'../public/{n_samples}_ex.csv'
    generate_batch(input_csv, output_csv, n_samples)
