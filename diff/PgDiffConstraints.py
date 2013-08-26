from PgDiffUtils import PgDiffUtils

class PgDiffConstraints(object):

    @staticmethod
    def createConstraints(oldSchema, newSchema, primaryKey, searchPathHelper):
        for newTableName, newTable in newSchema.tables.items():

            oldTable = None
            if (oldSchema is not None):
                oldTable = oldSchema.tables.get(newTableName)

            # Add new constraints
            for constraint in PgDiffConstraints.getNewConstraints(oldTable, newTable, primaryKey):
                searchPathHelper.outputSearchPath()
                print "\n%s\n" % constraint.getCreationSQL()

    @staticmethod
    def dropConstraints(oldSchema, newSchema, primaryKey, searchPathHelper):
        for newTableName in newSchema.tables:

            oldTable = None
            if oldSchema is not None:
                oldTable = oldSchema.tables.get(newTableName)

            newTable = newSchema.tables[newTableName]

            # Drop constraints that no more exist or are modified
            for constraint in PgDiffConstraints.getDropConstraints(oldTable, newTable, primaryKey):
                searchPathHelper.outputSearchPath()
                print "\n%s\n" % constraint.getDropSQL()

    @staticmethod
    def alterComments(oldSchema, newSchema, searchPathHelper):

        if oldSchema is None:
            return

        for oldTableName, oldTable in oldSchema.tables.items():
            newTable = newSchema.tables.get(oldTableName)

            if newTable is None:
                continue

            for oldConstraintName, oldConstraint in oldTable.constraints.items():
                newConstraint = newTable.constraints.get(oldConstraintName)

                if newConstraint is None:
                    continue

                sbSQL = []
                if (oldConstraint.comment is None
                        and newConstraint.comment is not None
                        or oldConstraint.comment is not None
                        and newConstraint.comment is not None
                        and oldConstraint.comment != newConstraint.comment):

                    searchPathHelper.outputSearchPath()

                    sbSQL.append("\nCOMMENT ON ")

                    if newConstraint.isPrimaryKeyConstraint():
                        sbSQL.append("INDEX ")
                        sbSQL.append(PgDiffUtils.getQuotedName(newConstraint.name))
                    else:
                        sbSQL.append("CONSTRAINT ")
                        sbSQL.append(PgDiffUtils.getQuotedName(newConstraint.name))
                        sbSQL.append(" ON ")
                        sbSQL.append(PgDiffUtils.getQuotedName(newConstraint.tableName))

                    sbSQL.append(" IS ")
                    sbSQL.append(newConstraint.comment)
                    sbSQL.append(';\n')
                    print ''.join(sbSQL)

                elif (oldConstraint.comment is not None and newConstraint.comment is None):
                    searchPathHelper.outputSearchPath()
                    sbSQL.append("\nCOMMENT ON ")

                    if newConstraint.isPrimaryKeyConstraint():
                        sbSQL.appendt("INDEX ");
                        sbSQL.append(PgDiffUtils.getQuotedName(newConstraint.name))
                    else:
                        sbSQL.append("CONSTRAINT ");
                        sbSQL.append(PgDiffUtils.getQuotedName(newConstraint.name))
                        sbSQL.append(" ON ");
                        sbSQL.append(PgDiffUtils.getQuotedName(newConstraint.tableName))

                    sbSQL.append(" IS NULL;\n");
                    print ''.join(sbSQL)

    @staticmethod
    def getNewConstraints(oldTable, newTable, primaryKey):
        result = []

        if newTable is not None:
            if oldTable is None:
                for constraintName, constraint in newTable.constraints.items():
                    if constraint.isPrimaryKeyConstraint() == primaryKey:
                        result.append(constraint)
            else:
                for constraintName, constraint in newTable.constraints.items():
                    if (constraint.isPrimaryKeyConstraint() == primaryKey
                            and (constraintName not in oldTable.constraints
                            or oldTable.constraints[constraintName] != constraint)):
                        print constraint.__dict__
                        print oldTable.constraints[constraintName].__dict__
                        result.append(constraint)

        return result

    @staticmethod
    def getDropConstraints(oldTable, newTable, primaryKey):
        result = list()

        if newTable is not None and oldTable is not None:
            for constraintName in oldTable.constraints:
                oldConstraint = oldTable.constraints[constraintName]
                newConstraint = newTable.constraints.get(constraintName)

                if (oldConstraint.isPrimaryKeyConstraint() == primaryKey
                    and (newConstraint is None or newConstraint != oldConstraint)):
                    result.append(oldConstraint)

        return result