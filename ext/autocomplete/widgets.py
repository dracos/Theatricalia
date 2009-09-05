# coding=utf8
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words

from django.contrib import admin
from django.db import models

import operator,settings
from django.contrib.auth.models import Message
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.db.models.query import QuerySet
from django.utils.encoding import smart_str

from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode 
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.datastructures import MultiValueDict, MergeDict

from search.views import search_autocomplete

class ForeignKeySearchInput(forms.MultiWidget):
	"""
	A Widget for displaying ForeignKeys in an autocomplete search input 
	instead in a <select> box.
	"""
	class Media:
		css = {
			'all': ('%scss/jquery.autocomplete.css' % settings.MEDIA_URL,)
		}
		js = (
			'%sjs/jquery.js' % settings.MEDIA_URL,
			'%sjs/jquery.autocomplete.js' % settings.MEDIA_URL,
			'%sautocomplete/AutocompleteObjectLookups.js ' % settings.MEDIA_URL,
			'%sjs/global.js' % settings.MEDIA_URL,
		)

	def label_for_value(self, value):
		key = self.rel.get_related_field().name
		obj = self.rel.to._default_manager.get(**{key: value})
		
		return obj

	def __init__(self, rel, search_fields, attrs=None):
		self.rel = rel
		self.search_fields = search_fields
		widgets = (forms.TextInput(attrs={'size':40}), forms.HiddenInput())
		super(ForeignKeySearchInput, self).__init__(widgets, attrs)

	def decompress(self, value):
		if value is None:
			return [ '', None ]
		return [ self.label_for_value(value), value ]

	def render(self, name, value, attrs=None):
		if attrs is None:
			attrs = {}
		rendered = super(ForeignKeySearchInput, self).render(name, value, attrs)
		return mark_safe('<span role="combobox">') + rendered + mark_safe('</span>') + mark_safe(u'''
<script type="text/javascript">

function addItem_id_%(namenodash)s(id, name) {
	
	$("#id_%(name)s_1").val( id );
	$("#id_%(name)s_0").val( name );
}

$(document).ready(function(){
    autocomplete_add({
        lookup: "#id_%(name)s_0",
        id: '#id_%(name)s_1',
        search_fields: '%(search_fields)s',
        app_label: '%(app_label)s',
        model_name: '%(model_name)s'
    }); 
});

</script>

		''' % {
			'search_fields': ','.join(self.search_fields),
			#'MEDIA_URL': settings.MEDIA_URL,
			'model_name': self.rel.to._meta.module_name,
			'app_label': self.rel.to._meta.app_label,
			'name': name,
			'namenodash': name.replace('-', '_'),
			#'value': value,
		})


class ManyToManySearchInput(forms.MultipleHiddenInput):
	"""
	A Widget for displaying ForeignKeys in an autocomplete search input 
	instead in a <select> box.
	"""
	class Media:
		css = {
			'all': ('%scss/jquery.autocomplete.css' % settings.MEDIA_URL,)
		}
		js = (
			'%sjs/jquery.js' % settings.MEDIA_URL,
			'%sjs/jquery.autocomplete.js' % settings.MEDIA_URL,
			'%sautocomplete/AutocompleteObjectLookups.js ' % settings.MEDIA_URL,
			'%sjs/global.js' % settings.MEDIA_URL,
		)


	def __init__(self, rel, search_fields, attrs=None):
		self.rel = rel
		self.search_fields = search_fields
		super(ManyToManySearchInput, self).__init__(attrs)
		self.help_text = u"To search, enter at least two characters"
	
	def value_from_datadict(self, data, files, name):
		if isinstance(data, (MultiValueDict, MergeDict)):
			res = data.getlist(name)
		else:
			res = data.get(name, None)
		print name, res
		for id in res:
			print self.rel.to.objects.get(pk=id)
		return res

	def render(self, name, value, attrs=None):
		if attrs is None:
			attrs = {}

		if value is None:
 			value = []
            
		label = ''
		selected = ''
		#rel_name = self.search_fields[0].split('__')[0]
		
		for id in value:
			obj = self.rel.to.objects.get(pk=id)
		
			selected = selected + mark_safe(u"""
				<div class="to_delete deletelink" ><input type="hidden" name="%(name)s" value="%(value)s"/>%(label)s</div>""" 
				)%{
					'label': obj, #getattr(obj,rel_name),
					'name': name,
					'value': obj.id,
		}

		
		return mark_safe(u'''
<input type="text" id="lookup_%(name)s" value="" size="40"/>%(label)s
<div style="float:left; padding-left:105px; width:300px;">
<font  style="color:#999999;font-size:10px !important;">%(help_text)s</font>
<div id="box_%(name)s" style="padding-left:20px;cursor:pointer;">

	%(selected)s
</div></div>

<script type="text/javascript">

function addItem_id_%(name)s(id,name) {
	// --- add new element from popup ---
	$('<div class="to_delete deletelink"><input type="hidden" name="%(name)s" value="'+id+'"/>'+name+'</div>')
	.click(function () {$(this).remove();})
	.appendTo("#box_%(name)s");

	$("#lookup_%(name)s").val( '' );
}

$(document).ready(function(){

	// --- Autocomplete ---
	$("#lookup_%(name)s").autocomplete("/ajax/autocomplete", {
		extraParams: {
			search_fields: '%(search_fields)s',
			app_label: '%(app_label)s',
			model_name: '%(model_name)s',
		},
		minChars:2,
		matchContains:1,
	}).result(function(event, data, formatted) {
        if (!data) return;
		// --- new element ---
		$('<div class="to_delete deletelink"><input type="hidden" name="%(name)s" value="' + data[1] + '"/>' + formatted + '</div>')
		.click(function () {$(this).remove();})
		.appendTo("#box_%(name)s");

		$("#lookup_%(name)s").val( '' );
	}); 
// --- delete initial element ---
	$(".to_delete").click(function () {$(this).remove();});
});
</script>

		''') % {
			'search_fields': ','.join(self.search_fields),
			'model_name': self.rel.to._meta.module_name,
			'app_label': self.rel.to._meta.app_label,
			'label': label,
			'name': name,
			'value': value,
			'selected':selected,
			'help_text':self.help_text
		}

