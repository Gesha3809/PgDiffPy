import re
from diff.PgDiffUtils import PgDiffUtils

class PgColumn(object):

    PATTERN_NULL = re.compile(r"^(.+)[\s]+NULL$", re.I)
    PATTERN_NOT_NULL = re.compile(r"^(.+)[\s]+NOT[\s]+NULL$", re.I)
    PATTERN_DEFAULT = re.compile(r"^(.+)[\s]+DEFAULT[\s]+(.+)$", re.I)

    def __init__(self, name):
        self.name = name
        self.defaultValue = None
        self.nullValue = True
        self.statistics = None
        self.storage = None
        self.comment = None

    def parseDefinition(self, definition):
        string = definition

        matcher = self.PATTERN_NOT_NULL.match(string)

        if matcher:
            string = matcher.group(1).strip()
            self.nullValue = False
        else:
            matcher = self.PATTERN_NULL.match(string)

            if matcher:
                string = matcher.group(1).strip()
                self.nullValue = True

        matcher = self.PATTERN_DEFAULT.match(string)

        if matcher:
            string = matcher.group(1).strip()
            self.defaultValue = matcher.group(2).strip()

        self.type = string

    def getFullDefinition(self, addDefaults):
        sbSQL = []
        sbSQL.append(PgDiffUtils.getQuotedName(self.name))
        sbSQL.append(' ')
        sbSQL.append(self.type)

        if (self.defaultValue is not None and len(self.defaultValue)):
            sbSQL.append(" DEFAULT ")
            sbSQL.append(self.defaultValue)
        elif (not self.nullValue and addDefaults):
            defaultColValue = PgColumnUtils.getDefaultValue(self.type);

            if (defaultColValue is not None):
                sbSQL.append(" DEFAULT ")
                sbSQL.append(defaultColValue)

        if not self.nullValue:
            sbSQL.append(" NOT NULL")

        return ''.join(sbSQL)


class PgColumnUtils(object):
    ZeroDefaultValueTypes = ["smallint",
            "integer",
            "bigint",
            "real",
            "double precision",
            "int2",
            "int4",
            "int8",
            "double",
            "money"]
    @staticmethod
    def getDefaultValue(adjType):
        if (adjType in PgColumnUtils.ZeroDefaultValueTypes
                or adjType.startswith("decimal")
                or adjType.startswith("numeric")
                or adjType.startswith("float")):
            defaultValue = "0";
        elif (adjType.startswith("character varying")
                or adjType.startswith("varchar")
                or adjType.startswith("character")
                or adjType.startswith("char")
                or "text" == adjType):
            defaultValue = "''"
        elif ("boolean" == adjType):
            defaultValue = "false"
        else:
            defaultValue = None

        return defaultValue