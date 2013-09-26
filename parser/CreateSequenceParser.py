from parser.Parser import Parser, ParserUtils
from schema.PgSequence import PgSequence

class CreateSequenceParser(object):
    @staticmethod
    def parse(database, statement):
        parser = Parser(statement)
        parser.expect("CREATE", "SEQUENCE")

        sequenceName = parser.parse_identifier();
        sequence = PgSequence(ParserUtils.get_object_name(sequenceName))
        schemaName = ParserUtils.get_schema_name(sequenceName, database)
        schema = database.getSchema(schemaName)

        if schema is None:
            raise Exception("Cannot find schema '%s' for statement '%s'. Missing CREATE SCHEMA statement?" % (schemaName, statement))

        schema.addSequence(sequence)

        while not parser.expect_optional(";"):
            if parser.expect_optional("INCREMENT"):
                parser.expect_optional("BY")
                sequence.increment = parser.parse_string()
            elif parser.expect_optional("MINVALUE"):
                sequence.minValue = parser.parse_string()
            elif parser.expect_optional("MAXVALUE"):
                sequence.maxValue = parser.parse_string()
            elif parser.expect_optional("START"):
                parser.expect_optional("WITH")
                sequence.startWith = parser.parse_string()
            elif parser.expect_optional("CACHE"):
                sequence.cache = parser.parse_string()
            elif parser.expect_optional("CYCLE"):
                sequence.cycle = True
            elif parser.expect_optional("OWNED", "BY"):
                if parser.expect_optional("NONE"):
                    sequence.ownedBy = None
                else:
                    sequence.ownedBy = ParserUtils.get_object_name(parser.parse_identifier())

            elif parser.expect_optional("NO"):
                if parser.expect_optional("MINVALUE"):
                    sequence.minValue = None
                elif parser.expect_optional("MAXVALUE"):
                    sequence.maxValue = None
                elif parser.expect_optional("CYCLE"):
                    sequence.cycle = False
                else:
                    parser.throw_unsupported_command()

            else:
                parser.throw_unsupported_command()
