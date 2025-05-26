from django.contrib import admin

from .models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'content', 'author__user__username')
    list_filter = ('created_at', 'tags')
    prepopulated_fields = {'content': ('title',)}

@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'question')
    search_fields = ('user__user__username', 'question__title')