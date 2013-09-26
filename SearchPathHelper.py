class SearchPathHelper(object):
    def __init__(self, searchPath):
        self.searchPath = searchPath
        self.wasOutput = False

    def outputSearchPath(self, writer):
        if self.searchPath is not None and not self.wasOutput:
            writer.writeln(self.searchPath)
            self.wasOutput = True