from django.contrib import admin

from .models import Post, Comment
from .models import Group, Follow


class PostAdmin(admin.ModelAdmin):
    list_editable = ('group',)
    list_display = ('pk', 'text', 'pub_date',
                    'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'description')
    search_fields = ('title',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'post', 'author', 'text', 'created')
    list_filter = ('author',)
    search_fields = ('author', 'created')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    list_filter = ('author',)
    search_fields = ('user', 'author')


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
