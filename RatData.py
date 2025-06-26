class RatData:
    def __init__(self):
        self.video_name = None
        self.group = None
        self.number_day = 0
        self.number_rat = 0
        self.step_distance = 0
        self.angel_distance = 0
        self.count_step = 0
        self.min_angel = 0
        self.max_angel = 0
        self.step_height = 0
        self.total_time_step = None
columns = ['Group', 'Day', 'Number Rat',
           'Step Params', 'Angel Params',
           'Count Step', 'Average Time Step', 'Total Time Step(%)',
           'Step Height', 'Max Angel', 'Min Angel']