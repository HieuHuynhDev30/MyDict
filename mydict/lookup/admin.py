from django.contrib import admin

from .models import Word


# Register your models here.
class WordAdmin(admin.ModelAdmin):
    fields = ['word', 'lookup_date']


admin.site.register(Word, WordAdmin)
