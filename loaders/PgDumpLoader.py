import sqlparse, re
from parser.CreateSchemaParser import CreateSchemaParser
from schema.PgDatabase import PgDatabase
from parser.CreateTableParser import  CreateTableParser
from parser.AlterTableParser import AlterTableParser
from parser.CreateIndexParser import CreateIndexParser
from parser.CreateFunctionParser import CreateFunctionParser
from parser.CreateSequenceParser import CreateSequenceParser
from parser.AlterSequenceParser import AlterSequenceParser
from parser.CreateViewParser import CreateViewParser
from parser.CreateTriggerParser import CreateTriggerParser
from parser.AlterViewParser import AlterViewParser
from parser.CommentParser import CommentParser

class PgDumpLoader(object):

    # Pattern for testing whether it is CREATE SCHEMA statement.
    PATTERN_CREATE_SCHEMA = re.compile(r"^CREATE[\s]+SCHEMA[\s]+.*$", re.I | re.S)
    # Pattern for parsing default schema (search_path).
    PATTERN_DEFAULT_SCHEMA = re.compile(r"^SET[\s]+search_path[\s]*=[\s]*\"?([^,\s\"]+)\"?(?:,[\s]+.*)?;$", re.I | re.S)
    # Pattern for testing whether it is CREATE TABLE statement.
    PATTERN_CREATE_TABLE = re.compile("^CREATE[\s]+TABLE[\s]+.*$", re.I | re.S)
    # Pattern for testing whether it is CREATE VIEW statement.
    PATTERN_CREATE_VIEW = re.compile("^CREATE[\s]+(?:OR[\s]+REPLACE[\s]+)?VIEW[\s]+.*$", re.I | re.S)
    # Pattern for testing whether it is ALTER TABLE statement.
    PATTERN_ALTER_TABLE = re.compile("^ALTER[\s]+TABLE[\s]+.*$", re.I | re.S)
    # Pattern for testing whether it is CREATE SEQUENCE statement.
    PATTERN_CREATE_SEQUENCE = re.compile("^CREATE[\s]+SEQUENCE[\s]+.*$", re.I | re.S)
    # Pattern for testing whether it is ALTER SEQUENCE statement.
    PATTERN_ALTER_SEQUENCE =re.compile("^ALTER[\s]+SEQUENCE[\s]+.*$", re.I | re.S)
    # Pattern for testing whether it is CREATE INDEX statement.
    PATTERN_CREATE_INDEX = re.compile("^CREATE[\s]+(?:UNIQUE[\s]+)?INDEX[\s]+.*$", re.I | re.S)
    # Pattern for testing whether it is SELECT statement.
    PATTERN_SELECT = re.compile("^SELECT[\s]+.*$", re.I | re.S)
    # Pattern for testing whether it is INSERT INTO statement.
    PATTERN_INSERT_INTO = re.compile("^INSERT[\s]+INTO[\\s]+.*$", re.I | re.S)
    # Pattern for testing whether it is UPDATE statement.
    PATTERN_UPDATE = re.compile("^UPDATE[\s].*$", re.I | re.S)
    # Pattern for testing whether it is DELETE FROM statement.
    PATTERN_DELETE_FROM = re.compile("^DELETE[\s]+FROM[\s]+.*$", re.I | re.S)
    # Pattern for testing whether it is CREATE TRIGGER statement.
    PATTERN_CREATE_TRIGGER = re.compile("^CREATE[\s]+TRIGGER[\s]+.*$", re.I | re.S)
    # Pattern for testing whether it is CREATE FUNCTION or CREATE OR REPLACE FUNCTION statement.
    PATTERN_CREATE_FUNCTION = re.compile("^CREATE[\s]+(?:OR[\s]+REPLACE[\s]+)?FUNCTION[\s]+.*$", re.I | re.S)
    # Pattern for testing whether it is ALTER VIEW statement.
    PATTERN_ALTER_VIEW = re.compile("^ALTER[\s]+VIEW[\s]+.*$", re.I | re.S)
    # Pattern for testing whether it is COMMENT statement.
    PATTERN_COMMENT = re.compile("^COMMENT[\s]+ON[\s]+.*$", re.I | re.S)

    @staticmethod
    def loadDatabaseSchema(dumpFileName, ignoreSlonyTriggers = False):
        database = PgDatabase()

        print "Loading file dump: %s\n" % dumpFileName

        statements = sqlparse.split(open(dumpFileName,'r'))
        for statement in statements:
            statement = PgDumpLoader.stripComment(statement).strip()
            if PgDumpLoader.PATTERN_CREATE_SCHEMA.match(statement):
                CreateSchemaParser.parse(database, statement)
                continue

            match = PgDumpLoader.PATTERN_DEFAULT_SCHEMA.match(statement)
            if match:
                database.setDefaultSchema(match.group(1))
                continue

            if PgDumpLoader.PATTERN_CREATE_TABLE.match(statement):
                CreateTableParser.parse(database, statement)
                continue

            if PgDumpLoader.PATTERN_ALTER_TABLE.match(statement):
                AlterTableParser.parse(database, statement)
                continue

            if PgDumpLoader.PATTERN_CREATE_SEQUENCE.match(statement):
                CreateSequenceParser.parse(database, statement)
                continue

            if PgDumpLoader.PATTERN_ALTER_SEQUENCE.match(statement):
                AlterSequenceParser.parse(database, statement)
                continue

            if PgDumpLoader.PATTERN_CREATE_INDEX.match(statement):
                CreateIndexParser.parse(database, statement)
                continue

            if PgDumpLoader.PATTERN_CREATE_VIEW.match(statement):
                CreateViewParser.parse(database, statement)
                continue

            if PgDumpLoader.PATTERN_ALTER_VIEW.match(statement):
                AlterViewParser.parse(database, statement)
                continue

            if PgDumpLoader.PATTERN_CREATE_TRIGGER.match(statement):
                CreateTriggerParser.parse(database, statement, ignoreSlonyTriggers)
                continue

            if PgDumpLoader.PATTERN_CREATE_FUNCTION.match(statement):
                CreateFunctionParser.parse(database, statement)
                continue

            if PgDumpLoader.PATTERN_COMMENT.match(statement):
                CommentParser.parse(database, statement)
                continue

        return database


    @staticmethod
    def stripComment(statement):
        start = statement.find("--")

        while start>=0:
            end = statement.find("\n", start)
            if start<end:
                statement = statement[end:]
            else:
                statement = statement[:start]

            start = statement.find("--")

        return statement
