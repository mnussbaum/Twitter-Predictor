import string
import re

class WordCounter(object):
    
    def __init__(self, text):
        self._word_data = {}
        index = 0
        formated_text = self._format_text(text)
        split_text = formated_text.split()
        for word in split_text :
            word_minus_punc = self._format_text(word)
            if word_minus_punc not in self._word_data:
                  word_data = {'count':0, 'word':word_minus_punc, 'neighbors':[]}
                  self._word_data[word_minus_punc] = word_data
            else:
                word_data = self._word_data[word_minus_punc]
            if index > 0:
                previous_word = split_text[index-1]
                #if the previous word ended a sentence then don't include it as a neighbor
                if previous_word[-1] in '.!?':
                    formated_previous = ""
                else:
                    formated_previous = self._format_text(previous_word)
            else:
                formated_previous = ''
            #if the current word ends a sentence then don't give it a forward neighbor
            if index < len(split_text)-1 and word[-1] not in ".!?":
                next_word = split_text[index+1]
                formated_next = self._format_text(next_word)
            else:
                formated_next = ''
            word_data['neighbors'].append({'previous_neighbor':formated_previous, 'next_neighbor':formated_next})
            word_data['count'] += 1
            index += 1    
    
    def _format_text(self, text):
        regex = re.compile('[%s]' % re.escape(';:,'))
        unpunctuated_text = regex.sub('', text)
        return unpunctuated_text.lower()
    
    def get_word_data(self):
        return self._word_data