from parser.Parser import Parser, ParserUtils
from schema.PgSequence import PgSequence

class CreateSequenceParser(object):
    @staticmethod
    def parse(database, statement):
        parser = Parser(statement)
        parser.expect("CREATE", "SEQUENCE")

        sequenceName = parser.parseIdentifier();
        sequence = PgSequence(ParserUtils.getObjectName(sequenceName))
        schemaName = ParserUtils.getSchemaName(sequenceName, database)
        schema = database.getSchema(schemaName)

        if schema is None:
            raise Exception("Cannot find schema '%s' for statement '%s'. Missing CREATE SCHEMA statement?" % (schemaName, statement))

        schema.addSequence(sequence)

        while not parser.expectOptional(";"):
            if parser.expectOptional("INCREMENT"):
                parser.expectOptional("BY")
                sequence.increment = parser.parseString()
            elif parser.expectOptional("MINVALUE"):
                sequence.minValue = parser.parseString()
            elif parser.expectOptional("MAXVALUE"):
                sequence.maxValue = parser.parseString()
            elif parser.expectOptional("START"):
                parser.expectOptional("WITH")
                sequence.startWith = parser.parseString()
            elif parser.expectOptional("CACHE"):
                sequence.cache = parser.parseString()
            elif parser.expectOptional("CYCLE"):
                sequence.cycle = True
            elif parser.expectOptional("OWNED", "BY"):
                if parser.expectOptional("NONE"):
                    sequence.ownedBy = None
                else:
                    sequence.ownedBy = ParserUtils.getObjectName(parser.parseIdentifier())

            elif parser.expectOptional("NO"):
                if parser.expectOptional("MINVALUE"):
                    sequence.minValue = None
                elif parser.expectOptional("MAXVALUE"):
                    sequence.maxValue = None
                elif parser.expectOptional("CYCLE"):
                    sequence.cycle = False
                else:
                    parser.throwUnsupportedCommand()

            else:
                parser.throwUnsupportedCommand()
