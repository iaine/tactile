'''
   Handle the tile and mappings
'''
from dao import DAO
from audioplay import Audio
import time


class TileState():
    STOP_RUN = 5*600000
    state = None
    overview = None
    cmd_time = 0

    def __init__(self):
        self.state = False
        self.overview = False
        self.cmd_time = 0

    def handle_tile(self, tile_num):
        '''
           Handles the sensor and audio interface
        '''
        audio = Audio()
        #change the state
        self.state = True
        # if the overview is hit, it sets a lock
        if tile_num == 16: 
            self.overview = True
            self.cmd_time = int(time.time())
            return audio.play(self._get_file_for_tile(tile_num))
        elif tile_num == 13:
            audio.stop()            
        elif int(time.time()) > (self.cmd_time + self.STOP_RUN):
            self.overview = False
            return audio.play(self._get_file_for_tile(tile_num))

    def _get_file_for_tile (self, tile_num):
        '''
           Interface for fetching the file attached to the tile
        '''
        #return the type of MP3 by the tile
        try:
            if tile_num is None:
                raise Exception("No tile given")

            #db = DAO()
            #fname = db.fetch(tile_num)
            fname = ''
            if tile_num == 24:
                return "/home/iain/sonicteatray/teatray/data/Barnacles_01.mp3"
            elif tile_num == 27:
                return "/home/iain/sonicteatray/teatray/data/Prayer_Wheel_01.mp3"
            elif tile_num == 16:
                return "/home/iain/sonicteatray/teatray/data/Chinese_Tea_Brick_01.mp3"
            if fname is None:
                raise Exception("No file returned")
            else:
                return fname
        except Exception,e:
            print(e)
