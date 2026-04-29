import cv2
from PyQt5.QtGui import QImage, QPixmap


def _frame_rows(widget, frame_number):
    frame_column = getattr(widget, "frame_column", None)
    if frame_column and frame_column in widget.csv_data.columns:
        return widget.csv_data[widget.csv_data[frame_column] == frame_number]

    if frame_number < len(widget.csv_data):
        return widget.csv_data.iloc[[frame_number]]

    return widget.csv_data.iloc[0:0]


def _to_int_coordinate(value):
    return int(float(str(value).replace(u"\xa0", "")))


def _paint_frame_header(widget, frame, frame_number):
    text = f"Frame: {frame_number}"
    title = f'{widget.name_video.split("/")[-1]}'
    font = cv2.FONT_HERSHEY_SIMPLEX
    color = (255, 255, 255)
    thickness = 2
    text_size, _ = cv2.getTextSize(text, font, 1, thickness)
    text_x = widget.video_width - text_size[0] - 10

    cv2.putText(frame, text, (text_x, 30), font, 1, color, thickness, cv2.LINE_AA)
    cv2.putText(frame, title, (0, 30), font, 1, color, thickness, cv2.LINE_AA)
    return font


def _show_qimage(widget, frame):
    scale_percent = 45
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    height, width, channel = frame.shape
    bytes_per_line = 3 * width
    qimg = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
    widget.image_label.setPixmap(QPixmap.fromImage(qimg))


def _draw_generic_points(widget, frame, frame_number, radius=6, font_scale=0.55):
    if widget.csv_data.empty or not widget.coordinates:
        return

    row_data = _frame_rows(widget, frame_number)
    if row_data.empty:
        return

    row_data = row_data.iloc[0]
    font = cv2.FONT_HERSHEY_SIMPLEX
    points = []

    for index, (label, (x_col, y_col)) in enumerate(widget.coordinates.items()):
        if row_data[[x_col, y_col]].isna().any():
            continue

        x = _to_int_coordinate(row_data[x_col])
        y = _to_int_coordinate(row_data[y_col])
        points.append((x, y))

        color = widget.colors[index % len(widget.colors)]
        cv2.circle(frame, (x, y), radius, color, -1)
        cv2.putText(frame, label, (x + 10, y - 10), font, font_scale, color, 2)

    if getattr(widget, "connect_points", True):
        for i in range(len(points) - 1):
            cv2.line(frame, points[i], points[i + 1], (0, 255, 255), 2)


def show_frame(self, frame_number):
    try:
        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        success, frame = self.video_cap.read()

        if success:
            _paint_frame_header(self, frame, frame_number)
            _draw_generic_points(self, frame, frame_number, radius=10, font_scale=0.7)
            _show_qimage(self, frame)

    except Exception as e:
        self.show_error_message(f"Error showing frame: {e}")


def show_frame_open_field(self, frame_number):
    try:
        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        success, frame = self.video_cap.read()

        if success:
            _paint_frame_header(self, frame, frame_number)
            _draw_generic_points(self, frame, frame_number)
            _show_qimage(self, frame)

    except Exception as e:
        self.show_error_message(f"Error showing frame: {e}")
