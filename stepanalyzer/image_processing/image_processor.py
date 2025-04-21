import cv2
from PIL.ImageQt import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog


def open_video(self):
    try:
        # Open file dialog to select video
        video_file, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)"
        )
        if video_file:
            self.video_cap = cv2.VideoCapture(video_file)
            if not self.video_cap.isOpened():
                raise IOError("Could not open video file.")

            self.total_frames = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.max_frame = self.total_frames - 1

            self.video_loaded = True
            self.slider.setEnabled(True)
            self.slider.setMinimum(0)
            self.slider.setMaximum(self.max_frame)
            self.slider.setValue(0)

            # Get video width and height for auto-resize
            self.video_width = int(self.video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.video_height = int(self.video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            self.show_frame(0)

            self.ax.clear()
            self.canvas.draw()
            self.valid_data = []

    except Exception as e:
        self.show_error_message(f"Error loading video: {e}")


def show_frame(self, frame_number):
    try:
        # Set the frame position in the video and read it
        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        success, frame = self.video_cap.read()

        if success:
            # Overlay the frame number in the upper right corner
            text = f"Frame: {frame_number}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            color = (255, 255, 255)  # White text
            thickness = 2
            text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
            text_x = self.video_width - text_size[0] - 10  # 10 pixels from the right edge
            text_y = 30  # 30 pixels from the top
            cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)

            # If CSV data is available, plot the dots and connect them
            if not self.csv_data.empty and frame_number in self.csv_data['coords'].values:
                row_data = self.csv_data[self.csv_data['coords'] == frame_number]

                # List of points to connect with lines (order: crest -> hip -> knee -> ankle -> mtp -> toe)
                key_points = ['iliaccrest', 'hip', 'knee', 'ankle', 'mtp', 'toe']
                points = []

                for index, (label, (x_col, y_col)) in enumerate(self.coordinates.items()):
                    if label in key_points:
                        x = int(float(str(row_data[x_col].values[0]).replace(u'\xa0', u'')))
                        y = int(float(str(row_data[y_col].values[0]).replace(u'\xa0', u'')))
                        points.append((x, y))  # Add the point to the list

                        # Draw the dot (adjust for OpenCV's coordinate system)
                        color = self.colors[index % len(self.colors)]
                        cv2.circle(frame, (x, y), 10, color, -1)

                        # Draw the label text next to the dot
                        label_x = x + 10  # Offset the label slightly
                        label_y = y - 10
                        cv2.putText(frame, label, (label_x, label_y), font, 0.7, color, 2)

                # Connect the points with lines
                for i in range(len(points) - 1):
                    start_point = points[i]
                    end_point = points[i + 1]
                    cv2.line(frame, start_point, end_point, (0, 255, 255), 2)  # Yellow line with thickness 2

            scale_percent = 45
            width = int(frame.shape[1] * scale_percent / 100)
            height = int(frame.shape[0] * scale_percent / 100)
            dim = (width, height)
            frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

            # Convert the frame to QImage format and display it
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            qimg = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(qimg))


    except Exception as e:
        self.show_error_message(f"Error showing frame: {e}")
