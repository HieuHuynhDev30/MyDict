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
                api_url = f'''https://www.dictionaryapi.com/api/v3/references/learners/json/{searched_word}?key={api_key}'''
                response = requests.get(api_url)
                if response.status_code == 200:
                    response = response.json()
                    if response:
                        response_str = str(response)
                        if 'meta' in response_str:
                            stems = next(find_key(response, 'stems'))
                            result['phrases'] = []
                            for phrase in stems:
                                result['phrases'].append(phrase.casefold())
                            for phrase in result['phrases']:
                                if phrase == searched_word:
                                    exact_word = result['phrases'][0]
                                    result['exact_word'] = exact_word
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
                                    result['meanings'] = []
                                    meanings = next(find_key(response, 'def'))
                                    if isinstance(meanings, list):
                                        for i, meaning in enumerate(meanings):
                                            if isinstance(meaning, str):
                                                meanings[i] = meaning.capitalize()
                                            else:
                                                meanings[i] = 'undefined'
                                            result['meanings'].append(meanings[i])
                                    result['message'] = f'Showing results for "{exact_word}"'
                                else:
                                    result['message'] = f'Do you mean one of these phrases:'
                                    result['phrases'] = response
                                break
                            else:
                                result['message'] = f'No results for "{searched_word}"'
                        else:
                            result['message'] = 'Server not working'
                    else:
                        result['message'] = 'Invalid typing'
        return result

    # if " " in searched_word:
    #     word_set = searched_word.split(" ")
    #     for each in word_set:
    #         api_url_each = f'''https://www.dictionaryapi.com/api/v3/references/learners/json/{each}?key={api_key}'''
    #         response_each = requests.get(api_url_each)
    #         if response_each.status_code == 200:
    #             response_each = response_each.json()
    #             if response_each:
    #                 response_each_str = str(response_each)
    #                 if 'meta' in response_each_str:
    #                     response_each_object = response_each
    #                     stems = next(find_key(response_each_object, 'stems'))
    #                     for phrase in stems:
    #                         if phrase == searched_word:
    #                             result['exact_word'] = phrase
    #                             break
    # else:
    #     if searched_word.isalpha():
    #         api_url = f'''https://www.dictionaryapi.com/api/v3/references/learners/json/{searched_word}?key={api_key}'''
    #         response = requests.get(api_url)
    #         if response.status_code == 200:
    #             response = response.json()
    #             if response:
    #                 response_str = str(response)
    #                 if 'meta' in response_str:
    #                     response = response
    #                     stems = next(find_key(response, 'stems'))
    #                     exact_word = stems[0]
    #                     result['exact_word'] = exact_word
    #                     result['type'] = next(find_key(response, 'fl'))
    #                     result['ipa'] = f"/{next(find_key(response, 'ipa'))}/"
    #                     audio = next(find_key(response, 'audio'))
    #                     if audio:
    #                         subdirectory = audio[0]
    #                         result['has_audio'] = True
    #                     prefixes = ['bix', 'gg', *tuple(list('0123456789'))]
    #                     for prefix in prefixes:
    #                         if audio.startswith(prefix, 0):
    #                             subdirectory = prefix
    #                     formats = ['mp3', 'wav', 'ogg']
    #                     audio_srcs = []
    #                     for ext in formats:
    #                         audio_srcs.append({
    #                             'src': f'''https://media.merriam-webster.com/audio/prons/en/us/mp3/{subdirectory}/{audio}.{ext}''',
    #                             'type': ext})
    #                     result['audio_srcs'] = audio_srcs
    #                     result['phrases'] = []
    #                     for phrase in stems[1:]:
    #                         result['phrases'].append(phrase.casefold())
    #                     result['meanings'] = []
    #                     meanings = next(find_key(response, 'def'))
    #                     if isinstance(meanings, list):
    #                         for i, meaning in enumerate(meanings):
    #                             if isinstance(meaning, str):
    #                                 meanings[i] = meaning.capitalize()
    #                             else:
    #                                 meanings[i] = 'undefined'
    #                             result['meanings'].append(meanings[i])
    #                     result['message'] = f'Showing results for "{exact_word}"'
    #                 else:
    #                     result['message'] = f'Do you mean one of these phrases:'
    #                     result['phrases'] = response
    #             else:
    #                 result['message'] = f'No results for "{searched_word}"'
    #         else:
    #             result['message'] = 'Server not working'
    #     else:
    #         result['message'] = 'Invalid typing'
    # return result
