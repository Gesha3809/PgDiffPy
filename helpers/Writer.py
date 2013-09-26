class Writer(object):
    def __init__(self):
        self.strings = []

    def __str__(self):
        return ''.join(self.strings)

    def write(self, string):
        self.strings.append(str(string))

    def writeln(self, string):
        self.strings.append(str(string))
        self.strings.append("\n")
        # Add aditional line if this is end of the statement
        if string[-1:]==';':
            self.strings.append("\n")
