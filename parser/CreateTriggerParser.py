from parser.Parser import Parser, ParserUtils
from schema.PgTrigger import PgTrigger

class CreateTriggerParser(object):
    @staticmethod
    def parse(database, statement, ignoreSlonyTriggers):
        parser = Parser(statement)
        parser.expect("CREATE", "TRIGGER")

        triggerName = parser.parseIdentifier()
        objectName = ParserUtils.getObjectName(triggerName)

        trigger = PgTrigger()
        trigger.name = objectName

        if parser.expectOptional("BEFORE"):
            trigger.before = True
        elif parser.expectOptional("AFTER"):
            trigger.before = False

        first = True

        while True:
            if not first and not parser.expectOptional("OR"):
                break
            elif parser.expectOptional("INSERT"):
                trigger.onInsert = True
            elif parser.expectOptional("UPDATE"):
                trigger.onUpdate = True

                if parser.expectOptional("OF"):
                    while True:
                        trigger.updateColumns.append(parser.parseIdentifier())
                        if not parser.expectOptional(","):
                            break

            elif parser.expectOptional("DELETE"):
                trigger.onDelete = True
            elif parser.expectOptional("TRUNCATE"):
                trigger.onTruncate = True
            elif (first):
                break
            else:
                parser.throwUnsupportedCommand()

            first = False

        parser.expect("ON")

        tableName = parser.parseIdentifier()

        trigger.tableName = ParserUtils.getObjectName(tableName)

        if parser.expectOptional("FOR"):
            parser.expectOptional("EACH")

            if parser.expectOptional("ROW"):
                trigger.forEachRow = True
            elif parser.expectOptional("STATEMENT"):
                trigger.forEachRow = False
            else:
                parser.throwUnsupportedCommand()

        if parser.expectOptional("WHEN"):
            parser.expect("(")
            trigger.when = parser.getExpression()
            parser.expect(")")

        parser.expect("EXECUTE", "PROCEDURE")
        trigger.function = parser.getRest()

        ignoreSlonyTrigger = ignoreSlonyTriggers and ("_slony_logtrigger" == trigger.name or "_slony_denyaccess" == trigger.name)

        if (not ignoreSlonyTrigger):
            tableSchema = database.getSchema(ParserUtils.getSchemaName(tableName, database))
            tableSchema.getTable(trigger.tableName).addTrigger(trigger)
