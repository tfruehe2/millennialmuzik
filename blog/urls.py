from django.conf.urls import url, include
from . import views
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.conf.urls.static import static

app_name = 'blog'

extra_patterns = [
     url(r'^$', views.Music.as_view(), name="Music"),
     url(r'^popular/(?P<kw>[\w]+)?/?$', views.PopularMusic.as_view(), name="PopularMusic"),
     url(r'^genre/(?P<kw>[\w]+)?/?$', views.MusicByGenre.as_view(), name="MusicByGenre"),
     url(r'^trending/$', views.TrendingMusic.as_view(),  name="TrendingMusic"),
     url(r'^random/$', views.random_song, name="random_song"),
 ]

urlpatterns = [
    url(r'^$', views.index.as_view(), name='index'),
    url(r'^musicblog/', include(extra_patterns)),
    url(r'^(?P<slug>[\w\-]+)blog/$', views.feed.as_view(), name="feed"),
    url(r'^(?P<slug>[\w\-]+)blog/(?P<pk>[0-9]+)/$', views.BlogPost.as_view(), name="BlogPost"),
    url(r'^profile/(?P<pk>[0-9]+)/$', views.profile_page.as_view(), name="profile_page"),
    url(r'^playlist/$', views.Playlist_Feed.as_view(), name="playlist_feed"),
    url(r'^playlist/(?P<pk>[0-9]+)', views.Playlist_View.as_view(), name="playlist"),
    url(r'^about/$', views.about, name="about"),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': reverse_lazy('blog:login')}, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^search/$', views.Search_Results.as_view(), name="search"),
    url(r'^add_feed/$', views.add_feed, name="add_feed"),
    url(r'^view_incrementor/$', views.view_incrementor, name="view_incrementor"),
    url(r'^post/add_like/$', views.add_like, name="add_like"),
    url(r'^fetch_music/(?P<kw>[\w]+)/$', views.music_by_genre.as_view(), name="music_by_genre"),
    url(r'^fetch_user_playlists/(?P<pk>[0-9]+)/$', views.fetch_user_playlists, name="user_playlists"),
    url(r'^post_comment/(?P<post_id>[0-9]+)/$', views.post_comment, name="post_comment"),
    url(r'^popular_music/(?P<kw>[\w]+)/$', views.popular_music.as_view(), name="popular_music"),
    url(r'^add_post/$', views.add_post.as_view(), name='add_post'),
    url(r'^add_song/$', views.add_song.as_view(), name='add_song'),
    url(r'^add_to_playlist/$', views.add_to_playlist, name="add_to_playlist"),
    url(r'^create_playlist/(?P<song_id>[0-9]+)/$', views.create_playlist, name="create_playlist"),
    url(r'^edit_playlist/$', views.edit_playlist, name="edit_playlist"),
    url(r'^delete_post/$', views.delete_post, name="delete_post"),
    url(r'^add_suggestion/$', views.suggestions, name="suggestions"),
    url(r'^submit_music/$', views.submit_music, name="submit_music"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
