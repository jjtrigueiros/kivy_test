import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.uix.camera import Camera
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.utils import platform
from kivy.graphics.texture import Texture
import cv2
import numpy as np


class MyCamera(Camera):
    """Camera widget that can be rotated"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.opencv_frame = None
        Clock.schedule_interval(self.process_frame, 1.0 / 30.0)

    def on_tex(self, camera):
        self.texture = texture = camera.texture
        self.texture_size = list(texture.size)

    def process_frame(self, dt):
        print(dt)
        tex = self.texture
        img = texture_to_opencv(tex.get_region(0, 0, tex.width, tex.height))
        if platform == 'android':
            img = np.rot90(img, 3)
        img = detect_quadrilateral(img)
        self.opencv_frame = img

        self.texture = opencv_to_texture(img)
        if platform != 'android':
            self.display_frame(self.opencv_frame)
        self.canvas.ask_update()

    def display_frame(self, frame):
        """Display the current frame using cv2.imshow"""
        if frame is not None:
            cv2.imshow("Camera Frame", frame)
            cv2.waitKey(1)  # Add a short delay to allow the image to be displayed

def detect_quadrilateral(frame: np.ndarray) -> np.ndarray:
    """Detect and draw the largest quadrilateral in the frame"""
    try:
        # due to a conversion error in Android, we need to explicitly convert the frame to UMat
        frame_umat = cv2.UMat(frame)
        gray = cv2.cvtColor(frame_umat, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 30, 150)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        largest_contour = max(contours, key=cv2.contourArea)

        peri = cv2.arcLength(largest_contour, True)
        approx = cv2.approxPolyDP(largest_contour, 0.02 * peri, True)
        approx_np = approx.get()  # Convert UMat to numpy.ndarray before checking length

        # If largest contour is a quadrilateral (4 points)
        if len(approx_np) == 4:
            cv2.drawContours(frame_umat, [approx], -1, (0, 255, 0), 2)
            for point in approx_np:
                cv2.circle(frame_umat, tuple(point[0]), 5, (0, 255, 255), -1)

        # Convert back to numpy.ndarray
        return frame_umat.get()

    except Exception as e:
        message = f"Traceback: line {sys.exc_info()[-1].tb_lineno} - {str(e)}"
        Logger.error(f"OpenCV error: {message}")
        return frame

def texture_to_opencv(tex: Texture) -> np.ndarray:
    """
    Convert a Kivy texture (RGBA) to an OpenCV-compatible numpy array (BGRA).
    Complement of opencv_to_texture.
    """
    # This orients the texture correctly, or else the result will be flipped depending on tex.uvpos and tex.uvsize.
    tex_region = tex.get_region(0, 0, tex.width, tex.height)
    arr = np.frombuffer(tex_region.pixels, dtype=np.uint8).reshape(tex.height, tex.width, 4)
    return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)


def opencv_to_texture(mat: np.ndarray) -> Texture:
    """
    Convert an OpenCV-compatible numpy array (BGRA) to a Kivy texture (RGBA).
    Complement of texture_to_opencv.
    """
    height, width = mat.shape[:2]
    mat_rgba = cv2.cvtColor(mat, cv2.COLOR_BGR2RGBA)
    mat_rgba_vflipped = cv2.flip(mat_rgba, 0)
    data = mat_rgba_vflipped.tobytes()

    tex = Texture.create(size=(width, height), colorfmt="rgba")
    tex.blit_buffer(data, bufferfmt="ubyte", colorfmt="rgba")
    return tex


class MainApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = None
        self.permission_granted = False

    def build(self):
        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))

        # Add a title label
        self.title_label = Label(
            text="Quad Detector",
            font_size=dp(24),
            size_hint_y=None,
            height=dp(50),
            color=(1, 1, 1, 1),
            bold=True,
        )

        # Placeholder for camera
        self.camera_layout = BoxLayout(size_hint=(1, 1), padding=dp(10))

        self.camera_placeholder = Label(text="Initializing camera...", font_size=dp(20))
        self.camera_layout.add_widget(self.camera_placeholder)

        # Capture button
        self.capture_button = Button(
            text="Capture",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            border=(dp(2), dp(2), dp(2), dp(2)),
            background_normal="",
            background_down="",
        )
        self.capture_button.bind(on_press=self.take_photo)
        self.capture_button.disabled = True

        # Status label
        self.status_label = Label(
            text="",
            font_size=dp(20),
            size_hint_y=None,
            height=dp(40),
            color=(1, 1, 1, 1),
        )

        # Add widgets to layout
        layout.add_widget(self.title_label)
        layout.add_widget(self.camera_layout)
        layout.add_widget(self.capture_button)
        layout.add_widget(self.status_label)

        # Start permission request process
        if platform == "android":
            Clock.schedule_once(self.request_android_permissions, 0.5)
        else:
            Clock.schedule_once(self.initialize_camera, 0.5)

        return layout

    def request_android_permissions(self, dt):
        try:
            from android.permissions import (
                request_permissions,
                Permission,
                check_permission,
            )

            if check_permission("android.permission.CAMERA"):
                self.permission_granted = True
                Clock.schedule_once(self.initialize_camera, 0.5)
                return

            def callback(permissions, results):
                if all(results):
                    self.permission_granted = True
                    Clock.schedule_once(self.initialize_camera, 0.5)
                else:
                    self.status_label.text = "Camera permission denied"

            request_permissions(
                [Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE], callback
            )

        except Exception as e:
            Logger.error(f"Permission error: {str(e)}")
            self.status_label.text = "Error requesting permissions"

    def initialize_camera(self, dt):
        try:
            if platform == "android" and not self.permission_granted:
                Logger.warning("Trying to initialize camera without permissions")
                return

            # Create new camera instance using CVCamera
            self.camera = MyCamera(resolution=(1920, 1080), play=True, size_hint=(1, 1))

            # Clear the camera layout and add the new camera
            self.camera_layout.clear_widgets()
            self.camera_layout.add_widget(self.camera)

            # Enable the capture button
            self.capture_button.disabled = False
            self.status_label.text = ""

        except Exception as e:
            Logger.error(f"Camera error: {str(e)}")
            self.status_label.text = "Camera not available"
            if not hasattr(self, "_retry_count"):
                self._retry_count = 0
            if self._retry_count < 3:
                self._retry_count += 1
                Clock.schedule_once(self.initialize_camera, 2)

    def take_photo(self, instance):
        try:
            if self.camera:
                import time

                timestr = time.strftime("%Y%m%d_%H%M%S")
                filename = f"IMG_{timestr}.png"

                self.camera.export_to_png(filename)
                self.status_label.text = f"Photo saved as {filename}"

                Clock.schedule_once(lambda dt: self.clear_status(), 3)
            else:
                self.status_label.text = "Camera not available"
                Clock.schedule_once(lambda dt: self.clear_status(), 3)

        except Exception as e:
            Logger.error(f"Photo error: {str(e)}")
            self.status_label.text = "Failed to take photo"
            Clock.schedule_once(lambda dt: self.clear_status(), 3)

    def clear_status(self):
        self.status_label.text = ""

    def on_stop(self):
        if self.camera:
            self.camera.play = False


if __name__ == "__main__":
    Window.minimum_width = dp(400)
    Window.minimum_height = dp(600)
    MainApp().run()
