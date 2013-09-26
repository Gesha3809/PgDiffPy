from parser.Parser import Parser, ParserUtils
from schema.PgTable import PgTable
from schema.PgConstraint import PgConstraint
from schema.PgColumn import PgColumn


class CreateTableParser(object):
    @staticmethod
    def parse(database, statement):
        parser = Parser(statement)
        parser.expect('CREATE', 'TABLE')

        # Optional IF NOT EXISTS, irrelevant for our purposes
        parser.expect_optional("IF", "NOT", "EXISTS")

        tableName = ParserUtils.get_object_name(parser.parse_identifier())
        table = PgTable(tableName)
        # Figure it out why do we need this
        schemaName = ParserUtils.get_schema_name(tableName, database)
        schema = database.getSchema(schemaName)

        if schema is None:
            raise Exception("Cannot find schema \'%s\' for statement \'%s\'. Missing CREATE SCHEMA statement?" % (schemaName, statement))

        schema.addTable(table)

        parser.expect("(")

        while not parser.expect_optional(")"):
            if parser.expect_optional("CONSTRAINT"):
                CreateTableParser.parseConstraint(parser, table)
            else:
                CreateTableParser.parseColumn(parser, table)

            if parser.expect_optional(")"):
                break
            else:
                parser.expect(",")


        while not parser.expect_optional(";"):
            if parser.expect_optional("INHERITS"):
                CreateTableParser.parseInherits(parser, table)
            elif parser.expect_optional("WITHOUT"):
                table.oids = "OIDS=false"
            elif parser.expect_optional("WITH"):
                if (parser.expect_optional("OIDS") or parser.expect_optional("OIDS=true")):
                    table.oids = "OIDS=true"
                elif parser.expect_optional("OIDS=false"):
                    table.oids = "OIDS=false"
                else:
                    print 'table.setWith(parser.getExpression())'
            elif parser.expect_optional("TABLESPACE"):
                print 'table.setTablespace(parser.parseString()'
            else:
                parser.throw_unsupported_command()

    @staticmethod
    def parseConstraint(parser, table):
        constraint = PgConstraint(ParserUtils.get_object_name(parser.parse_identifier()));
        table.addConstraint(constraint)
        constraint.definition = parser.get_expression()
        constraint.tableName = table.name

    @staticmethod
    def parseColumn(parser, table):
        column = PgColumn(ParserUtils.get_object_name(parser.parse_identifier()))
        table.addColumn(column)
        column.parseDefinition(parser.get_expression())

    @staticmethod
    def parseInherits(parser, table):
        parser.expect("(")

        while not parser.expect_optional(")"):
            table.addInherits(ParserUtils.get_object_name(parser.parse_identifier()))

            if parser.expect_optional(")"):
                break
            else:
                parser.expect(",")

