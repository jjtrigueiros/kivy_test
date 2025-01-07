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
from kivy.graphics import Rotate, PushMatrix, PopMatrix
from kivy.graphics.texture import Texture
import cv2
import numpy as np


class MyCamera(Camera):
    """Camera widget that can be rotated"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate()
            self.rot.angle = (
                -90 if platform == "android" else 0
            )  # Rotate only on Android
            self.rot.origin = self.center
            self.rot.axis = (0, 0, 1)
        with self.canvas.after:
            PopMatrix()

        # self.current_frame = None
        Clock.schedule_interval(self.process_frame, 1.0 / 30.0)

    def on_size(self, instance, value):
        """Update rotation origin when size changes"""
        self.rot.origin = self.center

    def on_tex(self, camera):
        texture = camera.texture
        img = texture_to_opencv(texture)
        # self.current_frame = img
        tex = opencv_to_texture(img)
        self.texture = tex
        self.texture_size = list(tex.size)

        Logger.info("Hi!!!!")

    def process_frame(self, dt):
        self.canvas.ask_update()
        # self.display_frame(self.current_frame)

    def display_frame(self, frame):
        """Display the current frame using cv2.imshow"""
        if frame is not None:
            cv2.imshow("Camera Frame", frame)
            cv2.waitKey(1)  # Add a short delay to allow the image to be displayed


def texture_to_opencv(tex: Texture) -> np.ndarray:
    """
    Convert a Kivy texture to an OpenCV-compatible numpy array.
    Complementary to opencv_to_texture.
    """
    arr = np.frombuffer(tex.pixels, dtype=np.uint8).reshape(tex.height, tex.width, 4)
    return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)


def opencv_to_texture(mat: np.ndarray) -> Texture:
    """
    Convert an OpenCV-compatible numpy array to a Kivy texture.
    Complementary to texture_to_opencv.
    """
    height, width = mat.shape[:2]
    data = cv2.cvtColor(mat, cv2.COLOR_BGRA2RGBA).tobytes()
    tex = Texture.create(size=(width, height), colorfmt="rgba")
    tex.blit_buffer(data, bufferfmt="ubyte", colorfmt="rgba")
    # We need to flip the texture vertically to match Kivy's coordinate system.
    # Flipping using Kivy makes it so that tex.tex_coords are equal to the original input.
    # This makes it so that opencv_to_texture and texture_to_opencv are complementary for the expected case, but
    # ideally the function would be aware of the Kivy orientation so that they would be truly complementar.
    tex.flip_vertical()
    return tex


class MainApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = None
        self.permission_granted = False

    def build(self):
        # Create the main layout
        layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(20))

        # Add a title label
        self.title_label = Label(
            text="Quad Detector", font_size=dp(32), size_hint_y=None, height=dp(60)
        )

        # Placeholder for camera
        self.camera_layout = BoxLayout(size_hint=(1, 0.8))
        self.camera_placeholder = Label(text="Initializing camera...", font_size=dp(20))
        self.camera_layout.add_widget(self.camera_placeholder)

        # Add capture button
        self.capture_button = Button(
            text="Take Photo",
            size_hint_y=None,
            height=dp(70),
            font_size=dp(24),
            background_color=(0.2, 0.6, 1, 1),
        )
        self.capture_button.bind(on_press=self.take_photo)
        self.capture_button.disabled = True

        # Status label
        self.status_label = Label(
            text="", font_size=dp(20), size_hint_y=None, height=dp(40)
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
