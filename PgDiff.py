import argparse
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
    def createDiff(self, arguments):
        oldDatabase = PgDumpLoader.loadDatabaseSchema(arguments.new_dump)
        newDatabase = PgDumpLoader.loadDatabaseSchema(arguments.old_dump)

        self.diffDatabaseSchemas(arguments, oldDatabase, newDatabase)

    def diffDatabaseSchemas(self, arguments, oldDatabase, newDatabase):
        if arguments.add_transaction:
            print "START TRANSACTION;"

        if (oldDatabase.comment is None
                and newDatabase.comment is not None
                or oldDatabase.comment is not None
                and newDatabase.comment is not None
                and oldDatabase.comment != newDatabase.comment):
            print "\nCOMMENT ON DATABASE current_database() IS %s;" % newDatabase.comment
        elif (oldDatabase.comment is not None and newDatabase.comment is None):
            print "\nCOMMENT ON DATABASE current_database() IS NULL;"


        self.dropOldSchemas(oldDatabase, newDatabase)
        self.createNewSchemas(oldDatabase, newDatabase)
        self.updateSchemas(arguments, oldDatabase, newDatabase)

        if arguments.add_transaction:
            print "\nCOMMIT TRANSACTION;"

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
    def dropOldSchemas(self, oldDatabase, newDatabase):
        for oldSchemaName in oldDatabase.schemas:
            if newDatabase.getSchema(oldSchemaName) is None:
                print "\nDROP SCHEMA "+ PgDiffUtils.getQuotedName(oldSchema.getName())+ " CASCADE;"

    def createNewSchemas(self, oldDatabase, newDatabase):
        for newSchema in newDatabase.schemas:
            if newDatabase.getSchema(newSchema) is None:
                print '\n'
                print newSchema.getCreationSQL()

    def updateSchemas(self, arguments, oldDatabase, newDatabase):
        # We set search path if more than one schemas or it's name is not public
        setSearchPath = len(newDatabase.schemas) > 1 or newDatabase.schemas.itervalues().next().name != "public"

        for newSchemaName in newDatabase.schemas:
            if setSearchPath:
                searchPathHelper = SearchPathHelper("SET search_path = %s, pg_catalog;" % PgDiffUtils.getQuotedName(newSchemaName, True))
            else:
                searchPathHelper = SearchPathHelper(None)

            oldSchema = oldDatabase.schemas[newSchemaName]
            newSchema = newDatabase.schemas[newSchemaName]
            
            sbSQL = []

            if oldSchema is not None:
                if (oldSchema.comment is None
                        and newSchema.comment is not None
                        or oldSchema.comment is not None
                        and newSchema.comment is not None
                        and oldSchema.comment != newSchema.comment):
                    sbSQL.append("\nCOMMENT ON SCHEMA ")
                    sbSQL.append(PgDiffUtils.getQuotedName(newSchema.name))
                    sbSQL.append(" IS ")
                    sbSQL.append(newSchema.comment)
                    sbSQL.append(';')                    
                    print ''.join(sbSQL)
                    
                elif (oldSchema.comment is not None and newSchema.comment is None):
                    sbSQL.append("\nCOMMENT ON SCHEMA ")
                    sbSQL.append(PgDiffUtils.getQuotedName(newSchema.name))
                    sbSQL.append(" IS NULL;")                    
                    print ''.join(sbSQL)


            PgDiffTriggers.dropTriggers(oldSchema, newSchema, searchPathHelper)
            PgDiffFunctions.dropFunctions(arguments, oldSchema, newSchema, searchPathHelper)
            PgDiffViews.dropViews(oldSchema, newSchema, searchPathHelper)
            PgDiffConstraints.dropConstraints(oldSchema, newSchema, True, searchPathHelper)
            PgDiffConstraints.dropConstraints(oldSchema, newSchema, False, searchPathHelper)
            PgDiffIndexes.dropIndexes(oldSchema, newSchema, searchPathHelper)
            # PgDiffTables.dropClusters(oldSchema, newSchema, searchPathHelper)
            PgDiffTables.dropTables(oldSchema, newSchema, searchPathHelper)
            PgDiffSequences.dropSequences(oldSchema, newSchema, searchPathHelper)

            PgDiffSequences.createSequences(oldSchema, newSchema, searchPathHelper)
            PgDiffSequences.alterSequences(arguments, oldSchema, newSchema, searchPathHelper)
            PgDiffTables.createTables(oldSchema, newSchema, searchPathHelper)
            PgDiffTables.alterTables(arguments, oldSchema, newSchema, searchPathHelper)
            PgDiffSequences.alterCreatedSequences(oldSchema, newSchema, searchPathHelper)
            PgDiffFunctions.createFunctions(arguments, oldSchema, newSchema, searchPathHelper)
            PgDiffConstraints.createConstraints(oldSchema, newSchema, True, searchPathHelper)
            PgDiffConstraints.createConstraints(oldSchema, newSchema, False, searchPathHelper)
            PgDiffIndexes.createIndexes(oldSchema, newSchema, searchPathHelper)
            # PgDiffTables.createClusters(oldSchema, newSchema, searchPathHelper)
            PgDiffTriggers.createTriggers(oldSchema, newSchema, searchPathHelper)
            PgDiffViews.createViews(oldSchema, newSchema, searchPathHelper)
            PgDiffViews.alterViews(oldSchema, newSchema, searchPathHelper)

            PgDiffFunctions.alterComments(oldSchema, newSchema, searchPathHelper)
            PgDiffConstraints.alterComments(oldSchema, newSchema, searchPathHelper)
            PgDiffIndexes.alterComments(oldSchema, newSchema, searchPathHelper)
            PgDiffTriggers.alterComments(oldSchema, newSchema, searchPathHelper)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage='Usage: apgdiff [options] <old_dump> <new_dump>')

    parser.add_argument('old_dump', nargs='?')
    parser.add_argument('new_dump', nargs='?')

    parser.add_argument('--add-transaction', dest='add_transaction', action='store_true', help="Adds START TRANSACTION and COMMIT TRANSACTION to the generated diff file")
    parser.add_argument('--add-defaults', dest='addDefaults', action='store_true', help="adds DEFAULT ... in case new column has NOT NULL constraint but no default value (the default value is dropped later)")
    parser.add_argument('--ignore-start-with', dest='ignoreStartWith', action='store_false', help="ignores START WITH modifications on SEQUENCEs (default is not to ignore these changes)")

    arguments = parser.parse_args()

    PgDiff().createDiff(arguments)