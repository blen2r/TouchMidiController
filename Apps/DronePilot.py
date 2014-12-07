import kivy
kivy.require('1.8.0')

from kivy.uix.widget import *
from kivy.uix.label import *
from kivy.uix.button import *
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle, Line

##DronePilot
##Blue = note on, gray = note off
class DronePilot(Widget):
    def __init__(self, **kwargs):
        super(DronePilot, self).__init__(**kwargs)
        
        self.midiManager = kwargs.get('midiManager')
        self.workspace = kwargs.get('workspace')
        
        self.touchCount = 0
        self.mode = "setup"
        self.firstSetup = True
        
        self.midiDevicesOut = self.midiManager.getMidiDevicesOut()
        
        self.midiDevicesOutNames = []
        for dev in self.midiDevicesOut:
            self.midiDevicesOutNames.append(dev[2])
        
        strChans = []
        for i in range(1, 17):
            strChans.append(str(i))

        strCC = ["Pitch Bend", "Note"]
        for i in range(0, 128):
            strCC.append(str(i))
        
        #pitch bend = 9999
        #note = 9998
        #velocity = 9997
        self.horizCC = 1
        self.vertCC = 1
        self.midiChannel = 1
        self.midiDevice=self.midiDevicesOut[0]
        self.noteOn = False
        self.horizPrev = -1
        self.vertPrev = -1
        
        self.touchCount = 0
        
        self.spinDevice = Spinner(text=str(self.midiDevicesOutNames[0]), values=self.midiDevicesOutNames)
        self.spinChannel = Spinner(text=str(self.midiChannel), values=strChans)
        self.spinHorizCC = Spinner(text=strCC[0], values=strCC)
        strCC.remove("Note")
        strCC[1:1] = ["Note velocity"]
        self.spinVertCC = Spinner(text=strCC[0], values=strCC)
        
        labelSize = 0.4
        self.okBtn = Button(text='Ok', size_hint_x=labelSize)
        self.okBtn.bind(on_press=self.ok_pressed)
        self.cancelBtn = Button(text='Cancel', on_press=self.cancel_pressed)
        
        self.gridLayout = GridLayout(cols=2, pos=self.pos, size=self.size)
        self.gridLayout.add_widget(Label(text='MIDI Device:', size_hint_x=labelSize))
        self.gridLayout.add_widget(self.spinDevice)
        self.gridLayout.add_widget(Label(text='Channel:', size_hint_x=labelSize))
        self.gridLayout.add_widget(self.spinChannel)
        self.gridLayout.add_widget(Label(text='Horiz. CC:', size_hint_x=labelSize))
        self.gridLayout.add_widget(self.spinHorizCC)
        self.gridLayout.add_widget(Label(text='Vert. CC:', size_hint_x=labelSize))
        self.gridLayout.add_widget(self.spinVertCC)
        self.gridLayout.add_widget(self.okBtn)
        self.gridLayout.add_widget(self.cancelBtn)
        
        self.crossX = self.pos[0] + self.size[0]/2
        self.crossY = self.pos[1] + self.size[1]/2
        
        self.update_graphics()
        self.bind(pos=self.update_graphics,
            size=self.update_graphics)
            
    def update_graphics(self, *largs):
        self.canvas.clear()
        
        if self.mode == "play":
            with self.canvas:
                if self.noteOn:
                    Color(0, 0, 0.3)
                else:
                    Color(0.1, 0.1, 0.1)
                
                Rectangle(size=self.size, pos=self.pos)
                
                Color(1, 1, 1)
                Line(points=[self.crossX, self.pos[1], self.crossX, self.pos[1] + self.size[1]])
                Line(points=[self.pos[0], self.crossY, self.pos[0] + self.size[0], self.crossY])
        else: #setup mode
            with self.canvas:
                Color(0.1, 0.1, 0.1)
                Rectangle(size=self.size, pos=self.pos)
                self.add_widget(self.gridLayout)
    
    def ok_pressed(self, instance):
        self.firstSetup = False
        self.mode = "play"
        
        #saves the selected settings
        if self.spinHorizCC.text == "Pitch Bend":
            self.horizCC = 9999
        elif self.spinHorizCC.text == "Note":
            self.horizCC = 9998
        elif self.spinHorizCC.text == "Note velocity":
            self.horizCC = 9997
        else:
            self.horizCC = int(self.spinHorizCC.text)
            
        if self.spinVertCC.text == "Pitch Bend":
            self.vertCC = 9999
        elif self.spinVertCC.text == "Note":
            self.vertCC = 9998
        elif self.spinVertCC.text == "Note velocity":
            self.vertCC = 9997
        else:
            self.vertCC = int(self.spinVertCC.text)
        
        self.midiChannel = int(self.spinChannel.text)
        
        for dev in self.midiDevicesOut:
            if dev[2] == self.spinDevice.text:
                self.midiDevice=dev
        
        self.remove_widget(self.gridLayout)
        self.update_graphics()
        
    def cancel_pressed(self, instance):
        if self.firstSetup:
            return
        
        self.mode = "play"
        self.remove_widget(self.gridLayout)
        self.update_graphics()
    
    def on_touch_down(self, touch):
        if super(DronePilot, self).on_touch_down(touch):
            return True
            
        if self.collide_point(touch.x, touch.y):
            if self.mode == "play":
                self.workspace.down(touch.id, self)
                if self.touchCount == 2:
                    self.noteOn = not self.noteOn
                    self.update_graphics()
                    
                    #if one of the axis is a note msg, send the appropriate midi msg
                    if self.horizCC == 9998:
                        horizVal = int((self.crossX - self.pos[0])/self.size[0] * 127)
                        
                        velo = 127
                        if self.vertCC == 9997:
                            velo = int((self.crossY - self.pos[1])/self.size[1] * 127)
                            
                        self.midiManager.toggleNote(self.midiDevice[0], horizVal, velo, self.midiChannel, self.noteOn)
            
            return True
        
        return False
    
    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.workspace.up(touch.id)
            return True
        
        return False
    
    def on_touch_move(self, touch):
        if super(DronePilot, self).on_touch_move(touch):
            return True
        
        if self.mode == "setup":
            return True
            
        if self.collide_point(touch.x, touch.y):
            self.crossX = touch.x
            self.crossY = touch.y
            if self.gridLayout.parent is None:
                self.update_graphics()
            
            horizVal = int((self.crossX - self.pos[0])/self.size[0] * 127)
            vertVal = int((self.crossY - self.pos[1])/self.size[1] * 127)
            
            horizMsg = None
            vertMsg = None
            
            #note
            if self.horizCC == 9998:
                velo = 127
                if self.vertCC == 9997:
                    velo = vertVal
                    
                if self.horizPrev != horizVal and self.noteOn:
                    self.midiManager.toggleNote(self.midiDevice[0], horizVal, velo, self.midiChannel, self.noteOn)
                
                #turn off previous note
                if self.horizPrev != -1 and self.horizPrev != horizVal and self.noteOn:
                    self.midiManager.toggleNote(self.midiDevice[0], self.horizPrev, velo, self.midiChannel, False)
           
           #pitch bend
            if self.horizCC == 9999:
                statusHoriz = 224 + self.midiChannel-1
                horizMsg = [[statusHoriz, 64, horizVal], self.midiManager.time()]
            else:
                statusHoriz = 176 + self.midiChannel-1
                horizMsg = [[statusHoriz, self.horizCC, horizVal], self.midiManager.time()]
                
            #pitch bend
            if self.vertCC == 9999:
                statusVert = 224 + self.midiChannel-1
                vertMsg = [[statusVert, 64, vertVal], self.midiManager.time()]
            else:
                statusVert = 176 + self.midiChannel-1
                vertMsg = [[statusVert, self.vertCC, vertVal], self.midiManager.time()]
            
            if horizMsg is None and vertMsg is not None:
                self.midiManager.sendMidi(self.midiDevice[0], [vertMsg])
            if horizMsg is not None and vertMsg is None:
                self.midiManager.sendMidi(self.midiDevice[0], [horizMsg])
            if horizMsg is not None and vertMsg is not None:
                self.midiManager.sendMidi(self.midiDevice[0], [horizMsg, vertMsg])
            
            self.horizPrev = horizVal
            self.vertPrev = vertVal
            