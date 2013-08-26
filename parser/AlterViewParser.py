from parser.Parser import Parser, ParserUtils
from schema import PgView

class AlterViewParser(object):
    @staticmethod
    def parse(database, statement):
        parser = Parser(statement)
        parser.expect("ALTER", "VIEW")

        viewName = parser.parseIdentifier()
        schemaName = ParserUtils.getSchemaName(viewName, database)
        schema = database.getSchema(schemaName)

        if schema is None:
            raise Exception("Cannot find schema '%s' for statement '%s'. Missing CREATE SCHEMA statement?" % (schemaName, statement))

        objectName = ParserUtils.getObjectName(viewName)
        view = schema.views[objectName]

        if view is None:
            raise Exception("Cannot find view '%s' for statement '%s'. Missing CREATE VIEW statement?" % (viewName, statement))

        while not parser.expectOptional(";"):
            if parser.expectOptional("ALTER"):
                parser.expectOptional("COLUMN")

                columnName = ParserUtils.getObjectName(parser.parseIdentifier())

                if parser.expectOptional("SET", "DEFAULT"):
                    expression = parser.getExpression()
                    view.addColumnDefaultValue(columnName, expression)
                elif parser.expectOptional("DROP", "DEFAULT"):
                    view.removeColumnDefaultValue(columnName)
                else:
                    parser.throwUnsupportedCommand()

            elif parser.expectOptional("OWNER", "TO"):
                # we do not parse this one so we just consume the identifier
                # if (outputIgnoredStatements) {
                #     database.addIgnoredStatement("ALTER TABLE " + viewName
                #             + " OWNER TO " + parser.parseIdentifier() + ';');
                # } else {
                parser.parseIdentifier()
                # }
            else:
                parser.throwUnsupportedCommand()