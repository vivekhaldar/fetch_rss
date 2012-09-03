# Copyright (C) 2012 Vivek Haldar
#
# Generic superclass for outputting RSS data.
#
# Author: Vivek Haldar <vh@vivekhaldar.com>

class Output(object):
    def __init__(self, articles):
        self._articles = articles

    def output(self):
        pass
