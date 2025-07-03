import os

import pandas as pd


def read_params(path, use_columns):
    """Read params for all videos.
    @:param path - path to the file with data params
    @:param use_columns - array of use columns
    @:return dict{Group+Number_Rut:[Step Params, Angle Distance]}
    """
    params_for_video = {}

    try:
        data_csv = pd.read_csv(path, usecols=use_columns)
        for index, row in data_csv.iterrows():
            key = row['Group'] + "_" + str(row['Number Rat'])
            params_for_video[key] = [row['Step Distance'], row['Angle Distance']]
    except FileNotFoundError:
        print(f'File with path {path} not found.')

    return params_for_video


def read_head_files(path, cond):
    """Read data with angles.
    @:param cond - array with file name
    @:return array of all names files
    """

