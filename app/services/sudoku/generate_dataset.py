import json
import os

from app.services.sudoku.generator_pole import GeneratorPole
from app.services.sudoku.generator_sudoku import GeneratorSudoku
from app.services.sudoku.solver_sudoku import SolverSudoku
from app.services.sudoku.pole_sudoku import PoleSudoku


PATH_DATASET_PREPROCESS = os.path.join(os.path.dirname(__file__), 'dataset_preprocess.json')
PATH_DATASETD = os.path.join(os.path.dirname(__file__), 'dataset.json')


def generate_dataset() -> None:
    if os.path.exists(PATH_DATASET_PREPROCESS):
        with open(PATH_DATASET_PREPROCESS, 'r', encoding='utf-8') as dt:
            dataset: dict[int, list[list[int]]] = json.load(dt)
    else:
        dataset: dict[int, list[list[int]]] = {}
    
    for quality in range(20, 18, -1):
        for _ in range(10):
            pole = GeneratorPole().run()
            sudoku = GeneratorSudoku(pole, quality=quality).generate_sudoke()

            if quality not in dataset:
                dataset[quality] = [str(sudoku.pole)]
            else:
                dataset[quality].append(str(sudoku.pole))

            print(sudoku.pole)
        
        with open(PATH_DATASET_PREPROCESS, 'w', encoding='utf-8') as dt:
            json.dump(dataset, dt)
        print(f'Судоку сложностью {quality} записаны')


def sudoku_list_to_str81(sudoku: PoleSudoku) -> str:
    return ''.join([str(digit) for row in sudoku for digit in row])


def processing_dataset_for_db() -> None:
    if os.path.exists(PATH_DATASET_PREPROCESS):
        with open(PATH_DATASET_PREPROCESS, 'r', encoding='utf-8') as dt:
            dataset: dict[int, list[list[list[int]]]] = json.load(dt)
    else:
        dataset: dict[int, list[list[list[int]]]] = {}
    
    new_dataset: dict[int, list[list[list[int]]]] = {}

    for quality, list_sudoku in dataset.items():
        new_dataset[quality] = []
        for sudoku in list_sudoku:
            solution = SolverSudoku(sudoku).solving_sudoku()

            solution_str81 = sudoku_list_to_str81(solution)
            sudoku_str81 = sudoku_list_to_str81(sudoku)

            new_dataset[quality].append(
                {
                    'sudoku': sudoku_str81,
                    'solution': solution_str81
                }
            )

    with open(PATH_DATASETD, 'w') as dt:
        json.dump(new_dataset, dt)
    print('dataset created')

if __name__ == '__main__':
    # generate_dataset()
    processing_dataset_for_db()