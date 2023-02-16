import kivy
kivy.require('2.1.0') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)

import time


class StandoffMushroom(Widget):

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            root = App.get_running_app().root
            if root.standoff:
                self.opacity -=0.5
                root.standoff = False
                return True


class Answer(BoxLayout):
    pass


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
    