from django.db import models
from conservancy.apps.staff.models import Person
from conservancy.apps.worldmap.models import EarthLocation
from datetime import datetime, timedelta

class EventTag(models.Model):
    """Tagging for events

    (currently unused)
    """

    label = models.CharField(max_length=100)

    date_created = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return self.label

class PastEventManager(models.Manager):
    """Returns all past events"""

    def get_queryset(self):
        return super(PastEventManager, self).get_queryset().filter(date__lt=datetime.today())

class FutureEventManager(models.Manager):
    """Returns all future events"""

    def get_queryset(self):
        return super(FutureEventManager, self).get_queryset().filter(date__gte=datetime.today())

class Event(models.Model):
    """Model for Conservancy staff member events (presentations, etc)"""

    title = models.CharField(max_length=400)
    date = models.DateField()
    date_tentative = models.BooleanField(default=False)
    datetime = models.CharField("Date and Time", max_length=300, blank=True)
    slug = models.SlugField(unique_for_year='date')
    description = models.TextField(blank=True)
    people = models.ManyToManyField(Person, null=True, blank=True)
    location = models.CharField(max_length=1000)
    earth_location = models.ForeignKey(EarthLocation, null=True, blank=True,
                                       help_text="Label will not be displayed")
    tags = models.ManyToManyField(EventTag, null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-date",)

    def __unicode__(self):
        return u"%s (%s)" % (self.title, self.date)

    def get_absolute_url(self):
        return u"/events/%s/%s/" % (self.date.strftime("%Y"), self.slug)

    def day_after(self):
        return self.date + timedelta(days=1)

    # for aggregate feed
    pub_date = property(lambda self: self.date_created)

    objects = models.Manager()
    past = PastEventManager()
    future = FutureEventManager()

class EventMedia(models.Model):
    """Media from an event

    includes transcripts, audio, and video pieces
    """

    event = models.ForeignKey(Event)
    format = models.CharField(max_length=1,
                              choices=(('T', 'Transcript'),
                                       ('A', 'Audio'),
                                       ('V', 'Video')))
    local = models.CharField(max_length=300, blank=True,
                             help_text="Local filename of the resource.  File should be uploaded into the static directory that corresponds to the event.")
    # verify_exists removed https://docs.djangoproject.com/en/1.7/releases/1.4/
    remote = models.URLField(blank=True,
                             help_text="Remote URL of the resource.  Required if 'local' is not given.")
    novel = models.BooleanField(help_text="Is it a new piece of media or another form of an old one?  If it is new it will be included in the event-media RSS feed and shown on the front page for a bit.", default=False)

    date_created = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'event media'

    def __unicode__(self):
        return u"%s media: %s" % (self.event, self.format)

