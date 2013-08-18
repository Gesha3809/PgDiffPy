from diff.PgDiffUtils import PgDiffUtils

class PgIndex(object):
    def __init__(self, name):
        self.name = name

    def getDropSQL(self):
        return "DROP INDEX %s;" % PgDiffUtils.getQuotedName(self.name)