from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button

class Menu_PlayState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)


    #Main methods

    def update(self, dt, events):
        cursor = cursors.normal

        utils.set_cursor(cursor=cursor)


    def render(self, canvas):
        pass