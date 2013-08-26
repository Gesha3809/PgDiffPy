from diff.PgDiffUtils import PgDiffUtils

class PgIndex(object):
    def __init__(self, name):
        self.name = name
        self.unique = False
        self.tableName = None
        self.definition = None
        self.comment = None

    def __eq__(self, other):
        return self._equals(other)

    def __ne__(self, other):
        return not self._equals(other)

    def _equals(self, other):
        return self.__dict__ == other.__dict__

    def getCreationSQL(self):
        sbSQL = []
        sbSQL.append("CREATE ")

        if self.unique:
            sbSQL.append("UNIQUE ")

        sbSQL.append("INDEX ")
        sbSQL.append(PgDiffUtils.getQuotedName(self.name))
        sbSQL.append(" ON ")
        sbSQL.append(PgDiffUtils.getQuotedName(self.tableName))
        sbSQL.append(' ')
        sbSQL.append(self.definition)
        sbSQL.append(';')

        if (self.comment is not None and len(self.comment) > 0):
            sbSQL.append("\n\nCOMMENT ON INDEX ")
            sbSQL.append(PgDiffUtils.getQuotedName(self.name))
            sbSQL.append(" IS ")
            sbSQL.append(self.comment)
            sbSQL.append(';')

        return ''.join(sbSQL)


    def getDropSQL(self):
        return "DROP INDEX %s;" % PgDiffUtils.getQuotedName(self.name)