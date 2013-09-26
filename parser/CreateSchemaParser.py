from parser.Parser import Parser, ParserUtils
from schema.PgSchema import PgSchema

class CreateSchemaParser(object):
	@staticmethod
	def parse(database, statement):
		parser = Parser(statement)
		parser.expect("CREATE", "SCHEMA")

		if parser.expect_optional("AUTHORIZATION"):
			schema = PgSchema(ParserUtils.get_object_name(parser.parse_identifier()))
			database.addSchema(schema)
			schema.authorization = schema.name

		else:
			schemaName = ParserUtils.get_object_name(parser.parse_identifier())
			schema = PgSchema(schemaName)
			database.schemas[schemaName] = schema

			if parser.expect_optional("AUTHORIZATION"):
				schema.authorization = ParserUtils.get_object_name(parser.parse_identifier())

		definition = parser.get_rest()

		if definition:
			schema.definition = definition