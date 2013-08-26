from diff.PgDiffUtils import PgDiffUtils

class PgSequence(object):
    def __init__(self, name):
        self.name = name
        self.startWith = None
        self.increment = None
        self.maxValue = None
        self.minValue = None
        self.cache = None
        self.cycle = False
        self.comment =None
        self.ownedBy = None

    def getDropSQL(self):
        return "DROP SEQUENCE %s;" % PgDiffUtils.getQuotedName(self.name)

    def getCreationSQL(self):
        sbSQL = []
        sbSQL.append("CREATE SEQUENCE ")
        sbSQL.append(PgDiffUtils.getQuotedName(self.name))

        if self.startWith is not None:
            sbSQL.append("\n\tSTART WITH ")
            sbSQL.append(self.startWith)

        if self.increment is not None:
            sbSQL.append("\n\tINCREMENT BY ")
            sbSQL.append(self.increment)

        sbSQL.append("\n\t")

        if self.maxValue is None:
            sbSQL.append("NO MAXVALUE")
        else:
            sbSQL.append("MAXVALUE ")
            sbSQL.append(self.maxValue)

        sbSQL.append("\n\t")

        if self.minValue is None:
            sbSQL.append("NO MINVALUE")
        else:
            sbSQL.append("MINVALUE ")
            sbSQL.append(self.minValue)

        if self.cache is not None:
            sbSQL.append("\n\tCACHE ")
            sbSQL.append(self.cache)

        if self.cycle:
            sbSQL.append("\n\tCYCLE")

        sbSQL.append(';')

        if (self.comment is not None and comment != ""):
            sbSQL.append("\n\nCOMMENT ON SEQUENCE ")
            sbSQL.append(PgDiffUtils.getQuotedName(self.name))
            sbSQL.append(" IS ")
            sbSQL.append(self.comment)
            sbSQL.append(';')

        return ''.join(sbSQL)