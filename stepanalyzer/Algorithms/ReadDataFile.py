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


def read_csv_coordinate(file_name, use_columns):
    """Read data with angles.
    @:param file_name - path+file_name
    @:param use_columns - y columns
    @:return list Y-[coordinates]
    """
    result_coordinates = []
    try:
        data_csv = pd.read_csv(file_name, usecols=use_columns)
        for index, row in data_csv.iterrows():
            result_coordinates.append(row[use_columns])
    except FileNotFoundError:
        print(f'File with path {file_name} not found.')
    return result_coordinates
