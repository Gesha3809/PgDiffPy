from parser.Parser import Parser, ParserUtils
from schema.PgSchema import PgSchema

class CreateSchemaParser(object):
	@staticmethod
	def parse(database, statement):
		parser = Parser(statement)
		parser.expect("CREATE", "SCHEMA")

		if parser.expectOptional("AUTHORIZATION"):
			schema = PgSchema(ParserUtils.getObjectName(parser.parseIdentifier()))
			database.addSchema(schema)
			schema.authorization = schema.name

		else:
			schemaName = ParserUtils.getObjectName(parser.parseIdentifier())
			schema = PgSchema(schemaName)
			database.schemas[schemaName] = schema

			if parser.expectOptional("AUTHORIZATION"):
				schema.authorization = ParserUtils.getObjectName(parser.parseIdentifier())

		definition = parser.getRest()

		if definition:
			schema.definition = definition