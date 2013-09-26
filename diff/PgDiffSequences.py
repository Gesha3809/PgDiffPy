from PgDiffUtils import PgDiffUtils

class PgDiffSequences(object):

    @staticmethod
    def dropSequences(writer, oldSchema, newSchema, searchPathHelper):
        if oldSchema is None:
            return

        # Drop sequences that do not exist in new schema
        for sequenceName in oldSchema.sequences:
            if sequenceName not in newSchema.sequences:
                searchPathHelper.outputSearchPath(writer)
                writer.writeln(oldSchema.sequences[sequenceName].getDropSQL())

    @staticmethod
    def createSequences(writer, oldSchema, newSchema, searchPathHelper):
        # Add new sequences
        for sequenceName in newSchema.sequences:
            if oldSchema is None or sequenceName not in oldSchema.sequences:
                searchPathHelper.outputSearchPath(writer)
                writer.writeln(newSchema.sequences[sequenceName].getCreationSQL())

    @staticmethod
    def alterSequences(writer, arguments, oldSchema, newSchema, searchPathHelper):
        if oldSchema is None:
            return

        for newSequenceName in newSchema.sequences:

            oldSequence = oldSchema.sequences.get(newSequenceName)
            newSequence = newSchema.sequences[newSequenceName]

            if oldSequence is None:
                continue

            sbSQL = []

            oldIncrement = oldSequence.increment
            newIncrement = newSequence.increment

            if (newIncrement is not None and oldIncrement != newIncrement):
                sbSQL.append("\n\tINCREMENT BY ")
                sbSQL.append(newIncrement)

            oldMinValue = oldSequence.minValue
            newMinValue = newSequence.minValue

            if (newMinValue is None and oldMinValue is not None):
                sbSQL.append("\n\tNO MINVALUE")
            elif (newMinValue is not None and newMinValue != oldMinValue):
                sbSQL.append("\n\tMINVALUE ")
                sbSQL.append(newMinValue)

            oldMaxValue = oldSequence.maxValue
            newMaxValue = newSequence.maxValue

            if (newMaxValue is None and oldMaxValue is not None):
                sbSQL.append("\n\tNO MAXVALUE")
            elif (newMaxValue is not None and newMaxValue != oldMaxValue):
                sbSQL.append("\n\tMAXVALUE ")
                sbSQL.append(newMaxValue)

            if not arguments.ignoreStartWith:
                oldStart = oldSequence.startWith
                newStart = newSequence.startWith

                if (newStart is not None and newStart != oldStart):
                    sbSQL.append("\n\tRESTART WITH ")
                    sbSQL.append(newStart)

            oldCache = oldSequence.cache
            newCache = newSequence.cache

            if (newCache is not None and newCache != oldCache):
                sbSQL.append("\n\tCACHE ")
                sbSQL.append(newCache)

            oldCycle = oldSequence.cycle
            newCycle = newSequence.cycle

            if (oldCycle and not newCycle):
                sbSQL.append("\n\tNO CYCLE")
            elif (not oldCycle and newCycle):
                sbSQL.append("\n\tCYCLE")

            oldOwnedBy = oldSequence.ownedBy
            newOwnedBy = newSequence.ownedBy

            if (newOwnedBy is not None and newOwnedBy != oldOwnedBy):
                sbSQL.append("\n\tOWNED BY ")
                sbSQL.append(newOwnedBy)

            if len(sbSQL):
                searchPathHelper.outputSearchPath(writer)
                writer.writeln("ALTER SEQUENCE %s%s;" % (PgDiffUtils.getQuotedName(newSequence.name), ''.join(sbSQL)))

            if (oldSequence.comment is None and newSequence.comment is not None
                    or oldSequence.comment is not None
                    and newSequence.comment is not None
                    and oldSequence.comment != newSequence.comment):
                searchPathHelper.outputSearchPath(writer)
                writer.writeln("COMMENT ON SEQUENCE %s IS %s;" % (PgDiffUtils.getQuotedName(newSequence.name), newSequence.comment))

            elif (oldSequence.comment is not None and newSequence.comment is None):
                searchPathHelper.outputSearchPath(writer)
                writer.writeln("COMMENT ON SEQUENCE %s IS NULL;" % PgDiffUtils.getQuotedName(newSequence.name))

    @staticmethod
    def alterCreatedSequences(writer, oldSchema, newSchema, searchPathHelper):
        # Alter created sequences
        for sequenceName, sequence in newSchema.sequences.items():
            if ((oldSchema is None or sequenceName not in oldSchema.sequences)
                    and sequence.ownedBy is not None
                    and len(sequence.ownedBy) > 0):
                searchPathHelper.outputSearchPath(writer)
                writer.writeln(sequence.getOwnedBySQL())
