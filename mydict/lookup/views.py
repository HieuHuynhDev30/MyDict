from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import WordForm
from .models import Word


# Create your views here.
@csrf_exempt
def lookup(request):
    if request.method == "POST":
        form = WordForm(request.POST)
        if form.is_valid():
            word = form.cleaned_data['word']
            added_instances = Word.objects.filter(word=word)
            added_instances_list = list(added_instances)
            search_result = form.search()
            search_result['success'] = True
            if not added_instances_list and 'exact_word' in search_result:
                instance_word = Word(word=word)
                instance_word.save()
            return JsonResponse({'result': search_result})
    else:
        return render(request, 'lookup/index.html')
