Theatricalia
============

A database of past and future theatre productions
http://theatricalia.com/

Nice data things
----------------

* Birmingham Rep archive 1913-1971.
* RSC archive, back to 1879.

Nice technical things
---------------------

* Homophone name matching in search
* Partial dates (spun off to another repo, but not cleanly included here yet)

Installation
------------

This is a standard Django project, running with MySQL.

Django modifications
--------------------

In my bad youth (it was using SVN when this project began), I made some
modifications to core Django, as follows, that still need tidying up:
* contrib/admin/media/js/urlify.js: Remove stop words removelist
* contrib/admin/filterspecs.py: Allow filtering of lookup_choices
* contrib/admin/views/main.py: smart_split the query
* contrib/admin/templates/admin/actions.html: Pass search terms through the form
