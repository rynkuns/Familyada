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
import json


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
    number = BoundedNumericProperty(0, min=0, max=8)
    content = StringProperty("XXXXX")
    score = BoundedNumericProperty(1, min=1, max=99)

    def __init__(self, **kwargs):
        super(Answer, self).__init__(**kwargs)
        self.number = kwargs['number']
        self.content = kwargs['content']
        self.score = kwargs['score']


class GameRootWidget(FloatLayout):
    
    team_red = ObjectProperty(None)
    team_blue = ObjectProperty(None)
    current_score = ObjectProperty(None)
    answers_container = ObjectProperty(None)

    standoff = False
    turn = 0

    def gamedata_from_json(self, file_path:str):
        with open(file_path, 'r') as file:
            self.gamedata = json.load(file)

    def load_question(self):
        answers = self.gamedata['questions'][self.turn]['answers']
        for ans in answers:
            self.answers_container.add_widget(Answer(
                number= answers.index(ans),
                content= ans[0],
                score= ans[1]
            ))


    






class FamilyadaApp(App):

    def build(self):
        self.game_root_widget = GameRootWidget()
        return self.game_root_widget

    def on_start(self):
        self.game_root_widget.gamedata_from_json('test.json')
        self.game_root_widget.load_question()
        return super().on_start()

if __name__ == '__main__':
    FamilyadaApp().run()
    