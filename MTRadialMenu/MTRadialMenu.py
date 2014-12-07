import kivy
kivy.require('1.8.0')

from kivy.uix.widget import *
from kivy.uix.label import *
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line

import math
from math import sin, cos, radians

##Radial menu
class MTRadialMenu(Widget):
    def __init__(self, **kwargs):
        kwargs.setdefault('radius', 200)
        kwargs.setdefault('options', [])
        kwargs.setdefault('textPadding', 0)
        kwargs.setdefault('bgColor', (0.4,0.4,0.4,1))
        kwargs.setdefault('hiColor', (0.5,0,0,1))
        kwargs.setdefault('linesColor', (0.8,0.8,0.8,1))
        super(MTRadialMenu, self).__init__(**kwargs)
        self.radius = kwargs.get('radius')
        self.idRadMen = kwargs.get('idRadMen')
        self.options = kwargs.get('options')
        self.textPadding = kwargs.get('textPadding')
        self.bgColor = kwargs.get('bgColor')
        self.linesColor = kwargs.get('linesColor')
        self.hiColor = kwargs.get('hiColor')
        
    def on_touch_down(self, touch):
        self.pos = [touch.x, touch.y]
        
        #make sure the menu isn't drawn outside of the window
        if touch.x - self.radius <= 0:
            self.pos[0] = self.radius
        elif touch.x + self.radius >= Window.size[0]:
            self.pos[0] = Window.size[0] - self.radius
            
        if touch.y - self.radius <= 0:
            self.pos[1] = self.radius
        elif touch.y + self.radius >= Window.size[1]:
            self.pos[1] = Window.size[1] - self.radius
        
        self.draw()
            
    def on_touch_up(self, touch):
        if self.idRadMen == touch.id:
            dx = touch.x - self.pos[0]
            dy = touch.y - self.pos[1]
            angle = 0
            radPerSection = 2*math.pi / len(self.options)
            degPerSection = math.degrees(radPerSection)
            
            if dy > 0:
                angle = math.atan(dx/dy)
            elif dy < 0 and dx >= 0:
                angle = math.pi + math.atan(dx/dy)
            elif dy < 0 and dx < 0:
                angle = -math.pi + math.atan(dx/dy)
                
            degAngle = (math.degrees(angle) + 360)%360
            
            seg = int(degAngle / degPerSection)
            
            self.canvas.clear()
            self.remove_radialMenu(touch.id)

            self.parent.spawnApp(self.options[seg], self.pos)
            
            return True
        
        return False
    
    def on_touch_move(self, touch):
        if self.idRadMen == touch.id:
            self.canvas.clear()
            self.draw(touch)
        
        return True
    
    def remove_radialMenu(self, touchId):
        for i in xrange(len(self.parent.children) - 1, -1, -1):
            if isinstance(self.parent.children[i], MTRadialMenu):
                if self.parent.children[i].idRadMen == touchId:
                    del self.parent.children[i]
    
    def draw(self, moveTouch=None):
        with self.canvas:
            Color(*self.bgColor)
            Ellipse(pos=(self.pos[0] - self.radius, self.pos[1] - self.radius), size=(self.radius*2, self.radius*2))
        
        radPerSection = 2*math.pi / len(self.options)
        degPerSection = math.degrees(radPerSection)
        
        #highlight segment if selected
        if moveTouch is not None:
            dx = moveTouch.x - self.pos[0]
            dy = moveTouch.y - self.pos[1]
            angle = 0
            
            if dy > 0:
                angle = math.atan(dx/dy)
            elif dy < 0 and dx >= 0:
                angle = math.pi + math.atan(dx/dy)
            elif dy < 0 and dx < 0:
                angle = -math.pi + math.atan(dx/dy)
                
            degAngle = (math.degrees(angle) + 360)%360
            
            seg = int(degAngle / degPerSection)
            anglestart = seg*degPerSection
            angleend = anglestart + degPerSection
            
            with self.canvas:
                Color(*self.hiColor)
                Ellipse(pos=(self.pos[0] - self.radius, self.pos[1] - self.radius), size=(self.radius*2, self.radius*2), angle_start=anglestart, angle_end=angleend)
        
        #dividing lines and text
        for i in range(0, len(self.options)):
            with self.canvas:
                Color(*self.linesColor)
                Line(points=[self.pos[0], self.pos[1], self.pos[0] + self.radius * sin(i*radPerSection), self.pos[1] + self.radius * cos(i*radPerSection)])
            
            label = Label(size_hint=(None, None))
            label.text = self.options[i]
            label.texture_update()
            label.pos = (self.pos[0] + self.radius * sin(i*radPerSection + 0.5*radPerSection), self.pos[1] + self.radius * cos(i*radPerSection + 0.5*radPerSection))
            
            #hacks for text alignment
            if label.pos[0] > self.pos[0]:
                label.pos[0] = label.pos[0] - 60
                
            if label.pos[1] > self.pos[1]:
                label.pos[1] = label.pos[1] - 20
                
            if label.pos[1] < self.pos[1] and label.pos[0] == self.pos[0]:
                label.pos[0] = label.pos[0] - 35
            
            label.size = label.texture_size[0] + 20, label.texture_size[1] + 20
            self.add_widget(label)
