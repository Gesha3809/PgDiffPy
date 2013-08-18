import hashlib

from diff.PgDiffUtils import PgDiffUtils
from helpers.OrderedDict import OrderedDict

class PgFunction(object):
    def __init__(self):
        self.name = ''
        self.arguments = OrderedDict()
        self.comment = None

    def addArgument(self, argument):
        self.arguments[argument.name] = argument

    def getCreationSQL(self):
        sbSQL = []
        sbSQL.append("CREATE OR REPLACE FUNCTION ")
        sbSQL.append(PgDiffUtils.getQuotedName(self.name))
        sbSQL.append('(')

        addComma = False

        for argumentName, argument in self.arguments.items():
            if addComma:
                sbSQL.append(", ")

            sbSQL.append(argument.getDeclaration(True))

            addComma = True

        sbSQL.append(") ")
        sbSQL.append(self.body)
        sbSQL.append(';')

        if self.comment is not None and len(comment) > 0:
            sbSQL.append("\n\nCOMMENT ON FUNCTION ")
            sbSQL.append(PgDiffUtils.getQuotedName(self.name))
            sbSQL.append('(')

            addComma = False

            for argument in self.arguments.items():
                if addComma:
                    sbSQL.append(", ")

                sbSQL.append(argument.getDeclaration(False))

                addComma = True

            sbSQL.append(") IS ")
            sbSQL.append(self.comment)
            sbSQL.append(';')

        return ''.join(sbSQL)


    def getDropSQL(self):
        sbSQL = []
        sbSQL.append("DROP FUNCTION ")
        sbSQL.append(self.name)
        sbSQL.append('(')

        addComma = False

        for argumentName, argument in self.arguments.items():
            if "OUT" == argument.mode:
                continue

            if addComma:
                sbSQL.append(", ")

            sbSQL.append(argument.getDeclaration(False))

            addComma = True

        sbSQL.append(");")

        return ''.join(sbSQL)

    def getSignature(self):
        sbSQL = []
        sbSQL.append(self.name)
        sbSQL.append('(')

        addComma = False

        for argumentName, argument in self.arguments.items():
            if argument.mode == "OUT":
                continue

            if addComma:
                sbSQL.append(',')

            sbSQL.append(argument.dataType)

            addComma = True

        sbSQL.append(')')

        return hashlib.md5(''.join(sbSQL)).digest().encode("base64")


class Argument(object):
    def __init__(self):
        self.mode = "IN"
        self.name = None
        self.dataType = None
        self.defaultExpression  = None

    def getDeclaration(self, includeDefaultValue):
            sbSQL = []

            if (self.mode is not None and self.mode != "IN"):
                sbSQL.append(self.mode)
                sbSQL.append(' ')

            if self.name is not None and len(self.name) > 0:
                sbSQL.append(PgDiffUtils.getQuotedName(self.name))
                sbSQL.append(' ')

            sbSQL.append(self.dataType)

            if (includeDefaultValue and self.defaultExpression is not None
                and len(self.defaultExpression) > 0):
                sbSQL.append(" = ")
                sbSQL.append(self.defaultExpression)

            return ''.join(sbSQL)
