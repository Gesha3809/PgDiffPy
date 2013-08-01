class TableDiff(object):
    def __init__(self, target_table, origin_table):
        self.target_table, self.origin_table = target_table, origin_table
        self.current_columns_set, self.past_columns_set = set(target_table.columns.keys()), set(origin_table.columns.keys())
        self.column_intersection = self.current_columns_set.intersection(self.past_columns_set)

    def renamed(self):
        return self.origin_table.name if self.origin_table.name!=self.target_table.name else False

    def added(self):
        return self.past_columns_set - self.column_intersection

    def removed(self):
        return self.current_columns_set - self.column_intersection

    def changed(self):
        return set(o for o in self.column_intersection if self.origin_table.columns[o] != self.target_table.columns[o])