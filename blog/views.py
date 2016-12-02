from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
import operator
import json
from django.db.models import DateField
from django.template import RequestContext
from django.template.loader import render_to_string
from .models import Feed, Post, UserProfile, Song, Like, Comment, Tag, Playlist, PlaylistEntry
from .forms import FeedForm, PostForm, UserProfileForm, CommentForm, SongForm, PlaylistForm, SuggestionsForm, SubmitMusicForm
from django.views.generic import DetailView, ListView
from django.views.generic.edit import ModelFormMixin, CreateView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from functools import reduce
from datetime import datetime

class JSONMixin(object):
    def render_to_response(self, context, **kwargs):
        return self.get_json_response(
            self.convert_context_to_json(context),
            **kwargs)

    def get_json_response(self, content, **kwargs):
        return HttpResponse(
            content,
            content_type='application/json',
            **kwargs)

    def convert_context_to_json(self, context):
        u""" This method serialises a Django form and
        returns JSON object with its fields and errors
        """
        form = context.get('form')
        to_json = {}
        options = context.get('options', {})
        to_json.update(options=options)
        to_json.update(success=context.get('success', False))
        fields = {}
        for field_name, field in form.fields.items():
            if isinstance(field, DateField) \
                    and isinstance(form[field_name].value(), datetime.date):
                fields[field_name] = \
                    unicode(form[field_name].value().strftime('%d.%m.%Y'))
            else:
                fields[field_name] = \
                    form[field_name].value() \
                    and unicode(form[field_name].value()) \
                    or form[field_name].value()
        to_json.update(fields=fields)
        if form.errors:
            errors = {
                'non_field_errors': form.non_field_errors(),
            }
            fields = {}
            for field_name, text in form.errors.items():
                fields[field_name] = text
            errors.update(fields=fields)
            to_json.update(errors=errors)
        return json.dumps(to_json)

class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


@login_required
def add_to_playlist(request):
    if request.method == "POST":
        playlist = request.POST.get('playlist_id')
        song = request.POST.get('song_id')
        if PlaylistEntry.objects.filter(song__pk=song,playlist__pk=playlist).exists():
            return HttpResponseRedirect('/')
        try:
            PlaylistEntry.objects.create(song=Song.objects.get(pk=song),
                                        playlist=Playlist.objects.get(pk=playlist))
            return HttpResponseRedirect('/')
        except:
            raise

@login_required
def edit_playlist(request):
    if request.method == "POST":
        i = 1
        playlist_id = request.POST.get('playlist_id')
        playlist = []

        if request.POST.get('deleted_songs'):
            delete_songs = [x for x in request.POST.get('deleted_songs').split(',') if str(x) != '']
            print(delete_songs)
            for song_id in delete_songs:
                print(song_id)
                song = PlaylistEntry.objects.get(playlist__pk=playlist_id, song__pk=song_id)
                song.delete()
                playlist = Playlist.objects.get(pk=playlist_id)
                playlist.save()
        if request.POST.get('song_order'):
            new_song_order = request.POST.get('song_order').split(',')
            for song_id in new_song_order:
                print(song_id)
                song = PlaylistEntry.objects.get(playlist__pk=playlist_id, song__pk=song_id)
                song.to(i)
                song.save()
                i+=1
                playlist = Playlist.objects.get(pk=playlist_id)
                playlist.save()
        context = {}
        context['playlist'] = playlist
        entrys = PlaylistEntry.objects.filter(playlist__pk=playlist_id)
        context['PlaylistEntry'] = entrys
        id_list = []
        for entry in entrys:
            id_list.append(str(entry.song.video_id))
        context['video_ids'] = id_list
        return render(request, 'blog/playlist.html', context)

@login_required
def create_playlist(request, **kwargs):

    if request.method == 'POST':
        form = PlaylistForm(request.POST)

        if form.is_valid():
            form.instance.created_by = request.user
            if 'image' in request.FILES:
                print("got here")
                form.instance.image = request.FILES['image']
            playlist = form.save()
            playlist.tags = Tag.objects.filter(name="PLLST")
            PlaylistEntry.objects.create(song=Song.objects.get(pk=kwargs['song_id']), playlist=playlist)
            playlist.save()

            return HttpResponseRedirect('/')
        else:
            song = Song.objects.get(pk=kwargs['song_id'])
            song_name = song.full_name
            song_id = song.pk
            feed_list = Post.objects.filter(is_private=False).order_by('-pub_date', 'title')
            return render(request, 'snippets/laziness.html', {'playlist_form': form, "song_name":song_name, "song_id":song_id, "feed_list":feed_list })


