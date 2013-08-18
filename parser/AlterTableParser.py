from parser.Parser import Parser, ParserUtils
from schema.PgConstraint import PgConstraint

class AlterTableParser(object):

    @staticmethod
    def parse(database, statement):
        parser = Parser(statement)

        parser.expect("ALTER", "TABLE")
        parser.expectOptional("ONLY")

        tableName = parser.parseIdentifier()
        schemaName = ParserUtils.getSchemaName(tableName, database)
        schema = database.getSchema(schemaName)

        if schema is None:
            raise Exception("CannotFindSchema")

        objectName = ParserUtils.getObjectName(tableName)
        table = schema.tables.get(objectName)

        if table is None:
            view = schema.views.get(objectName)

            if view is not None:
                AlterTableParser.parseView(parser, view, tableName, database)
                return

            sequence = schema.sequences.get(objectName)

            if sequence is not None:
                AlterTableParser.parseSequence(parser, sequence, tableName, database);
                return

            raise Exception("Cannot find object '%s' for statement '%s'." % (tableName, statement))

        while not parser.expectOptional(";"):
            if parser.expectOptional("ALTER"):
                AlterTableParser.parseAlterColumn(parser, table)
            elif (parser.expectOptional("CLUSTER", "ON")):
                table.clusterIndexName = ParserUtils.getObjectName(parser.parseIdentifier())
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
                    AlterTableParser.parseAddConstraint(parser, table, schema)
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

    @staticmethod
    def parseAddConstraint(parser, table, schema):
        constraintName = ParserUtils.getObjectName(parser.parseIdentifier())
        constraint = PgConstraint(constraintName)
        constraint.tableName = table.name
        table.addConstraint(constraint)

        if parser.expectOptional("PRIMARY", "KEY"):
            schema.addPrimaryKey(constraint)
            constraint.definition = "PRIMARY KEY " + parser.getExpression()
        else:
            constraint.setDefinition = parser.getExpression()
            
    @staticmethod
    def parseView(parser, view, viewName, database):
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
                    parser.parseIdentifier()
            else:
                parser.throwUnsupportedCommand()
    
    @staticmethod
    def parseSequence(parser, sequence,  sequenceName, database):
        while not parser.expectOptional(";"):
            if parser.expectOptional("OWNER", "TO"):
                    parser.parseIdentifier()
            else:
                parser.throwUnsupportedCommand()
