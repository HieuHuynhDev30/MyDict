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


def get_meanings(json, key):
    meanings = []
    if isinstance(json, dict):
        meanings_list = next(find_key(json, key))
    else:
        meanings_list = [json]
    if isinstance(meanings_list, list):
        for i, meaning in enumerate(meanings_list):
            if isinstance(meaning, str):
                meaning = meaning.replace('{bc}', '')
                meaning = meaning.replace('{b}', '<strong>')
                meaning = meaning.replace('{/b}', '</strong>')
                meaning = meaning.replace('{inf}', '<sub>')
                meaning = meaning.replace('{/inf}', '</sub>')
                meaning = meaning.replace('{it}', '<i>')
                meaning = meaning.replace('{/it}', '</i>')
                meaning = meaning.strip()
                meanings_list[i] = meaning.capitalize()
            else:
                meanings_list[i] = 'undefined'
            meanings.append(meanings_list[i])
    else:
        meanings.append(meanings_list)
    return meanings


class WordForm(forms.Form):
    word = forms.CharField(label='Your word', max_length=50)

    def search(self):
        result = {}
        api_key = '57f42480-9178-4af8-9398-2f75f536fc08'
        searched_word = self.cleaned_data['word']
        searched_word = searched_word.strip()
        searched_word = searched_word.casefold()
        word_set = searched_word.split()
        for each in word_set:
            if each.isalpha():
                api_url = f'''https://www.dictionaryapi.com/api/v3/references/learners/json/{each}?key={api_key}'''
                response = requests.get(api_url)
                if response.status_code == 200:
                    response = response.json()
                    response_str = str(response)
                    if response:
                        if 'meta' in response_str:
                            if " " not in searched_word:
                                # if 'meta' in response_str:
                                stems = next(find_key(response, 'stems'))
                                result['phrases'] = []
                                for phrase in stems:
                                    result['phrases'].append(phrase.casefold())
                                if searched_word in result['phrases']:
                                    for phrase in result['phrases']:
                                        if phrase == searched_word:
                                            result['exact_word'] = phrase
                                result['type'] = next(find_key(response, 'fl'))
                                result['ipa'] = f"/{next(find_key(response, 'ipa'))}/"
                                audio = next(find_key(response, 'audio'))
                                if audio:
                                    subdirectory = audio[0]
                                    result['has_audio'] = True
                                    prefixes = ['bix', 'gg', *tuple(list('0123456789'))]
                                    for prefix in prefixes:
                                        if audio.startswith(prefix, 0):
                                            subdirectory = prefix
                                    formats = ['mp3', 'wav', 'ogg']
                                    audio_srcs = []
                                    for ext in formats:
                                        audio_srcs.append({
                                            'src': f'''https://media.merriam-webster.com/audio/prons/en/us/mp3/{subdirectory}/{audio}.{ext}''',
                                            'type': ext})
                                    result['audio_srcs'] = audio_srcs
                                result['meanings'] = get_meanings(response, 'def')
                                result['message'] = f'Showing results for "{searched_word}"'
                                break
                            else:
                                dros_object = next(find_key(response, 'dros'))
                                dros_object_str = str(dros_object)
                                if searched_word in dros_object_str:
                                    phrase_object = {}
                                    for dro in dros_object:
                                        if dro['drp'] == searched_word:
                                            phrase_object = dro
                                            result['exact_word'] = dro['drp']
                                            break
                                    result['gram'] = next(find_key(phrase_object, 'gram'),
                                                          'collocation')
                                    # result['meanings'] = next(find_key(phrase_object, 'dt'))[0][1]
                                    result['meanings'] = get_meanings(next(find_key(phrase_object, 'dt'))[0][1], '')
                                    result['usage'] = next(find_key(phrase_object, 'pva'),
                                                           result['meanings'])
                                    break
                                else:
                                    continue
                        else:
                            result['message'] = f'Do you mean one of these phrases:'
                            result['phrases'] = response
                    else:
                        result['message'] = f'No results for "{searched_word}"'
                else:
                    result['message'] = 'Server not working'
            else:
                result['message'] = 'Invalid typing'
        return result
