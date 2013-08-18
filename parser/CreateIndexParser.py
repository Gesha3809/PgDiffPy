from parser.Parser import Parser, ParserUtils
from schema.PgIndex import PgIndex

class CreateIndexParser(object):
    @staticmethod
    def parse(database, statement):
        parser = Parser(statement)
        parser.expect("CREATE")

        unique = parser.expectOptional("UNIQUE")

        parser.expect("INDEX")
        parser.expectOptional("CONCURRENTLY")

        indexName = ParserUtils.getObjectName(parser.parseIdentifier())

        parser.expect("ON")

        tableName = parser.parseIdentifier()
        definition = parser.getRest()
        schemaName =ParserUtils.getSchemaName(tableName, database)
        schema = database.getSchema(schemaName)

        if (schema is None):
            print 'ERROR: CreateIndexParser[Line 21]'
            # throw new RuntimeException(MessageFormat.format(
            #         Resources.getString("CannotFindSchema"), schemaName,
            #         statement));

        objectName = ParserUtils.getObjectName(tableName)
        table = schema.getTable(objectName)

        if (table is None):
            print 'ERROR: CreateIndexParser[Line 32]'
            # throw new RuntimeException(MessageFormat.format(
            #         Resources.getString("CannotFindTable"), tableName,
            #         statement));

        index = PgIndex(indexName)
        table.addIndex(index)
        schema.addIndex(index)
        index.definition = definition.strip()
        index.tableName = table.name
        index.unique = unique
