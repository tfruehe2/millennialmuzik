from .models import Tag
from .forms import CommentForm, PlaylistForm


def base(request):
    return {'genre_list': Tag.objects.all(), 'comment_form': CommentForm, 'playlist_form': PlaylistForm}

def session(request):
    for k,v in request.session.items():
        print ("{0}, {1}".format(k, v))
        session['k'] = v
    return session
