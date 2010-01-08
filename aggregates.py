# A way to access MySQL's GROUP_CONCAT function from within Django

from django.db.models import Q, Aggregate
from django.db.models.sql.aggregates import Aggregate as AggregateSQL
from django.db.models import DecimalField

class ConcatenateSQL(AggregateSQL):
    sql_function = 'GROUP_CONCAT'
    def __init__(self, col, separator='|', source=None, **extra):
        self.sql_template = "%%(function)s(%%(field)s ORDER BY %%(field)s SEPARATOR '%s')" % separator
        c = DecimalField() # XXX
        super(ConcatenateSQL, self).__init__(col, source=c, **extra)

class Concatenate(Aggregate):
    name = 'Concatenate'
    def add_to_query(self, query, alias, col, source, is_summary):
        aggregate = ConcatenateSQL(col, source=source, separator=' / ', is_summary=is_summary, **self.extra)
        query.connection.ops.check_aggregate_support(aggregate)
        query.aggregates[alias] = aggregate
