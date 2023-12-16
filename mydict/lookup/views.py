import json

from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import WordForm
from .models import Word


# Create your views here.
@csrf_exempt
def lookup(request):
    latest_word_list = Word.objects.order_by('-lookup_date')[:10]
    latest_word_json = serializers.serialize('json', latest_word_list)
    latest_word_object = json.loads(latest_word_json)
    if request.method == "POST":
        form = WordForm(request.POST)
        search_result = {}
        if form.is_valid():
            word = form.cleaned_data['word']
            added_instances = Word.objects.filter(word=word)
            added_instances_list = list(added_instances)
            search_result = form.search()
            search_result['success'] = True
            if not added_instances_list and 'exact_word' in search_result:
                instance_word = Word(word=word)
                instance_word.save()
        return JsonResponse({'result': search_result, 'history': latest_word_object, })
    else:
        return render(request, 'lookup/index.html', {'history': latest_word_list})
