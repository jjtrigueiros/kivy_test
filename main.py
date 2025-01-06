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

class MainApp(App):
    def build(self):
        try:
            # Request Android permissions first if we're on Android
            if platform == 'android':
                self.request_android_permissions()

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
            
            try:
                # Create the camera widget with error handling
                self.camera = Camera(
                    resolution=(640, 480),
                    play=True,
                    size_hint=(1, 0.8),
                    index=0  # Use the first available camera
                )
            except Exception as e:
                Logger.error(f'Camera error: {str(e)}')
                # If camera fails, show an error message instead
                self.camera = Label(
                    text='Camera not available',
                    size_hint=(1, 0.8)
                )
            
            # Add capture button
            self.capture_button = Button(
                text='Take Photo',
                size_hint_y=None,
                height=dp(70),
                font_size=dp(24),
                background_color=(0.2, 0.6, 1, 1)
            )
            self.capture_button.bind(on_press=self.take_photo)
            
            # Status label
            self.status_label = Label(
                text='',
                font_size=dp(20),
                size_hint_y=None,
                height=dp(40)
            )
            
            # Add widgets to layout
            layout.add_widget(self.title_label)
            layout.add_widget(self.camera)
            layout.add_widget(self.capture_button)
            layout.add_widget(self.status_label)
            
            return layout
            
        except Exception as e:
            Logger.error(f'Build error: {str(e)}')
            # If something goes wrong, show a minimal error layout
            error_layout = BoxLayout(orientation='vertical', padding=dp(20))
            error_layout.add_widget(Label(
                text=f'Error initializing app:\n{str(e)}',
                font_size=dp(20)
            ))
            return error_layout

    def request_android_permissions(self):
        """Request permissions on Android"""
        try:
            if platform == 'android':
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.CAMERA,
                    Permission.WRITE_EXTERNAL_STORAGE
                ])
        except Exception as e:
            Logger.error(f'Permission error: {str(e)}')
            # Continue without permissions - the app will handle camera/storage errors gracefully
    
    def take_photo(self, instance):
        try:
            # Only try to take photo if we have a working camera
            if isinstance(self.camera, Camera):
                import time
                timestr = time.strftime("%Y%m%d_%H%M%S")
                filename = f"IMG_{timestr}.png"
                
                self.camera.export_to_png(filename)
                self.status_label.text = f'Photo saved as {filename}'
                
                # Clear status after 3 seconds
                Clock.schedule_once(lambda dt: self.clear_status(), 3)
            else:
                self.status_label.text = 'Camera not available'
                Clock.schedule_once(lambda dt: self.clear_status(), 3)
                
        except Exception as e:
            Logger.error(f'Photo error: {str(e)}')
            self.status_label.text = 'Failed to take photo'
            Clock.schedule_once(lambda dt: self.clear_status(), 3)
    
    def clear_status(self):
        """Clear the status message"""
        self.status_label.text = ''

    def on_stop(self):
        """Clean up when the app closes"""
        try:
            if isinstance(self.camera, Camera):
                self.camera.play = False
        except Exception as e:
            Logger.error(f'Cleanup error: {str(e)}')

if __name__ == '__main__':
    # Set minimum window size for desktop testing
    Window.minimum_width = dp(400)
    Window.minimum_height = dp(600)
    MainApp().run()