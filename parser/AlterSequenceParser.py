from parser.Parser import Parser, ParserUtils
from schema.PgSequence import PgSequence

class AlterSequenceParser(object):
    @staticmethod
    def parse(database, statement):
        parser = Parser(statement)

        parser.expect("ALTER", "SEQUENCE")

        sequenceName = parser.parseIdentifier()
        schemaName = ParserUtils.getSchemaName(sequenceName, database)
        schema = database.getSchema(schemaName)

        if schema is None:
            raise Exception("CannotFindSchema")

        objectName = ParserUtils.getObjectName(sequenceName);
        sequence = schema.sequences[objectName]

        if sequence is None:
            raise Exception("Cannot find sequence '%s' for statement '%s'. Missing CREATE SEQUENCE?" % (sequenceName, statement))

        while not parser.expectOptional(";"):

            if (parser.expectOptional("OWNED", "BY")):
                if parser.expectOptional("NONE"):
                    sequence.ownedBy = None
                else:
                    sequence.ownedBy = parser.getExpression()
            else:
                parser.throwUnsupportedCommand()