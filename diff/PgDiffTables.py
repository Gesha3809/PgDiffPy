from PgDiffUtils import PgDiffUtils

class PgDiffTables(object):

    @staticmethod
    def dropTables(oldSchema, newSchema, searchPathHelper):
        if oldSchema is None:
            return

        for tableName in oldSchema.tables:
            if tableName not in newSchema.tables:
                searchPathHelper.outputSearchPath()
                print '\n'
                print oldSchema.tables[tableName].getDropSQL()


    @staticmethod
    def alterTables(arguments, oldSchema, newSchema, searchPathHelper):
        for newTablename in newSchema.tables:
            if oldSchema is None or newTablename not in oldSchema.tables:
                continue

            oldTable = oldSchema.tables[newTablename]
            newTable = newSchema.tables[newTablename]

            PgDiffTables.updateTableColumns(arguments, oldTable, newTable, searchPathHelper)
            PgDiffTables.checkWithOIDS(oldTable, newTable, searchPathHelper)
            PgDiffTables.checkInherits(oldTable, newTable, searchPathHelper)
            PgDiffTables.checkTablespace(oldTable, newTable, searchPathHelper)
            PgDiffTables.addAlterStatistics(oldTable, newTable, searchPathHelper)
            PgDiffTables.addAlterStorage(oldTable, newTable, searchPathHelper)
            PgDiffTables.alterComments(oldTable, newTable, searchPathHelper)

    @staticmethod
    def updateTableColumns(arguments, oldTable, newTable, searchPathHelper):
        statements = []
        dropDefaultsColumns = []

        PgDiffTables.addDropTableColumns(statements, oldTable, newTable)
        PgDiffTables.addCreateTableColumns(statements, arguments, oldTable, newTable, dropDefaultsColumns)
        PgDiffTables.addModifyTableColumns(statements, arguments, oldTable, newTable, dropDefaultsColumns)

        if len(statements):
            quotedTableName = PgDiffUtils.getQuotedName(newTable.name)
            searchPathHelper.outputSearchPath()
            print "ALTER TABLE %s" % quotedTableName

            print "%s;" % ",".join(statements)

            # Still test needed
            if len(dropDefaultsColumns):
                print "ALTER TABLE " + quotedTableName

                _printStatements = []
                for dropDefaultsColumn in dropDefaultsColumns:
                    _printStatements.append("\tALTER COLUMN %s DROP DEFAULT" % PgDiffUtils.getQuotedName(dropDefaultsColumn.name))

                print "%s;" % ",".join(_printStatements)

    @staticmethod
    def checkWithOIDS(oldTable, newTable, searchPathHelper):
        if (oldTable.oids is None and newTable.oids is None
                or oldTable.oids is not None
                and oldTable.oids == newTable.oids):
            return

        searchPathHelper.outputSearchPath()
        print "\n"
        print "\nALTER TABLE %s" % PgDiffUtils.getQuotedName(newTable.name)

        if newTable.oids in (None, "OIDS=false"):
            print "\tSET WITHOUT OIDS;"
        elif newTable.oids in ("OIDS", "OIDS=true"):
            print "\tSET WITH OIDS;"
        else:
            print "\tSET %s;" % newTable.oids

    @staticmethod
    def checkInherits(oldTable, newTable, searchPathHelper):

        for oldTableName in oldTable.inherits:
            if oldTableName not in newTable.inherits:
                searchPathHelper.outputSearchPath()
                print '\n'
                print "ALTER TABLE %s\tNO INHERIT %s;" % (PgDiffUtils.getQuotedName(newTable.name), PgDiffUtils.getQuotedName(oldTableName))

        for newTableName in newTable.inherits:
            if newTableName not in oldTable.inherits:
                searchPathHelper.outputSearchPath()
                print '\n'
                print "ALTER TABLE %s\tINHERIT %s;" % (PgDiffUtils.getQuotedName(newTable.name), PgDiffUtils.getQuotedName(newTableName))

    @staticmethod
    def checkTablespace(oldTable, newTable, searchPathHelper):
        if (oldTable.tablespace is None and newTable.tablespace is None
                or oldTable.tablespace is not None
                and oldTable.tablespace == newTable.tablespace):
            return

        searchPathHelper.outputSearchPath()
        print '\n'
        print "ALTER TABLE %s\tTABLESPACE %s" % (PgDiffUtils.getQuotedName(newTable.name), newTable.tablespace)


    @staticmethod
    def addAlterStatistics(oldTable, newTable, searchPathHelper):
        # final Map<String, Integer> stats = new HashMap<String, Integer>();
        stats = dict()

        for newColumnName in newTable.columns:
            oldColumn = oldTable.columns[newColumnName]
            newColumn = newTable.columns[newColumnName]

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
            searchPathHelper.outputSearchPath()
            print '\n'
            print "ALTER TABLE ONLY %s ALTER COLUMN %s SET STATISTICS %s;" % (PgDiffUtils.getQuotedName(newTable.name), PgDiffUtils.getQuotedName(columnName), stats[columnName])

    @staticmethod
    def addAlterStorage(oldTable, newTable, searchPathHelper):
        for newColumnName in newTable.columns:
            oldColumn = oldTable.columns[newColumnName]
            newColumn = newTable.columns[newColumnName]

            oldStorage = None if (oldColumn is None
                    or oldColumn.storage is None
                    or oldColumn.storage == '') else oldColumn.storage
            newStorage = None if (newColumn.storage is None
                    or newColumn.storage == '') else newColumn.storage

            if (newStorage is None and oldStorage is not None):
                searchPathHelper.outputSearchPath()
                print '\n'
                print "WARNING: Column %s.%s in new table has no STORAGE set but in old table storage was set. Unable to determine STORAGE type." % (newTable.name, newColumn.name)
                continue

            if (newStorage is None or newStorage == oldStorage):
                continue

            searchPathHelper.outputSearchPath()
            print '\n'
            print "ALTER TABLE ONLY %s ALTER COLUMN %s SET STORAGE %s;" % (PgDiffUtils.getQuotedName(newTable.name), PgDiffUtils.getQuotedName(newColumn.name), newStorage)

    @staticmethod
    def alterComments(oldTable, newTable, searchPathHelper):
        if (oldTable.comment is None
                and newTable.comment is not None
                or oldTable.comment is not None
                and newTable.comment is not None
                and oldTable.comment != newTable.comment):
            searchPathHelper.outputSearchPath()
            print '\n'
            print "COMMENT ON TABLE %s IS %s;" % (PgDiffUtils.getQuotedName(newTable.name), newTable.comment)
        elif (oldTable.comment is not None and newTable.comment is None):
            searchPathHelper.outputSearchPath()
            print '\n'
            print "COMMENT ON TABLE %s IS NULL;" % PgDiffUtils.getQuotedName(newTable.name)


        for newColumnName in newTable.columns:
            oldColumn = oldTable.columns[newColumnName]
            newColumn = newTable.columns[newColumnName]
            oldComment = None if oldColumn is None else oldColumn.comment
            newComment = newColumn.comment

            if (newComment is not None and (newComment is not None if oldComment is None else oldComment != newComment)):
                searchPathHelper.outputSearchPath()
                print '\n'
                print "COMMENT ON COLUMN %s.%s IS %s;" % (PgDiffUtils.getQuotedName(newTable.name), PgDiffUtils.getQuotedName(newColumn.name), newColumn.comment)
            elif (oldComment is not None and newComment is None):
                searchPathHelper.outputSearchPath()
                print '\n'
                print "COMMENT ON COLUMN %s.%s IS NULL;" % (PgDiffUtils.getQuotedName(newTable.name), PgDiffUtils.getQuotedName(newColumn.name))

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

