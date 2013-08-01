from diff.PgDiffUtils import PgDiffUtils

class PgTable(object):
    def __init__(self, tableName):
        self.name=tableName
        self.columns=dict()
        self.indexes=dict()
        self.inherits=[]
        self.oids = None
        self.tablespace = ''

    def addColumn(self, column):
        self.columns[column.name] = column

    def addIndex(self, index):
        self.indexes[index.name] = index

    def addInherits(self, tableName):
        self.inherits.append(tableName)

    def getDropSQL(self):
        return "DROP TABLE %s;" % PgDiffUtils.getQuotedName(self.name)