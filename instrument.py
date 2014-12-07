import kivy
kivy.require('1.8.0')

from kivy.app import App
from MTRadialMenu import MTWorkspace

##app
class InstrumentApp(App):
    def build(self):
        root = MTWorkspace(size=(1200,600), style={'bg-color':(0,0,0,150), 
                                'draw-background': True})
        return root

if __name__ == '__main__':
  InstrumentApp().run()