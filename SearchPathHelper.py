class SearchPathHelper(object):
    def __init__(self, searchPath):
        self.searchPath = searchPath
        self.wasOutput = False

    def outputSearchPath(self):
        if self.searchPath is not None and not self.wasOutput:
            print self.searchPath
            self.wasOutput = True