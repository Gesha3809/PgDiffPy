from diff import TableDiff

class Column(object):

    def __init__(self, name, type=None):
        self.key = self.name = name
        self.type = type

    def __cmp__(self, other):
        if other.name == self.name and other.type == self.type:
            return 0
        else:
            return 1


class Table(object):

    def __init__(self, name, *columns):
        self.name = name
        self.columns = dict()
        for c in columns:
            self.columns[c.key] = c

    def compare(self, origin_table):
        return TableDiff(self, origin_table)