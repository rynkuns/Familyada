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
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.animation import Animation

import os
import json

from gesture_receiver import GestureReceiver
from animated_background import AnimatedBackground
from keyboard_receiver import KeyboardReceiver

NUMBERS= ["1", "2", "3", "4", "5", "5", "6", "7", "8", "9", "0"]
TEAMS = ["R","B"]
MISTAKES = ["X"]
MISC = ["<", "None"]
ALL_SIGNS = NUMBERS + TEAMS + MISTAKES + MISC

DUMMY_CALLBACK = lambda *args: None


class StandoffMushroom(Widget):

    team = OptionProperty("None", options=["RED", "BLUE"])

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            root = App.get_running_app().root
            if root.standoff:
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



class Answer_f(BoxLayout):
    pass



class MistakesPanel(AnchorLayout):
    small_mistakes = ObjectProperty(None)
    large_mistake = ObjectProperty(None)



class RoundPreview(Label):
    round_number = NumericProperty(0)

    def __init__(self, round_number:int, **kwargs):
        super(RoundPreview, self).__init__(**kwargs)
        self.round_number = round_number



class OutroPreview(Label):
    
    def __init__(self, txt:str, **kwargs):
        super(OutroPreview, self).__init__(**kwargs)
        self.text = txt



class GameRootWidget(Screen):

    global ALL_SIGNS, NUMBERS, TEAMS, MISTAKES, MISC, DUMMY_CALLBACK
    
    team_red = ObjectProperty(None)
    team_blue = ObjectProperty(None)
    current_score_widget = ObjectProperty(None)
    answers_container = ObjectProperty(None)
    standoff_scene = ObjectProperty(None)
    red_mistakes= ObjectProperty(None)
    blue_mistakes= ObjectProperty(None)
    game_board= ObjectProperty(None)
    final_round_panel = ObjectProperty(None)
    timer = ObjectProperty(None)

    current_score = 0
    red_score = 0
    blue_score = 0
    standoff = False
    turn = 0
    n_turns = 0
    n_mistakes = 0
    available_answers = []
    round = 1
    next_round_turn = {0:1, 4:2, 6:3}
    now_answering = OptionProperty("NO", options=["RED", "BLUE", "NO"])
    current_command = OptionProperty("None", options=ALL_SIGNS)
    next = DUMMY_CALLBACK
    typing_buffer = ""
    finalist = 0
    answer_finalist = 0
    
    make_sound = lambda file: SoundLoader.load(os.path.join("audio", file))
    sounds = {
        "mistake": make_sound("mistake.mp3"),
        "answer": make_sound("answer.mp3"),
        "intro": make_sound("intro.mp3"),
        "repeat_final": make_sound("repeat_final.mp3"),
        "timeup_final": make_sound("timeup_final.mp3"),
        "before_round": make_sound("before_round.mp3"),
        "before_final": make_sound("before_final.mp3"),
        "between_final": make_sound("after_1_final_round.mp3")
    } #TODO volume!


    def __init__(self, *args, **kwargs):
        super(GameRootWidget, self).__init__()
        # self.add_widget(GestureReceiver(root_widget=self))
        self.add_widget(KeyboardReceiver(root_widget=self))
        self.bind(now_answering=self.answering_visual)
        self.sounds["before_round"].volume = 0.3

        Clock.schedule_once(self.intro) #TODO
        # Clock.schedule_once(self.prepare_final) #TODO


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


    def answering_visual(self, obj, val):
        colors = {"NO": [1,1,1,1], "BLUE": [0.8, 0.8, 1, 1], "RED": [1, 0.8, 0.8, 1]}
        self.game_board.color = colors[val]
        anim = Animation(color=[1,1,1,1], duration=2)
        animate = lambda dt: anim.start(self.game_board)
        Clock.schedule_once(animate, 1)


    def gamedata_from_json(self, file_path:str):
        with open(file_path, 'r') as file:
            self.gamedata = json.load(file)
            self.n_turns = len(self.gamedata['questions'])
        self.round = 1


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


    def preview_round(self, dt=None):
        preview = RoundPreview(self.round)
        self.add_widget(preview)
        self.sounds["before_round"].play()
        def stop(dt):
            self.remove_widget(preview)
        Clock.schedule_once(stop, 4.1)


    def intro(self, dt=None):
        print("intro")
        #TODO ekran powitalny
        self.sounds["intro"].play()
        def next(dt):
            self.next = self.prepare_question
        Clock.schedule_once(next, 20)


    def engage_standoff(self):
        print("engage_standoff")
        self.standoff = True
        self.standoff_scene.opacity = 1.0


    def prepare_question(self, dt=None, command=None):
        print("prepare_question")
        if self.turn < self.n_turns:
            if self.turn in self.next_round_turn:
                self.round = self.next_round_turn[self.turn]
                self.preview_round()
            self.now_answering = "NO"
            self.current_score = 0
            self.load_question()
            self.engage_standoff()
            self.clear_mistakes("BOTH")
            self.timer.text = " "
            self.final_round_panel.opacity = 0.0
            self.next = DUMMY_CALLBACK
        else:
            print("No more questions left!")
            self.prepare_final()


    def disengage_standoff(self, team:str):
        print("disengage_standoff")
        self.standoff = False
        self.standoff_scene.opacity = 0.0
        #TODO GRAFICZNY CUE JAKIŚ TUTAJ!!!
        print(team)
        self.now_answering = team
        self.next =  self.resolve_standoff
        

    def resolve_standoff(self, command):
        print("resolve_standoff")
        if command == "X":
            self.play_big_mistake()
            self.switch_now_answering()
        elif command in self.available_answers:
            self.reveal_answer(command) 
            if command == "1":
                self.next = self.pick_team
            else:
                self.switch_now_answering()
                self.next = self.resolve_standoff_second
        else:
            print("Unexpected command for resolve_standoff!")

        
    def resolve_standoff_second(self, command):
        print("resolve_standoff_2")
        if command == "X":
            self.play_big_mistake()
        elif command in self.available_answers:
            self.reveal_answer(command)
        self.next = self.pick_team
                         

    def pick_team(self, command):
        print("pick_team")
        self.answering_visual(None, "NO")
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
            self.play_mistake()
            self.n_mistakes += 1
        ### Check whether to await another standard answer:
        if self.n_mistakes == 3:
            self.switch_now_answering()
            self.next = self.make_final_answer
        elif self.available_answers == []:
            self.summarize_question()


    def make_final_answer(self, command):
        print("make_final_answer")
        if command in self.available_answers:
            self.reveal_answer(command)
            Clock.schedule_once(self.summarize_question, 2)
        if command == "X":
            self.play_big_mistake()
            self.switch_now_answering()
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
                    self.sounds["answer"].play()
                    return
        print("Unexpected number for reveal_answer!")


    def summarize_question(self, dt=None):
        print("summarize_question")
        #TODO muzyczka
        self.add_team_score(self.current_score * self.round, self.now_answering)
        self.make_score(0)
        self.next = self.unsolved_answer


    def play_big_mistake(self):
        print("play_big_mistake")
        mistakes_dict = {"RED": self.red_mistakes, "BLUE": self.blue_mistakes}
        team = self.now_answering
        def play(dt):
            mistakes_dict[team].children[0].children[0].opacity = 1.0
            self.sounds["mistake"].play()
        self.clear_mistakes(team)
        Clock.schedule_once(play, 0.2)


    def play_mistake(self):
        print("play_mistake")
        mistakes_dict = {"RED": self.red_mistakes, "BLUE": self.blue_mistakes}
        team = self.now_answering
        mistakes_dict[team].children[1].children[self.n_mistakes].opacity = 1.0
        self.sounds["mistake"].play()


    def unsolved_answer(self, command):
        print("unsolved_answer")
        if self.available_answers != []:
            self.reveal_answer(self.available_answers[-1], add_score=False)
            if self.available_answers == []:
                self.next = self.finish_turn
        else:
            self.next = self.finish_turn


    def clear_mistakes(self, team: str):
        mistakes_dict = {"RED": [self.red_mistakes], "BLUE": [self.blue_mistakes], "BOTH": [self.red_mistakes, self.blue_mistakes]}
        for panel in mistakes_dict[team]:
            for layout in panel.children:
                for image in layout.children:
                    image.opacity = 0.0
        self.n_mistakes = 0 #TODO sprawdzić to


    def finish_turn(self, command):
        print("finish_turn")
        self.turn += 1
        self.prepare_question()

    ### Methods for final round

    def prepare_final(self, dt=None):
        print("prepare_final")
        self.answers_container.clear_widgets()
        self.sounds["before_final"].play()
        self.final_round_panel.opacity = 1.0
        self.next = self.time_trial
        #TODO


    def final_second_round(self, command):
        print("final_second_round")
        self.sounds["between_final"].play()
        self.finalist = 1
        self.answer_finalist = 0
        self.next = self.same_answer_preview
        #TODO


    def same_answer_preview(self, command):
        print("same_answer_preview")
        self.sounds["repeat_final"].play()
        self.next =  lambda com: self.time_trial(com, second=True)


    def same_answer(self, command):
        print("same_answer")
        self.sounds["repeat_final"].play()


    def time_trial(self, command, second:bool=False):
        print("time_trial")
        self.next = self.same_answer if second else DUMMY_CALLBACK
        time = 20 if second else 15
        def set_timer(t):
            if isinstance(t, str):
                self.timer.text = t
            else:
                self.timer.text = str(t) if t>=10 else "0"+str(t)
        def timer_recursion(t):
            set_timer(t)
            if t>1:
                f = lambda dt: timer_recursion(t-1)
                Clock.schedule_once(f, 1)
        timer_recursion(time)
        def end_timer(dt):
            self.timer.text="00"
            self.sounds["timeup_final"].play()
            self.next = self.type_answer_f
        Clock.schedule_once(end_timer, time)
        f = lambda dt: set_timer(" ")
        Clock.schedule_once(f, time+2)

        
    def type_answer_f(self, command):
        if command == "ENTER":
            self.add_answer_f()
            self.typing_buffer = ""
            self.next = self.type_score_f
        elif command == "BACKSPACE":
            self.typing_buffer = ""
        elif len(self.typing_buffer) < 17:
            self.typing_buffer += command


    def type_score_f(self, command):
        if command == "ENTER":
            self.add_score_f()
            self.typing_buffer = ""
            self.answer_finalist +=1
            if self.answer_finalist == 5:
                if self.finalist == 0: 
                    self.next = self.final_second_round
                elif self.finalist == 1:
                    self.next = self.outro
            else:
                self.next = self.type_answer_f
        elif command == "BACKSPACE":
            self.typing_buffer = ""
        elif len(self.typing_buffer) < 2:
            self.typing_buffer += command

    
    def add_answer_f(self):
        self.final_round_panel.children[1-self.finalist].children[4-self.answer_finalist].children[2].text = self.typing_buffer
        #TODO dodaj dzwonki


    def add_score_f(self):
        self.final_round_panel.children[1-self.finalist].children[4-self.answer_finalist].children[0].text = self.typing_buffer
        if self.typing_buffer in ["00", "0", " 0"]:
            self.sounds["mistake"].play()
        else:
            self.sounds["answer"].play()
        new_score = self.current_score + int(self.typing_buffer)
        self.make_score(new_score)


    def outro(self, command):
        print("outro!")
        if self.current_score >= 200:
            self.add_widget(OutroPreview("GG WP"))
        elif self.current_score < 200:
             self.add_widget(OutroPreview("Wielkie bylo staranie,\na jednak wyszlo zesranie."))
        self.sounds["before_final"].play()
        #TODO



class FamilyadaApp(App):

    title = 'Familyada'

    def build(self):
        self.game_root_widget = GameRootWidget()
        return self.game_root_widget


    def on_start(self):
        self.game_root_widget.gamedata_from_json('test_manual.json')
        # self.switch_fullscreen() #TODO
        return super().on_start()


    def switch_fullscreen(self):
        if Window.fullscreen != "auto":
            Window.fullscreen = "auto"
        elif Window.fullscreen == "auto":
            Window.fullscreen = 0



if __name__ == '__main__':
    FamilyadaApp().run()
    