class index(ListView):
    template_name = 'blog/index.html'
    context_object_name = 'feed_list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(index, self).get_context_data(**kwargs)
        context['request'] = self.request
        context['user'] = self.request.user
        #can pass request to cookie handler later
        return context

    def get_queryset(self):
        return Post.objects.filter(is_private=False).order_by('-pub_date', 'title')

class feed(ListView):
    template_name = "blog/blog_feed.html"
    context_object_name = 'post_list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(feed, self).get_context_data(**kwargs)
        context['title'] = self.kwargs['slug'].capitalize()
        return context

    def get_queryset(self):
        return Post.objects.filter(feed__slug=self.kwargs['slug'])

class BlogPost(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/blog_post.html'
    def get_context_data(self, **kwargs):
        context = super(BlogPost, self).get_context_data(**kwargs)
        if self.request.session.get(self.object.title, False):
            last_visit_cookie = get_server_side_cookie(self.request, self.object.title)
            last_visit_time = datetime.strptime(last_visit_cookie[:16], "%Y-%m-%d %H:%M")
            if (datetime.now() - last_visit_time).seconds > 1800:
                self.object.increment_view_count()
                self.request.session[self.object.title] = str(datetime.now())
        else:
            self.object.increment_view_count()
            self.request.session[self.object.title] = str(datetime.now())

        return context

class PopularMusic(ListView):
    template_name = "blog/blog_feed.html"
    context_object_name = 'post_list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(PopularMusic, self).get_context_data(**kwargs)
        context['title'] = "Popular Music"
        return context

    def get_queryset(self):
        return Post.objects.filter(is_song=True).order_by('-num_likes', 'title')

class MusicByGenre(ListView):
    template_name = "blog/music_genre.html"
    context_object_name = 'post_list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(MusicByGenre, self).get_context_data(**kwargs)
        context['title'] = "Music by Genre"
        return context

    def get_queryset(self):
        if self.kwargs['kw'] != None:
            tag = Tag.objects.get(name=self.kwargs['kw'].upper())
            return tag.post_set.all()
        return Post.objects.filter(is_song=True)

class music_by_genre(ListView):
    template_name="blog/post_list.html"
    context_object_name = 'post_list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(music_by_genre, self).get_context_data(**kwargs)
        context['newurl'] = "/musicblog/genre/" + self.kwargs['kw'] +"/"
        return context

    def get_queryset(self):
        #if self.kwargs['kw']:
        tag = Tag.objects.get(name=self.kwargs['kw'].upper())
        return tag.post_set.all()

class TrendingMusic(ListView):
    template_name = "blog/blog_feed.html"
    context_object_name = 'post_list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(TrendingMusic, self).get_context_data(**kwargs)
        context['title'] = "Trending Music"
        return context

    def get_queryset(self):
        return Post.objects.filter(is_song=True).order_by('-views', 'title')

class Search_Results(ListView):
    template_name = "blog/search_results.html"
    context_object_name = "search_results"
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        result = Post.objects.all()
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                       (Q(title__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(description__icontains=q) for q in query_list))
            )

        return result


class Playlist_Feed(ListView):
    template_name = "blog/blog_feed.html"
    context_object_name = 'post_list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(Playlist_Feed, self).get_context_data(**kwargs)
        context['title'] = "Playlists"
        return context

    def get_queryset(self, *args, **kwargs):
        return Post.objects.filter(is_playlist=True, is_private=False).order_by('-pub_date', 'title')

class Playlist_View(DetailView):
    model = Playlist
    context_object_name = 'playlist'
    template_name = 'blog/playlist_sample.html'

    def get_context_data(self, **kwargs):
        context = super(Playlist_View, self).get_context_data(**kwargs)
        entrys = PlaylistEntry.objects.filter(playlist=self.object)
        if self.request.session.get(self.object.post.title, False):
            last_visit_cookie = get_server_side_cookie(self.request, self.object.post.title)
            last_visit_time = datetime.strptime(last_visit_cookie[:16], "%Y-%m-%d %H:%M")
            if (datetime.now() - last_visit_time).seconds > 1800:
                self.object.post.increment_view_count()
                self.request.session[self.object.post.title] = str(datetime.now())
        else:
            self.object.post.increment_view_count()
            self.request.session[self.object.post.title] = str(datetime.now())

        context['PlaylistEntry'] = entrys
        id_list = []
        for entry in entrys:
            id_list.append(str(entry.song.video_id))
        context['video_ids'] = id_list
        return context


class profile_page(DetailView):
    model = UserProfile
    context_object_name = 'profile'
    template_name = 'blog/profile_page.html'

    def get_context_data(self, **kwargs):
        context = super(profile_page, self).get_context_data(**kwargs)
        context['playlists'] = self.object.playlist_set.all()
        return context


