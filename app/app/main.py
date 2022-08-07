import aiogram
import datetime
import pickle
import re
import nltk
#from config import TOKEN
TOKEN = '5502436426:AAEP1C5ZG5-CXfgdE6Kt0Xt2XkeWK1LYnA8'
from aiogram.dispatcher.filters import Text
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,

    Doc
)

segmenter = Segmenter()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
morph_vocab = MorphVocab()

bot = aiogram.Bot(token = TOKEN)
dp = aiogram.Dispatcher(bot, storage=MemoryStorage())
import sqlite3

text_res = ''
print('Понеслась')

command = aiogram.types.CallbackQuery('function')
def get_free_executor(group):
    users =  reviewdb = sqlite3.connect('app.db')
    cursorstart = reviewdb.cursor()
    min_queue = 65535
    free_executor = None
    for user in users:
        if user.queue<min_queue and user.group==group:
            min_queue=user.queue
            free_executor = user.id
    return free_executor
@dp.message_handler(commands=['start'])
async def first_start(message: aiogram.types.Message):
    reviewdb = sqlite3.connect('app.db')
    cursorstart = reviewdb.cursor()
    reviewdb.close()
    sql = '''SELECT * FROM review WHERE id = (?)'''
    adr = (str(message.from_user.id),)
    cursorstart.execute(sql, adr)
    myresult = cursorstart.fetchall()
    if myresult is None or myresult == [] or myresult == ():
        cursorstart = reviewdb.cursor()
        sql = '''SELECT executor, text FROM review WHERE id = (?)'''
        adr = (str(message.text),)
        cursorstart.execute(sql, adr)


        sql = '''INSERT INTO review (executor) VALUES (?)'''

        cursorstart.execute(sql, adr)
        reviewdb.commit()
    reviewdb.close()
    await message.answer('Здравствуйте!\nЧто бы написать отзыв отправьте команду /test')

@dp.message_handler(commands=['test'])
async def text(message: aiogram.types.Message):
    await message.answer('Отправьте свой отзыв одним сообщением')

@dp.message_handler()
async def text(message: aiogram.types.Message):
    reviewdb = sqlite3.connect('app.db')
    cursorstart = reviewdb.cursor()
    sql = '''SELECT executor, text FROM review WHERE id = (?)'''
    adr = (str(message.text),)
    cursorstart.execute(sql, adr)
    myresult = cursorstart.fetchall()
    if myresult is None or myresult == [] or myresult == ():
        cursorstart = reviewdb.cursor()
        sql = '''SELECT id,queue,_group FROM user'''
        cursorstart.execute(sql)
        exec_id = cursorstart.fetchall()

        global text_res
        text_res = message.text

        GROUP = int(predict_category(prepare_data(text_res))[0])
        print(GROUP)


        min_len = 65535
        exec_user_id = 0
        for user in exec_id:
            if user[2]==GROUP:
                if user[1]<=min_len:
                    min_len = user[1]
                    exec_user_id = user[0]
        print(exec_user_id)

        #sql = "INSERT INTO review(executor, text, is_done, user_id) VALUES ((?), (?), 0, (?))"
        #val = (exec_user_id,str(message.text),message.from_user.id)
        #cursorstart.execute(sql, val)

        sql = "INSERT INTO review(executor, text, is_done, user_id, _group) VALUES ((?), (?), 0, (?), (?))"
        val = (exec_user_id, str(message.text), message.from_user.id, GROUP)
        cursorstart.execute(sql, val)
        reviewdb.commit()
        sql = "UPDATE user SET queue = (?) WHERE id = (?)"
        val = (min_len + 1,exec_user_id)
        cursorstart.execute(sql, val)
        reviewdb.commit()




        await message.answer('Спасибо, ваш ответ записан.\nСледующий отзыв просто отправляйте в сообщении.')


    reviewdb.close()
    return text_res

def bot_answer(message: aiogram.types.Message):
    reviewdb = sqlite3.connect('app.db')
    cursor_ex = reviewdb.cursor()
    sql = '''SELECT is_done FROM review WHERE text = (?)'''
    adr = message.text
    cursor_ex.execute(sql, adr)
    my_res = str(cursor_ex.fetchall())
    if my_res is not None or my_res != [] or my_res != ():
        sql = '''SELECT answer FROM review WHERE text = (?)'''
        adr = (message.text,)
        cursor_ex.execute(sql, adr)
        my_res = str(cursor_ex.fetchall())
        bot.send_message(message.from_user.id,'Здравствуйте!\nОтвет тех. поддержки на ваш отзыв:\n' + my_res)
    reviewdb.close()

def predict_category(feedback):
    loaded_model = pickle.load(open('finalized_model.sav', 'rb'))
    result = loaded_model.predict(feedback)
    return result

def prepare_data(feedback):
    feedback = re.sub(
    r'[^A-Za-z0-9А-Яа-яЁё]+',
    ' ',
    feedback
    )
    feedback = feedback.replace(r'[^A-Za-z0-9А-Яа-яЁё]+', ' ')
    feedback = feedback.lower()
    feedback = word_tokenize(feedback)
    stop_words = stopwords.words('russian')
    stop_words.append('т')
    stop_words.append('к')
    stop_words.append('типа')
    stop_words.append('мол')
    feedback = ' '.join([word for word in feedback if word not in stop_words])

    doc = Doc(feedback)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)
    for token in doc.tokens:
        token.lemmatize(morph_vocab)

    feedback_cleared = [word.lemma for word in doc.tokens]
    feedback_cleared = ' '.join(feedback_cleared)

    loaded_tfidf = joblib.load('tfidf_model.pkl')
    test_new = loaded_tfidf.transform([feedback]).toarray()
    print(predict_category(test_new))
    return test_new

if __name__ == '__main__':
    aiogram.executor.start_polling(dp)