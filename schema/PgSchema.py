class PgSchema(object):
    def __init__(self, schemaName):
        self.tables = dict()
        self.indexes = dict()
        self.functions = dict()
        self.sequences = dict()
        self.primaryKeys = dict()
        self.views = dict()
        self.name = schemaName
        self.comment = None

    def getName(self):
        return self.name

    def addTable(self, table):
        self.tables[table.name] = table

    def getTable(self, tablename):
        return self.tables.get(tablename)

    def addIndex(self, index):
        self.indexes[index.name] = index

    def addFunction(self, function):
        self.functions[function.getSignature()] = function

    def addSequence(self, sequence):
        self.sequences[sequence.name] = sequence

    def addPrimaryKey(self, primaryKey):
        self.primaryKeys[primaryKey.name] = primaryKey

    def addView(self, view):
        self.views[view.name] = view