from PgDiffUtils import PgDiffUtils

class PgDiffConstraints(object):

    @staticmethod
    def createConstraints(writer, oldSchema, newSchema, primaryKey, searchPathHelper):
        for newTableName, newTable in newSchema.tables.items():

            oldTable = None
            if (oldSchema is not None):
                oldTable = oldSchema.tables.get(newTableName)

            # Add new constraints
            for constraint in PgDiffConstraints.getNewConstraints(oldTable, newTable, primaryKey):
                searchPathHelper.outputSearchPath(writer)
                writer.writeln(constraint.getCreationSQL())

    @staticmethod
    def dropConstraints(writer, oldSchema, newSchema, primaryKey, searchPathHelper):
        for newTableName in newSchema.tables:

            oldTable = None
            if oldSchema is not None:
                oldTable = oldSchema.tables.get(newTableName)

            newTable = newSchema.tables[newTableName]

            # Drop constraints that no more exist or are modified
            for constraint in PgDiffConstraints.getDropConstraints(oldTable, newTable, primaryKey):
                searchPathHelper.outputSearchPath(writer)
                writer.writeln(constraint.getDropSQL())

    @staticmethod
    def alterComments(writer, oldSchema, newSchema, searchPathHelper):

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

                # sbSQL = []
                if (oldConstraint.comment is None
                        and newConstraint.comment is not None
                        or oldConstraint.comment is not None
                        and newConstraint.comment is not None
                        and oldConstraint.comment != newConstraint.comment):

                    searchPathHelper.outputSearchPath(writer)

                    writer.write("COMMENT ON ")

                    if newConstraint.isPrimaryKeyConstraint():
                        writer.write("INDEX ")
                        writer.write(PgDiffUtils.getQuotedName(newConstraint.name))
                    else:
                        writer.write("CONSTRAINT ")
                        writer.write(PgDiffUtils.getQuotedName(newConstraint.name))
                        writer.write(" ON ")
                        writer.write(PgDiffUtils.getQuotedName(newConstraint.tableName))

                    writer.write(" IS ")
                    writer.write(newConstraint.comment)
                    writer.writeln(';')

                elif (oldConstraint.comment is not None and newConstraint.comment is None):
                    searchPathHelper.outputSearchPath(writer)
                    writer.write("COMMENT ON ")

                    if newConstraint.isPrimaryKeyConstraint():
                        writer.write("INDEX ");
                        writer.write(PgDiffUtils.getQuotedName(newConstraint.name))
                    else:
                        writer.write("CONSTRAINT ");
                        writer.write(PgDiffUtils.getQuotedName(newConstraint.name))
                        writer.write(" ON ");
                        writer.write(PgDiffUtils.getQuotedName(newConstraint.tableName))

                    writer.writeln(" IS NULL;")

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