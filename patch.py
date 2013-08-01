class Patch(object):

    def __init__(self, diffObject):
        self.diff = diffObject
        self.sql = ''

    def __repr__(self):
        if self.diff.renamed():
            self.sql += 'ALTER TABLE %(name)s RENAME TO %(new_name)s;\n' % {'name': self.diff.target_table.name, 'new_name': self.diff.origin_table.name}
        actions = list()
        added_columns = self.diff.added()
        changed_columns = self.diff.changed()
        removed_columns = self.diff.removed()

        for added_column in added_columns:
            actions.append('\tADD COLUMN %(name)s %(type)s'.expandtabs(4) % {'name':added_column, 'type':self.diff.origin_table.columns[added_column].type})

        for changed_column in changed_columns:
            actions.append('\tALTER COLUMN %(name)s %(type)s'.expandtabs(4) % {'name':changed_column, 'type':self.diff.origin_table.columns[added_column].type})

        for removed_column in removed_columns:
            actions.append('\tDROP COLUMN %(name)s'.expandtabs(4) % {'name':removed_column})

        self.sql += 'ALTER TABLE %(name)s\n' % {'name': self.diff.target_table.name}

        self.sql += ',\n'.join(actions) + ';'
        return self.sql