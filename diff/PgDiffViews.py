from PgDiffUtils import PgDiffUtils

class PgDiffViews(object):

    @staticmethod
    def createViews(writer, oldSchema, newSchema,searchPathHelper):
        for newViewName, newView in newSchema.views.items():
            if (oldSchema is None or newViewName not in oldSchema.views
                    or oldSchema.views.get(newViewName) != newView):
                searchPathHelper.outputSearchPath(writer)
                writer.writeln(newView.getCreationSQL())

    @staticmethod
    def alterViews(writer, oldSchema, newSchema, searchPathHelper):
        if oldSchema is None:
            return

        for oldViewName, oldView in oldSchema.views.items():
            newView = newSchema.views.get(oldViewName)

            if newView is None:
                continue

            PgDiffViews.diffDefaultValues(writer, oldView, newView, searchPathHelper)

            if (oldView.comment is None
                    and newView.comment is not None
                    or oldView.comment is not None
                    and newView.comment is not None
                    and oldView.comment != newView.comment):
                searchPathHelper.outputSearchPath(writer)
                writer.write("COMMENT ON VIEW ")
                writer.write(PgDiffUtils.getQuotedName(newView.name))
                writer.write(" IS ")
                writer.write(newView.comment)
                writer.writeln(";")
            elif oldView.comment is not None and newView.comment is None:
                searchPathHelper.outputSearchPath(writer)
                writer.write("COMMENT ON VIEW ")
                writer.write(PgDiffUtils.getQuotedName(newView.name))
                writer.writeln(" IS NULL;")

            columnNames = set(newView.columnComments.keys()) | set(oldView.columnComments.keys())
            for columnName in columnNames:
                oldColumnComment = oldView.columnComments.get(columnName)
                newColumnComment = newView.columnComments.get(columnName)

                if (oldColumnComment is None and newColumnComment is not None
                        or oldColumnComment is not None and newColumnComment is not None
                        and oldColumnComment != newColumnComment):
                    searchPathHelper.outputSearchPath(writer)
                    writer.write("COMMENT ON COLUMN ")
                    writer.write(PgDiffUtils.getQuotedName(newView.name))
                    writer.write(".")
                    writer.write(PgDiffUtils.getQuotedName(columnName))
                    writer.write(" IS ")
                    writer.write(newColumnComment)
                    writer.writeln(";")

                elif oldColumnComment is not None and newColumnComment is None:
                    searchPathHelper.outputSearchPath(writer)
                    writer.write("COMMENT ON COLUMN ")
                    writer.write(PgDiffUtils.getQuotedName(newView.name))
                    writer.write(".")
                    writer.write(PgDiffUtils.getQuotedName(columnName))
                    writer.writeln(" IS NULL;")

    @staticmethod
    def dropViews(writer, oldSchema, newSchema, searchPathHelper):
        if oldSchema is None:
            return

        for oldViewName in oldSchema.views:
            newView = newSchema.views.get(oldViewName)
            oldView = oldSchema.views[oldViewName]

            if newView is None or oldView != newView:
                searchPathHelper.outputSearchPath(writer)
                writer.writeln(oldView.getDropSQL())

    @staticmethod
    def diffDefaultValues(writer, oldView, newView, searchPathHelper):

        oldValues = oldView.defaultValues
        newValues = newView.defaultValues

        # modify defaults that are in old view
        for oldValueColumnName in oldValues:

            oldValueColumnValue = oldValues[oldValueColumnName]
            newValueColumnValue = newValues.get(oldValueColumnName)

            if (newValueColumnValue is not None and oldValueColumnValue != newValueColumnValue):
                searchPathHelper.outputSearchPath(writer)
                writer.write("ALTER TABLE ")
                writer.write(PgDiffUtils.getQuotedName(newView.name))
                writer.write(" ALTER COLUMN ")
                writer.write(PgDiffUtils.getQuotedName(oldValueColumnName))
                writer.write(" SET DEFAULT ")
                writer.write(newValueColumnValue)
                writer.writeln(";")

            elif newValueColumnValue is None:
                searchPathHelper.outputSearchPath(writer)
                writer.write("ALTER TABLE ")
                writer.write(PgDiffUtils.getQuotedName(newView.name))
                writer.write(" ALTER COLUMN ")
                writer.write(PgDiffUtils.getQuotedName(oldValueColumnName))
                writer.writeln(" DROP DEFAULT;")

        # add new defaults
        for newValueColumnName in newValues:
            if newValueColumnName not in oldValues:
                searchPathHelper.outputSearchPath(writer)
                writer.write("ALTER TABLE ")
                writer.write(PgDiffUtils.getQuotedName(newView.name))
                writer.write(" ALTER COLUMN ")
                writer.write(PgDiffUtils.getQuotedName(newValueColumnName))
                writer.write(" SET DEFAULT ")
                writer.write(newValues[newValueColumnName])
                writer.writeln(";")
