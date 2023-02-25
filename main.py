import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.layout import Layout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, OptionProperty, BoundedNumericProperty, StringProperty
)

import time
import json

NUMBERS= ["1", "2", "3", "4", "5", "5", "6", "7", "8", "9", "0"]
TEAMS = ["R","B"]
MISTAKES = ["X"]
MISC = ["<"]
ALL_SIGNS = NUMBERS + TEAMS + MISTAKES + MISC

class StandoffMushroom(Widget):

    team = OptionProperty("None", options=["RED", "BLUE"])

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            root = App.get_running_app().root
            if root.standoff:
                # self.opacity -=0.5
                # root.standoff = False
                root.disengage_standoff(self.team)
                return True


class Answer(BoxLayout):
    number = BoundedNumericProperty(0, min=0, max=8)
    content = StringProperty("X X X X")
    score = BoundedNumericProperty(1, min=1, max=50)

    def __init__(self, **kwargs):
        super(Answer, self).__init__(**kwargs)
        self.number = kwargs['number']
        self.content = kwargs['content']
        self.score = kwargs['score']


class MistakesPanel(Widget):
    small_mistakes = ObjectProperty(None)
    large_mistake = ObjectProperty(None)


class GameRootWidget(FloatLayout):

    global ALL_SIGNS, NUMBERS, TEAMS, MISTAKES, MISC
    
    team_red = ObjectProperty(None)
    team_blue = ObjectProperty(None)
    current_score = ObjectProperty(None)
    answers_container = ObjectProperty(None)
    standoff_scene = ObjectProperty(None)

    standoff = False
    turn = 0
    n_turns = 0
    now_answering = OptionProperty("NO", options=["RED", "BLUE", "NO"])
    current_command = OptionProperty(None, options=ALL_SIGNS+[None])


    def gamedata_from_json(self, file_path:str):
        with open(file_path, 'r') as file:
            self.gamedata = json.load(file)
            self.n_turns = len(self.gamedata['questions'])


    def load_question(self):
        answers = self.gamedata['questions'][self.turn]['answers']
        self.answers_container.clear_widgets()
        for ans in answers:
            self.answers_container.add_widget(Answer(
                number= answers.index(ans)+1,
                content= ans[0],
                score= ans[1]
            ))


    def engage_standoff(self):
        self.standoff = True
        self.standoff_scene.opacity = 1.0

    
    def disengage_standoff(self, team:str):
        self.standoff = False
        self.standoff_scene.opacity = 0.0
        ### GRAFICZNY CUE JAKIŚ TUTAJ!!!
        print(team)
        self.now_answering = team


    def receive_command(self, options=ALL_SIGNS):
        #TODO miej widget na cały ekran, który cał czas zbiera gesty i input z klawiatury
        self.current_command = None
        print(ALL_SIGNS)
        while True:
            if self.current_command is not None:
                if self.current_command not in options:
                    print("Unexpected command!")
                    self.current_command = None
                else:
                    return self.current_command


    def do_question(self):
        if self.turn < self.n_turns:
            self.now_answering = "NO"
            self.load_question()
            self.engage_standoff()
            ### .....
            ### od razu obsługuj odpowiedzi od zawodników
            no_correct_answer = True
            while no_correct_answer:
                print('elo')

                #weź komendę
                #jeśli zła odpowiedź:
                    # odpal mistake i zmień team
                #jeśli dobra:
                    # pokaż na planszy, zakończ tą pętlę
            #weź komendę który team bierze pytanie
            #wyzeruj mistakes
            #pętla zbieraj komendy i odpalaj mistake albo odpowieź
                #gdy 3 mistake
                    # zmiana zespołu
                    #jedna próba
                #gdy wszystko odgadnięte
                    # break
            #podsumowanie, podlicz punkty
            #pętla pokaż wyniki od końca zakryte

                break
        else:
            print("No more questions left!")
    






class FamilyadaApp(App):

    title = 'Familyada'

    def build(self):
        self.game_root_widget = GameRootWidget()
        return self.game_root_widget

    def on_start(self):
        ### TO JEST ŹLE, BO PRZED WCZYTANIEM EKRANU, PRZEROBIĆ NA PO WCZYTANIU EKRANU! #TODO
        self.game_root_widget.gamedata_from_json('test.json')
        self.game_root_widget.do_question()
        return super().on_start()

if __name__ == '__main__':
    FamilyadaApp().run()
    