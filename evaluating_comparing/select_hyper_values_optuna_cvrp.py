import optuna
import pandas as pd

from preprocessing.input_preprocess import get_all_filenames
from v2oop.preprocess import get_meta_data
from v3_cvrp.fitness import fitness
from v3_cvrp.genetic_algorithm_cvrp import genetic_algorithm
from optuna.visualization import plot_optimization_history, plot_param_importances

config = {
    'city_name': "Saint Petersburg, Russia",
    'graph_filename': "../public/road_network_graph.pickle",
    'input_dir': "../public/test_routes/",
    'output_dir': "../public/result_routes/",
    'output_results': '../public/results_optuna.csv',
    'study': '../public/optuna_results_weights/',
    'file': '30_ex_10.csv',
    'vehicle_capacity': 1000,
}


def objective(trial):
    settings = {
        'population_size': 10,
        'generations': 10,
        'converge_threshold': 1e-08,
        'converge_patience': 5,
        'over_penalty_rate': trial.suggest_float('over_penalty_rate', 0.4, 1),
        'under_penalty_rate': trial.suggest_float('under_penalty_rate', 0, 0.6),
        'penalty_weight': trial.suggest_float('penalty_weight', 0, 5),
        'bonus_rate': trial.suggest_float('bonus_rate', 0.2, 3),
        'bonus_weight': trial.suggest_float('bonus_weight', 0, 0.6),
        'desired_threshold': 2.7e05,
        'mutation_rate': trial.suggest_float('mutation_rate', 0, 0.7),
        'relocation_rate': trial.suggest_float('relocation_rate', 0, 1)
    }

    best_route = genetic_algorithm(points=city_points, matrix=distance_matrix, capacity=config['vehicle_capacity'],
                                   tuning=settings)

    fitness_value = fitness(best_route, distance_matrix, config['vehicle_capacity'], settings)
    return 1 / fitness_value


def draw(study):
    # Визуализация истории оптимизации
    fig_history = plot_optimization_history(study)
    fig_history.update_layout(title="Optimization History", xaxis_title="Trial", yaxis_title="Objective Value",
                              legend_title="Hyperparameters", showlegend=True)

    # Визуализация важности параметров
    fig_importance = plot_param_importances(study)
    fig_importance.update_layout(title="Parameter Importances", xaxis_title="Parameter", yaxis_title="Importance")

    # best_params_str = ', '.join([f"{key}: {value}" for key, value in best_params.items()])
    # fig_history.add_annotation(x=study.best_trial.number, y=study.best_value, text=f"Best Params: {best_params_str}",
    #                            showarrow=True, arrowhead=4, ax=-30, ay=-40)
    fig_history.show()
    fig_importance.show()


# Сохранение study в JSON файл
def save_study_to_json(study, file_path):
    df = study.trials_dataframe(attrs=('number', 'value', 'params', 'state'))
    df.to_json(file_path, orient='split')


if __name__ == "__main__":
    results = []
    filenames = sorted(get_all_filenames(config['input_dir']))
    res_filenames = sorted(get_all_filenames(config['study']))
    res_filenames = [file.replace(".json", ".csv") for file in res_filenames]
    filenames = set(filenames).difference(set(res_filenames))
    print(filenames)

    for file in filenames:
        print(file)
        # file = config['file']

        distance_matrix, city_points, input_csv, output_csv, G = get_meta_data(config, file)

        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=20)

        print("Лучшие гиперпараметры:", study.best_params)
        data = study.best_params.copy()
        data['source_filename'] = file
        results.append(data)

        output_path = config['study'] + file.replace(".csv", ".json")
        save_study_to_json(study, output_path)

    df = pd.DataFrame(results)
    df.to_csv(config['output_results'])

    # draw(study)
