from parser.Parser import Parser, ParserUtils
from schema import PgView

class AlterViewParser(object):
    @staticmethod
    def parse(database, statement):
        parser = Parser(statement)
        parser.expect("ALTER", "VIEW")

        viewName = parser.parse_identifier()
        schemaName = ParserUtils.get_schema_name(viewName, database)
        schema = database.getSchema(schemaName)

        if schema is None:
            raise Exception("Cannot find schema '%s' for statement '%s'. Missing CREATE SCHEMA statement?" % (schemaName, statement))

        objectName = ParserUtils.get_object_name(viewName)
        view = schema.views[objectName]

        if view is None:
            raise Exception("Cannot find view '%s' for statement '%s'. Missing CREATE VIEW statement?" % (viewName, statement))

        while not parser.expect_optional(";"):
            if parser.expect_optional("ALTER"):
                parser.expect_optional("COLUMN")

                columnName = ParserUtils.get_object_name(parser.parse_identifier())

                if parser.expect_optional("SET", "DEFAULT"):
                    expression = parser.get_expression()
                    view.addColumnDefaultValue(columnName, expression)
                elif parser.expect_optional("DROP", "DEFAULT"):
                    view.removeColumnDefaultValue(columnName)
                else:
                    parser.throw_unsupported_command()

            elif parser.expect_optional("OWNER", "TO"):
                # we do not parse this one so we just consume the identifier
                # if (outputIgnoredStatements) {
                #     database.addIgnoredStatement("ALTER TABLE " + viewName
                #             + " OWNER TO " + parser.parseIdentifier() + ';');
                # } else {
                parser.parse_identifier()
                # }
            else:
                parser.throw_unsupported_command()