import optuna
import matplotlib.pyplot as plt
from genetic_algorithm import read_csv_to_dict, genetic_algorithm, fitness, reorder_csv
from optuna.visualization import plot_optimization_history, plot_param_importances
import plotly.express as px

def objective(trial):
    population_size = trial.suggest_int('population_size', 5, 100)
    generations = trial.suggest_int('generations', 5, 2000)
    mutation_rate = trial.suggest_float('mutation_rate', 0.05, 0.5)


    input_csv = 'public/30_ex.csv'
    points = read_csv_to_dict(input_csv)

    best_route = genetic_algorithm(population_size=population_size,
                                   generations=generations,
                                   mutation_rate=mutation_rate,
                                   points=points)

    fitness_value = fitness(best_route, points)
    return 1 / fitness_value

if __name__ == "__main__":
    input_csv = 'public/30_ex.csv'
    output_csv = 'public/output_ordered_points.csv'
    points = read_csv_to_dict(input_csv)


    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=20)

    # Визуализация истории оптимизации
    fig_history = plot_optimization_history(study)
    fig_history.update_layout(
        title="Optimization History",
        xaxis_title="Trial",
        yaxis_title="Objective Value",
        legend_title="Hyperparameters",
        showlegend=True
    )

    # Визуализация важности параметров
    fig_importance = plot_param_importances(study)
    fig_importance.update_layout(
        title="Parameter Importances",
        xaxis_title="Parameter",
        yaxis_title="Importance",
    )

    # Получение лучших гиперпараметров
    best_params = study.best_params
    print("Лучшие гиперпараметры:", best_params)

    # Запуск алгоритма с лучшими параметрами для получения оптимального маршрута
    best_route = genetic_algorithm(population_size=best_params['population_size'],
                                   generations=best_params['generations'],
                                   mutation_rate=best_params['mutation_rate'],
                                   points=points)

    reorder_csv(input_csv, output_csv, best_route)
    print("\nОптимальный маршрут готов")

    best_params_str = ', '.join([f"{key}: {value}" for key, value in best_params.items()])
    fig_history.add_annotation(
        x=study.best_trial.number,
        y=study.best_value,
        text=f"Best Params: {best_params_str}",
        showarrow=True,
        arrowhead=4,
        ax=-30,
        ay=-40
    )
    fig_history.show()
    fig_importance.show()

