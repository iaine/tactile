'''
   Audio handling
'''

import pygame.mixer

class Audio():
    set_time = None
    def __init__(self):
        #self.pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        self.set_time = None

    def play(self, filename):
        '''
           Play a file. 
           @parameter filename
        '''
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            if filename is None or filename == '':
                raise Exception("No file name provided")
            else:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.stop()
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()    
                #while pygame.mixer.music.get_busy():
                #    pygame.time.delay(100)
        except Exception, e:
            print(e)

    def pause(self):
        '''
           Pause the file and set the position if we need to return
        '''
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        pygame.mixer.music.pause()
        self.set_time = pygame.mixer.music.get_pos()

    def stop(self):
        '''
           Stops all play
        '''
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        pygame.mixer.stop()
