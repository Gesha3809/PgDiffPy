from parser.Parser import Parser, ParserUtils
from schema.PgSequence import PgSequence

class AlterSequenceParser(object):
    @staticmethod
    def parse(database, statement):
        parser = Parser(statement)

        parser.expect("ALTER", "SEQUENCE")

        sequenceName = parser.parse_identifier()
        schemaName = ParserUtils.get_schema_name(sequenceName, database)
        schema = database.getSchema(schemaName)

        if schema is None:
            raise Exception("CannotFindSchema")

        objectName = ParserUtils.get_object_name(sequenceName);
        sequence = schema.sequences[objectName]

        if sequence is None:
            raise Exception("Cannot find sequence '%s' for statement '%s'. Missing CREATE SEQUENCE?" % (sequenceName, statement))

        while not parser.expect_optional(";"):

            if (parser.expect_optional("OWNED", "BY")):
                if parser.expect_optional("NONE"):
                    sequence.ownedBy = None
                else:
                    sequence.ownedBy = parser.get_expression()
            else:
                parser.throw_unsupported_command()