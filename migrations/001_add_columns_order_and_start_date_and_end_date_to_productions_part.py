from dmigrations.mysql import migrations as m
import datetime
migration = m.Compound([
    m.AddColumn('productions', 'part', 'order', 'integer'),
    m.AddColumn('productions', 'part', 'start_date', 'date'),
    m.AddColumn('productions', 'part', 'end_date', 'date'),
])

