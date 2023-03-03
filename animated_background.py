import kivy
kivy.require('2.1.0')

from kivy.uix.widget import Widget
from kivy.uix.effectwidget import EffectWidget
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.graphics import *
from kivy.properties import NumericProperty
from kivy.core.window import Window

from random import randint, choice, uniform


N_ORBS = 13
DURATION_RANGE = (30,75)



Builder.load_string('''

#:import uniform random.uniform
#:import ew kivy.uix.effectwidget
#:import Window kivy.core.window.Window
#:set blur_radius min(Window.size)/15
#:set ORB_SIZE 0.78

<AnimatedBackground>:
    # effects: ew.HorizontalBlurEffect(size=blur_radius), ew.VerticalBlurEffect(size=blur_radius), #ew.PixelateEffect(pixel_size=10)

<Orb>:
    pos: uniform(0, Window.width), uniform(0, Window.height)
    canvas:
        Color:
            # rgba: [uniform(0.5,1.0), uniform(0.05,0.4), uniform(0.5,1.0), uniform(0.2,0.6)] #v1
            rgba: [uniform(0.8,1.0), uniform(0.4,0.8), uniform(0.8,1.0), uniform(0.25,0.7)] #v2
        Ellipse:
            pos: self.pos
            size: tuple([min(Window.size)*ORB_SIZE] * 2)
''')


class AnimatedBackground(EffectWidget):
    n_orbs = NumericProperty()
    global N_ORBS, DURATION_RANGE

    def __init__(self, n_orbs=N_ORBS, **kwargs):
        super(AnimatedBackground, self).__init__(**kwargs)
        self.n_orbs = n_orbs
        orbs = [Orb() for _ in range(self.n_orbs)]
        for orb in orbs:
            self.add_widget(orb)
            self.generate_anim(orb)
    

    def generate_anim(self, target, duration_range=DURATION_RANGE):
        xy = choice([(0-target.width, randint(0-target.height,Window.height)), (Window.width, randint(0-target.height,Window.height)), (randint(0-target.width,Window.width), 0-target.height), (randint(0-target.width,Window.width), Window.height)])
        dur = randint(*duration_range)
        anim = Animation(pos=xy, duration=dur)
        anim.bind(on_complete= lambda anim, target: self.generate_anim(target))
        anim.start(target)



class Orb(Widget):

    def __init__(self, **kwargs):
        super(Orb, self).__init__(**kwargs)



class backgroundPreviewApp(App):
    def build(self):
        return AnimatedBackground(n_orbs=10)


if __name__ == "__main__":
    backgroundPreviewApp().run()