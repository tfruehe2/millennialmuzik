from django.db import models
from ordered_model.models import OrderedModel
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from embed_video.fields import EmbedVideoField
from django.core.files import File
from django.conf import settings
import datetime
import urllib.parse
import os

class Feed(models.Model):
    title = models.CharField(max_length=40)
    description = models.CharField(max_length=200)
    url = models.URLField(blank=True)
    slug = models.SlugField(max_length=40, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '{}blog/'.format(self.slug)

    def save(self):
        if not self.slug:
            self.slug = slugify(self.title)
            self.url = "blog/{}".format(self.slug)
        super(Feed, self).save()

class UserProfile(AbstractUser):
    signup_date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
            'Post',
            through='Like',
            through_fields=('user', 'post'),
            blank=True,
            related_name='liked_by',
    )

    def __str__(self):
        return self.username

class Post(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    comments = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Comment',
        through_fields=('post', 'userprofile'),
        related_name='commenter',
        blank=True,
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="post_images/", blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    num_likes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    is_song = models.BooleanField(default=False)
    is_playlist = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def increment_view_count(self):
        self.views = self.views + 1
        self.save()
        return self.views

    def increment_like_count(self):
        likes = self.num_likes + 1
        self.num_likes = likes
        self.save()

    def get_absolute_url(self):
        return 'http://www.millennialsmusic.com/{}blog/{}'.format(self.feed.slug, self.id)


    def quote_url(self):
        return urllib.parse.quote(self.get_absolute_url())


class Song(models.Model):
    artist = models.CharField(max_length=50)
    song_name = models.CharField(max_length=100, unique=True)
    feat_artist = models.CharField(max_length=50, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    video = EmbedVideoField(unique=True)
    video_id = models.CharField(max_length=20, blank=True)
    post = models.OneToOneField(Post, on_delete=models.CASCADE, blank=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lyrics = models.TextField(blank=True)
    image = models.ImageField(upload_to="song_images/", blank=True)

    def _get_full_name(self):
        if self.feat_artist:
            return '{} - {} (Ft. {})'.format(self.artist, self.song_name, self.feat_artist)

        return '{} - {}'.format(self.artist, self.song_name)

    def set_lyrics(self, song, artist):
        self.lyrics = fetch_lyrics(song, artist)
        return self.lyrics

    def grep_video_id(self):
        if not self.video_id:
            import re
            idRegex = re.compile(r'(?<=\?v=).{11}')
            self.video_id = idRegex.search(self.video).group()
        return self.video_id

    def set_image(self, video_id):
        f, fn = retrieve_thumbnail(video_id)
        self.image.save(fn, f, save=False)

    full_name = property(_get_full_name)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.set_lyrics(self.song_name, self.artist)
            self.set_image(self.grep_video_id())
            self.post = Post.objects.create(feed=Feed.objects.get(title='Music'),
                                    title=self.full_name, author=self.added_by,
                                    description=self.lyrics,
                                    image=self.image,
                                    is_song=True)
        super(Song, self).save(*args, **kwargs)
        self.post.tags = self.tags.all()
        self.post.save()


class Playlist(models.Model):
    name = models.CharField(max_length=100)
    pub_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    song_list = models.TextField(blank=True)
    songs = models.ManyToManyField('Song', through='PlaylistEntry')
    image = models.ImageField(upload_to="playlist_images/", blank=True)
    tags = models.ManyToManyField('Tag')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.OneToOneField(Post, on_delete=models.CASCADE, blank=True)
    is_private = models.BooleanField(default=False)

    def create_song_list(self):
        names = ""
        i = 1
        for song in self.songs.all():
            formatted_name = str(i) + ") " + song.full_name + "\n"
            names += formatted_name
            i += 1
        return names

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.post = Post.objects.create(feed=Feed.objects.get(title='Playlists'),
                        title=self.name, author=self.created_by,
                        description=self.description, image=self.image,
                        is_playlist=True,
                        is_private=self.is_private)

        super(Playlist, self).save(*args, **kwargs)
        self.post.tags = Tag.objects.filter(name='PLLST')
        self.post.save()

class PlaylistEntry(OrderedModel):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    order_with_respect_to = 'playlist'

    class Meta(OrderedModel.Meta):
        ordering = ('playlist','order')


class Comment(models.Model):
    body = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    userprofile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    def __str__(self):
        return "{}-{}: {}".format(self.userprofile, self.post, self.pub_date)

    def upvote_comment(self):
        count = self.upvotes + 1
        self.upvotes = count

    def upvote_comment(self):
        count = self.downvotes + 1
        self.downvotes = count

class Like(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__ (self):
        return "{} liked by: {}".format(str(self.post), str(self.user))

    def save(self, **kwargs):
        self.post.increment_like_count()
        super(Like, self).save(**kwargs)

class Tag(models.Model):
    TAG_CHOICES = (
        ('ACSTC','Acoustic'),
        ('ALTR', 'Alt Rock'),
        ('ALT', 'Alternative'),
        ('CLSR', 'Classic Rock'),
        ('ELEC', 'Electronic'),
        ('FEML', 'Female Vocals'),
        ('FLK', 'Folk'),
        ('FNK', 'Funk'),
        ('HH', 'Hip-Hop'),
        ('IND', 'Indie'),
        ('POP', 'Pop.'),
        ('PSYCH', 'Psychedelic'),
        ('PUNK', 'Punk Rock'),
        ('RB', "R & B"),
        ('REG', 'Reggae'),
        ('RMX', 'Remix'),
        ('SOUL', 'Soul'),
        ('SKA', 'Ska'),
        ('PLLST', 'Playlist'),
    )
    name = models.CharField(max_length=5, choices=TAG_CHOICES)
    def __str__(self):
        return self.name


class Suggestion(models.Model):
    what = models.CharField(max_length=144)
    how = models.TextField(max_length=250,blank=True)
    def __str__(self):
        return self.what

class MusicRecommendation(models.Model):
    artist = models.CharField(max_length=100)
    song_name = models.CharField(max_length=100)
    user = models.ForeignKey(UserProfile, blank=True)
    url = models.URLField(blank=True)
    def __str__(self):
        return "{} - {}".format(self.artist, self.song_name)

def retrieve_thumbnail(vid_id):
    import urllib.request
    from django.core.files import File

    def create_url(v_id):
        base_url = 'http://img.youtube.com/vi/'
        url = base_url + v_id +'/0.jpg'
        return url

    def fetch_jpg(url, v_id):
        sauce = urllib.request.urlopen(url).read()
        fn = str(v_id) + '.jpg'
        path = settings.MEDIA_ROOT + '/post_images/' + fn
        with open(path, 'wb') as f:
            myfile = File(f)
            myfile.write(sauce)
            f.close()
        return (path, fn)

    URL = create_url(vid_id)
    path, fn = fetch_jpg(URL, vid_id)
    reopen_f = open(path, 'rb')
    django_file = File(reopen_f)
    return (django_file, fn)

def fetch_lyrics(song_title, artist_name):
    import requests
    from bs4 import BeautifulSoup
    from secrets import GENIUS_AUTH_TOKEN

    headers = {'Authorization': GENIUS_AUTH_TOKEN}

    base_url = "http://api.genius.com"
    search_url = base_url + "/search"

    def lyrics_from_song_api_path(song_api_path):
        song_url = base_url + song_api_path
        resp = requests.get(song_url, headers=headers)
        json = resp.json()
        path = json["response"]["song"]["path"]
        #html scraping
        page_url = "http://genius.com" + path
        page = requests.get(page_url)
        html = BeautifulSoup(page.text, "html.parser")
        [ h.extract() for h in html('script')]
        lyrics = html.find("lyrics").get_text()
        return lyrics

    data = {'q' : song_title}
    resp = requests.get(search_url, data=data, headers=headers)
    json = resp.json()
    song_info = None
    for hit in json["response"]["hits"]:
        if artist_name in hit["result"]["primary_artist"]["name"]:
            song_info = hit
            break
    if song_info:
        song_api_path = song_info["result"]["api_path"]
        return lyrics_from_song_api_path(song_api_path)
    else:
        data = {'q' : artist_name + " - " + song_title }
        resp = requests.get(search_url, data=data, headers=headers)
        json = resp.json()
        for hit in json["response"]["hits"]:
            if artist_name in hit["result"]["primary_artist"]["name"]:
                song_info = hit
                song_api_path = song_info["result"]["api_path"]
                return lyrics_from_song_api_path(song_api_path)

    return "Sorry!\nThe lyrics for this song are unavailable"