class music_post(DetailView):
    model = Post
    context_object_name = 'music_post'
    template_name = 'blog/music_post.html'

def fetch_user_playlists(request, **kwargs):
    if request.is_ajax():
        userprofile = UserProfile.objects.get(pk=kwargs['pk'])
        playlists = Playlist.objects.all()
        context = {'playlists': playlists}
        html = render_to_string('blog/playlist_list.html', context)
        return HttpResponse(html)

def suggestions(request):
    if request.method == "GET":
        form = SuggestionsForm()
        return render(request, 'blog/suggestions.html', {'form': form})
    if request.method == "POST":
        form = SuggestionsForm(request.POST)
        return HttpResponseRedirect('/')

def submit_music(request):
    if request.method == "GET":
        form = SubmitMusicForm()
        return render(request, 'blog/submit_music.html', {'form': form})
    if request.method == "POST":
        form = SubmitMusicForm(request.POST)
        return HttpResponseRedirect('/')


def about(request):
    return render(request, 'blog/about.html')

def add_feed(request):
    form = FeedForm()
    if request.method == 'POST':
        form = FeedForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
    else:
        return render(request, 'blog/add_feed.html', {'form': form})

def add_post_test(request, feed_name_slug):
    try:
        feed = Feed.objects.get(slug=feed_name_slug)
    except Feed.DoesNotExist:
        feed = None
    form = PostForm()
    if request.method == 'POST':
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)

    context_dict = {'form': form, 'feed': feed}
    return render(request, 'blog/add_post.html', context_dict)

def delete_post(request):
    if request.method == 'POST':
        post = Post.objects.get(pk=request.POST.get('post_id'))
        post.delete()
        return HttpResponse(
            json.dumps({'success': 'success'}),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({'failure':'this should never happen'}),
            content_type="application/json"
        )

class add_song(CreateView):
    model = Song
    form_class = SongForm
    template_name = "blog/add_song.html"
    success_url ='/'

    def form_valid(self, form):
        user = self.request.user
        form.instance.author = UserProfile.objects.get(user=user)
        return super(add_post, self).form_valid(form)



class add_post(CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/add_post.html"
    success_url ='/'

    def form_valid(self, form):
        user = self.request.user
        form.instance.author = UserProfile.objects.get(user=user)
        return super(add_post, self).form_valid(form)

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserProfileForm(data=request.POST)

        if user_form.is_valid():
            from django.contrib.auth.backends import ModelBackend
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True
            user = authenticate(username=user.username, password=user.password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                print('fuck')
        else:
            print(user_form.errors)
            return render(request, 'blog/register.html', {'user_form': user_form})

    else:
        user_form = UserProfileForm()

    return render(request, 'blog/register.html', {'user_form': user_form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                request.session['loggedin'] = True
                return HttpResponseRedirect('/')

            else:
                return HttpResponse("your account is disabled")

        else:
            print("invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details entered")

    else:
        return render(request, 'blog/login.html', {})

def view_incrementor(request):
    if request.method == 'POST':
        vid_id = request.POST.get('vid_id')
        post = Post.objects.get(song__video_id=vid_id)
        response_object = {}
        response_object['views'] = post.increment_view_count()
        return HttpResponse(
            json.dumps(response_object),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({'failure':'this should never happen'}),
            content_type="application/json"
        )

def add_like(request):
    if request.method == 'POST':
        user_prof = UserProfile.objects.get(username=request.user.username)
        post = Post.objects.get(pk=request.POST.get('post_id'))
        response_data = {}
        if Like.objects.filter(user=user_prof, post=post).exists():
            like = Like.objects.get(user=user_prof, post=post)
            like.delete()
            like_count = post.num_likes - 1
            post.num_likes = like_count
            post.save()
            response_data['num_likes'] = like_count
            response_data['already_liked'] = True
            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
        Like.objects.create(user=user_prof, post=post)
        response_data['num_likes'] = post.num_likes
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({'failure':'this should never happen'}),
            content_type="application/json"
        )



def post_comment(request, **kwargs):
    if request.method == "POST":
        form = CommentForm(request.POST)
        print(form)
        if form.is_valid():
            form.instance.userprofile = request.user
            form.instance.post = Post.objects.get(pk=kwargs['post_id'])
            form.save()
            return HttpResponse(
                json.dumps({"success":"True"}),
                content_type="application/json"
            )

    response_data = {"success":"False"}
    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', 1))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:7], '%Y-%m')

    if (datetime.now() - last_visit_time).days > 0:
        visits += 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits
