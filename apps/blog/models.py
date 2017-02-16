import datetime
from django.db import models
# Create your models here.
from django.template.defaultfilters import slugify


class ArticleQuerySet(models.QuerySet):

    def published(self):
        return self.filter(publish=True)


class Article(models.Model):
    title = models.CharField(max_length=200)
    ingress = models.CharField(max_length=500)
    body = models.TextField()
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    publish = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = ArticleQuerySet.as_manager()

    def __str__(self):
        return self.title

    def _get_slug(self):
        slug = slugify(self.title)
        date = self.created
        if not date:
            date = datetime.datetime.now()
        complete_slug = '{}-{}-{}-{}'.format(
            date.year, date.month, date.day, slug
        )
        return complete_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_slug()
        super(Article, self).save()

    class Meta:
        verbose_name = 'Blog Article'
        verbose_name_plural = 'Blog Articles'
        ordering = ['-created']
