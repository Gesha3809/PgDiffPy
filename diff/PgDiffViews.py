from PgDiffUtils import PgDiffUtils

class PgDiffViews(object):

    @staticmethod
    def createViews(oldSchema, newSchema,searchPathHelper):
        for newViewName, newView in newSchema.views.items():
            if (oldSchema is None or newViewName not in oldSchema.views
                    or oldSchema.views.get(newViewName) != newView):
                searchPathHelper.outputSearchPath()
                print "\n%s\n" % newView.getCreationSQL()

    @staticmethod
    def alterViews(oldSchema, newSchema, searchPathHelper):
        if oldSchema is None:
            return

        for oldViewName, oldView in oldSchema.views.items():
            newView = newSchema.views.get(oldViewName)

            if newView is None:
                continue

            PgDiffViews.diffDefaultValues(oldView, newView, searchPathHelper)

            if (oldView.comment is None
                    and newView.comment is not None
                    or oldView.comment is not None
                    and newView.comment is not None
                    and oldView.comment != newView.comment):
                searchPathHelper.outputSearchPath()
                print "\nCOMMENT ON VIEW %s IS %s;" % (PgDiffUtils.getQuotedName(newView.name), newView.comment)
            elif oldView.comment is not None and newView.comment is None:
                searchPathHelper.outputSearchPath()
                print "\nCOMMENT ON VIEW %s IS NULL" %PgDiffUtils.getQuotedName(newView.name)

            columnNames = set(newView.columnComments.keys()) | set(oldView.columnComments.keys())
            for columnName in columnNames:
                oldColumnComment = oldView.columnComments.get(columnName)
                newColumnComment = newView.columnComments.get(columnName)

                if (oldColumnComment is None and newColumnComment is not None
                        or oldColumnComment is not None and newColumnComment is not None
                        and oldColumnComment != newColumnComment):
                    searchPathHelper.outputSearchPath()
                    print "\nCOMMENT ON COLUMN %s.%s IS %s;\n" % (PgDiffUtils.getQuotedName(newView.name),
                            PgDiffUtils.getQuotedName(columnName), newColumnComment)
                elif oldColumnComment is not None and newColumnComment is None:
                    searchPathHelper.outputSearchPath()
                    print "\nCOMMENT ON COLUMN %s.%s IS NULL;\n" % (PgDiffUtils.getQuotedName(newView.name),
                            PgDiffUtils.getQuotedName(columnName))

    @staticmethod
    def dropViews(oldSchema, newSchema, searchPathHelper):
        if oldSchema is None:
            return

        for oldViewName in oldSchema.views:
            newView = newSchema.views.get(oldViewName)
            oldView = oldSchema.views[oldViewName]

            if newView is None or oldView != newView:
                searchPathHelper.outputSearchPath()
                print "\n%s\n" % oldView.getDropSQL()

    @staticmethod
    def diffDefaultValues(oldView, newView, searchPathHelper):

        oldValues = oldView.defaultValues
        newValues = newView.defaultValues

        # modify defaults that are in old view
        for oldValueColumnName in oldValues:

            oldValueColumnValue = oldValues[oldValueColumnName]
            newValueColumnValue = newValues.get(oldValueColumnName)

            if (newValueColumnValue is not None and oldValueColumnValue != newValueColumnValue):
                searchPathHelper.outputSearchPath()
                print "\nALTER TABLE %s ALTER COLUMN %s SET DEFAULT %s;\n" % (PgDiffUtils.getQuotedName(newView.name),
                        oldValueColumnName, newValueColumnValue)
            elif newValueColumnValue is None:
                searchPathHelper.outputSearchPath()
                print "\nALTER TABLE %s ALTER COLUMN %s DROP DEFAULT;" % (PgDiffUtils.getQuotedName(newView.name),
                        PgDiffUtils.getQuotedName(oldValueColumnName))

        # add new defaults
        for newValueColumnName in newValues:
            if newValueColumnName not in oldValues:
                searchPathHelper.outputSearchPath()
                print "\nALTER TABLE %s ALTER COLUMN %s  SET DEFAULT ;\n" % (PgDiffUtils.getQuotedName(newView.name),
                        PgDiffUtils.getQuotedName(newValuecolumnName), newValues[newValuecolumnName])

