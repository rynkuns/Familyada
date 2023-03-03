import kivy
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.core.window import Window


class KeyboardReceiver(FloatLayout):

    game_root = ObjectProperty(None)

    def __init__(self, root_widget=None, **kwargs):
        super(KeyboardReceiver, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        # if self._keyboard.widget:
        #     # If it exists, this widget is a VKeyboard object which you can use
        #     # to change the keyboard layout.
        #     pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.game_root = root_widget


    def _keyboard_closed(self):
        print('_keyboard_closed')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None


    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        self.game_root.next(keycode[1].upper())

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True



if __name__ == '__main__':
    from kivy.base import runTouchApp
    runTouchApp(KeyboardReceiver())