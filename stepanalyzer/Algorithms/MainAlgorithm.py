import os

from stepanalyzer.Algorithms.KinematicsFun import definition_step_cycle
from stepanalyzer.Algorithms.ReadDataFile import read_params

N_cond = ['Intact', 'SCI_3_dpi', 'SCI_TMT_3_dpi', 'SCI_7_dpi', 'SCI_TMT_7_dpi', 'SCI_14_dpi', 'SCI_TMT_14_dpi',
          'SCI_21_dpi',
          'SCI_TMT_21_dpi', 'SCI_28_dpi', 'SCI_TMT_28_dpi']

if __name__ == "__main__":
    result_step_cycle = {}  # Dict{"file_name":Array with step position}
    data_path = "D:/Diplom/DiplomPy"
    params_for_video = read_params(data_path + "/data/Result_SCI_7.csv",
                                   ['Group', 'Number Rat', 'Step Distance', 'Angle Distance'])
    for cond_idx in range(0, len(N_cond)):
        cond = cond_idx  # Use consistent variable types for indexing
        cond_dir = os.path.join(data_path + "/data/", N_cond[cond])  # Directory for this condition
        file_names = [f for f in os.listdir(cond_dir) if
                      f.endswith('_angles.csv')]
        for n, fname in enumerate(file_names):
            result_step_cycle[fname.split("_angles")[0]] = definition_step_cycle(cond_dir, params_for_video, fname)
        print(result_step_cycle)
