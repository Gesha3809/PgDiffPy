import re
from diff.PgDiffUtils import PgDiffUtils

class PgConstraint(object):
    PATTERN_PRIMARY_KEY = re.compile(r".*PRIMARY[\s]+KEY.*", re.I)

    def __init__(self, name):
        self.name = name
        self.definition = None
        self.tableName = None

    # used for compare functions
    def _compare(self, other):
        return self.__dict__ == other.__dict__

    def __eq__(self, other):
        return self._compare(other)

    def __ne__(self, other):
        return not self._compare(other)

    def setDefinition(self, definition):
        self.definition = definition

    def isPrimaryKeyConstraint(self):
        return self.PATTERN_PRIMARY_KEY.search(self.definition) is not None

    def getDropSQL(self):
        return "ALTER TABLE %s DROP CONSTRAINT %s;" % (PgDiffUtils.getQuotedName(self.tableName), PgDiffUtils.getQuotedName(self.name))