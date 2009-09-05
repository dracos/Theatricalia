Python modules needed:
* flup
* PIL
* MySQLdb

Installing on NetBSD 4 issues:
* No root access. Set up a "virtual" python following
  http://peak.telecommunity.com/DevCenter/EasyInstall#creating-a-virtual-python
  then flup installed fine with easy_install.

* PIL installs in the root rather than under PIL. Installed, then renamed PIL[...].egg to PIL.

* MySQLdb installs, but it can't find the shared object when imported.
  I used --editable to download the source, edited setup.py to add
    options['extra_link_args'] = '-R/usr/pkg/lib/mysql'
  and then it was fine.

* django is in ext/django because it's so edited.

