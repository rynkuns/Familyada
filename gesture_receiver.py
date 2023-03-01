from kivy.uix.floatlayout import FloatLayout
from kivy.gesture import Gesture, GestureDatabase

import gestures as gest

#TODO usuń to
from kivy.app import App
from kivy.graphics import Color, Ellipse, Line

import operator


def simplegesture(name, point_list):
    """
    A simple helper function
    """
    g = Gesture()
    g.add_stroke(point_list)
    g.normalize()
    g.name = name
    return g

class GestureReceiver(FloatLayout):

    gesture_threshold = 0.9
    
    def __init__(self, root_widget=None, *args, **kwargs):
        super(GestureReceiver, self).__init__()
        self.gdb = GestureDatabase()
        self.root_widget = root_widget


    def on_touch_down(self, touch):
        # start collecting points in touch.ud
        # create a line to display the points
        userdata = touch.ud
        with self.canvas:
            Color(1, 1, 0)
            d = 10.
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
            userdata['line'] = Line(points=(touch.x, touch.y))
        # return True


    def on_touch_move(self, touch):
        # store points of the touch movement
        try:
            touch.ud['line'].points += [touch.x, touch.y]
            return True
        except (KeyError) as e:
            pass


    def on_touch_up(self, touch):
        # touch is over, display information, and check if it matches some
        # known gesture.
        g = simplegesture('', list(zip(touch.ud['line'].points[::2],
                                       touch.ud['line'].points[1::2])))

        # print match scores between all known gestures
        
        #MÓJ KOD!!!!!!
        scores = []
        for command in gest.gestures_dict:
            for gesture in gest.gestures_dict[command]:
                scores.append((command, g.get_score(gesture)))
        scores = sorted(scores, key=operator.itemgetter(1), reverse=True)
        print(scores[:3])

        if self.root_widget is not "None":
            if scores[0][1] > self.gesture_threshold:
                self.root_widget.current_command = scores[0][0]
                self.root_widget.next(scores[0][0])
            else:
                self.root_widget.current_command = "None"
                

        # erase the lines on the screen, this is a bit quick&dirty, since we can have another touch event on the way...
        self.canvas.clear()




class DemoGesture(App):
    def build(self):
        return GestureReceiver()


if __name__ == '__main__':
    DemoGesture().run()
