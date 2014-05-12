import logging
from PgSchema import PgSchema


class PgDatabase(object):
    def __init__(self):
        # Add default public schema
        self.default_schema = None
        self.schemas = dict()
        self.schemas["public"] = PgSchema("public")
        self.setDefaultSchema("public")
        self.comment = None

    def setDefaultSchema(self, schema):
        self.default_schema = self.getSchema(schema)
        logging.debug('Set default schema to %s' % self.default_schema)

    def getDefaultSchema(self):
        return self.default_schema

    # Returns schemaName object or Default schema if schemaName is None
    def getSchema(self, schema_name):
        return self.schemas.get(schema_name, self.default_schema)