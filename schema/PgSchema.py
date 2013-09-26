from helpers.OrderedDict import OrderedDict
from diff.PgDiffUtils import PgDiffUtils

class PgSchema(object):
    def __init__(self, schemaName):
        self.tables = OrderedDict()
        self.indexes = dict()
        self.functions = dict()
        self.sequences = dict()
        self.primaryKeys = dict()
        self.views = dict()
        self.name = schemaName
        self.comment = None
        self.authorization = None

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

    def getCreationSQL(self):
        sbSQL = []
        sbSQL.append("CREATE SCHEMA ")
        sbSQL.append(PgDiffUtils.getQuotedName(self.name))

        if self.authorization is not None:
            sbSQL.append(" AUTHORIZATION ")
            sbSQL.append(PgDiffUtils.getQuotedName(self.authorization))

        sbSQL.append(';')

        if self.comment:
            sbSQL.append("\n\nCOMMENT ON SCHEMA ")
            sbSQL.append(PgDiffUtils.getQuotedName(self.name))
            sbSQL.append(" IS ")
            sbSQL.append(self.comment)
            sbSQL.append(';')

        return ''.join(sbSQL)
