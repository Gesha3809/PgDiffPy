from PgSchema import PgSchema

class PgDatabase(object):
    def __init__(self):
        # Add default public schema
        self.schemas = dict()
        self.schemas["public"] = PgSchema("public")
        self.setDefaultSchema("public")
        self.comment = None

    def setDefaultSchema(self, schema):
        self.defaultSchema = self.getSchema(schema)

    def getDefaultSchema(self):
        return self.defaultSchema

    # Returns schemaName object or Default schema if schemaName is None
    def getSchema(self, schemaName):
        if schemaName is None:
            return self.defaultSchema

        return self.schemas[schemaName]