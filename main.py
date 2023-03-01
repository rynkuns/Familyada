import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.layout import Layout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, OptionProperty, BoundedNumericProperty, StringProperty
)
from kivy.clock import Clock

import time
import json

from gesture_receiver import GestureReceiver

NUMBERS= ["1", "2", "3", "4", "5", "5", "6", "7", "8", "9", "0"]
TEAMS = ["R","B"]
MISTAKES = ["X"]
MISC = ["<", "None"]
ALL_SIGNS = NUMBERS + TEAMS + MISTAKES + MISC

DUMMY_CALLBACK = lambda x: None


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
    number = BoundedNumericProperty(0, min=1, max=9)
    content = StringProperty("X X X X")
    score = BoundedNumericProperty(1, min=1, max=50)

    def __init__(self, **kwargs):
        super(Answer, self).__init__(**kwargs)
        self.number = kwargs['number']
        self.content = kwargs['content']
        self.score = kwargs['score']



class MistakesPanel(AnchorLayout):
    small_mistakes = ObjectProperty(None)
    large_mistake = ObjectProperty(None)



class GameRootWidget(Screen):

    global ALL_SIGNS, NUMBERS, TEAMS, MISTAKES, MISC, DUMMY_CALLBACK
    
    team_red = ObjectProperty(None)
    team_blue = ObjectProperty(None)
    current_score_widget = ObjectProperty(None)
    answers_container = ObjectProperty(None)
    standoff_scene = ObjectProperty(None)
    red_mistakes= ObjectProperty(None)
    blue_mistakes= ObjectProperty(None)

    current_score = 0
    red_score = 0
    blue_score = 0
    standoff = False
    turn = 0
    n_turns = 0
    n_mistakes = 0
    available_answers = []
    now_answering = OptionProperty("NO", options=["RED", "BLUE", "NO"])
    current_command = OptionProperty("None", options=ALL_SIGNS)
    next = DUMMY_CALLBACK


    def __init__(self, *args, **kwargs):
        super(GameRootWidget, self).__init__()
        self.add_widget(GestureReceiver(root_widget=self))

        #TODO może jakoś ogólniej zainicjować niż prepare question
        Clock.schedule_once(self.prepare_question)


    def make_score(self, value: int):
        self.current_score = value
        self. current_score_widget.text = str(self.current_score)


    def add_team_score(self, value: int, team: str):
        if team == "RED":
            self.red_score += value
            self.team_red.text = str(self.red_score)
        elif team == "BLUE":
            self.blue_score += value
            self.team_blue.text = str(self.blue_score)
        else:
            print("Unexpected team for add_team_score!")


    def switch_now_answering(self):
        print("switch_now_answering")
        if self.now_answering == "RED": self.now_answering = "BLUE"
        elif self.now_answering == "BLUE": self.now_answering = "RED"
        else: print("Unexpected team switch!")


    def gamedata_from_json(self, file_path:str):
        with open(file_path, 'r') as file:
            self.gamedata = json.load(file)
            self.n_turns = len(self.gamedata['questions'])


    def load_question(self):
        answers = self.gamedata['questions'][self.turn]['answers']
        self.available_answers = [str(x) for x in list( range(1,len(answers)+1) )]
        print("available answers:", self.available_answers)
        self.answers_container.clear_widgets()
        for ans in answers:
            self.answers_container.add_widget(Answer(
                number= answers.index(ans)+1,
                content= ans[0],
                score= ans[1]
            ))


    def engage_standoff(self):
        print("engage_standoff")
        self.standoff = True
        self.standoff_scene.opacity = 1.0


    # def receive_command(self, options=ALL_SIGNS):
    #     self.current_command = "None"
    #     print(options)
    #     while True: #TODO tu jest zjebane
    #         if self.current_command is not "None":
    #             if self.current_command not in options:
    #                 print("Unexpected command!")
    #                 self.current_command = "None"
    #             else:
    #                 return self.current_command


    def prepare_question(self, dt=None):
        print("prepare_question")
        if self.turn < self.n_turns:
            self.now_answering = "NO"
            self.current_score = 0
            self.load_question()
            self.engage_standoff()
        else:
            print("No more questions left!")


    def disengage_standoff(self, team:str):
        print("disengage_standoff")
        self.standoff = False
        self.standoff_scene.opacity = 0.0
        #TODO GRAFICZNY CUE JAKIŚ TUTAJ!!!
        print(team)
        self.now_answering = team
        self.next =  self.resolve_standoff
        
            # while no_correct_answer:
            #     print('elo')
            #     self.receive_command()
            #     if self.current_command in NUMBERS:
            #         #TODO odsłoń odpowiedź
            #         no_correct_answer = False
            #         #TODO wybierz team który przejmuje pytanie
            #     elif self.current_command in MISTAKES:
            #         #TODO odpal mistake po dobrej stronie
            #         pass

    def resolve_standoff(self, command):
        print("resolve_standoff")
        if command == "X":
            self.play_big_mistake() #TODO odpal mistake po dobrej stronie!
            self.switch_now_answering()
        elif command in NUMBERS:
            self.reveal_answer(command) 
            self.next = self.pick_team
        else:
            print("Unexpected command for resolve_standoff!")


    def pick_team(self, command):
        print("pick_team")
        def act():
            self.clear_mistakes("BOTH")
            self.next = self.make_standard_answer # zacznij odpytywać

        if command == "R":
            self.now_answering = "RED"
            act()
        elif command == "B":
            self.now_answering = "BLUE"
            act()
        else:
            print("Unexpected command for pick_team!")
            

    def make_standard_answer(self, command):
        print("make_standard_answer")
        if command in self.available_answers:
            self.reveal_answer(command)
        elif command == "X":
            self.n_mistakes += 1
            self.play_mistake() #TODO odpal mistake
        ### Check whether to await another standard answer:
        if self.n_mistakes == 3:
            self.switch_now_answering()
            self.next = self.make_final_answer # finalna odpoweidź
        elif self.available_answers == []:
            self.summarize_question()


    def make_final_answer(self, command):
        print("make_final_answer")
        if command in self.available_answers:
            self.reveal_answer(command)
            Clock.schedule_once(self.summarize_question, 2)
            # self.summarize_question() #TODO za kilka sekund
        if command == "X":
            self.play_big_mistake() #TODO odpal duży mistake
            self.switch_now_answering()
            # self.summarize_question() #TODO(zaplanuj na clock za kilka sekund)
            Clock.schedule_once(self.summarize_question, 4)


    def reveal_answer(self, number:str, add_score:bool=True):
        print("reveal_answer")
        if number in self.available_answers:
            for answer in self.answers_container.children:
                if answer.number == int(number):
                    answer.children[2].text = answer.content
                    answer.children[0].text = str(answer.score)
                    if add_score:
                        new_score = self.current_score + answer.score
                        self.make_score(new_score)
                    self.available_answers.remove(number)
                    #TODO play sound!
                    return
        print("Unexpected number for reveal_answer!")


    def summarize_question(self):
        pass
        #TODO muzyczka
        # #TODO podliczenie punktów
        self.add_team_score(self.current_score, self.now_answering)
        self.make_score(0)
        self.next = self.unsolved_answer


    def play_big_mistake(self):
        print("play_big_mistake")
        mistakes_dict = {"RED": self.red_mistakes, "BLUE": self.blue_mistakes}
        team = self.now_answering
        def play(dt):
            mistakes_dict[team].children[0].children[0].opacity = 1.0
            #TODO play sound!
        self.clear_mistakes(team)
        Clock.schedule_once(play, 1)


    def play_mistake(self):
        print("play_mistake")
        #TODO


    def unsolved_answer(self):
        print("unsolved_answer")
        #TODO po jednym odkryj pozostałe odpowiedzi
        for ans in self.available_answers.reverse():
            self.reveal_answer(ans, add_score=False)

        #TODO gdy wszystkie odkryte przekmiń następne pytanie


    def clear_mistakes(self, team: str):
        mistakes_dict = {"RED": [self.red_mistakes], "BLUE": [self.blue_mistakes], "BOTH": [self.red_mistakes, self.blue_mistakes]}
        for panel in mistakes_dict[team]:
            for layout in panel.children:
                for image in layout.children:
                    image.opacity = 0.0
        self.n_mistakes = 0 #TODO sprawdzić to



class FamilyadaApp(App):

    title = 'Familyada'

    def build(self):
        self.game_root_widget = GameRootWidget()
        return self.game_root_widget

    def on_start(self):
        self.game_root_widget.gamedata_from_json('test_manual.json')
        #TODO
        # self.game_root_widget.do_question() ### TO JEST ŹLE, BO PRZED WCZYTANIEM EKRANU, PRZEROBIĆ NA PO WCZYTANIU EKRANU!
        return super().on_start()


if __name__ == '__main__':
    FamilyadaApp().run()
    