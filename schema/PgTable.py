from diff.PgDiffUtils import PgDiffUtils

class PgTable(object):
    def __init__(self, tableName):
        self.name=tableName
        self.columns=dict()
        self.indexes=dict()
        self.constraints=dict()
        self.triggers=dict()
        self.inherits=[]
        self.oids = None
        self.tablespace = ''
        self.comment = None
        clusterIndexName = None

    def addColumn(self, column):
        self.columns[column.name] = column

    def addIndex(self, index):
        self.indexes[index.name] = index

    def addInherits(self, tableName):
        self.inherits.append(tableName)

    def addConstraint(self, constraint):
        self.constraints[constraint.name] = constraint

    def addTrigger(self, trigger):
        self.triggers[trigger.name] = trigger

    def getCreationSQL(self):
        sbSQL = []
        sbSQL.append("CREATE TABLE ")
        sbSQL.append(PgDiffUtils.getQuotedName(self.name))
        sbSQL.append(" (\n")

        first = True

        if len(self.columns) == 0:
            sbSQL.append(')')
        else:
            for columnName in self.columns:
                if first:
                    first = False
                else:
                    sbSQL.append(",\n")

                sbSQL.append("\t")
                sbSQL.append(self.columns[columnName].getFullDefinition(False))

            sbSQL.append("\n)")

        if (self.inherits is not None and len(self.inherits) > 0):
            sbSQL.append("\nINHERITS (")

            first = True

            for tableName in self.inherits:
                if first:
                    first = False
                else:
                    sbSQL.append(", ")

                sbSQL.append(tableName)

            sbSQL.append(")")

        if (self.oids is not None and len(self.oids) > 0):
            sbSQL.append("\n")

            if ("OIDS=false" == self.oids):
                sbSQL.append("WITHOUT OIDS")
            else:
                sbSQL.append("WITH ")

                if ("OIDS" == self.oids or "OIDS=true" == self.oids):
                    sbSQL.append("OIDS")
                else:
                    sbSQL.append(self.oids)

        if (self.tablespace is not None and len(self.tablespace) > 0):
            sbSQL.append("\nTABLESPACE ")
            sbSQL.append(tablespace)

        sbSQL.append(';')

        for column in self.getColumnsWithStatistics():
            sbSQL.append("\nALTER TABLE ONLY ")
            sbSQL.append(PgDiffUtils.getQuotedName(self.name))
            sbSQL.append(" ALTER COLUMN ")
            sbSQL.append(PgDiffUtils.getQuotedName(column.name))
            sbSQL.append(" SET STATISTICS ")
            sbSQL.append(column.statistics)
            sbSQL.append(';')

        if (self.comment is not None and len(self.comment)>0):
            sbSQL.append("\n\nCOMMENT ON TABLE ")
            sbSQL.append(PgDiffUtils.getQuotedName(self.name))
            sbSQL.append(" IS ")
            sbSQL.append(self.comment)
            sbSQL.append(';')

        for columnName in self.columns:
            column = self.columns[columnName]
            if (column.comment is not None and len(column.comment) > 0):
                sbSQL.append("\n\nCOMMENT ON COLUMN ")
                sbSQL.append(PgDiffUtils.getQuotedName(self.name))
                sbSQL.append('.')
                sbSQL.append(PgDiffUtils.getQuotedName(column.name))
                sbSQL.append(" IS ")
                sbSQL.append(column.getComment())
                sbSQL.append(';')

        return ''.join(sbSQL)

    def getDropSQL(self):
        return "DROP TABLE %s;\n" % PgDiffUtils.getQuotedName(self.name)

    def getColumnsWithStatistics(self):
        return [column for columnName, column in self.columns.items() if column.statistics is not None]
