import matplotlib.pyplot as plt
from preprocessing.input_preprocess import get_all_filenames, get_route


def levenshtein_distance(str1, str2):
    len_str1 = len(str1) + 1
    len_str2 = len(str2) + 1

    matrix = [[0 for _ in range(len_str2)] for _ in range(len_str1)]

    for i in range(len_str1):
        matrix[i][0] = i

    for j in range(len_str2):
        matrix[0][j] = j

    for i in range(1, len_str1):
        for j in range(1, len_str2):
            cost = 0 if str1[i - 1] == str2[j - 1] else 1
            matrix[i][j] = min(matrix[i - 1][j] + 1,  # deletion
                               matrix[i][j - 1] + 1,  # insertion
                               matrix[i - 1][j - 1] + cost)  # substitution

    return matrix[len_str1 - 1][len_str2 - 1]


def visualize_error_percentages(error_dict):
    filenames = list(error_dict.keys())
    percentages = list(error_dict.values())

    plt.bar(filenames, percentages, color='blue')
    plt.xlabel('Название файла')
    plt.ylabel('Процент ошибки')
    plt.title('Процент ошибки для каждого файла')
    plt.xticks(rotation=45, ha='right')
    plt.show()


if __name__ == "__main__":
    filenames = get_all_filenames("../public/result_routes")
    optimal_routes_dir = "optimal_routes"
    ga_routes_dir = "result_routes"

    error_rates = {}

    for filename in filenames:
        optimal_route = get_route(optimal_routes_dir, filename)
        ga_route = get_route(ga_routes_dir, filename)

        # Прямая и обратная длина на случай если маршрут развернут в другую сторону
        distance = levenshtein_distance(optimal_route, ga_route) / len(ga_route)
        reverse_distance = levenshtein_distance(optimal_route, ga_route[::-1]) / len(ga_route)

        error_rates[filename] = distance if distance < reverse_distance else reverse_distance

    sorted_error_dict = dict(sorted(error_rates.items(), key=lambda item: item[1]))
    visualize_error_percentages(sorted_error_dict)
