class Writer(object):
    def __init__(self):
        self.strings = []

    def __str__(self):
        return ''.join(self.strings)

    def write(self, string):
        self.strings.append(string)

    def writeln(self, string):
        self.strings.append(string)
        self.strings.append("\n")
