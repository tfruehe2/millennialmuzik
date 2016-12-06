from django.contrib import admin
from ordered_model.admin import OrderedTabularInline
from .models import Feed, Post, Comment, UserProfile, Tag, Song, Like, Playlist, PlaylistEntry, MusicRecommendation, Suggestion

SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']

class PlaylistEntryThroughModelInline(OrderedTabularInline):
    model = PlaylistEntry
    fields = ('song', 'order', 'move_up_down_links',)
    readonly_fields = ('order', 'move_up_down_links',)
    extra = 1
    ordering = ('order',)

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = (PlaylistEntryThroughModelInline, )

    def get_urls(self):
        urls = super(PlaylistAdmin, self).get_urls()
        for inline in self.inlines:
            if hasattr(inline, 'get_urls'):
                urls = inline.get_urls(self) + urls
        return urls

class FeedAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('title',)}

admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Feed, FeedAdmin)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(UserProfile)
admin.site.register(Tag)
admin.site.register(Song)
admin.site.register(Like)
admin.site.register(MusicRecommendation)
admin.site.register(Suggestion)
