class PgFunction(object):
    def __init__(self):
        self.name = ''
        self.arguments = dict()

    def addArgument(self, argument):
        self.arguments[argument.name] = argument

class Argument(object):
    def __init__(self):
        self.mode = "IN"
        self.name = ''
        self.dataType = ''
        self.defaultExpression  = ''