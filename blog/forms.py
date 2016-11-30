from django import forms
from django.forms import ModelForm
from .models import Feed, Post, UserProfile, Comment, Song, Playlist
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
        fields = ['name', 'description', 'image', 'is_private', 'tags', 'created_by', 'songs']
        widgets = {'songs': forms.HiddenInput(),
                'tags': forms.HiddenInput(),'created_by':forms.HiddenInput()}
        labels = {
        'name': 'Playlist Name'
        }
    def __init__(self, *args, **kwargs):
        super(PlaylistForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'playlistForm'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-8'
        self.helper.form_method = "POST"




class CommentForm(ModelForm):
    body = forms.CharField(widget=forms.Textarea(
        attrs={'class':'form-control', 'placeholder':"comment...", "rows":'6'}
    ))
    class Meta:
        model = Comment
        fields = ['body',]
