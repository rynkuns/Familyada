import kivy
kivy.require('2.1.0')

from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder

from random import randint, choice


Builder.load_string('''

<AnimatedBackground>:

<Orb>:
    canvas:
        Color:
            rgba: [0.8, 0.2, 0.1, 0.9]
        Ellipse:
            pos: self.pos
            size: self.size
''')



class AnimatedBackground(Widget):

    def __init__(self, n_orbs=3, **kwargs):
        super(AnimatedBackground, self).__init__(**kwargs)
        self.n_orbs = n_orbs
        orbs = [Orb() for _ in range(self.n_orbs)]
        for orb in orbs:
            self.add_widget(orb)
            self.generate_anim(orb)

        # anim.bind(on_complete= lambda anim, target: self.generate_anim(target))
        # anim.start(orb)
    

    def generate_anim(self, target, duration_range=(8,15)):
        xy = choice([(0-target.width, randint(0-target.height,self.height)), (self.width, randint(0-target.height,self.height)), (randint(0-target.width,self.width), 0-target.height), (randint(0-target.width,self.width), self.height)])
        dur = randint(*duration_range)
        anim = Animation(pos=xy, duration=dur)
        anim.bind(on_complete= lambda anim, target: self.generate_anim(target))
        anim.start(target)



class Orb(Widget):
    pass



class backgroundPreviewApp(App):
    def build(self):
        return AnimatedBackground(n_orbs=10)


if __name__ == "__main__":
    backgroundPreviewApp().run()