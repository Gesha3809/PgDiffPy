from parser.Parser import Parser, ParserUtils
from schema.PgView import PgView

class CreateViewParser(object):
    @staticmethod
    def parse(database, statement):
        parser = Parser(statement)
        parser.expect("CREATE")
        parser.expect_optional("OR", "REPLACE")
        parser.expect("VIEW")

        viewName = parser.parse_identifier()

        columnsExist = parser.expect_optional("(")
        columnNames = list()

        if (columnsExist):
            while not parser.expect_optional(")"):
                columnNames.append(ParserUtils.get_object_name(parser.parse_identifier()))
                parser.expect_optional(",")

        parser.expect("AS")

        query = parser.get_rest()

        view = PgView(ParserUtils.get_object_name(viewName))
        view.columnNames = columnNames
        view.query = query

        schemaName = ParserUtils.get_schema_name(viewName, database)
        schema = database.getSchema(schemaName)

        if schema is None:
            raise Exception("CannotFindSchema" % (schemaName, statement))

        schema.addView(view)
