from PgDiffUtils import PgDiffUtils
from schema.PgColumn import PgColumnUtils

class PgDiffTables(object):

    @staticmethod
    def createTables(writer, oldSchema, newSchema, searchPathHelper):
        for tableName in newSchema.tables:
            if (oldSchema is None or tableName not in oldSchema.tables):
                searchPathHelper.outputSearchPath(writer)
                writer.writeln(newSchema.tables[tableName].getCreationSQL())

    @staticmethod
    def dropTables(writer, oldSchema, newSchema, searchPathHelper):
        if oldSchema is None:
            return

        for tableName in oldSchema.tables:
            if tableName not in newSchema.tables:
                searchPathHelper.outputSearchPath(writer)
                writer.writeln(oldSchema.tables[tableName].getDropSQL())


    @staticmethod
    def alterTables(writer, arguments, oldSchema, newSchema, searchPathHelper):
        for newTablename in newSchema.tables:
            if oldSchema is None or newTablename not in oldSchema.tables:
                continue

            oldTable = oldSchema.tables[newTablename]
            newTable = newSchema.tables[newTablename]

            PgDiffTables.updateTableColumns(writer, arguments, oldTable, newTable, searchPathHelper)
            PgDiffTables.checkWithOIDS(writer, oldTable, newTable, searchPathHelper)
            PgDiffTables.checkInherits(writer, oldTable, newTable, searchPathHelper)
            PgDiffTables.checkTablespace(writer, oldTable, newTable, searchPathHelper)
            PgDiffTables.addAlterStatistics(writer, oldTable, newTable, searchPathHelper)
            PgDiffTables.addAlterStorage(writer, oldTable, newTable, searchPathHelper)
            PgDiffTables.alterComments(writer, oldTable, newTable, searchPathHelper)

    @staticmethod
    def updateTableColumns(writer, arguments, oldTable, newTable, searchPathHelper):
        statements = []
        dropDefaultsColumns = []

        PgDiffTables.addDropTableColumns(statements, oldTable, newTable)
        PgDiffTables.addCreateTableColumns(statements, arguments, oldTable, newTable, dropDefaultsColumns)
        PgDiffTables.addModifyTableColumns(statements, arguments, oldTable, newTable, dropDefaultsColumns)

        if len(statements):
            quotedTableName = PgDiffUtils.getQuotedName(newTable.name)
            searchPathHelper.outputSearchPath(writer)
            writer.write("ALTER TABLE ")
            writer.writeln(quotedTableName)
            writer.write(",\n".join(statements))
            writer.writeln(";")

            # Still test needed
            if len(dropDefaultsColumns):
                writer.write("ALTER TABLE ")
                writer.writeln(quotedTableName)

                _printStatements = []
                for dropDefaultsColumn in dropDefaultsColumns:
                    _printStatements.append("\tALTER COLUMN %s DROP DEFAULT" % PgDiffUtils.getQuotedName(dropDefaultsColumn.name))

                writer.write(",\n".join(_printStatements))
                writer.writeln(";")

    @staticmethod
    def checkWithOIDS(writer, oldTable, newTable, searchPathHelper):
        if (oldTable.oids is None and newTable.oids is None
                or oldTable.oids is not None
                and oldTable.oids == newTable.oids):
            return

        searchPathHelper.outputSearchPath(writer)
        writer.write("ALTER TABLE ")
        writer.writeln(PgDiffUtils.getQuotedName(newTable.name))

        if newTable.oids in (None, "OIDS=false"):
            writer.write("\tSET WITHOUT OIDS;")
        elif newTable.oids in ("OIDS", "OIDS=true"):
            writer.write("\tSET WITH OIDS;")
        else:
            writer.write("\tSET ")
            writer.write(newTable.oids)
            writer.writeln(";")

    @staticmethod
    def checkInherits(writer, oldTable, newTable, searchPathHelper):

        for oldTableName in oldTable.inherits:
            if oldTableName not in newTable.inherits:
                searchPathHelper.outputSearchPath(writer)
                writer.write("ALTER TABLE ")
                writer.writeln(PgDiffUtils.getQuotedName(newTable.name))
                writer.write("\tNO INHERIT ")
                writer.write(PgDiffUtils.getQuotedName(oldTableName))
                writer.writeln(";")

        for newTableName in newTable.inherits:
            if newTableName not in oldTable.inherits:
                searchPathHelper.outputSearchPath(writer)
                writer.write("ALTER TABLE ")
                writer.writeln(PgDiffUtils.getQuotedName(newTable.name))
                writer.write("\tINHERIT ")
                writer.write(PgDiffUtils.getQuotedName(newTableName))
                writer.writeln(";")

    @staticmethod
    def checkTablespace(writer, oldTable, newTable, searchPathHelper):
        if (oldTable.tablespace is None and newTable.tablespace is None
                or oldTable.tablespace is not None
                and oldTable.tablespace == newTable.tablespace):
            return

        searchPathHelper.outputSearchPath(writer)
        writer.write("ALTER TABLE ")
        writer.writeln(PgDiffUtils.getQuotedName(newTable.name))
        writer.write("\tTABLESPACE ")
        writer.write(newTable.tablespace)
        writer.writeln(";")

    @staticmethod
    def addAlterStatistics(writer, oldTable, newTable, searchPathHelper):
        # final Map<String, Integer> stats = new HashMap<String, Integer>();
        stats = dict()

        for newColumnName in newTable.columns:
            newColumn = newTable.columns[newColumnName]
            oldColumn = oldTable.columns.get(newColumnName)

            if oldColumn:
                oldStat = oldColumn.statistics
                newStat = newColumn.statistics
                newStatValue = None

                if newStat is not None and (oldStat is None
                        or newStat != oldStat):
                    newStatValue = newStat
                elif (oldStat is not None and newStat is None):
                    newStatValue = -1

                if (newStatValue is not None):
                    stats[newColumn.name] = newStatValue

        for columnName in stats:
            searchPathHelper.outputSearchPath(writer)
            writer.write("ALTER TABLE ONLY ")
            writer.write(PgDiffUtils.getQuotedName(newTable.name))
            writer.write(" ALTER COLUMN ")
            writer.write(PgDiffUtils.getQuotedName(columnName))
            writer.write(" SET STATISTICS ")
            writer.write(stats[columnName])
            writer.write(";")

    @staticmethod
    def addAlterStorage(writer, oldTable, newTable, searchPathHelper):
        for newColumnName in newTable.columns:
            newColumn = newTable.columns[newColumnName]
            oldColumn = oldTable.columns.get(newColumnName)

            oldStorage = None if (oldColumn is None
                    or oldColumn.storage is None
                    or oldColumn.storage == '') else oldColumn.storage
            newStorage = None if (newColumn.storage is None
                    or newColumn.storage == '') else newColumn.storage

            if (newStorage is None and oldStorage is not None):
                searchPathHelper.outputSearchPath(writer)
                writer.write("WARNING: Column ")
                writer.write(newTable.name)
                writer.write(".")
                writer.write(newColumn.name)
                writer.writeln(" in new table has no STORAGE set but in old table storage was set. Unable to determine STORAGE type.")
                continue

            if (newStorage is None or newStorage == oldStorage):
                continue

            searchPathHelper.outputSearchPath(writer)
            writer.write("ALTER TABLE ONLY ")
            writer.write(PgDiffUtils.getQuotedName(newTable.name))
            writer.write(" ALTER COLUMN ")
            writer.write(PgDiffUtils.getQuotedName(newColumn.name))
            writer.write(" SET STORAGE ")
            writer.write(newStorage)
            writer.write(";")

    @staticmethod
    def alterComments(writer, oldTable, newTable, searchPathHelper):
        if (oldTable.comment is None
                and newTable.comment is not None
                or oldTable.comment is not None
                and newTable.comment is not None
                and oldTable.comment != newTable.comment):
            searchPathHelper.outputSearchPath(writer)
            writer.write("COMMENT ON TABLE ")
            writer.write(PgDiffUtils.getQuotedName(newTable.name))
            writer.write(" IS ")
            writer.write(newTable.comment)
            writer.writeln(";")

        elif (oldTable.comment is not None and newTable.comment is None):
            searchPathHelper.outputSearchPath(writer)
            writer.write("COMMENT ON TABLE ")
            writer.write(PgDiffUtils.getQuotedName(newTable.name))
            writer.writeln(" IS NULL;")

        for newColumnName in newTable.columns:
            newColumn = newTable.columns[newColumnName]
            oldColumn = oldTable.columns.get(newColumnName)

            oldComment = None if oldColumn is None else oldColumn.comment
            newComment = newColumn.comment

            if (newComment is not None and (newComment is not None if oldComment is None else oldComment != newComment)):
                searchPathHelper.outputSearchPath(writer)
                writer.write("COMMENT ON COLUMN ")
                writer.write(PgDiffUtils.getQuotedName(newTable.name))
                writer.write(".")
                writer.write(PgDiffUtils.getQuotedName(newColumn.name))
                writer.write(" IS ")
                writer.write(newColumn.comment)
                writer.writeln(";")
            elif (oldComment is not None and newComment is None):
                searchPathHelper.outputSearchPath(writer)
                searchPathHelper.outputSearchPath(writer)
                writer.write("COMMENT ON COLUMN ")
                writer.write(PgDiffUtils.getQuotedName(newTable.name))
                writer.write(".")
                writer.write(PgDiffUtils.getQuotedName(newColumn.name))
                writer.writeln(" IS NULL;")

    @staticmethod
    def addDropTableColumns(statements, oldTable, newTable):
        for oldColumnName in oldTable.columns:
            if oldColumnName not in newTable.columns:
                statements.append("\tDROP COLUMN %s" % PgDiffUtils.getQuotedName(oldColumnName))

    @staticmethod
    def addCreateTableColumns(statements, arguments, oldTable, newTable, dropDefaultsColumns):
        for newColumnName in newTable.columns:
            if newColumnName not in oldTable.columns:
                statements.append("\tADD COLUMN %s" % newTable.columns[newColumnName].getFullDefinition(arguments.addDefaults))

                newColumn = newTable.columns[newColumnName]
                if (arguments.addDefaults and not newColumn.nullValue
                        and (newColumn.defaultValue is None or newColumn.defaultValue == '')):
                    dropDefaultsColumns.append(newColumn)

    @staticmethod
    def addModifyTableColumns(statements, arguments, oldTable, newTable, dropDefaultsColumns):
        for newColumnName in newTable.columns:
            if newColumnName not in oldTable.columns:
                continue

            oldColumn = oldTable.columns[newColumnName]
            newColumn = newTable.columns[newColumnName]

            if newColumn.type != oldColumn.type:
                statements.append("\tALTER COLUMN %s TYPE %s /* TYPE change - table: %s original: %s new: %s */" %
                    (PgDiffUtils.getQuotedName(newColumnName), newColumn.type, newTable.name, oldColumn.type, newColumn.type))

            oldDefault = "" if (oldColumn.defaultValue is None) else oldColumn.defaultValue
            newDefault = "" if (newColumn.defaultValue is None) else newColumn.defaultValue

            if (oldDefault != newDefault):
                if len(newDefault) == 0:
                    statements.append("\tALTER COLUMN %s DROP DEFAULT" % newColumnName)
                else:
                    statements.append("\tALTER COLUMN %s SET DEFAULT %s" % (newColumnName, newDefault))

            if (oldColumn.nullValue != newColumn.nullValue):
                if (newColumn.nullValue):
                    statements.append("\tALTER COLUMN %s DROP NOT NULL" % newColumnName)
                else:
                    if (arguments.addDefaults):
                        defaultValue = PgColumnUtils.getDefaultValue(newColumn.type)

                        if (defaultValue is not None):
                            statements.append("\tALTER COLUMN %s SET DEFAULT %s" % (newColumnName, defaultValue))
                            dropDefaultsColumns.append(newColumn)


                    statements.append("\tALTER COLUMN %s SET NOT NULL" % newColumnName)

