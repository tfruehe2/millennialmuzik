from django import forms
from django.forms import ModelForm
from .models import Feed, Post, UserProfile, Comment, Song, Playlist, Suggestion, MusicRecommendation
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, HTML
from crispy_forms.bootstrap import FormActions, StrictButton

class FeedForm(ModelForm):
    class Meta:
        model = Feed
        fields = ['title', 'description']
        labels = {
        'title': "Title:",
        'description': "Description:",
        }

class PostForm(ModelForm):
    description = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Post
        fields = ['feed', 'title', 'description', 'image', 'tags']
        labels = {
        'feed': "Feed:",
        'title': "Title:",
        'description': "Description:",
        'image': "Image:",
        'tags': 'Tags:',
        }

class SongForm(ModelForm):

    class Meta:
        model = Song
        fields = ['artist', 'song_name', 'video', 'tags']


class UserProfileForm(ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}
    ), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}
    ), label="Confirm Password")

    class Meta:
        model = UserProfile
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter Username'}
            ),
            'email': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter Email'}
            ),
            'password1': forms.PasswordInput(
                attrs={'class': 'form-control', 'placeholder': 'Password'}
            ),
            'password1': forms.PasswordInput(
                attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}
            ),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(UserProfileForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class PlaylistForm(ModelForm):

    class Meta:
        model = Playlist
        fields = ['name', 'description', 'image', 'is_private']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': "playlist name..."}
            ),
            'description': forms.Textarea(
                attrs={'class':'form-control', "rows":'4', 'placeholder':"my favorite [insert genre] songs..."}
            ),
            'image': forms.FileInput(),
        }

        labels = {
        'name': 'Playlist Name',
        'description': 'Description',
        'image': "Playlist Image",
        'is_private': "I want this playlist to be private"
        }


class CommentForm(ModelForm):
    body = forms.CharField(widget=forms.Textarea(
        attrs={'class':'form-control', 'placeholder':"comment...", "rows":'6'}
    ))
    class Meta:
        model = Comment
        fields = ['body',]

class SubmitMusicForm(ModelForm):
    artist = forms.CharField(required=True, label="Artist", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': "artist's name..."}
        ));
    song_name = forms.CharField(required=True, label="Song Name", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': "song's name..."}
    ));
    url = forms.CharField(required=False, label="Video Url", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': "optional url to music video..."}
    ));
    class Meta:
        model = MusicRecommendation
        fields = ['artist', 'song_name', 'url']


class SuggestionsForm(ModelForm):
    what = forms.CharField(required=True, label="What Needs Improvement?", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': "what about this website pisses you off..."}
    ));
    how = forms.CharField(label="How Should I Improve it?", widget=forms.Textarea(
        attrs={'class':'form-control', 'placeholder':"suggestions or example of website that does it better...", "rows":'4'}
    ));
    class Meta:
        model = Suggestion
        fields = ['what', 'how']
