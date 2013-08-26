from parser.Parser import Parser, ParserUtils
from schema.PgView import PgView

class CreateViewParser(object):
    @staticmethod
    def parse(database, statement):
        parser = Parser(statement)
        parser.expect("CREATE")
        parser.expectOptional("OR", "REPLACE")
        parser.expect("VIEW")

        viewName = parser.parseIdentifier()

        columnsExist = parser.expectOptional("(")
        columnNames = list()

        if (columnsExist):
            while not parser.expectOptional(")"):
                columnNames.append(ParserUtils.getObjectName(parser.parseIdentifier()))
                parser.expectOptional(",")

        parser.expect("AS")

        query = parser.getRest()

        view = PgView(ParserUtils.getObjectName(viewName))
        view.columnNames = columnNames
        view.query = query

        schemaName = ParserUtils.getSchemaName(viewName, database)
        schema = database.getSchema(schemaName)

        if schema is None:
            raise Exception("CannotFindSchema" % (schemaName, statement))

        schema.addView(view)
