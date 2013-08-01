from db import Table, Column
from patch import Patch

if __name__ == "__main__":
    table1=Table('table1', Column('c1','text'), Column('c2','text'), Column('c4','text'))
    table2=Table('table1', Column('c1','text'), Column('c2','int'), Column('c3','text'))


    diff=table1.compare(table2)

    print Patch(diff)