import telebot
from telebot import types
from telebot.types import ReplyKeyboardRemove

from numpy.random import randint
from numpy.random import permutation
from numpy import arange

from credentials import API_KEY
from greek import *

bot = telebot.TeleBot(API_KEY)

class user_info:
    def __init__(self):
        self.IS_PRACTICE = False
        self.ANSWER = -1
        self.L = -1
        self.R = -1
        self.correct = 0
        self.total = 0
    
    def stop_training(self):
        self.IS_PRACTICE = False
        self.ANSWER = -1
        self.L = -1
        self.R = -1
       
    def start_training(self, L, R):
        self.IS_PRACTICE = True
        self.ANSWER = -1
        self.L = L
        self.R = R
        if self.R - self.L + 1 <= 30:
            self.questions = permutation(arange(self.L, self.R + 1))

        self.correct = 0
        self.total = 0
    
    def ask_question(self, num):
        if self.R - self.L + 1 <= 30:
            if num == self.questions.size:
                return -1
            else:
                return self.questions[num]
        else:
            return randint(self.L, self.R + 1)
    


practice_types = ['1-9', '10-19', '<100', '<1000', '<10\'000', '≤100\'000']
left = [1, 10, 1, 1, 1, 1] 
right = [9, 19, 99, 999, 9999, 100000]
btns = []
for practice_type in practice_types:
    btns.append(types.KeyboardButton(practice_type))
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add(*btns)
users = {}

@bot.message_handler(commands=['start'])
def start(message):
    users[message.from_user.username] = user_info()
    bot.send_message(message.from_user.id, "Χαίρε. Выберите, в каком диапазоне вы хотите попрактиковаться", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def response(message):
    txt = message.text
    name = message.from_user.username
    user = users[name]

    if txt == 'stop':
        message_text = 'Тренировка закончена. Вы верно ответили на ' + f'{user.correct}' + ' вопросов из ' + f'{user.total}' + '.'
        bot.send_message(message.from_user.id, message_text)
        user.stop_training()
        bot.send_message(message.from_user.id, 'Если еще захотите потренироваться, просто снова выберите диапазон.', reply_markup=markup)

    elif not user.IS_PRACTICE:
        for i, str in enumerate(practice_types):
            if str == txt:
                L = left[i]
                R = right[i]
                break

        if L == -1 and R == -1:
            bot.send_message(message.from_user.id, 'Не удалось распознать диапазон. Попробуйте еще раз.', reply_markup=markup)
            return
        
        user.start_training(L, R)
        bot.send_message(message.from_user.id, 'Отлично! Сейчас я буду писать числа по-гречески, а Вам надо будет написать их перевод арабскими цифрами. Например, на сообщение \"πέντε καὶ εἴκοσιν\" следует ответить \"25\"' )
        bot.send_message(message.from_user.id, 'Тренировку можно прекратить в любой момент, написав мне \"stop\"')
        
        user.ANSWER = user.ask_question(user.total)
        bot.send_message(message.from_user.id, translate_to_greek(user.ANSWER), reply_markup=ReplyKeyboardRemove())
        user.total += 1

    else: # practice mode
        prefix = ''
        if txt == f'{user.ANSWER}':
            prefix = 'Верно!\n'
            user.correct += 1
        else:
            prefix = 'Неверно! Правильный ответ -- ' + f'{user.ANSWER}' + '\n'
        
        user.ANSWER = user.ask_question(user.total)
        if user.ANSWER == -1:
            bot.send_message(message.from_user.id, 'Числа из данного диапазона закончились. Вы верно ответили на ' + f'{user.correct}' + ' вопросов из ' + f'{user.total}' + '. Если захотите потренироваться еще, просто выберите диапазон.', reply_markup=markup)
            return
        bot.send_message(message.from_user.id, prefix + 'Следующий вопрос: ' + translate_to_greek(user.ANSWER))
        user.total += 1

        
        


bot.polling(none_stop=True, interval=0)