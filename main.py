import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import time
import requests
from config import *
from consts import *


def keyboard_maker(keyboard_labels):
    my_keyboard = []
    for row in keyboard_labels:
        keyboard_row = []
        for label in row:
            keyboard_row.append(KeyboardButton(text=label))

        my_keyboard.append(keyboard_row)

    return ReplyKeyboardMarkup(keyboard=my_keyboard, resize_keyboard=True)


def get_poll_results(profile_id):
    try:
        courses = eval(requests.get(poll_result_api_url + str(profile_id)).text)

    except SyntaxError:
        yield 'Not found!!🤷‍♂️'
        return

    for course in courses:
        data = course['course'] + '\n\n'
        top_grade = 0
        for score in course['scores']:
            data += score['question'] + ' : ' + str(round(score['answer'])) + ' (%d رای)' % score['count'] + '\n'
            top_grade += score['answer'] * score['coeff']

        top_grade /= 10

        data += '\nنمره کل: ' + str(round(top_grade)) + ' (%d رای)' % course['participant_count']
        yield data


def get_graders_name():
    graders = eval(requests.get(graders_api_url).text)
    names = []
    for grader in graders:
        full_name = grader['first_name'] + ' ' + grader['last_name']
        names.append([full_name])

    names.sort()
    return names


def get_grader_id(full_name):
    graders = eval(requests.get(graders_api_url).text)
    for grader in graders:
        if full_name == grader['first_name'] + ' ' + grader['last_name']:
            return grader['id']

    raise KeyError


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if chat_type == u'private':
        if content_type == 'text':
            if msg['text'] == '/start':
                bot.sendMessage(admin_id, '[%s](tg://user?id=%d)' % (msg['from']['first_name'], chat_id), 'Markdown')
                bot.sendMessage(chat_id, start_msg, reply_markup=keyboard_maker(get_graders_name()))

            else:
                try:
                    for grades in get_poll_results(get_grader_id(msg['text'])):
                        bot.sendMessage(chat_id, grades)

                except KeyError:
                    bot.sendMessage(chat_id, bad_input_msg, reply_markup=keyboard_maker(get_graders_name()))


bot = telepot.Bot(TOKEN)

MessageLoop(bot, handle).run_as_thread()

while True:
    time.sleep(30)
