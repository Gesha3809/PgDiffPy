from PgDiffUtils import PgDiffUtils

class PgDiffFunctions(object):

    @staticmethod
    def dropFunctions(arguments, oldSchema, newSchema, searchPathHelper):
        if oldSchema is None:
            return

        # Drop functions that exist no more
        for oldFunctionSignature in oldSchema.functions:
            if (oldFunctionSignature not in newSchema.functions):
                searchPathHelper.outputSearchPath()
                print "\n%s\n" % oldSchema.functions[oldFunctionSignature].getDropSQL()

    @staticmethod
    def createFunctions(arguments, oldSchema, newSchema, searchPathHelper):
        # Add new functions and replace modified functions
        for newFunctionName, newFunction  in newSchema.functions.items():

            oldFunction = None
            if oldSchema is not None:
                oldFunction = oldSchema.functions.get(newFunction.getSignature())

            if oldFunction is None or newFunction != oldFunction:
                searchPathHelper.outputSearchPath()
                print newFunction.getCreationSQL()

    @staticmethod
    def alterComments(oldSchema, newSchema, searchPathHelper):

        if oldSchema is None:
            return

        for oldfunctionName, oldfunction in oldSchema.functions.items():
            newFunction = newSchema.functions.get(oldfunction.getSignature())

            if newFunction is None:
                continue

            sbSQL = []
            if (oldfunction.comment is None and newFunction.comment is not None
                    or oldfunction.comment is not None
                    and newFunction.comment is not None
                    and oldfunction.comment != newFunction.comment):
                searchPathHelper.outputSearchPath()
                sbSQL.append("\nCOMMENT ON FUNCTION ")
                sbSQL.append(PgDiffUtils.getQuotedName(newFunction.name))
                sbSQL.append('(')

                sbSQL.append(','.join(argument.getDeclaration(False) for argument in newFunction.arguments.values()))

                sbSQL.append(") IS ")
                sbSQL.append(newFunction.comment)
                sbSQL.append(';\n')

                print ''.join(sbSQL)
            elif (oldfunction.comment is not None and newFunction.comment is None):
                searchPathHelper.outputSearchPath()
                sbSQL.append("\nCOMMENT ON FUNCTION ")
                sbSQL.append(PgDiffUtils.getQuotedName(newFunction.name))
                sbSQL.append('(')

                sbSQL.append(','.join(argument.getDeclaration(False) for argument in newFunction.arguments.values()))

                sbSQL.append(") IS NULL;\n")

                print ''.join(sbSQL)

