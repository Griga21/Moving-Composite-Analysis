import os

from stepanalyzer.Algorithms.KinematicsFun import (
    calculate_average_height,
    calculate_number_time_steps,
    definition_step_cycle,
)
from stepanalyzer.Algorithms.ReadDataFile import read_params
from stepanalyzer.Algorithms.step_cycle_utils import parse_result_identity

N_cond = ['Intact', 'SCI_3_dpi', 'SCI_TMT_3_dpi', 'SCI_7_dpi', 'SCI_TMT_7_dpi', 'SCI_14_dpi', 'SCI_TMT_14_dpi',
          'SCI_21_dpi',
          'SCI_TMT_21_dpi', 'SCI_28_dpi', 'SCI_TMT_28_dpi']
colums = ['toe_x', 'toe_y']
data_csv_columns = ['Group', 'Day', 'Number Rat',
                    'Step Params', 'Angle Params',
                    'Average Max Angel', 'Average Min Angel',
                    'Average Step Duration (s)', 'Total Count Step', 'Average height Step']
result_csv_data = []
if __name__ == "__main__":
    result_step_cycle = {}  # Dict{"file_name":Array with step position}
    result_average_max = {}
    result_average_min = {}
    result_average_time_step = {}
    result_all_count_step = {}
    result_average_height = {}
    data_path = "D:/Diplom/DiplomPy"
    trajectory_path = "D:/Diplom/Trajectory"

    params_for_video = read_params(data_path + "/data/Result_SCI_7.csv",
                                   ['Group', 'Number Rat', 'Step Distance', 'Angle Distance'])
    for cond_idx in range(0, len(N_cond)):
        cond = cond_idx  # Use consistent variable types for indexing
        cond_dir = os.path.join(data_path + "/data/", N_cond[cond])  # Directory for this condition
        file_names = [f for f in os.listdir(cond_dir) if
                      f.endswith('_angles.csv')]
        for n, fname in enumerate(file_names):
            key_map = fname.split("_angles")[0]
            (result_step_cycle[key_map],
             result_average_max[key_map],
             result_average_min[key_map]) = definition_step_cycle(cond_dir, fname, params_for_video)
            result_all_count_step[key_map], result_average_time_step[key_map] = calculate_number_time_steps(
                result_step_cycle[key_map])

            if key_map[-2] == "_":
                trajectory_dir = key_map[:-2]
            else:
                trajectory_dir = key_map[:-3]
            result_average_height[key_map] = calculate_average_height(
                result_step_cycle[key_map],
                trajectory_path + "/" + trajectory_dir + "/" + key_map + ".csv",
            )

            group_name, day, rat_number = parse_result_identity(key_map)
            temp = [group_name, day, rat_number]
            temp.append(params_for_video[fname.split("_angles")[0]][0])
            temp.append(params_for_video[fname.split("_angles")[0]][1])
            temp.append(result_average_max[key_map])
            temp.append(result_average_min[key_map])
            temp.append(result_average_time_step[key_map] / 60)
            temp.append(result_all_count_step[key_map])
            temp.append(result_average_height[key_map])
            result_csv_data.append(temp)

    # Open file dialog to select video
    print(result_average_max)

    print(result_average_min)
    print(result_average_time_step)
    print(result_all_count_step)
    print(result_average_height)
    # pd.DataFrame(result_csv_data, columns=data_csv_columns).to_csv("Result.csv")
