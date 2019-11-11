import urllib.parse

from django.db import models

from hackerspace.models.events import updateTime


class WishesSet(models.QuerySet):
    def search_results(self):
        results_list = []
        results = self.all()
        for result in results:
            results_list.append({
                'icon': 'wish',
                'name': result.str_name,
                'url': '/'+result.str_slug,
                'menu_heading': 'menu_h_wishes'
            })
        return results_list


class Wish(models.Model):
    objects = WishesSet.as_manager()
    str_name = models.CharField(
        max_length=250, blank=True, null=True, verbose_name='Name')
    one_person = models.ForeignKey(
        'Person', related_name="o_wishes_person", default=None, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Guilde')
    text_description = models.TextField(
        blank=True, null=True, verbose_name='Description')
    int_UNIXtime_created = models.IntegerField(blank=True, null=True)
    int_UNIXtime_updated = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.str_name

    @property
    def menu_heading(self):
        return 'menu_h_wishes'

    def save(self, *args, **kwargs):
        self = updateTime(self)
        self.str_slug = urllib.parse.quote(
            'wish/'+self.str_name.lower().replace(' ', '-'))
        super(Wish, self).save(*args, **kwargs)
