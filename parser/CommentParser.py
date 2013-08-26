from parser.Parser import Parser, ParserUtils
from schema.PgFunction import PgFunction, Argument

class CommentParser(object):

    @staticmethod
    def parse(database, statement):
        parser = Parser(statement)
        parser.expect("COMMENT", "ON")

        if parser.expectOptional("TABLE"):
            CommentParser.parseTable(parser, database)
        elif parser.expectOptional("COLUMN"):
            CommentParser.parseColumn(parser, database)
        elif parser.expectOptional("CONSTRAINT"):
            CommentParser.parseConstraint(parser, database)
        elif parser.expectOptional("DATABASE"):
            CommentParser.parseDatabase(parser, database)
        elif parser.expectOptional("FUNCTION"):
            CommentParser.parseFunction(parser, database)
        elif parser.expectOptional("INDEX"):
            CommentParser.parseIndex(parser, database)
        elif parser.expectOptional("SCHEMA"):
            CommentParser.parseSchema(parser, database)
        elif parser.expectOptional("SEQUENCE"):
            CommentParser.parseSequence(parser, database)
        elif parser.expectOptional("TRIGGER"):
            CommentParser.parseTrigger(parser, database)
        elif parser.expectOptional("VIEW"):
            CommentParser.parseView(parser, database)
        # elif outputIgnoredStatements:
        #     database.addIgnoredStatement(statement)

    @staticmethod
    def parseTable(parser, database):
        tableName = parser.parseIdentifier()
        objectName = ParserUtils.getObjectName(tableName)
        schemaName = ParserUtils.getSchemaName(tableName, database)

        table = database.getSchema(schemaName).getTable(objectName)

        parser.expect("IS")
        table.comment = CommentParser.getComment(parser)
        parser.expect(";")

    @staticmethod
    def parseColumn(parser, database):
        columnName = parser.parseIdentifier()
        objectName = ParserUtils.getObjectName(columnName)
        tableName = ParserUtils.getSecondObjectName(columnName)
        schemaName = ParserUtils.getThirdObjectName(columnName)
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
        constraintName = ParserUtils.getObjectName(parser.parseIdentifier())

        parser.expect("ON")

        tableName = parser.parseIdentifier()
        objectName = ParserUtils.getObjectName(tableName)
        schemaName = ParserUtils.getSchemaName(constraintName, database)

        constraint = database.getSchema(schemaName).getTable(objectName).constraints[constraintName]

        parser.expect("IS")
        constraint.comment = CommentParser.getComment(parser)
        parser.expect(";")


    @staticmethod
    def parseDatabase(parser, database):
        parser.parseIdentifier()
        parser.expect("IS")
        database.comment = CommentParser.getComment(parser)
        parser.expect(";")

    @staticmethod
    def parseFunction(parser, database):
        functionName = parser.parseIdentifier()
        objectName = ParserUtils.getObjectName(functionName)
        schemaName = ParserUtils.getSchemaName(functionName, database)
        schema = database.getSchema(schemaName)

        parser.expect("(")

        tmpFunction = PgFunction()
        tmpFunction.name = objectName

        while not parser.expectOptional(")"):
            mode = ''

            if parser.expectOptional("IN"):
                mode = "IN"
            elif parser.expectOptional("OUT"):
                mode = "OUT"
            elif parser.expectOptional("INOUT"):
                mode = "INOUT"
            elif parser.expectOptional("VARIADIC"):
                mode = "VARIADIC"
            else:
                mode = None

            position = parser.position
            argumentName = None
            dataType = parser.parseDataType()

            position2 = parser.position

            if not parser.expectOptional(")") and not parser.expectOptional(","):
                parser.position = position
                argumentName = ParserUtils.getObjectName(parser.parseIdentifier())
                dataType = parser.parseDataType()
            else:
                parser.position = position2

            argument = Argument()
            argument.dataType = dataType
            argument.mode = mode
            argument.name = argumentName
            tmpFunction.addArgument(argument)

            if parser.expectOptional(")"):
                break
            else:
                parser.expect(",")

        function = schema.functions.get(tmpFunction.getSignature())

        parser.expect("IS")
        function.comment = CommentParser.getComment(parser)
        parser.expect(";")
        
    @staticmethod
    def parseIndex(parser, database):
        indexName = parser.parseIdentifier()
        objectName = ParserUtils.getObjectName(indexName)
        schemaName = ParserUtils.getSchemaName(indexName, database)
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
        schemaName = ParserUtils.getObjectName(parser.parseIdentifier())
        schema = database.getSchema(schemaName)

        parser.expect("IS")
        schema.comment = CommentParser.getComment(parser)
        parser.expect(";")
        
    @staticmethod
    def parseSequence(parser, database):
        sequenceName = parser.parseIdentifier();
        objectName = ParserUtils.getObjectName(sequenceName)
        schemaName = ParserUtils.getSchemaName(sequenceName, database)

        sequence = database.getSchema(schemaName).sequences[objectName]

        parser.expect("IS")
        sequence.comment = CommentParser.getComment(parser)
        parser.expect(";")
        
    @staticmethod
    def parseTrigger(parser, database):
        triggerName = ParserUtils.getObjectName(parser.parseIdentifier())

        parser.expect("ON")

        tableName = parser.parseIdentifier()
        objectName = ParserUtils.getObjectName(tableName)
        schemaName = ParserUtils.getSchemaName(triggerName, database)

        trigger = database.getSchema(schemaName).tables[objectName].triggers[triggerName]

        parser.expect("IS")
        trigger.comment = CommentParser.getComment(parser)
        parser.expect(";")
        
    @staticmethod
    def parseView(parser, database):
        viewName = parser.parseIdentifier()
        objectName = ParserUtils.getObjectName(viewName)
        schemaName = ParserUtils.getSchemaName(viewName, database)

        view = database.getSchema(schemaName).views[objectName]

        parser.expect("IS")
        view.comment = CommentParser.getComment(parser)
        parser.expect(";")


    @staticmethod
    def getComment(parser):
        comment = parser.parseString()

        if comment.lower() == "null".lower():
            return None

        return comment
