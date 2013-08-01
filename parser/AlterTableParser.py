from parser.Parser import Parser, ParserUtils

class AlterTableParser(object):
    def __init__(self):
        pass

    def parse(self, database, statement):
        parser = Parser(statement)

        parser.expect("ALTER", "TABLE")
        parser.expectOptional("ONLY")

        tableName = parser.parseIdentifier()
        schemaName = ParserUtils.getSchemaName(tableName, database)
        schema = database.getSchema(schemaName)

        if schema is None:
            raise Exception("CannotFindSchema")

        objectName = ParserUtils.getObjectName(tableName)
        table = schema.getTable(objectName)

        if table is None:
            print 'NOT IMPLEMENTED. AlterTableParser.java:55'

        while not parser.expectOptional(";"):
            if parser.expectOptional("ALTER"):
                AlterTableParser.parseAlterColumn(parser, table)
            elif (parser.expectOptional("CLUSTER", "ON")):
                print 'table.setClusterIndexName(ParserUtils.getObjectName(parser.parseIdentifier()));'
            elif (parser.expectOptional("OWNER", "TO")):
                # we do not parse this one so we just consume the identifier
                # if (outputIgnoredStatements):
                #     print 'database.addIgnoredStatement("ALTER TABLE " + tableName + " OWNER TO " + parser.parseIdentifier() + ';')'
                # else:
                    parser.parseIdentifier()
            elif (parser.expectOptional("ADD")):
                if (parser.expectOptional("FOREIGN", "KEY")):
                    print 'parseAddForeignKey(parser, table);'
                elif (parser.expectOptional("CONSTRAINT")):
                    print 'parseAddConstraint(parser, table, schema);'
                else:
                    parser.throwUnsupportedCommand()
            elif (parser.expectOptional("ENABLE")):
                print 'parseEnable(parser, outputIgnoredStatements, tableName, database);'
            elif (parser.expectOptional("DISABLE")):
                print 'parseDisable(parser, outputIgnoredStatements, tableName, database);'
            else:
                parser.throwUnsupportedCommand()

            if (parser.expectOptional(";")):
                break
            else:
                parser.expect(",")

    @staticmethod
    def parseAlterColumn(parser, table):
        parser.expectOptional("COLUMN")

        columnName = ParserUtils.getObjectName(parser.parseIdentifier());

        if parser.expectOptional("SET"):
            if parser.expectOptional("STATISTICS"):
                column = table.columns[columnName]

                if column is None:
                    raise Exception("Cannot find column '%s' in table '%s' for statement '%s'.") % (columnName, table.name, parser.statement)

                column.statistics = parser.parseInteger()
            elif parser.expectOptional("DEFAULT"):
                defaultValue = parser.getExpression()

                if columnName in table.columns:
                    column = table.columns[columnName]

                    if column is None:
                        raise Exception("Cannot find column '%s' in table '%s' for statement '%s'.") % (columnName, table.name, parser.statement)

                    column.defaultValue = defaultValue
                else:
                    raise Exception("Cannot find column '%s' in table '%s' for statement '%s'.") % (columnName, table.name, parser.statement)

            elif parser.expectOptional("STORAGE"):
                column = table.columns[columnName]

                if (column is None):
                    raise Exception("Cannot find column '%s' in table '%s' for statement '%s'.") % (columnName, table.name, parser.statement)

                if parser.expectOptional("PLAIN"):
                    column.storage = "PLAIN"
                elif parser.expectOptional("EXTERNAL"):
                    column.storage = "EXTERNAL"
                elif parser.expectOptional("EXTENDED"):
                    column.storage = "EXTENDED"
                elif parser.expectOptional("MAIN"):
                    column.storage = "MAIN"
                else:
                    parser.throwUnsupportedCommand()
            else:
                parser.throwUnsupportedCommand()
        else:
            parser.throwUnsupportedCommand()
