from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.core.window import Window

class MainApp(App):
    def build(self):
        # Create the main layout with proper padding
        layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),  # Consistent padding on all devices
            spacing=dp(20)   # Consistent spacing between widgets
        )
        
        # Add a welcome label that scales with screen size
        self.welcome_label = Label(
            text='Welcome to My First App!',
            font_size=dp(32),  # Larger, scalable font
            size_hint_y=None,
            height=dp(60)
        )
        
        # Spacer to push content down from top
        layout.add_widget(Label(size_hint_y=0.1))
        
        # Add a text input field with better sizing
        self.name_input = TextInput(
            hint_text='Enter your name',
            size_hint_y=None,
            height=dp(60),  # Taller input field
            multiline=False,
            font_size=dp(20),  # Larger font for input
            padding=[dp(15), dp(15)],  # Internal padding
            background_color=(1, 1, 1, 0.9)  # Slightly transparent white
        )
        
        # Add a button with better sizing
        self.greet_button = Button(
            text='Greet Me!',
            size_hint_y=None,
            height=dp(70),  # Taller button
            font_size=dp(24),  # Larger font for button
            background_color=(0.2, 0.6, 1, 1)  # Nice blue color
        )
        self.greet_button.bind(on_press=self.greet_user)
        
        # Add a label for displaying the greeting
        self.greeting_label = Label(
            text='',
            font_size=dp(24),
            size_hint_y=0.4,  # Takes up remaining space
            halign='center',
            valign='middle'
        )
        self.greeting_label.bind(size=self.greeting_label.setter('text_size'))
        
        # Add all widgets to the layout with some spacing
        layout.add_widget(self.welcome_label)
        layout.add_widget(self.name_input)
        layout.add_widget(Label(size_hint_y=0.05))  # Small spacer
        layout.add_widget(self.greet_button)
        layout.add_widget(self.greeting_label)
        
        return layout
    
    def greet_user(self, instance):
        name = self.name_input.text.strip()
        if name:
            self.greeting_label.text = f'Hello, {name}!\nNice to meet you!'
        else:
            self.greeting_label.text = 'Please enter your name first!'

if __name__ == '__main__':
    # Set minimum window size for desktop testing
    Window.minimum_width = dp(400)
    Window.minimum_height = dp(600)
    MainApp().run()