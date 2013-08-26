from parser.Parser import Parser, ParserUtils
from schema.PgFunction import PgFunction, Argument

class CreateFunctionParser(object):
    @staticmethod
    def parse(database, statement):
        parser = Parser(statement)
        parser.expect("CREATE")
        parser.expectOptional("OR", "REPLACE")
        parser.expect("FUNCTION")

        functionName = parser.parseIdentifier();
        schemaName = ParserUtils.getSchemaName(functionName, database)
        schema = database.getSchema(schemaName)

        if schema is None:
            raise Exception("Cannot find schema '%s' for statement '%s'. Missing CREATE SCHEMA statement?" % (schemaName, statement))

        function = PgFunction()
        function.name = ParserUtils.getObjectName(functionName)

        parser.expect("(")

        while not parser.expectOptional(")"):
            mode = ''

            if parser.expectOptional("IN"):
                mode = "IN"
            elif parser.expectOptional("OUT"):
                mode = "OUT"
            elif parser.expectOptional("INOUT"):
                mode = "INOUT"
            elif parser.expectOptional("VARIADIC"):
                mode = "VARIADIC"
            else:
                mode = None

            position = parser.position
            argumentName = None
            dataType = parser.parseDataType()

            position2 = parser.position

            if (not parser.expectOptional(")") and not parser.expectOptional(",")
                    and not parser.expectOptional("=")
                    and not parser.expectOptional("DEFAULT")):
                parser.position = position
                argumentName = ParserUtils.getObjectName(parser.parseIdentifier())
                dataType = parser.parseDataType()
            else:
                parser.position = position2

            defaultExpression = ''

            if (parser.expectOptional("=")
                    or parser.expectOptional("DEFAULT")):
                defaultExpression = parser.getExpression()
            else:
                defaultExpression = None

            argument = Argument()
            argument.dataType = dataType
            argument.defaultExpression = defaultExpression
            argument.mode = mode
            argument.name = argumentName
            function.addArgument(argument)

            if (parser.expectOptional(")")):
                break
            else:
                parser.expect(",")

        function.body = parser.getRest()

        schema.addFunction(function)
