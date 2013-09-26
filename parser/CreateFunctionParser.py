from parser.Parser import Parser, ParserUtils
from schema.PgFunction import PgFunction, Argument

class CreateFunctionParser(object):
    @staticmethod
    def parse(database, statement):
        parser = Parser(statement)
        parser.expect("CREATE")
        parser.expect_optional("OR", "REPLACE")
        parser.expect("FUNCTION")

        functionName = parser.parse_identifier();
        schemaName = ParserUtils.get_schema_name(functionName, database)
        schema = database.getSchema(schemaName)

        if schema is None:
            raise Exception("Cannot find schema '%s' for statement '%s'. Missing CREATE SCHEMA statement?" % (schemaName, statement))

        function = PgFunction()
        function.name = ParserUtils.get_object_name(functionName)

        parser.expect("(")

        while not parser.expect_optional(")"):
            mode = None

            if parser.expect_optional("IN"):
                mode = "IN"
            elif parser.expect_optional("OUT"):
                mode = "OUT"
            elif parser.expect_optional("INOUT"):
                mode = "INOUT"
            elif parser.expect_optional("VARIADIC"):
                mode = "VARIADIC"

            position = parser.position
            argumentName = None
            dataType = parser.parse_data_type()

            position2 = parser.position

            if (not parser.expect_optional(")") and not parser.expect_optional(",")
                    and not parser.expect_optional("=")
                    and not parser.expect_optional("DEFAULT")):
                parser.position = position
                argumentName = ParserUtils.get_object_name(parser.parse_identifier())
                dataType = parser.parse_data_type()
            else:
                parser.position = position2

            defaultExpression = ''

            if (parser.expect_optional("=")
                    or parser.expect_optional("DEFAULT")):
                defaultExpression = parser.get_expression()
            else:
                defaultExpression = None

            argument = Argument()
            argument.dataType = dataType
            argument.defaultExpression = defaultExpression
            argument.mode = mode
            argument.name = argumentName
            function.addArgument(argument)

            if (parser.expect_optional(")")):
                break
            else:
                parser.expect(",")

        function.body = parser.get_rest()

        schema.addFunction(function)
