from parser.Parser import Parser, ParserUtils
from schema.PgTrigger import PgTrigger

class CreateTriggerParser(object):
    @staticmethod
    def parse(database, statement, ignoreSlonyTriggers):
        parser = Parser(statement)
        parser.expect("CREATE", "TRIGGER")

        triggerName = parser.parse_identifier()
        objectName = ParserUtils.get_object_name(triggerName)

        trigger = PgTrigger()
        trigger.name = objectName

        if parser.expect_optional("BEFORE"):
            trigger.event = PgTrigger.EVENT_BEFORE
        elif parser.expect_optional("AFTER"):
            trigger.event = PgTrigger.EVENT_AFTER
        elif parser.expect_optional("INSTEAD OF"):
            trigger.event = PgTrigger.EVENT_INSTEAD_OF

        first = True

        while True:
            if not first and not parser.expect_optional("OR"):
                break
            elif parser.expect_optional("INSERT"):
                trigger.onInsert = True
            elif parser.expect_optional("UPDATE"):
                trigger.onUpdate = True

                if parser.expect_optional("OF"):
                    while True:
                        trigger.updateColumns.append(parser.parse_identifier())
                        if not parser.expect_optional(","):
                            break

            elif parser.expect_optional("DELETE"):
                trigger.onDelete = True
            elif parser.expect_optional("TRUNCATE"):
                trigger.onTruncate = True
            elif (first):
                break
            else:
                parser.throw_unsupported_command()

            first = False

        parser.expect("ON")

        trigger.tableName = ParserUtils.get_object_name(parser.parse_identifier())

        if parser.expect_optional("FOR"):
            parser.expect_optional("EACH")

            if parser.expect_optional("ROW"):
                trigger.forEachRow = True
            elif parser.expect_optional("STATEMENT"):
                trigger.forEachRow = False
            else:
                parser.throw_unsupported_command()

        if parser.expect_optional("WHEN"):
            parser.expect("(")
            trigger.when = parser.get_expression()
            parser.expect(")")

        parser.expect("EXECUTE", "PROCEDURE")
        trigger.function = parser.get_rest()

        ignoreSlonyTrigger = ignoreSlonyTriggers and ("_slony_logtrigger" == trigger.name or "_slony_denyaccess" == trigger.name)

        if (not ignoreSlonyTrigger):
            schema = database.getSchema(ParserUtils.get_schema_name(trigger.tableName, database))
            container = schema.tables.get(trigger.tableName)
            if not container:
                container = schema.views.get(trigger.tableName)

            if container:
                container.triggers[trigger.name] = trigger
            else:
                raise Exception()

             

