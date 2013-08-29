from diff.PgDiffUtils import PgDiffUtils

class PgTrigger(object):

    EVENT_BEFORE = 'BEFORE'
    EVENT_AFTER = 'AFTER'
    EVENT_INSTEAD_OF = 'INSTEAD OF'

    def __init__(self):
        self.name = None
        self.event = None
        self.onInsert = None
        self.onUpdate = None
        self.onDelete = None
        self.onTruncate = None
        self.tableName = None
        self.forEachRow = None
        self.updateColumns = list()
        self.when = None
        self.function = None
        self.comment = None

    def getCreationSQL(self):
        sbSQL = []
        sbSQL.append("CREATE TRIGGER ")
        sbSQL.append(PgDiffUtils.getQuotedName(self.name))
        sbSQL.append("\n\t")
        sbSQL.append(self.event)

        firstEvent = True

        if self.onInsert:
            sbSQL.append(" INSERT")
            firstEvent = False

        if self.onUpdate:
            if firstEvent:
                firstEvent = False
            else:
                sbSQL.append(" OR")

            sbSQL.append(" UPDATE")

            if len(self.updateColumns) > 0:
                sbSQL.append(" OF ")

                sbSQL.append(', '.join(self.updateColumns))

        if self.onDelete:
            if not firstEvent:
                sbSQL.append(" OR")

            sbSQL.append(" DELETE")

        if self.onTruncate:
            if not firstEvent:
                sbSQL.append(" OR")

            sbSQL.append(" TRUNCATE")

        sbSQL.append(" ON ")
        sbSQL.append(PgDiffUtils.getQuotedName(self.tableName))
        sbSQL.append("\n\tFOR EACH ")
        sbSQL.append("ROW" if self.forEachRow else "STATEMENT")

        if (self.when is not None and len(self.when) > 0):
            sbSQL.append("\n\tWHEN (")
            sbSQL.append(self.when)
            sbSQL.append(')')

        sbSQL.append("\n\tEXECUTE PROCEDURE ")
        sbSQL.append(self.function)
        sbSQL.append(';')

        if (self.comment is not None and len(self.comment) > 0):
            sbSQL.append("\n\nCOMMENT ON TRIGGER ")
            sbSQL.append(PgDiffUtils.getQuotedName(self.name))
            sbSQL.append(" ON ")
            sbSQL.append(PgDiffUtils.getQuotedName(self.tableName))
            sbSQL.append(" IS ")
            sbSQL.append(self.comment)
            sbSQL.append(';')

        return ''.join(sbSQL)

    def getDropSQL(self):
        return "DROP TRIGGER %s ON %s;\n" % (PgDiffUtils.getQuotedName(self.name), PgDiffUtils.getQuotedName(self.tableName))