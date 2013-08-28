from diff.PgDiffUtils import PgDiffUtils

class PgView(object):
    def __init__(self, name):
        self.name = name
        self.comment = None
        self.columnNames = None
        self.defaultValues = dict()
        self.triggers=dict()
        self.columnComments = dict()
        self.query = None

    def __cmp__(self, other):
        if set(self.columnNames) != set(other.columnNames):
            return 1

        if self.query.strip() != other.query.strip():
            return 1

        return 0

    def getCreationSQL(self):
        sbSQL = []
        sbSQL.append("CREATE VIEW ")
        sbSQL.append(PgDiffUtils.getQuotedName(self.name))

        if (self.columnNames is not None and len(self.columnNames) > 0):
            sbSQL.append(" (")

            sbSQL.append(','.join([PgDiffUtils.getQuotedName(columnName) for columnName in self.columnNames]))
            # for (int i = 0; i < columnNames.size(); i++) {
            #     if (i > 0) {
            #         sbSQL.append(", ");
            #     }

            #     sbSQL.append(PgDiffUtils.getQuotedName(columnNames.get(i)));
            # }
            sbSQL.append(')')

        sbSQL.append(" AS\n\t")
        sbSQL.append(self.query)
        sbSQL.append(';')

        for defaultValue in self.defaultValues:
            sbSQL.append("\n\nALTER VIEW ")
            sbSQL.append(PgDiffUtils.getQuotedName(self.name))
            sbSQL.append(" ALTER COLUMN ")
            sbSQL.append(PgDiffUtils.getQuotedName(defaultValue.columnName))
            sbSQL.append(" SET DEFAULT ")
            sbSQL.append(defaultValue.defaultValue)
            sbSQL.append(';')

        if self.comment:
            sbSQL.append("\n\nCOMMENT ON VIEW ")
            sbSQL.append(PgDiffUtils.getQuotedName(self.name))
            sbSQL.append(" IS ")
            sbSQL.append(self.comment)
            sbSQL.append(';')

        for columnComment in self.columnComments:
            if columnComment.comment:
                sbSQL.append("\n\nCOMMENT ON COLUMN ")
                sbSQL.append(PgDiffUtils.getQuotedName(columnComment.columnName))
                sbSQL.append(" IS ")
                sbSQL.append(columnComment.getComment())
                sbSQL.append(';')

        return ''.join(sbSQL)

    def getDropSQL(self):
        return "DROP VIEW %s;" % PgDiffUtils.getQuotedName(self.name)

    def removeColumnDefaultValue(self, columnName):
        self.defaultValues.pop(columnName, None)

    def addColumnComment(self, columnName, comment):
        self.removeColumnDefaultValue(columnName)
        self.columnComments[columnName] = comment
