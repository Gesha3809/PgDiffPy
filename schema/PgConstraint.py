import re
from diff.PgDiffUtils import PgDiffUtils

class PgConstraint(object):
    PATTERN_PRIMARY_KEY = re.compile(r".*PRIMARY[\s]+KEY.*", re.I)

    def __init__(self, name):
        self.name = name
        self.definition = None
        self.tableName = None
        self.comment = None

    def __equal(self, other):
        return (self.name == other.name and self.definition == other.definition
                and self.tableName == other.tableName)

    def __eq__(self, other):
        return self.__equal(other)

    def __ne__(self, other):
        return not self.__equal(other)

    def isPrimaryKeyConstraint(self):
        if self.definition:
            return self.PATTERN_PRIMARY_KEY.search(self.definition) is not None
        return False

    def getCreationSQL(self):
        sbSQL = []
        sbSQL.append("ALTER TABLE ")
        sbSQL.append(PgDiffUtils.getQuotedName(self.tableName))
        sbSQL.append("\n\tADD CONSTRAINT ")
        sbSQL.append(PgDiffUtils.getQuotedName(self.name))
        sbSQL.append(' ')
        sbSQL.append(self.definition)
        sbSQL.append(';')

        if (self.comment is not None and len(self.comment) > 0):
            sbSQL.append("\n\nCOMMENT ON CONSTRAINT ")
            sbSQL.append(PgDiffUtils.getQuotedName(self.name))
            sbSQL.append(" ON ")
            sbSQL.append(PgDiffUtils.getQuotedName(self.tableName))
            sbSQL.append(" IS ")
            sbSQL.append(self.comment)
            sbSQL.append(';')

        return ''.join(sbSQL)

    def getDropSQL(self):
        return "ALTER TABLE %s DROP CONSTRAINT %s;" % (PgDiffUtils.getQuotedName(self.tableName),
                PgDiffUtils.getQuotedName(self.name))
