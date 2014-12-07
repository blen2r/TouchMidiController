import kivy
kivy.require('1.8.0')

from kivy.uix.widget import *
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Line

from MTRadialMenu import MTRadialMenu
from Midi import *

from Apps import *

##workspace
class MTWorkspace(Widget):
    def __init__(self, **kwargs):
        super(MTWorkspace, self).__init__(**kwargs)
        self.options = ["Grid", "Strings", "Bubbles", "Drone Pilot", "Cancel"]
        self.floatLayout = FloatLayout(size=Window.size)
        self.add_widget(self.floatLayout)
        
        self.gridHorizSpacing = 300
        self.gridVertSpacing = 300
        
        self.midiManager = MidiManager()
        
        self.touches = {} #used to track touches to fix bug where up events would not be sent to the right source app
        
        self.update_graphics()
        self.bind(pos=self.update_graphics,
            size=self.update_graphics)
    
    def update_graphics(self, *largs):
        nbrOfVertLines = Window.size[0] / self.gridHorizSpacing
        nbrOfHorizLines = Window.size[1] / self.gridVertSpacing
        
        #self.canvas.clear()
        with self.canvas:
            Color(0.3, 0.3, 0.3)
            
            for i in range(1, nbrOfVertLines+1):
                Line(points=[i*self.gridHorizSpacing, 0, i*self.gridHorizSpacing, Window.size[1]])
            
            for i in range(1, nbrOfHorizLines+1):
                Line(points=[0, i*self.gridVertSpacing, Window.size[0], i*self.gridVertSpacing])
        
    def on_touch_down(self, touch):
        if super(MTWorkspace, self).on_touch_down(touch):
            return True
        
        radmenu = MTRadialMenu(idRadMen=touch.id, options=self.options)
        self.add_widget(radmenu)
        super(MTWorkspace, self).on_touch_down(touch)
        return True
        
    def on_touch_up(self, touch):
        if super(MTWorkspace, self).on_touch_up(touch):
            return True
        
        #manage up events in order to catch events that are no longer on their original app
        self.up(touch.id)
        
        return True
    
    def on_touch_move(self, touch):
        super(MTWorkspace, self).on_touch_move(touch)
        return True
    
    def getClosestGridPos(self, touchPos):
        return (self.gridHorizSpacing*int(touchPos[0]/self.gridHorizSpacing), self.gridVertSpacing*int(touchPos[1]/self.gridVertSpacing))
    
    def spawnApp(self, optionName, touchPos):
        if optionName == "Drone Pilot":
            pilot = DronePilot(pos=self.getClosestGridPos(touchPos), size_hint=(self.gridHorizSpacing/Window.size[0], self.gridVertSpacing/Window.size[1]),
                size=(self.gridHorizSpacing, self.gridVertSpacing), midiManager=self.midiManager, workspace=self)
            self.floatLayout.add_widget(pilot)
        elif optionName == "Cancel":
            pass
        else:
            print "Pas encore code!"
    
    def down(self, touchId, sourceApp):
        if touchId in self.touches:
            #print "Error! Touch already tracked in workspace!"
            return
            
        self.touches[touchId] = sourceApp
        sourceApp.touchCount += 1
    
    def up(self, touchId):
        if touchId not in self.touches:
            #print "Error! Touch not tracked in workspace!"
            return
        
        self.touches[touchId].touchCount -= 1
        del self.touches[touchId]