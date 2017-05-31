from nose.tools import assert_false, assert_true

from audioplay import Audio

import pygame.mixer

def test_play_state():
    a = Audio()
    assert_false(pygame.mixer.get_busy())

def testplay_state_file():
    a = Audio()
    a.play('../examples/DragonBite.wav')

def testplay_state_no_file():
    a = Audio()
    a.play('')
    assert_false(pygame.mixer.get_busy())
