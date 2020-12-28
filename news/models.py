from django.db import models
from django.conf import settings
from django.urls import reverse

class ArticleManager(models.Manager):
    def visible(self):
        return super(ArticleManager, self).get_queryset().filter(visible=True)

class Article(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    enable_comments = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique_for_month='created')
    title = models.CharField(max_length=100)
    visible = models.BooleanField(default=False)
    body = models.TextField()
    body_html = models.TextField(editable=False, blank=True)

    objects = ArticleManager()

    class Meta:
        get_latest_by = 'created'
        ordering = ['-created']

    def __str__(self):
        return self.title

    def save(self, **kwargs):
        super(Article, self).save(kwargs)

    def get_absolute_url(self):
        return reverse('news-entry', kwargs={
            'year': self.created.year, 
            'month': self.created.strftime('%B').lower(),
            'slug': self.slug,
        })

    def get_next(self):
        return self.get_next_by_pub_date(visible=True)

    def get_previous(self):
        return self.get_previous_by_pub_date(visible=True)