class AutocompleteModelAdmin(admin.ModelAdmin):
	def __call__(self, request, url):
		if url is None:
			pass
		elif url == 'search':
			return self.search(request)
		return super(AutocompleteModelAdmin, self).__call__(request, url)

	def search(self, request):
		"""Factor out this function to my own code to be used by front-end"""
		return search_autocomplete(request)

	def formfield_for_dbfield(self, db_field, **kwargs):
		# For ForeignKey use a special Autocomplete widget.
		if isinstance(db_field, models.ForeignKey) and db_field.name in self.related_search_fields:
			kwargs['widget'] = ForeignKeySearchInput(db_field.rel,
									self.related_search_fields[db_field.name])

			# extra HTML to the end of the rendered output.
			if 'request' in kwargs.keys():
				kwargs.pop('request')
							
			formfield = db_field.formfield(**kwargs)
			# Don't wrap raw_id fields. Their add function is in the popup window.
			if not db_field.name in self.raw_id_fields:
				# formfield can be None if it came from a OneToOneField with
				# parent_link=True
				if formfield is not None:
					formfield.widget = AutocompleteWidgetWrapper(formfield.widget, db_field.rel, self.admin_site)
			return formfield
					
		# For ManyToManyField use a special Autocomplete widget.
		if isinstance(db_field, models.ManyToManyField)and db_field.name in self.related_search_fields:
			kwargs['widget'] = ManyToManySearchInput(db_field.rel,
									self.related_search_fields[db_field.name])
			db_field.help_text = ''

			# extra HTML to the end of the rendered output.
			if 'request' in kwargs.keys():
				kwargs.pop('request')
							
			formfield = db_field.formfield(**kwargs)
			# Don't wrap raw_id fields. Their add function is in the popup window.
			if not db_field.name in self.raw_id_fields:
				# formfield can be None if it came from a OneToOneField with
				# parent_link=True
				if formfield is not None:
					formfield.widget = AutocompleteWidgetWrapper(formfield.widget, db_field.rel, self.admin_site)
			return formfield
		
		
		return super(AutocompleteModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
	
	def response_add(self, request, obj, post_url_continue='../%s/'):
		"""
		Determines the HttpResponse for the add_view stage.
		"""
		opts = obj._meta
		pk_value = obj._get_pk_val()
		
		msg = _('The %(name)s "%(obj)s" was added successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}
		# Here, we distinguish between different save types by checking for
		# the presence of keys in request.POST.
		if request.POST.has_key("_continue"):
			self.message_user(request, msg + ' ' + _("You may edit it again below."))
			if request.POST.has_key("_popup"):
				post_url_continue += "?_popup=%s" % request.POST.get('_popup')
			return HttpResponseRedirect(post_url_continue % pk_value)
		
		if request.POST.has_key("_popup"):
			#htturn response to Autocomplete PopUp
			if request.POST.has_key("_popup"):
				return HttpResponse('<script type="text/javascript">opener.dismissAutocompletePopup(window, "%s", "%s");</script>' % (escape(pk_value), escape(obj)))
						
		elif request.POST.has_key("_addanother"):
			self.message_user(request, msg + ' ' + (_("You may add another %s below.") % force_unicode(opts.verbose_name)))
			return HttpResponseRedirect(request.path)
		else:
			self.message_user(request, msg)

			# Figure out where to redirect. If the user has change permission,
			# redirect to the change-list page for this object. Otherwise,
			# redirect to the admin index.
			if self.has_change_permission(request, None):
				post_url = '../'
			else:
				post_url = '../../../'
			return HttpResponseRedirect(post_url)
	
class AutocompleteWidgetWrapper(RelatedFieldWidgetWrapper):
	def render(self, name, value, *args, **kwargs):
		rel_to = self.rel.to
		related_url = '../../../%s/%s/' % (rel_to._meta.app_label, rel_to._meta.object_name.lower())
		self.widget.choices = self.choices
		output = [self.widget.render(name, value, *args, **kwargs)]
		if rel_to in self.admin_site._registry: # If the related object has an admin interface:
			# TODO: "id_" is hard-coded here. This should instead use the correct
			# API to determine the ID dynamically.
			output.append(u'<a href="%sadd/" class="add-another" id="add_id_%s" onclick="return showAutocompletePopup(this);"> ' % \
				(related_url, name))
			output.append(u'<img src="%simg/admin/icon_addlink.gif" width="10" height="10" alt="%s"/></a>' % (settings.ADMIN_MEDIA_PREFIX, _('Add Another')))
		return mark_safe(u''.join(output))
