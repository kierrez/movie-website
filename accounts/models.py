import os
from datetime import datetime

from django.conf import settings
from django.db import models

from django.utils import timezone
from django.forms import ValidationError
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse

from titles.models import Title
from common.sql_queries import avg_of_user_current_ratings


def update_filename(instance, file_name):
    path = os.path.join('user_files', instance.username)
    extension = '.' + file_name.split('.')[1]
    new_file_name = datetime.now().strftime('%Y-%m-%d %H-%M-%S') + extension
    return os.path.join(path, new_file_name)


def validate_file_ext(value):
    if not value.name.endswith('.csv'):
        raise ValidationError('Only csv files are supported')


class User(AbstractUser):
    picture = models.ImageField(upload_to=update_filename, blank=True, null=True)
    imdb_id = models.CharField(blank=True, null=True, max_length=15)
    tagline = models.CharField(blank=True, null=True, max_length=100)
    csv_ratings = models.FileField(upload_to=update_filename, validators=[validate_file_ext], blank=True, null=True)

    last_updated_csv_ratings = models.DateTimeField(null=True, blank=True)
    last_updated_rss_ratings = models.DateTimeField(null=True, blank=True)
    last_updated_rss_watchlist = models.DateTimeField(null=True, blank=True)
    last_updated_profile = models.DateTimeField(auto_now=True, null=True, blank=True)

    # __original_picture = None
    # __original_csv = None
    #
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     self.__original_picture = self.picture
    #     self.__original_csv = self.csv_ratings

    def __str__(self):
        return self.username

    # def clean_fields(self, exclude=None):
    #     super().clean_fields(exclude)

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'username': self.username})

    def edit_url(self):
        return reverse('user-edit', kwargs={'username': self.username})

    def watchlist_url(self):
        return reverse('watchlist', kwargs={'username': self.username})

    def favourite_url(self):
        return reverse('favourite', kwargs={'username': self.username})

    def recommend_url(self):
        return reverse('recommend', kwargs={'username': self.username})

    def ratings_url(self):
        return reverse('title-list') + '?u={}'.format(self.username)

    def all_ratings_url(self):
        return reverse('title-list') + '?u={}'.format(self.username) + '&all_ratings=on'

    def ratings_exclude(self):
        return reverse('title-list') + '?u={}&exclude_mine=on'.format(self.username)

    @property
    def picture_filename(self):
        return str(self.picture).split('/')[-1] if self.picture else ''

    @property
    def count_titles(self):
        """counts rated distinct titles"""
        return Title.objects.filter(rating__user=self).distinct().count()

    @property
    def count_ratings(self):
        """counts all the ratings"""
        return Title.objects.filter(rating__user=self).count()

    @property
    def count_movies(self):
        """counts rated distinct movies"""
        return Title.objects.filter(rating__user=self, type__name='movie').distinct().count()

    @property
    def count_series(self):
        """counts rated distinct series"""
        return Title.objects.filter(rating__user=self, type__name='series').distinct().count()

    # TODO
    @property
    def avg_of_current_ratings(self):
        """returns for a user average of his current ratings eg. {avg: 6.40, count: 1942}"""
        return avg_of_user_current_ratings(self.pk)

    @property
    def can_update_csv_ratings(self):
        return self.have_minutes_passed(self.last_updated_csv_ratings)

    @property
    def can_update_rss_ratings(self):
        return self.have_minutes_passed(self.last_updated_rss_ratings)

    @property
    def can_update_rss_watchlist(self):
        return self.have_minutes_passed(self.last_updated_rss_watchlist)

    @staticmethod
    def have_minutes_passed(time):
        three_minutes = 3 * 60
        if not time:
            # time is empty if user never did update
            return True
        return (timezone.now() - time).seconds > three_minutes

    @staticmethod
    def get_extension_condition(file, what_to_delete):
        if what_to_delete == 'picture':
            return any(file.endswith(ext) for ext in ['.jpg', '.png'])
        elif what_to_delete == 'csv':
            return file.endswith('.csv')
        return False


class UserFollow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='second_user')

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return '{} follows {}'.format(self.follower.username, self.followed.username)
