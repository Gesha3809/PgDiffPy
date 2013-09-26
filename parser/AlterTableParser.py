from parser.Parser import Parser, ParserUtils
from schema.PgConstraint import PgConstraint

class AlterTableParser(object):

    @staticmethod
    def parse(database, statement):
        parser = Parser(statement)

        parser.expect("ALTER", "TABLE")
        parser.expect_optional("ONLY")

        tableName = parser.parse_identifier()
        schemaName = ParserUtils.get_schema_name(tableName, database)
        schema = database.getSchema(schemaName)

        if schema is None:
            raise Exception("CannotFindSchema")

        objectName = ParserUtils.get_object_name(tableName)
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

        while not parser.expect_optional(";"):
            if parser.expect_optional("ALTER"):
                AlterTableParser.parseAlterColumn(parser, table)
            elif (parser.expect_optional("CLUSTER", "ON")):
                table.clusterIndexName = ParserUtils.get_object_name(parser.parse_identifier())
            elif (parser.expect_optional("OWNER", "TO")):
                # we do not parse this one so we just consume the identifier
                # if (outputIgnoredStatements):
                #     print 'database.addIgnoredStatement("ALTER TABLE " + tableName + " OWNER TO " + parser.parseIdentifier() + ';')'
                # else:
                    parser.parse_identifier()
            elif (parser.expect_optional("ADD")):
                if (parser.expect_optional("FOREIGN", "KEY")):
                    print 'parseAddForeignKey(parser, table);'
                elif (parser.expect_optional("CONSTRAINT")):
                    AlterTableParser.parseAddConstraint(parser, table, schema)
                else:
                    parser.throw_unsupported_command()
            elif (parser.expect_optional("ENABLE")):
                print 'parseEnable(parser, outputIgnoredStatements, tableName, database);'
            elif (parser.expect_optional("DISABLE")):
                print 'parseDisable(parser, outputIgnoredStatements, tableName, database);'
            else:
                parser.throw_unsupported_command()

            if (parser.expect_optional(";")):
                break
            else:
                parser.expect(",")

    @staticmethod
    def parseAlterColumn(parser, table):
        parser.expect_optional("COLUMN")

        columnName = ParserUtils.get_object_name(parser.parse_identifier());

        if parser.expect_optional("SET"):
            if parser.expect_optional("STATISTICS"):
                column = table.columns[columnName]

                if column is None:
                    raise Exception("Cannot find column '%s' in table '%s' for statement '%s'.") % (columnName, table.name, parser.statement)

                column.statistics = parser.parse_integer()
            elif parser.expect_optional("DEFAULT"):
                defaultValue = parser.get_expression()

                if columnName in table.columns:
                    column = table.columns[columnName]

                    if column is None:
                        raise Exception("Cannot find column '%s' in table '%s' for statement '%s'.") % (columnName, table.name, parser.statement)

                    column.defaultValue = defaultValue
                else:
                    raise Exception("Cannot find column '%s' in table '%s' for statement '%s'.") % (columnName, table.name, parser.statement)

            elif parser.expect_optional("STORAGE"):
                column = table.columns[columnName]

                if (column is None):
                    raise Exception("Cannot find column '%s' in table '%s' for statement '%s'.") % (columnName, table.name, parser.statement)

                if parser.expect_optional("PLAIN"):
                    column.storage = "PLAIN"
                elif parser.expect_optional("EXTERNAL"):
                    column.storage = "EXTERNAL"
                elif parser.expect_optional("EXTENDED"):
                    column.storage = "EXTENDED"
                elif parser.expect_optional("MAIN"):
                    column.storage = "MAIN"
                else:
                    parser.throw_unsupported_command()
            else:
                parser.throw_unsupported_command()
        else:
            parser.throw_unsupported_command()

    @staticmethod
    def parseAddConstraint(parser, table, schema):
        constraintName = ParserUtils.get_object_name(parser.parse_identifier())
        constraint = PgConstraint(constraintName)
        constraint.tableName = table.name
        table.addConstraint(constraint)

        if parser.expect_optional("PRIMARY", "KEY"):
            schema.addPrimaryKey(constraint)
            constraint.definition = "PRIMARY KEY " + parser.get_expression()
        else:
            constraint.definition = parser.get_expression()

    @staticmethod
    def parseView(parser, view, viewName, database):
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
                    parser.parse_identifier()
            else:
                parser.throw_unsupported_command()

    @staticmethod
    def parseSequence(parser, sequence,  sequenceName, database):
        while not parser.expect_optional(";"):
            if parser.expect_optional("OWNER", "TO"):
                    parser.parse_identifier()
            else:
                parser.throw_unsupported_command()
