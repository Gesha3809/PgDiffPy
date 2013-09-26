from PgDiffUtils import PgDiffUtils

class PgDiffFunctions(object):

    @staticmethod
    def dropFunctions(writer, arguments, oldSchema, newSchema, searchPathHelper):
        if oldSchema is None:
            return

        # Drop functions that exist no more
        for oldFunctionSignature in oldSchema.functions:
            if (oldFunctionSignature not in newSchema.functions):
                searchPathHelper.outputSearchPath(writer)
                writer.writeln(oldSchema.functions[oldFunctionSignature].getDropSQL())

    @staticmethod
    def createFunctions(writer, arguments, oldSchema, newSchema, searchPathHelper):
        # Add new functions and replace modified functions
        for newFunctionName, newFunction  in newSchema.functions.items():

            oldFunction = None
            if oldSchema is not None:
                oldFunction = oldSchema.functions.get(newFunction.getSignature())

            if oldFunction is None or not newFunction.equals(oldFunction, arguments.ignoreFunctionWhitespace):
                searchPathHelper.outputSearchPath(writer)
                writer.writeln(newFunction.getCreationSQL())

    @staticmethod
    def alterComments(writer, oldSchema, newSchema, searchPathHelper):

        if oldSchema is None:
            return

        for oldfunctionName, oldfunction in oldSchema.functions.items():
            newFunction = newSchema.functions.get(oldfunction.getSignature())

            if newFunction is None:
                continue

            if (oldfunction.comment is None and newFunction.comment is not None
                    or oldfunction.comment is not None
                    and newFunction.comment is not None
                    and oldfunction.comment != newFunction.comment):
                searchPathHelper.outputSearchPath(writer)
                writer.write("COMMENT ON FUNCTION ")
                writer.write(PgDiffUtils.getQuotedName(newFunction.name))
                writer.write('(')

                writer.write(','.join(argument.getDeclaration(False) for argument in newFunction.arguments))

                writer.write(") IS ")
                writer.write(newFunction.comment)
                writer.writeln(';')

            elif (oldfunction.comment is not None and newFunction.comment is None):
                searchPathHelper.outputSearchPath(writer)
                writer.write("COMMENT ON FUNCTION ")
                writer.write(PgDiffUtils.getQuotedName(newFunction.name))
                writer.write('(')

                writer.write(','.join(argument.getDeclaration(False) for argument in newFunction.arguments))

                writer.writeln(") IS NULL;")
