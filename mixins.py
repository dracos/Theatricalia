import string

from django.contrib.auth.decorators import login_required
from django.utils.cache import patch_response_headers
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.csrf import csrf_exempt

# Cacheing and the like

class NeverCacheMixin(object):
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(NeverCacheMixin, self).dispatch(*args, **kwargs)

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

class CSRFExemptMixin(object):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptMixin, self).dispatch(*args, **kwargs)

class CacheMixin(object):
    cache_timeout = 60

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(super(CacheMixin, self).dispatch)(*args, **kwargs)

class CacheControlMixin(object):
    cache_timeout = 60

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        response = super(CacheControlMixin, self).dispatch(*args, **kwargs)
        patch_response_headers(response, self.get_cache_timeout())
        return response

class JitterCacheMixin(CacheControlMixin):
    cache_range = [40, 80]

    def get_cache_range(self):
        return self.cache_range

    def get_cache_timeout(self):
        return random.randint(*self.get_cache_range())


# Project mixins
class ListMixin(CacheMixin):
    cache_timeout = 60 * 5

    def get_paginator(self, *args, **kwargs):
        kwargs['orphans'] = 10
        return super(ListMixin, self).get_paginator(*args, **kwargs)

    def get_queryset(self):
        letter = self.kwargs.get('letter', 'a')
        if letter == '0':
            args = { '%s__regex' % self.field: r'^[0-9]' }
            objs = self.model.objects.filter(**args)
            letter = '0-9'
        elif letter == '*':
            args = { '%s__regex' % self.field: r'^[A-Za-z0-9]' }
            objs = self.model.objects.exclude(**args)
            letter = 'Symbols'
        else:
            args = { '%s__istartswith' % self.field: letter }
            objs = self.model.objects.filter(**args)
            letter = letter.upper()
        self.letter = letter
        return objs

    def get_context_data(self, **kwargs):
        context = super(ListMixin, self).get_context_data(**kwargs)
        context['letter'] = self.letter
        context['letters'] = list(string.ascii_uppercase)
        return context
