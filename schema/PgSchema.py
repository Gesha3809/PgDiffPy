class PgSchema(object):
    def __init__(self, schemaName):
        self.tables = dict()
        self.indexes = dict()
        self.functions = dict()
        self.name = schemaName
        self.comment = None

    def getName(self):
        return self.name

    def addTable(self, table):
        self.tables[table.name] = table

    def getTable(self, tablename):
        return self.tables[tablename]

    def addIndex(self, index):
        self.indexes[index.name] = index

    def addFunction(self, function):
        self.functions[function.name] = function