Theatricalia
============

A database of past and future theatre productions
http://theatricalia.com/

Nice things
-----------

* Homophone name matching in search
* Partial dates (spun off to another repo, but not cleanly included here, sigh)

Installation
------------

This is a standard Django project, running with MySQL.

Django modifications
--------------------

The following were previously made by Django code modifications and need to be
reintroduced some other way:
* db/models/fields/related.py: to not have the provided multi-select help-text
* forms/formsets.py & models.py: to not have Delete on last form
* forms/forms.py: Move the label_suffix to inside label_tag
* Email uniqueness
* contrib/comments/views/comments.py: Remove c parameter from redirect

In my bad youth (look, it was using SVN when this project began), I have made
some modifications to Django, as follows (to be cleaned up soon):

* contrib/admin/media/js/urlify.js: Remove stop words removelist
* contrib/admin/filterspecs.py: Allow filtering of lookup_choices
* contrib/admin/views/main.py: smart_split the query
* contrib/admin/templates/admin/actions.html: Pass search terms through the form
