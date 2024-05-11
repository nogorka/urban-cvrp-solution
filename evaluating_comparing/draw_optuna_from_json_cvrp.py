import json

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def draw_optuna_from_json_cvrp(filename):
    with open(filename, 'r') as file:
        data_json = json.load(file)
    df = pd.DataFrame(data_json['data'], columns=data_json['columns'])

    sns.set(style="whitegrid")

    plt.figure(figsize=(10, 6))
    scatter = sns.scatterplot(x='params_population_size', y='value', hue='params_generations', palette='viridis',
                              data=df,
                              size='params_generations', sizes=(50, 200), legend="full")

    # Add titles and labels
    plt.title('Optimization Trial Outcomes')
    plt.xlabel('Population Size')
    plt.ylabel('Objective Value')
    plt.legend(title='Generations')

    plt.show()


if __name__ == "__main__":
    _dir = '../public/optuna_results/'
    file = '30_ex_10.json'
    draw_optuna_from_json_cvrp(_dir + file)
