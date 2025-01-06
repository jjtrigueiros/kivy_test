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

class RotatedCamera(Camera):
    """Camera widget that can be rotated"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate()
            self.rot.angle = -90 if platform == 'android' else 0  # Rotate only on Android
            self.rot.origin = self.center
            self.rot.axis = (0, 0, 1)
        with self.canvas.after:
            PopMatrix()

    def on_size(self, instance, value):
        """Update rotation origin when size changes"""
        self.rot.origin = self.center

class MainApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = None
        self.permission_granted = False

    def build(self):
        # Create the main layout
        layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(20)
        )
        
        # Add a title label
        self.title_label = Label(
            text='Camera App',
            font_size=dp(32),
            size_hint_y=None,
            height=dp(60)
        )
        
        # Placeholder for camera
        self.camera_layout = BoxLayout(size_hint=(1, 0.8))
        self.camera_placeholder = Label(
            text='Initializing camera...',
            font_size=dp(20)
        )
        self.camera_layout.add_widget(self.camera_placeholder)
        
        # Add capture button
        self.capture_button = Button(
            text='Take Photo',
            size_hint_y=None,
            height=dp(70),
            font_size=dp(24),
            background_color=(0.2, 0.6, 1, 1)
        )
        self.capture_button.bind(on_press=self.take_photo)
        self.capture_button.disabled = True
        
        # Status label
        self.status_label = Label(
            text='',
            font_size=dp(20),
            size_hint_y=None,
            height=dp(40)
        )
        
        # Add widgets to layout
        layout.add_widget(self.title_label)
        layout.add_widget(self.camera_layout)
        layout.add_widget(self.capture_button)
        layout.add_widget(self.status_label)
        
        # Start permission request process
        if platform == 'android':
            Clock.schedule_once(self.request_android_permissions, 0.5)
        else:
            Clock.schedule_once(self.initialize_camera, 0.5)
        
        return layout

    def request_android_permissions(self, dt):
        """Request permissions on Android"""
        try:
            from android.permissions import request_permissions, Permission, check_permission
            
            # First check if we already have permissions
            if check_permission('android.permission.CAMERA'):
                self.permission_granted = True
                Clock.schedule_once(self.initialize_camera, 0.5)
                return

            def callback(permissions, results):
                if all(results):
                    self.permission_granted = True
                    Clock.schedule_once(self.initialize_camera, 0.5)
                else:
                    self.status_label.text = 'Camera permission denied'

            request_permissions([
                Permission.CAMERA,
                Permission.WRITE_EXTERNAL_STORAGE
            ], callback)

        except Exception as e:
            Logger.error(f'Permission error: {str(e)}')
            self.status_label.text = 'Error requesting permissions'

    def initialize_camera(self, dt):
        """Initialize the camera with error handling"""
        try:
            if platform == 'android' and not self.permission_granted:
                Logger.warning('Trying to initialize camera without permissions')
                return

            # Create new camera instance
            self.camera = RotatedCamera(
                resolution=(1920, 1080),
                play=True,
                size_hint=(1, 1)
            )
            
            # Clear the camera layout and add the new camera
            self.camera_layout.clear_widgets()
            self.camera_layout.add_widget(self.camera)
            
            # Enable the capture button
            self.capture_button.disabled = False
            self.status_label.text = ''
            
        except Exception as e:
            Logger.error(f'Camera error: {str(e)}')
            self.status_label.text = 'Camera not available'
            # Try to reinitialize after a delay
            if not hasattr(self, '_retry_count'):
                self._retry_count = 0
            if self._retry_count < 3:  # Limit retries
                self._retry_count += 1
                Clock.schedule_once(self.initialize_camera, 2)
    
    def take_photo(self, instance):
        try:
            if self.camera:
                import time
                timestr = time.strftime("%Y%m%d_%H%M%S")
                filename = f"IMG_{timestr}.png"
                
                self.camera.export_to_png(filename)
                self.status_label.text = f'Photo saved as {filename}'
                
                Clock.schedule_once(lambda dt: self.clear_status(), 3)
            else:
                self.status_label.text = 'Camera not available'
                Clock.schedule_once(lambda dt: self.clear_status(), 3)
                
        except Exception as e:
            Logger.error(f'Photo error: {str(e)}')
            self.status_label.text = 'Failed to take photo'
            Clock.schedule_once(lambda dt: self.clear_status(), 3)
    
    def clear_status(self):
        self.status_label.text = ''

    def on_stop(self):
        if self.camera:
            self.camera.play = False

if __name__ == '__main__':
    Window.minimum_width = dp(400)
    Window.minimum_height = dp(600)
    MainApp().run()