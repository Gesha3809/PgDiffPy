class PgDiffIndexes(object):
    @staticmethod
    def createIndexes(oldSchema, newSchema, searchPathHelper):
        for newTableName, newTable in newSchema.tables.items():

            # Add new indexes
            if oldSchema is None:
                for index in newTable.indexes.values():
                    searchPathHelper.outputSearchPath()
                    print "\n%s\n" % index.getCreationSQL()
            else:
                for index in PgDiffIndexes.getNewIndexes(oldSchema.getTable(newTableName), newTable):
                    searchPathHelper.outputSearchPath()
                    print "\n%s\n" % index.getCreationSQL()

    @staticmethod
    def dropIndexes(oldSchema, newSchema, searchPathHelper):
        for newTableName in newSchema.tables:
            oldTable = None

            if oldSchema is not None:
                oldTable = oldSchema.tables.get(newTableName)

            newTable = newSchema.tables[newTableName]

            # Drop indexes that do not exist in new schema or are modified
            for index in PgDiffIndexes.getDropIndexes(oldTable, newTable):
                searchPathHelper.outputSearchPath()
                print "\n%s\n" % index.getDropSQL()

    @staticmethod
    def alterComments(oldSchema, newSchema, searchPathHelper):
        if oldSchema is None:
            return

        for oldIndexName in oldSchema.indexes:
            newIndex = newSchema.indexes.get(oldIndexName)

            if newIndex is None:
                continue

            oldIndex = newSchema.indexes[oldIndexName]

            sbSQL = []
            if (oldIndex.comment is None
                    and newIndex.comment is not None
                    or oldIndex.comment is not None
                    and newIndex.comment is not None
                    and oldIndex.comment !=  newIndex.comment):
                searchPathHelper.outputSearchPath()
                sbSQL.append("\nCOMMENT ON INDEX ")
                sbSQL.append(PgDiffUtils.getQuotedName(newIndex.name))
                sbSQL.append(" IS ")
                sbSQL.append(newIndex.comment)
                sbSQL.append(';\n')
                print ''.join(sbSQL)

            elif oldIndex.comment is not None and newIndex.comment is None:
                searchPathHelper.outputSearchPath()
                sbSQL.append("\nCOMMENT ON INDEX ");
                sbSQL.append(PgDiffUtils.getQuotedName(newIndex.name))
                sbSQL.append(" IS NULL;")
                print ''.join(sbSQL)

    @staticmethod
    def getNewIndexes(oldTable, newTable):
        result = []

        if newTable is not None:
            if oldTable is None:
                for index in newTable.indexes.values():
                    result.append(index)
            else:
                for indexName, index in newTable.indexes.items():
                    if (indexName not in oldTable.indexes
                        or oldTable.indexes[indexName] != index):
                        result.append(index)

        return result

    @staticmethod
    def getDropIndexes(oldTable, newTable):
        result = list()

        if (newTable is not None and oldTable is not None):
            for indexName in oldTable.indexes:
                if indexName not in newTable.indexes:
                    result.append(oldTable.indexes[indexName])

        return result
