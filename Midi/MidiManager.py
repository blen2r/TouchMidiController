import pygame.midi

class MidiManager:
    def __init__(self):
        pygame.midi.init()
    
    def getMidiDevicesOut(self):
        devices = []
        
        for x in range( 0, pygame.midi.get_count() ):
            d = pygame.midi.get_device_info(x)
            (interf, name, input, output, opened) = d
            if output == 1:
                withId = (x,) + d
                devices.append(withId)
        
        return devices
        
    def __del__(self):
        #close midi out devices
        for x in range( 0, pygame.midi.get_count() ):
            d = pygame.midi.get_device_info(x)
            (interf, name, input, output, opened) = d
            if output == 1:
                pygame.midi.Output(x).close()
        
        pygame.midi.quit()
    
    def sendMidi(self, device, data):
        pygame.midi.Output(device).write(data)
    
    def toggleNote(self, device, note, velocity, channel, noteValue):
        status = 0
        
        if noteValue:
            status = 144 + channel - 1
        else:
            status = 128 + channel - 1
        
        pygame.midi.Output(device).write([[[status, note, velocity], pygame.midi.time()]])
    
    def time(self):
        return pygame.midi.time()