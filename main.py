from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

class MainApp(App):
    def build(self):
        # Create the main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Add a welcome label
        self.welcome_label = Label(
            text='Welcome to My First App!',
            font_size=24,
            size_hint_y=None,
            height=50
        )
        
        # Add a text input field
        self.name_input = TextInput(
            hint_text='Enter your name',
            size_hint_y=None,
            height=40,
            multiline=False
        )
        
        # Add a button
        self.greet_button = Button(
            text='Greet Me!',
            size_hint_y=None,
            height=50
        )
        self.greet_button.bind(on_press=self.greet_user)
        
        # Add a label for displaying the greeting
        self.greeting_label = Label(
            text='',
            font_size=20
        )
        
        # Add all widgets to the layout
        layout.add_widget(self.welcome_label)
        layout.add_widget(self.name_input)
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
    MainApp().run()