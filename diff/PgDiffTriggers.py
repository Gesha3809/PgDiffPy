from PgDiffUtils import PgDiffUtils

class PgDiffTriggers(object):

    @staticmethod
    def createTriggers(oldSchema, newSchema, searchPathHelper):
        for newTableName, newTable in newSchema.tables.items():
            oldTable = None

            if oldSchema is not None:
                oldTable = oldSchema.tables[newTableName]

            # Add new triggers
            for trigger in PgDiffTriggers.getNewTriggers(oldTable, newTable):
                searchPathHelper.outputSearchPath()
                print "\n%s\n" % trigger.getCreationSQL()

    @staticmethod
    def dropTriggers(oldSchema, newSchema, searchPathHelper):
        for newTableName in newSchema.tables:
            oldTable = None

            if oldSchema is not None:
                oldTable = oldSchema.tables.get(newTableName)
                newTable = newSchema.tables[newTableName]

            # Drop triggers that no more exist or are modified
            for trigger in PgDiffTriggers.getDropTriggers(oldTable, newTable):
                searchPathHelper.outputSearchPath()
                print "\n%s\n" % trigger.getDropSQL()

    @staticmethod
    def alterComments(oldSchema, newSchema, searchPathHelper):
        if oldSchema is None:
            return

        for oldTableName in oldSchema.tables:
            newTable = newSchema.getTable(oldTableName)

            if newTable is None:
                continue

            oldTable = oldSchema.getTable(oldTableName)

            for oldTriggerName in oldTable.triggers:
                newTrigger = newTable.triggers.get(oldTriggerName);

                if newTrigger is None:
                    continue

                oldTrigger = oldTable.triggers.get(oldTriggerName);
                sbSQL = []
                if (oldTrigger.comment is None
                        and newTrigger.comment is not None
                        or oldTrigger.comment is not None
                        and newTrigger.comment is not None
                        and oldTrigger.comment !=  newTrigger.comment):
                    searchPathHelper.outputSearchPath()
                    sbSQL.append("\nCOMMENT ON TRIGGER ")
                    sbSQL.append(PgDiffUtils.getQuotedName(newTrigger.name))
                    sbSQL.append(" ON ")
                    sbSQL.append(PgDiffUtils.getQuotedName(newTrigger.tableName))
                    sbSQL.append(" IS ");
                    sbSQL.append(newTrigger.comment)
                    sbSQL.append(';')
                    print ''.join(sbSQL)

                elif (oldTrigger.comment is not None
                        and newTrigger.comment is None):
                    searchPathHelper.outputSearchPath()
                    sbSQL.append("\nCOMMENT ON TRIGGER ")
                    sbSQL.append(PgDiffUtils.getQuotedName(newTrigger.name))
                    sbSQL.append(" ON ")
                    sbSQL.append(PgDiffUtils.getQuotedName(newTrigger.tableName))
                    sbSQL.append(" IS NULL;\n")
                    print ''.join(sbSQL)

    @staticmethod
    def getNewTriggers(oldTable, newTable):
        result = []

        if newTable is not None:
            if oldTable is None:
                result = newTable.triggers.keys()
            else:
                for newTriggerName, newTrigger in newTable.triggers.items():
                    if newTriggerName not in oldTable.triggers:
                        result.append(newTrigger)

        return result

    @staticmethod
    def getDropTriggers(oldTable, newTable):
        result = list()

        if (newTable is not None and oldTable is not None):
            newTriggers = newTable.triggers

            for oldTriggerName in oldTable.triggers:
                if oldTriggerName not in newTriggers:
                    result.append(oldTable.triggers[oldTriggerName]);

        return result
