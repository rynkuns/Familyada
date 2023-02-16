import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, OptionProperty, BoundedNumericProperty, StringProperty
)

import time


class StandoffMushroom(Widget):

    team = OptionProperty("None", options=["RED", "BLUE"])

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            root = App.get_running_app().root
            if root.standoff:
                self.opacity -=0.5
                root.standoff = False
                return True


class Answer(BoxLayout):
    number = BoundedNumericProperty(1, min=1, max=9)
    content = StringProperty("XXXXX")
    score = BoundedNumericProperty(1, min=1, max=99)


class GameRootWidget(FloatLayout):
    
    team_red = ObjectProperty(None)
    team_blue = ObjectProperty(None)
    current_score = ObjectProperty(None)

    standoff = True
    






class FamilyadaApp(App):

    def build(self):
        return GameRootWidget()


if __name__ == '__main__':
    FamilyadaApp().run()
    