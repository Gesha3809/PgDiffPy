import argparse
from helpers.Writer import Writer
from loaders.PgDumpLoader import PgDumpLoader
from diff.PgDiffUtils import PgDiffUtils
from SearchPathHelper import SearchPathHelper
from diff.PgDiffTables import PgDiffTables
from diff.PgDiffTriggers import PgDiffTriggers
from diff.PgDiffViews import PgDiffViews
from diff.PgDiffConstraints import PgDiffConstraints
from diff.PgDiffIndexes import PgDiffIndexes
from diff.PgDiffSequences import PgDiffSequences
from diff.PgDiffFunctions import PgDiffFunctions

class PgDiff(object):

    @staticmethod
    def createDiff(writer, arguments):
        oldDatabase = PgDumpLoader.loadDatabaseSchema(arguments.old_dump)
        newDatabase = PgDumpLoader.loadDatabaseSchema(arguments.new_dump)

        PgDiff.diffDatabaseSchemas(writer, arguments, oldDatabase, newDatabase)

    @staticmethod
    def diffDatabaseSchemas(writer, arguments, oldDatabase, newDatabase):
        if arguments.add_transaction:
            writer.writeln("START TRANSACTION;")

        if (oldDatabase.comment is None
                and newDatabase.comment is not None
                or oldDatabase.comment is not None
                and newDatabase.comment is not None
                and oldDatabase.comment != newDatabase.comment):
            writer.write("COMMENT ON DATABASE current_database() IS ")
            writer.write(newDatabase.comment)
            writer.writeln(";")
        elif (oldDatabase.comment is not None and newDatabase.comment is None):
            writer.writeln("COMMENT ON DATABASE current_database() IS NULL;")


        PgDiff.dropOldSchemas(writer, oldDatabase, newDatabase)
        PgDiff.createNewSchemas(writer, oldDatabase, newDatabase)
        PgDiff.updateSchemas(writer, arguments, oldDatabase, newDatabase)

        if arguments.add_transaction:
            writer.writeln("COMMIT TRANSACTION;")

        # if (arguments.isOutputIgnoredStatements()) {
        #     if (!oldDatabase.getIgnoredStatements().isEmpty()) {
        #         writer.println();
        #         writer.print("/* ");
        #         writer.println(Resources.getString(
        #                 "OriginalDatabaseIgnoredStatements"));

        #         for (final String statement :
        #                 oldDatabase.getIgnoredStatements()) {
        #             writer.println();
        #             writer.println(statement);
        #         }

        #         writer.println("*/");
        #     }

        #     if (!newDatabase.getIgnoredStatements().isEmpty()) {
        #         writer.println();
        #         writer.print("/* ");
        #         writer.println(Resources.getString("NewDatabaseIgnoredStatements"));

        #         for (final String statement :
        #                 newDatabase.getIgnoredStatements()) {
        #             writer.println();
        #             writer.println(statement);
        #         }

        #         writer.println("*/");
        #     }
        # }

    @staticmethod
    def dropOldSchemas(writer, oldDatabase, newDatabase):
        for oldSchemaName in oldDatabase.schemas:
            if newDatabase.getSchema(oldSchemaName) is None:
                writer.writeln("DROP SCHEMA "+ PgDiffUtils.getQuotedName(oldSchema.getName())+ " CASCADE;")

    @staticmethod
    def createNewSchemas(writer, oldDatabase, newDatabase):
        for newSchema in newDatabase.schemas:
            if newDatabase.getSchema(newSchema) is None:
                writer.writeln(newSchema.getCreationSQL())

    @staticmethod
    def updateSchemas(writer, arguments, oldDatabase, newDatabase):
        # We set search path if more than one schemas or it's name is not public
        setSearchPath = len(newDatabase.schemas) > 1 or newDatabase.schemas.itervalues().next().name != "public"

        for newSchemaName in newDatabase.schemas:
            if setSearchPath:
                searchPathHelper = SearchPathHelper("SET search_path = %s, pg_catalog;" % PgDiffUtils.getQuotedName(newSchemaName, True))
            else:
                searchPathHelper = SearchPathHelper(None)

            oldSchema = oldDatabase.schemas[newSchemaName]
            newSchema = newDatabase.schemas[newSchemaName]

            if oldSchema is not None:
                if (oldSchema.comment is None
                        and newSchema.comment is not None
                        or oldSchema.comment is not None
                        and newSchema.comment is not None
                        and oldSchema.comment != newSchema.comment):
                    writer.write("COMMENT ON SCHEMA ")
                    writer.write(PgDiffUtils.getQuotedName(newSchema.name))
                    writer.write(" IS ")
                    writer.write(newSchema.comment)
                    writer.writeln(';')

                elif (oldSchema.comment is not None and newSchema.comment is None):
                    writer.write("COMMENT ON SCHEMA ")
                    writer.write(PgDiffUtils.getQuotedName(newSchema.name))
                    writer.writeln(" IS NULL;")

            PgDiffTriggers.dropTriggers(writer, oldSchema, newSchema, searchPathHelper)
            PgDiffFunctions.dropFunctions(writer, arguments, oldSchema, newSchema, searchPathHelper)
            PgDiffViews.dropViews(writer, oldSchema, newSchema, searchPathHelper)
            PgDiffConstraints.dropConstraints(writer, oldSchema, newSchema, True, searchPathHelper)
            PgDiffConstraints.dropConstraints(writer, oldSchema, newSchema, False, searchPathHelper)
            PgDiffIndexes.dropIndexes(writer, oldSchema, newSchema, searchPathHelper)
            # # PgDiffTables.dropClusters(oldSchema, newSchema, searchPathHelper)
            PgDiffTables.dropTables(writer, oldSchema, newSchema, searchPathHelper)
            PgDiffSequences.dropSequences(writer, oldSchema, newSchema, searchPathHelper)

            PgDiffSequences.createSequences(writer, oldSchema, newSchema, searchPathHelper)
            PgDiffSequences.alterSequences(writer, arguments, oldSchema, newSchema, searchPathHelper)
            PgDiffTables.createTables(writer, oldSchema, newSchema, searchPathHelper)
            PgDiffTables.alterTables(writer, arguments, oldSchema, newSchema, searchPathHelper)
            PgDiffSequences.alterCreatedSequences(writer, oldSchema, newSchema, searchPathHelper)
            PgDiffFunctions.createFunctions(writer, arguments, oldSchema, newSchema, searchPathHelper)
            PgDiffConstraints.createConstraints(writer, oldSchema, newSchema, True, searchPathHelper)
            PgDiffConstraints.createConstraints(writer, oldSchema, newSchema, False, searchPathHelper)
            PgDiffIndexes.createIndexes(writer, oldSchema, newSchema, searchPathHelper)
            # # PgDiffTables.createClusters(oldSchema, newSchema, searchPathHelper)
            PgDiffTriggers.createTriggers(writer, oldSchema, newSchema, searchPathHelper)
            PgDiffViews.createViews(writer, oldSchema, newSchema, searchPathHelper)
            PgDiffViews.alterViews(writer, oldSchema, newSchema, searchPathHelper)

            PgDiffFunctions.alterComments(writer, oldSchema, newSchema, searchPathHelper)
            PgDiffConstraints.alterComments(writer, oldSchema, newSchema, searchPathHelper)
            PgDiffIndexes.alterComments(writer, oldSchema, newSchema, searchPathHelper)
            PgDiffTriggers.alterComments(writer, oldSchema, newSchema, searchPathHelper)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage='Usage: PgDiff.py [options] <old_dump> <new_dump>')

    parser.add_argument('old_dump', nargs='?')
    parser.add_argument('new_dump', nargs='?')

    parser.add_argument('--add-transaction', dest='add_transaction', action='store_true', help="Adds START TRANSACTION and COMMIT TRANSACTION to the generated diff file")
    parser.add_argument('--add-defaults', dest='addDefaults', action='store_true', help="adds DEFAULT ... in case new column has NOT NULL constraint but no default value (the default value is dropped later)")
    parser.add_argument('--ignore-start-with', dest='ignoreStartWith', action='store_false', help="ignores START WITH modifications on SEQUENCEs (default is not to ignore these changes)")

    parser.add_argument('--debug', dest='debug', action='store_true', help="outputs debug information as trceback etc. (default is not to output traceback)")

    arguments = parser.parse_args()
    writer = Writer()

    try:
        PgDiff.createDiff(writer, arguments)
        print(writer)
    except Exception as e:
        if arguments.debug:
            import sys, traceback
            print(traceback.print_exception(*sys.exc_info()))
        else:
            print('Error: %s' % e)
