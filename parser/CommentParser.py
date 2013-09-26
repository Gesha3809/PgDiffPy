from parser.Parser import Parser, ParserUtils
from schema.PgFunction import PgFunction, Argument

class CommentParser(object):

    @staticmethod
    def parse(database, statement):
        parser = Parser(statement)
        parser.expect("COMMENT", "ON")

        if parser.expect_optional("TABLE"):
            CommentParser.parseTable(parser, database)
        elif parser.expect_optional("COLUMN"):
            CommentParser.parseColumn(parser, database)
        elif parser.expect_optional("CONSTRAINT"):
            CommentParser.parseConstraint(parser, database)
        elif parser.expect_optional("DATABASE"):
            CommentParser.parseDatabase(parser, database)
        elif parser.expect_optional("FUNCTION"):
            CommentParser.parseFunction(parser, database)
        elif parser.expect_optional("INDEX"):
            CommentParser.parseIndex(parser, database)
        elif parser.expect_optional("SCHEMA"):
            CommentParser.parseSchema(parser, database)
        elif parser.expect_optional("SEQUENCE"):
            CommentParser.parseSequence(parser, database)
        elif parser.expect_optional("TRIGGER"):
            CommentParser.parseTrigger(parser, database)
        elif parser.expect_optional("VIEW"):
            CommentParser.parseView(parser, database)
        # elif outputIgnoredStatements:
        #     database.addIgnoredStatement(statement)

    @staticmethod
    def parseTable(parser, database):
        tableName = parser.parse_identifier()
        objectName = ParserUtils.get_object_name(tableName)
        schemaName = ParserUtils.get_schema_name(tableName, database)

        table = database.getSchema(schemaName).getTable(objectName)

        parser.expect("IS")
        table.comment = CommentParser.getComment(parser)
        parser.expect(";")

    @staticmethod
    def parseColumn(parser, database):
        columnName = parser.parse_identifier()
        objectName = ParserUtils.get_object_name(columnName)
        tableName = ParserUtils.get_second_object_name(columnName)
        schemaName = ParserUtils.get_third_object_name(columnName)
        schema = database.getSchema(schemaName)

        table = schema.getTable(tableName)

        if table is None:
            view = schema.views[tableName]
            parser.expect("IS")

            comment = CommentParser.getComment(parser)

            if comment is None:
                view.removeColumnComment(objectName)
            else:
                view.addColumnComment(objectName, comment)
            parser.expect(";")
        else:
            column = table.columns.get(objectName)

            if column is None:
                raise Error("Cannot find column '%s' in table '%s'" % (columnName, table.name))

            parser.expect("IS")
            column.comment = CommentParser.getComment(parser)
            parser.expect(";")

    @staticmethod
    def parseConstraint(parser, database):
        constraintName = ParserUtils.get_object_name(parser.parse_identifier())

        parser.expect("ON")

        tableName = parser.parse_identifier()
        objectName = ParserUtils.get_object_name(tableName)
        schemaName = ParserUtils.get_schema_name(constraintName, database)

        constraint = database.getSchema(schemaName).getTable(objectName).constraints[constraintName]

        parser.expect("IS")
        constraint.comment = CommentParser.getComment(parser)
        parser.expect(";")


    @staticmethod
    def parseDatabase(parser, database):
        parser.parse_identifier()
        parser.expect("IS")
        database.comment = CommentParser.getComment(parser)
        parser.expect(";")

    @staticmethod
    def parseFunction(parser, database):
        functionName = parser.parse_identifier()
        objectName = ParserUtils.get_object_name(functionName)
        schemaName = ParserUtils.get_schema_name(functionName, database)
        schema = database.getSchema(schemaName)

        parser.expect("(")

        tmpFunction = PgFunction()
        tmpFunction.name = objectName

        while not parser.expect_optional(")"):
            mode = ''

            if parser.expect_optional("IN"):
                mode = "IN"
            elif parser.expect_optional("OUT"):
                mode = "OUT"
            elif parser.expect_optional("INOUT"):
                mode = "INOUT"
            elif parser.expect_optional("VARIADIC"):
                mode = "VARIADIC"
            else:
                mode = None

            position = parser.position
            argumentName = None
            dataType = parser.parse_data_type()

            position2 = parser.position

            if not parser.expect_optional(")") and not parser.expect_optional(","):
                parser.position = position
                argumentName = ParserUtils.get_object_name(parser.parse_identifier())
                dataType = parser.parse_data_type()
            else:
                parser.position = position2

            argument = Argument()
            argument.dataType = dataType
            argument.mode = mode
            argument.name = argumentName
            tmpFunction.addArgument(argument)

            if parser.expect_optional(")"):
                break
            else:
                parser.expect(",")

        function = schema.functions.get(tmpFunction.getSignature())

        parser.expect("IS")
        function.comment = CommentParser.getComment(parser)
        parser.expect(";")
        
    @staticmethod
    def parseIndex(parser, database):
        indexName = parser.parse_identifier()
        objectName = ParserUtils.get_object_name(indexName)
        schemaName = ParserUtils.get_schema_name(indexName, database)
        schema = database.getSchema(schemaName)

        index = schema.indexes.get(objectName)

        if index is None:
            primaryKey = schema.primaryKeys[objectName]
            parser.expect("IS")
            primaryKey.comment = CommentParser.getComment(parser)
            parser.expect(";")
        else:
            parser.expect("IS")
            index.comment = CommentParser.getComment(parser)
            parser.expect(";")
            
    @staticmethod
    def parseSchema(parser, database):
        schemaName = ParserUtils.get_object_name(parser.parse_identifier())
        schema = database.getSchema(schemaName)

        parser.expect("IS")
        schema.comment = CommentParser.getComment(parser)
        parser.expect(";")
        
    @staticmethod
    def parseSequence(parser, database):
        sequenceName = parser.parse_identifier();
        objectName = ParserUtils.get_object_name(sequenceName)
        schemaName = ParserUtils.get_schema_name(sequenceName, database)

        sequence = database.getSchema(schemaName).sequences[objectName]

        parser.expect("IS")
        sequence.comment = CommentParser.getComment(parser)
        parser.expect(";")
        
    @staticmethod
    def parseTrigger(parser, database):
        triggerName = ParserUtils.get_object_name(parser.parse_identifier())

        parser.expect("ON")

        tableName = parser.parse_identifier()
        objectName = ParserUtils.get_object_name(tableName)
        schemaName = ParserUtils.get_schema_name(triggerName, database)

        trigger = database.getSchema(schemaName).tables[objectName].triggers[triggerName]

        parser.expect("IS")
        trigger.comment = CommentParser.getComment(parser)
        parser.expect(";")
        
    @staticmethod
    def parseView(parser, database):
        viewName = parser.parse_identifier()
        objectName = ParserUtils.get_object_name(viewName)
        schemaName = ParserUtils.get_schema_name(viewName, database)

        view = database.getSchema(schemaName).views[objectName]

        parser.expect("IS")
        view.comment = CommentParser.getComment(parser)
        parser.expect(";")


    @staticmethod
    def getComment(parser):
        comment = parser.parse_string()

        if comment.lower() == "null".lower():
            return None

        return comment
