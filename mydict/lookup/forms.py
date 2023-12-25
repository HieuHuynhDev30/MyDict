import requests
from django import forms


def find_key(json_input, key):
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            if k == key:
                yield v
            if isinstance(v, (dict, list)):
                yield from find_key(v, key)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from find_key(item, key)


def get_valid(json, key):
    valid_list = []
    stems = next(find_key(json, key))
    for phrase in stems:
        valid_list.append(phrase.casefold())
    return valid_list


def get_audio(json):
    audio = next(find_key(json, 'audio'))
    audio_srcs = []
    if audio:
        subdirectory = audio[0]
        prefixes = ['bix', 'gg', *tuple(list('0123456789'))]
        for prefix in prefixes:
            if audio.startswith(prefix, 0):
                subdirectory = prefix
        formats = ['mp3', 'wav', 'ogg']
        for ext in formats:
            audio_srcs.append({'src': f'''https://media.merriam-webster.com/audio/prons/en/us/mp3/{subdirectory}/{audio}.{ext}''', 'type': ext})
    return audio_srcs


def get_meanings(json, key=''):
    meanings = []
    if type(json) is str:
        meanings_list = [json]
    else:
        meanings_list = next(find_key(json, key))
    if isinstance(meanings_list, list):
        for i, meaning in enumerate(meanings_list):
            if isinstance(meaning, str):
                meaning = meaning.replace('{b}', '<strong>')
                meaning = meaning.replace('{/b}', '</strong>')
                meaning = meaning.replace('{inf}', '<sub>')
                meaning = meaning.replace('{/inf}', '</sub>')
                meaning = meaning.replace('{it}', '<i>')
                meaning = meaning.replace('{/it}', '</i>')
                meaning = meaning.replace('{ldquo}', '"')
                meaning = meaning.replace('{rdquo}', '"')
                meaning = meaning.replace('{', '<')
                meaning = meaning.replace('}', '>')
                meaning = meaning.strip()
                meanings_list[i] = meaning.capitalize()
            else:
                meanings_list[i] = 'undefined'
            meanings.append(meanings_list[i])
    else:
        meanings.append(meanings_list)
    return meanings


def get_collocations(json):
    collocations_list = []
    dros_object = next(find_key(json, 'dros'), [])
    for dro in dros_object:
        collo_object = {}
        collo_object['exact_word'] = dro['drp']
        collo_object['gram'] = next(find_key(dro, 'gram'), 'collocation')
        meaning_str = f"{next(find_key(dro, 'dt'))[0][1]}"
        collo_object['meaning'] = get_meanings(meaning_str)
        collo_object['usage'] = next(find_key(dro, 'pva'), collo_object['meaning'])
        collocations_list.append(collo_object)
    return collocations_list


class WordForm(forms.Form):
    word = forms.CharField(label='Your word', max_length=50)

    def search(self):
        result = {}
        api_key = '57f42480-9178-4af8-9398-2f75f536fc08'
        searched_word = self.cleaned_data['word']
        searched_word = searched_word.strip()
        searched_word = searched_word.casefold()
        word_list = searched_word.split()
        result['valid'] = []
        result['exact_word'] = []
        result['types'] = []
        result['ipas'] = []
        result['audio_srcs'] = []
        result['meanings'] = []
        result['collocations'] = []
        result['message'] = ''
        if '' in searched_word:
            result['is_collocations'] = True
        for each in word_list:
            if each.isalpha():
                api_url = f'''https://www.dictionaryapi.com/api/v3/references/learners/json/{each}?key={api_key}'''
                response = requests.get(api_url)
                if response.status_code == 200:
                    response = response.json()
                    response_str = str(response)
                    if response:
                        if 'meta' in response_str:
                            # if " " not in searched_word:
                            result['valid'] += get_valid(response, 'stems')
                            result['types'].append(next(find_key(response, 'fl')))
                            result['ipas'].append(f"/{next(find_key(response, 'ipa'))}/")
                            result['audio_srcs'] += get_audio(response)
                            result['meanings'] += get_meanings(response, 'def')
                            result['collocations'] += get_collocations(response)
                        else:
                            result['message'] = f'Do you mean one of these valid:'
                            result['valid'].append(*tuple(response))
                    else:
                        result['message'] = f'No results for "{searched_word}"'
                else:
                    result['message'] = 'Server not working'
            else:
                result['message'] = 'Invalid typing'
        if not result['message']:
            if searched_word in result['valid']:
                result['exact_word'].append(searched_word)
            if result['is_collocations']:
                for each in result['collocations']:
                    if each['exact_word'] == searched_word:
                        result['gram'] = each['gram']
                        result['meanings'] = [each['meaning']]
                        result['usage'] = each['usage']
                        break
            result['message'] = f'Showing results for "{searched_word}"'
        return result
