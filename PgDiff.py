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
    def create_diff(writer, arguments):
        old_database = PgDumpLoader.loadDatabaseSchema(arguments.old_dump)
        new_database = PgDumpLoader.loadDatabaseSchema(arguments.new_dump)

        PgDiff.diff_database_schemas(writer, arguments, old_database, new_database)

    @staticmethod
    def diff_database_schemas(writer, arguments, old_database, new_database):
        if arguments.addTransaction:
            writer.writeln("START TRANSACTION;")

        if (old_database.comment is None
                and new_database.comment is not None
                or old_database.comment is not None
                and new_database.comment is not None
                and old_database.comment != new_database.comment):
            writer.write("COMMENT ON DATABASE current_database() IS ")
            writer.write(new_database.comment)
            writer.writeln(";")
        elif old_database.comment is not None and new_database.comment is None:
            writer.writeln("COMMENT ON DATABASE current_database() IS NULL;")

        PgDiff.drop_old_schemas(writer, old_database, new_database)
        PgDiff.create_new_schemas(writer, old_database, new_database)
        PgDiff.update_schemas(writer, arguments, old_database, new_database)

        if arguments.addTransaction:
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
    def drop_old_schemas(writer, old_database, new_database):
        for oldSchemaName in old_database.schemas:
            if new_database.getSchema(oldSchemaName) is None:
                writer.writeln("DROP SCHEMA %s CASCADE;" % PgDiffUtils.getQuotedName(oldSchemaName))

    @staticmethod
    def create_new_schemas(writer, old_database, new_database):
        for newSchemaName in new_database.schemas:
            if old_database.getSchema(newSchemaName) is None:
                writer.writeln(new_database.schemas[newSchemaName].getCreationSQL())

    @staticmethod
    def update_schemas(writer, arguments, old_database, new_database):
        # We set search path if more than one schemas or it's name is not public
        set_search_path = len(new_database.schemas) > 1 or new_database.schemas.itervalues().next().name != "public"

        for newSchemaName in new_database.schemas:
            if set_search_path:
                search_path_helper = SearchPathHelper("SET search_path = %s, pg_catalog;" %
                                                      PgDiffUtils.getQuotedName(newSchemaName, True))
            else:
                search_path_helper = SearchPathHelper(None)

            old_schema = old_database.schemas.get(newSchemaName)
            new_schema = new_database.schemas[newSchemaName]

            if old_schema is not None:
                if (old_schema.comment is None
                        and new_schema.comment is not None
                        or old_schema.comment is not None
                        and new_schema.comment is not None
                        and old_schema.comment != new_schema.comment):
                    writer.write("COMMENT ON SCHEMA ")
                    writer.write(PgDiffUtils.getQuotedName(new_schema.name))
                    writer.write(" IS ")
                    writer.write(new_schema.comment)
                    writer.writeln(';')

                elif old_schema.comment is not None and new_schema.comment is None:
                    writer.write("COMMENT ON SCHEMA ")
                    writer.write(PgDiffUtils.getQuotedName(new_schema.name))
                    writer.writeln(" IS NULL;")

            PgDiffTriggers.dropTriggers(writer, old_schema, new_schema, search_path_helper)
            PgDiffFunctions.dropFunctions(writer, arguments, old_schema, new_schema, search_path_helper)
            PgDiffViews.dropViews(writer, old_schema, new_schema, search_path_helper)
            PgDiffConstraints.dropConstraints(writer, old_schema, new_schema, True, search_path_helper)
            PgDiffConstraints.dropConstraints(writer, old_schema, new_schema, False, search_path_helper)
            PgDiffIndexes.dropIndexes(writer, old_schema, new_schema, search_path_helper)
            # # PgDiffTables.dropClusters(oldSchema, newSchema, searchPathHelper)
            PgDiffTables.dropTables(writer, old_schema, new_schema, search_path_helper)
            PgDiffSequences.dropSequences(writer, old_schema, new_schema, search_path_helper)

            PgDiffSequences.createSequences(writer, old_schema, new_schema, search_path_helper)
            PgDiffSequences.alterSequences(writer, arguments, old_schema, new_schema, search_path_helper)
            PgDiffTables.createTables(writer, old_schema, new_schema, search_path_helper)
            PgDiffTables.alterTables(writer, arguments, old_schema, new_schema, search_path_helper)
            PgDiffSequences.alterCreatedSequences(writer, old_schema, new_schema, search_path_helper)
            PgDiffFunctions.createFunctions(writer, arguments, old_schema, new_schema, search_path_helper)
            PgDiffConstraints.createConstraints(writer, old_schema, new_schema, True, search_path_helper)
            PgDiffConstraints.createConstraints(writer, old_schema, new_schema, False, search_path_helper)
            PgDiffIndexes.createIndexes(writer, old_schema, new_schema, search_path_helper)
            # # PgDiffTables.createClusters(oldSchema, newSchema, searchPathHelper)
            PgDiffTriggers.createTriggers(writer, old_schema, new_schema, search_path_helper)
            PgDiffViews.createViews(writer, old_schema, new_schema, search_path_helper)
            PgDiffViews.alterViews(writer, old_schema, new_schema, search_path_helper)

            PgDiffFunctions.alterComments(writer, old_schema, new_schema, search_path_helper)
            PgDiffConstraints.alterComments(writer, old_schema, new_schema, search_path_helper)
            PgDiffIndexes.alterComments(writer, old_schema, new_schema, search_path_helper)
            PgDiffTriggers.alterComments(writer, old_schema, new_schema, search_path_helper)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage='Usage: PgDiff.py [options] <old_dump> <new_dump>')

    parser.add_argument('old_dump', nargs='?')
    parser.add_argument('new_dump', nargs='?')

    parser.add_argument('--add-transaction', dest='addTransaction', action='store_true', help="Adds START TRANSACTION and COMMIT TRANSACTION to the generated diff file")
    parser.add_argument('--add-defaults', dest='addDefaults', action='store_true', help="adds DEFAULT ... in case new column has NOT NULL constraint but no default value (the default value is dropped later)")
    parser.add_argument('--ignore-start-with', dest='ignoreStartWith', action='store_false', help="ignores START WITH modifications on SEQUENCEs (default is not to ignore these changes)")
    parser.add_argument('--ignore-function-whitespace', dest='ignoreFunctionWhitespace', action='store_true', help="ignores multiple spaces and new lines when comparing content of functions\n\
                                                                \t- WARNING: this may cause functions to appear to be same in cases they are\n\
                                                                \tnot, so use this feature only if you know what you are doing")


    parser.add_argument('--debug', dest='debug', action='store_true', help="outputs debug information as trceback etc. (default is not to output traceback)")

    arguments = parser.parse_args()
    writer = Writer()

    try:
        PgDiff.create_diff(writer, arguments)
        print(writer)
    except Exception as e:
        if arguments.debug:
            import sys
            import traceback
            print(traceback.print_exception(*sys.exc_info()))
        else:
            print('Error: %s' % e)
