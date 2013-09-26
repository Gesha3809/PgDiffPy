import hashlib

from diff.PgDiffUtils import PgDiffUtils
from helpers.OrderedDict import OrderedDict

class PgFunction(object):
    def __init__(self):
        self.name = ''
        self.arguments = []
        self.body = None
        self.comment = None

    def __eq__(self, other):
        return self._equals(other, False)

    def __ne__(self, other):
        return not self._equals(other, False)

    def equals(self, other, ignoreFunctionWhitespace):
        return self._equals(other, ignoreFunctionWhitespace)


    def _equals(self, other, ignoreFunctionWhitespace = False):

        if isinstance(other, PgFunction):
            if (self.name is None
                and other.name is not None or self.name is not None
                and self.name != other.name):
                return False

            if ignoreFunctionWhitespace:
                selfBody = ' '.join(self.body.split())
                otherBody = ' '.join(other.body.split())
            else:
                selfBody = self.body
                otherBody = other.body

            if (selfBody is None
                and otherBody is not None or selfBody is not None
                and selfBody != otherBody):
                return False

            if len(self.arguments) != len(other.arguments):
                return False
            else:
                for index, argument in enumerate(self.arguments):
                    if (argument != other.arguments[index]):
                        return False
            return True

        return False

    def addArgument(self, argument):
        self.arguments.append(argument)

    def getCreationSQL(self):
        sbSQL = []
        sbSQL.append("CREATE OR REPLACE FUNCTION ")
        sbSQL.append(PgDiffUtils.getQuotedName(self.name))
        sbSQL.append('(')

        argumentsString = ', '.join([argument.getDeclaration(True) for argument in self.arguments])
        sbSQL.append(argumentsString)

        sbSQL.append(") ")
        sbSQL.append(self.body)

        if self.comment:
            sbSQL.append("\n\nCOMMENT ON FUNCTION ")
            sbSQL.append(PgDiffUtils.getQuotedName(self.name))
            sbSQL.append('(')

            sbSQL.append(argumentsString)

            sbSQL.append(") IS ")
            sbSQL.append(self.comment)

        sbSQL.append(';\n')
        return ''.join(sbSQL)


    def getDropSQL(self):
        sbSQL = []
        sbSQL.append("DROP FUNCTION ")
        sbSQL.append(self.name)
        sbSQL.append('(')

        addComma = False

        for argument in self.arguments:
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

        for argument in self.arguments:
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

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return self.__dict__ != other.__dict__

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
