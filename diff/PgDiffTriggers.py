from PgDiffUtils import PgDiffUtils

class PgDiffTriggers(object):

    @staticmethod
    def createTriggers(writer, oldSchema, newSchema, searchPathHelper):
        for newTableName, newTable in newSchema.tables.items():
            oldTable = None

            if oldSchema is not None:
                oldTable = oldSchema.tables.get(newTableName)

            # Add new triggers
            for trigger in PgDiffTriggers.getNewTriggers(oldTable, newTable):
                searchPathHelper.outputSearchPath(writer)
                writer.writeln(trigger.getCreationSQL())

    @staticmethod
    def dropTriggers(writer, oldSchema, newSchema, searchPathHelper):
        for newTableName in newSchema.tables:
            oldTable = None

            if oldSchema is not None:
                oldTable = oldSchema.tables.get(newTableName)

            newTable = newSchema.tables[newTableName]

            # Drop triggers that no more exist or are modified
            for trigger in PgDiffTriggers.getDropTriggers(oldTable, newTable):
                searchPathHelper.outputSearchPath(writer)
                writer.writeln(trigger.getDropSQL())

    @staticmethod
    def alterComments(writer, oldSchema, newSchema, searchPathHelper):
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

                oldTrigger = oldTable.triggers.get(oldTriggerName)
                if (oldTrigger.comment is None
                        and newTrigger.comment is not None
                        or oldTrigger.comment is not None
                        and newTrigger.comment is not None
                        and oldTrigger.comment !=  newTrigger.comment):
                    searchPathHelper.outputSearchPath(writer)
                    writer.write("COMMENT ON TRIGGER ")
                    writer.write(PgDiffUtils.getQuotedName(newTrigger.name))
                    writer.write(" ON ")
                    writer.write(PgDiffUtils.getQuotedName(newTrigger.tableName))
                    writer.write(" IS ");
                    writer.write(newTrigger.comment)
                    writer.writeln(';')

                elif (oldTrigger.comment is not None and newTrigger.comment is None):
                    searchPathHelper.outputSearchPath(writer)
                    writer.write("COMMENT ON TRIGGER ")
                    writer.write(PgDiffUtils.getQuotedName(newTrigger.name))
                    writer.write(" ON ")
                    writer.write(PgDiffUtils.getQuotedName(newTrigger.tableName))
                    writer.write(" IS NULL")
                    writer.writeln(';')

    @staticmethod
    def getNewTriggers(oldTable, newTable):
        result = []

        if newTable is not None:
            if oldTable is None:
                result = newTable.triggers.keys()
            else:
                for newTriggerName, newTrigger in newTable.triggers.items():
                    if (newTriggerName not in oldTable.triggers
                        or newTrigger != oldTable.triggers[newTriggerName]):
                        result.append(newTrigger)

        return result

    @staticmethod
    def getDropTriggers(oldTable, newTable):
        result = list()

        if None not in (newTable, oldTable):
            newTriggers = newTable.triggers

            for oldTriggerName in oldTable.triggers:
                if (oldTriggerName not in newTriggers
                    or newTriggers[oldTriggerName] != oldTable.triggers[oldTriggerName]):
                    result.append(oldTable.triggers[oldTriggerName]);

        return result
