from parser.Parser import Parser, ParserUtils
from schema.PgTable import PgTable
from schema.PgConstraint import PgConstraint
from schema.PgColumn import PgColumn

class CreateTableParser(object):
    def __init__(self):
        pass

    def parse(self, database, statement):
        parser = Parser(statement)
        parser.expect('CREATE', 'TABLE')

        # Optional IF NOT EXISTS, irrelevant for our purposes
        parser.expectOptional("IF", "NOT", "EXISTS")

        tableName = parser.parseIdentifier()
        table = PgTable(tableName)
        # Figure it out why do we need this
        schemaName = ParserUtils.getSchemaName(tableName, database)
        schema = database.getSchema(schemaName)

        if schema is None:
            raise Exception("Cannot find schema \'%s\' for statement \'%s\'. Missing CREATE SCHEMA statement?" % (schemaName, statement))

        schema.addTable(table)

        parser.expect("(")

        while not parser.expectOptional(")"):
            if parser.expectOptional("CONSTRAINT"):
                self.parseConstraint(parser, table)
            else:
                self.parseColumn(parser, table)

            if parser.expectOptional(")"):
                break
            else:
                parser.expect(",")


        while not parser.expectOptional(";"):
            if parser.expectOptional("INHERITS"):
                self.parseInherits(parser, table)
            elif parser.expectOptional("WITHOUT"):
                table.oids = "OIDS=false"
            elif parser.expectOptional("WITH"):
                if (parser.expectOptional("OIDS") or parser.expectOptional("OIDS=true")):
                    table.oids = "OIDS=true"
                elif parser.expectOptional("OIDS=false"):
                    table.oids = "OIDS=false"
                else:
                    print 'table.setWith(parser.getExpression())'
            elif parser.expectOptional("TABLESPACE"):
                print 'table.setTablespace(parser.parseString()'
            else:
                parser.throwUnsupportedCommand()


    def parseConstraint(self, parser, table):
        #pass
        #constraint = PgConstraint(ParserUtils.getObjectName(parser.parseIdentifier()));
        # print parser.parseIdentifier()
        # table.addConstraint(constraint);
        # constraint.setDefinition(parser.getExpression());
        # constraint.setTableName(table.getName());
        print 'Found constraint!!!'

    def parseColumn(self, parser, table):
        column = PgColumn(ParserUtils.getObjectName(parser.parseIdentifier()))
        table.addColumn(column)
        column.parseDefinition(parser.getExpression())

    def parseInherits(self, parser, table):
        parser.expect("(")

        while not parser.expectOptional(")"):
            table.addInherits(ParserUtils.getObjectName(parser.parseIdentifier()))

            if parser.expectOptional(")"):
                break
            else:
                parser.expect(",")

