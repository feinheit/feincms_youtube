# coding=utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django import forms
import gdata
from gdata.youtube.service import RequestError, YouTubeService
from django.template.context import RequestContext
from django.conf import settings
from datetime import date
import random

""" 
To use this content type, you need the Gdata Python Client Library.
Download it here: http://code.google.com/p/gdata-python-client/downloads/list
Make a symlink to src/gdata and src/atom

Check out http://googlesystem.blogspot.com/2008/01/youtube-feeds.html for
how to get the URL of the feeds.

Make sure you set the permission on the gdata and atom folder for your webserver.
"""

DIMENSION_CHOICES = (
    ('504x324', _('Facebook Tab Video')),
)

YOUTUBE_FORM_MEDIA_DICT = {'youtube_choices': 
                             {'css':{'all':('content/youtube/choices.css',)},
                               'js':('content/youtube/jquery.infinitecarousel2.min.js', 
                                     'content/youtube/choices.js')},
}


YOUTUBE_CHOICES = (
    ('feed', _('Playlist')),
    ('choices', _('Choices')),
    ('first', _('First video')),
    ('daily', _('Daily video')),
    ('random', _('Random video')),
)

class YoutubeVideoFeedContent(models.Model):
    
    feed = models.URLField(_('Playlist'), max_length=100,
                help_text='i.e. http://gdata.youtube.com/feeds/api/users/garyferro/favorites?orderby=updated<br />http://gdata.youtube.com/feeds/api/playlists/50653251EDB4E764')
    
    @classmethod
    def initialize_type(cls, TYPE_CHOICES=YOUTUBE_CHOICES, DIMENSION_CHOICES=DIMENSION_CHOICES,
                        MOVIE_ATTRS=None, FORM_MEDIA_DICT=YOUTUBE_FORM_MEDIA_DICT):
        cls.add_to_class('type', models.CharField(_('Type'), max_length=10, 
                                choices=TYPE_CHOICES))
        if DIMENSION_CHOICES is not None:
            cls.add_to_class('dimension', models.CharField(_('dimension'),
                max_length=12, blank=True, null=True, choices=DIMENSION_CHOICES,
                default=DIMENSION_CHOICES[0][0]))
        cls.FORM_MEDIA_DICT = FORM_MEDIA_DICT
    
    class Meta:
        verbose_name = _('Video feed')
        verbose_name_plural = _('Video feeds')
        abstract = True
    
    def __unicode__(self):
        return unicode(self.feed)
    
    @property
    def media(self):
        media = forms.Media()
        if self.FORM_MEDIA_DICT.get('youtube_%s' % self.type, None):
            media.add_css(self.FORM_MEDIA_DICT['youtube_%s' % self.type].get('css', {}))
            media.add_js(self.FORM_MEDIA_DICT['youtube_%s' % self.type].get('js', ''))    
        return media
    
    def service(self):
        yt_service = YouTubeService()
        yt_service.ssl = False
        yt_service.developer_key = getattr(settings, 'YOUTUBE_DEV_KEY', None)
        yt_service.client_id = getattr(settings, 'YOUTUBE_CLIENT_ID', None)
        return yt_service
    
    def render(self, **kwargs):
        request = kwargs.get('request')
        yt_service = self.service()
        today = date.today().toordinal()
        try:
            feed = yt_service.GetYouTubeVideoFeed(self.feed)
        except RequestError:
            return HttpResponse(ugettext(u'Es gab ein Fehler beim Verbinden mit Youtube. Bitte versuchen Sie es nochmals.'))
        entries = feed.entry
        
        context = {'entries': entries, 'first': entries[0], 'movie': entries[0] }
        if 'dimension' in dir(self):
            context['dimensions'] = self.dimension.split('x')
        
        if self.type == 'daily':
            # Get daily movie:
            if len(entries) > 0:
                index = today % len(entries)
                context['movie'] = entries[index]
        
        elif self.type == 'random':
            if len(entries) > 0:
                context ['movie'] = random.choice(entries)
                
        if settings.DEBUG:
            context['self'] = self
        
        return render_to_string(['content/youtube/%s.html' % self.type, 
                                 'content/youtube/default.html'], 
                         context, RequestContext(request))
