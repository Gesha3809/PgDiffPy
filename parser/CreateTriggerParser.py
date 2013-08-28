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
            trigger.event = PgTrigger.EVENT_BEFORE
        elif parser.expectOptional("AFTER"):
            trigger.event = PgTrigger.EVENT_AFTER
        elif parser.expectOptional("INSTEAD OF"):
            trigger.event = PgTrigger.EVENT_INSTEAD_OF

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

        trigger.tableName = ParserUtils.getObjectName(parser.parseIdentifier())

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
            schema = database.getSchema(ParserUtils.getSchemaName(trigger.tableName, database))
            container = schema.tables.get(trigger.tableName)
            if not container:
                container = schema.views.get(trigger.tableName)

            if container:
                container.triggers[trigger.name] = trigger
            else:
                raise Exception()

             

