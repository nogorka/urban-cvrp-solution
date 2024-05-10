import time
import pandas as pd
from matplotlib import pyplot as plt

from v3_cvrp.genetic_algorithm_cvrp import genetic_algorithm
from preprocessing.input_preprocess import get_all_filenames, write_compare_csv_cvrp
from v2oop.preprocess import get_meta_data


def get_comparing_metrics_result(config):
    filenames = get_all_filenames(config['metrics_dir'])
    dataframes = []

    for file in filenames:
        df = pd.read_csv(config['metrics_dir'] + file)
        df['Source_File'] = file
        dataframes.append(df)

    combined_dataframe = pd.concat(dataframes, ignore_index=True)
    combined_dataframe.sort_values(by='Source_File')
    combined_dataframe.to_csv(config['result_csv'], index=False)
    print(f'Done writing {config["result_csv"]}')


def calc_median(config):
    filenames = get_all_filenames(config['compare_output_dir'])
    for file in filenames:

        input_csv = config['compare_output_dir'] + file
        output_csv = config['metrics_dir'] + file

        process_algorithm_data(input_csv, output_csv)
        print(f'Done: {output_csv}')


def process_algorithm_data(input_file, output_file):
    df = pd.read_csv(input_file)

    metrics = ['Distance (km)', 'Execution Time (s)']
    df[metrics] = df[metrics].apply(pd.to_numeric, errors='coerce')

    median_values = df[metrics].median().round(2)
    std_deviation = df[metrics].std().round(2)

    results = pd.DataFrame({
        'Metric': metrics,
        'Median': median_values.values,
        'Standard Deviation': std_deviation.values
    })
    results.to_csv(output_file)


def collect_batch_data(config):
    filenames = get_all_filenames(config['input_dir'])
    for file in filenames:
        # file = '10_ex_1.csv'

        compare_output_csv = config['compare_output_dir'] + file

        distance_matrix, city_points, _, _, G = get_meta_data(config, file)

        results = []
        for batch_try in range(config['batch_size']):
            best_route, time_taken = run_genetic_algorithm(city_points, distance_matrix,
                                                           capacity=config['vehicle_capacity'])
            best_route.calculate_distance_G(G)
            best_length = best_route.distance

            results.append([best_route, best_length, round(time_taken, 3), batch_try])

        write_compare_csv_cvrp(compare_output_csv, results)


def run_genetic_algorithm(city_points, distance_matrix, capacity):
    start = time.time()

    best_route = genetic_algorithm(population_size=10, generations=10, points=city_points, matrix=distance_matrix,
                                   capacity=capacity)
    end = time.time()
    return best_route, end - start


def draw_charts(config):
    df = pd.read_csv(config['result_csv'])

    fig, ax = plt.subplots(1, 2, figsize=(12, 6), sharex=True)

    def plot(sub_plot_id, metric_name, label):
        distance_df = df[df['Metric'] == metric_name].sort_values(by='Source_File')
        ax[sub_plot_id].bar(distance_df['Source_File'], distance_df['Median'], yerr=distance_df['Standard Deviation'],
                            capsize=5)
        ax[sub_plot_id].set_title(f'Медиана {label} со стандартным отклонением')
        ax[sub_plot_id].set_ylabel(label)
        ax[sub_plot_id].tick_params(axis='x', rotation=90)

    plot(0, 'Distance (km)', 'Расстояние (км)')
    plot(1, 'Execution Time (s)', 'Время выполнения (сек)')

    plt.tight_layout()
    plt.show()


def print_route_info(length, time_taken, length_diff, n_try):
    print(f"Execution time, seconds: {time_taken}")
    print(f"Length, km: {length / 1000:.1f}")
    print(f"Length difference, km: {length_diff}")
    print(f"TRY: {n_try}")


if __name__ == '__main__':
    config = {
        'city_name': "Saint Petersburg, Russia",
        'graph_filename': "../public/road_network_graph.pickle",
        'data_type': 'dict',
        'input_dir': "../public/test_routes/",
        'output_dir': "../public/result_routes/",
        'compare_output_dir': '../public/compare_result_routes/',
        'metrics_dir': '../public/metrics_result/',
        'result_csv': '../public/compare_result_main.csv',
        'batch_size': 5,
        'vehicle_capacity': 1000
    }

    collect_batch_data(config)
    calc_median(config)
    get_comparing_metrics_result(config)
    draw_charts(config)
