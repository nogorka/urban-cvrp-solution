import json

import pandas as pd
from matplotlib import pyplot as plt

from preprocessing.input_preprocess import get_all_filenames

plt.rcParams.update({'font.size': 16})

best = []
def read_from_json(file_path):
    with open(file_path, 'r') as file:
        data_json = json.load(file)

    return pd.DataFrame(data_json['data'], columns=data_json['columns'])


def draw_history(filename):
    df = read_from_json(filename)

    optimization_history = df[['number', 'value']]

    plt.figure(figsize=(10, 5))
    plt.plot(df['number'], df['value'], marker='o')
    plt.title('Optimization History')
    plt.xlabel('Trial Number')
    plt.ylabel('Objective Value')
    plt.grid(True)
    plt.show()


def draw_importance(filename):
    df = read_from_json(filename)

    param_importance_data = df[[col for col in df.columns if 'params_' in col]]

    if 'value' in df.columns:
        # Proceed with operations on the 'value' column

        best_trials = df[df['value'] <= df['value'].quantile(0.1)]  # Consider top 10% trials as best

        mean_params = best_trials[[col for col in df.columns if 'params_' in col]].mean()

        plt.figure(figsize=(12, 6))
        mean_params.sort_values().plot(kind='barh')
        plt.title('Parameter Importance (Mean in Best Trials)')
        plt.xlabel('Average Value')
        plt.ylabel('Parameters')
        plt.grid(True)
        plt.show()

    else:
        print("Error: 'value' column not found in DataFrame")


def calculate_importance(df):
    best_trials = df[df['value'] <= df['value'].quantile(0.1)]

    best.append(best_trials)
    param_columns = [col for col in df.columns if 'params_' in col]
    return best_trials[param_columns].var()


def aggregate_importances(files):
    importance_list = []
    for file in files:
        df = read_from_json(file)
        importance = calculate_importance(df)
        importance_list.append(importance)

    importance_df = pd.DataFrame(importance_list)
    median_importance = importance_df.median()
    std_importance = importance_df.std()
    return median_importance, std_importance, importance_df


def plot_importance_with_std(median_importance, std_importance):
    # Sort values for better visualization
    # print(median_importance)
    indices = median_importance.sort_values(ascending=True).index
    sorted_medians = median_importance.loc[indices]
    sorted_stds = std_importance.loc[indices]

    # print(indices)
    clean_indices = [index.replace('params_', '') for index in indices]
    error_bars = (0 * sorted_stds, sorted_stds)  # (lower errors, upper errors)

    plt.figure(figsize=(13, 7))
    plt.barh(clean_indices, sorted_medians, xerr=error_bars, capsize=7)
    plt.xlabel('Медианное значение с стандартным отклонением')
    plt.ylabel('Параметры')
    plt.title('Важность параметров на тестовых выборках')
    plt.grid(True)
    plt.subplots_adjust(left=0.2)

    plt.show()


if __name__ == '__main__':
    dir = '../public/optuna_results_weights/'
    # file = '30_ex_10.json'
    # draw_history(dir + file)
    # draw_importance(dir + file)

    files = [dir + file for file in get_all_filenames(dir)]
    median, std, _ = aggregate_importances(files)
    # print(median, std)
    print(best)
    common_df = pd.concat(best, ignore_index=True)
    common_df.drop('state', axis=1, inplace=True)
    print(common_df)
    med = common_df.median()
    med.to_csv('median.csv')
    common_df.to_csv('best.csv')
    plot_importance_with_std(median, std)
