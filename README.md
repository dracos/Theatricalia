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

In my bad youth (look, it was using SVN when this project began), I have made
some modifications to Django, as follows (this is mostly so hopefully this can
eventually be cleaned up):

* db/models/sql/query.py: to allow 'IFNULL(' strings to be passed through
* db/models/fields/related.py: to not have the provided multi-select help-text
* forms/formsets.py & models.py: to not have Delete on last form (I think?)
* forms/fields.py: Add aria-required to required fields
* forms/forms.py: Move label_suffix to inside label
* forms/widgets.py: De-XHTMLize stuff
* core/servers/basehttp.py: Add a log_request function
* views/generic/list_detail.py: Add an orphans parameter
* contrib/comments/views/comments.py: Remove c parameter from redirect
* contrib/admin/media/js/urlify.js: Remove stop words removelist
* contrib/admin/filterspecs.py: Allow filtering of lookup_choices
* contrib/admin/views/main.py: smart_split the query
* contrib/admin/templates/admin/actions.html: Pass search terms through the form
* contrib/csrf/middleware.py: De-XHTMLize
* contrib/auth/admin.py: Use name rather than first/last name
* contrib/auth/models.py: Ditto, and make email unique
* utils/html.py & template/defaultfilters.py: De-XHTMLize
* middleware/common.py: Provide reverse of APPEND_SLASH, removing one if one is present and not needed.

