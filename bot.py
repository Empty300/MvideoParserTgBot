from settings import cookies, bot_key
import telebot
import json
import categories
from city_id import ids, c_ids
from parser import get_id, get_product_info,get_product_price,get_together

bot = telebot.TeleBot(bot_key)
bot_idmsgs_list = list()
bot_vid_idmsgs_list = list()
markup_b = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
change_city = telebot.types.KeyboardButton("Изменить город")
back = telebot.types.KeyboardButton("Начать сначала")
clear_cards = telebot.types.KeyboardButton("Очистить выдачу")
markup_b.add(change_city, back, clear_cards)

def del_bot_msgs(bot_idmsgs_list, chat_id):
    for i in bot_idmsgs_list:
        try:
            bot.delete_message(chat_id, i)
        except:
            print("")
    bot_idmsgs_list.clear()

print("Бот запущен")
@bot.message_handler(commands=["start"])
def start(message):
    try:
        bot.delete_message(message.chat.id, message.id)
    except:
        print("")
    first_msg = bot.send_message(message.chat.id, f"Привет! Я бот который позволит парсить Мвидео по скидкам!\n"
                                                  f"Текущий город: <b>{ids[cookies['MVID_REGION_SHOP']]}</b>. "
                                                  f"Ты можешь изменить его в меню!\n",reply_markup=markup_b,parse_mode="HTML")
    del_bot_msgs(bot_idmsgs_list, message.chat.id)
    bot_idmsgs_list.append(first_msg.id)
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    nouts = telebot.types.InlineKeyboardButton(text="Ноутбуки", callback_data="Ноутбуки")
    pla = telebot.types.InlineKeyboardButton(text="Планшеты", callback_data="Планшеты")
    tel = telebot.types.InlineKeyboardButton(text="Смартфоны", callback_data="Смартфоны")
    mon = telebot.types.InlineKeyboardButton(text="Мониторы", callback_data="Мониторы")
    nau = telebot.types.InlineKeyboardButton(text="Наушники", callback_data="Наушники")
    vid = telebot.types.InlineKeyboardButton(text="Видеокарты", callback_data="Видеокарты")

    markup.add(nouts, pla, tel, mon, nau, vid)
    second_msg = bot.send_message(message.chat.id,
                                  "Какой раздел будем парсить? Если твоего раздела нет в кнопках, ты можешь просто его написать",
                                  reply_markup=markup)
    bot_idmsgs_list.append(second_msg.id)


@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback_data(callback):
    del_bot_msgs(bot_idmsgs_list, callback.message.chat.id)
    if callback.data.capitalize() in categories.all_categories.keys():
        categoryId = categories.all_categories[callback.data.capitalize()]
        third_msg = bot.send_message(callback.message.chat.id,
                                     f"Окей, начинаю парсить. Это может занять некоторое время",
                                     reply_markup=markup_b)
        bot_idmsgs_list.append(third_msg.id)
        id_list = get_id(categoryId)
        if len(id_list) > 0:
            result_info = get_product_info(id_list)
            resul_price = get_product_price(id_list)
            get_together(result_info, resul_price)
            markup1 = telebot.types.InlineKeyboardMarkup(row_width=1)
            all_nouts = telebot.types.InlineKeyboardButton(text=f"Все {callback.data.lower()} со скидкой",
                                                           callback_data="Все")
            advantageous = telebot.types.InlineKeyboardButton(text="Самый выгодный", callback_data="Выгодный")
            markup1.add(all_nouts, advantageous)
            four_msg = bot.send_message(callback.message.chat.id,
                                        f"Всего нашлось <b>{len(id_list)}</b> товаров со скидкой!"
                                        f" Как мне тебе их вывести?", reply_markup=markup1, parse_mode="HTML")
            bot_idmsgs_list.append(four_msg.id)
        else:
            fitf_msg = bot.send_message(callback.message.chat.id,
                                        f"Нашел эту категорию, но в ней сейчас нет скидок. Попробуй позже! ",
                                        reply_markup=markup_b)
            bot_idmsgs_list.append(fitf_msg.id)
    elif callback.data == f"Все":
        with open("result.json", "r", encoding="utf8") as file:
            info = json.load(file)
            for i in info:
                vid_msg = bot.send_photo(callback.message.chat.id, info[i]['img_link'],
                                         caption=f"<a href='{info[i]['link']}'>{info[i]['name']}</a>\n"
                                                 f"Цена со скидкой: {info[i]['salePrice']}р \n"
                                                 f"Без: {info[i]['price']}р\n"
                                                 f"Итоговая скидка: {info[i]['discount']}р, или {info[i]['discount_in_pr']}%",
                                         parse_mode="html", reply_markup=markup_b)
                bot_vid_idmsgs_list.append(vid_msg.id)
    elif callback.data == "Выгодный":
        with open("result.json", "r", encoding="utf8") as file:
            info = json.load(file)
            maxim = 0
            for i in info:
                if maxim < info[i]['discount_in_pr']:
                    result = i
                    maxim = info[i]['discount_in_pr']
            vid_msg = bot.send_photo(callback.message.chat.id, info[result]['img_link'],
                                     caption=f"<a href='{info[result]['link']}'>{info[result]['name']}</a>\n"
                                             f"Цена со скидкой: {info[result]['salePrice']} \n"
                                             f"Без: {info[result]['price']}\n"
                                             f"Итоговая скидка: {info[result]['discount']}, или {info[result]['discount_in_pr']}%",
                                     parse_mode="html", reply_markup=markup_b)
            bot_vid_idmsgs_list.append(vid_msg.id)


@bot.message_handler(content_types=["text"])
def with_one(message):
    try:
        bot.delete_message(message.chat.id, message.id)
    except:
        print("")
    del_bot_msgs(bot_idmsgs_list, message.chat.id)
    if message.text.capitalize() in categories.all_categories.keys():
        categoryId = categories.all_categories[message.text.capitalize()]
        six_msg = bot.send_message(message.chat.id, f"Окей, начинаю парсить. Это может занять некоторое время",
                                   reply_markup=markup_b)
        bot_idmsgs_list.append(six_msg.id)
        id_list = get_id(categoryId)
        if len(id_list) > 0:
            result_info = get_product_info(id_list)
            resul_price = get_product_price(id_list)
            get_together(result_info, resul_price)
            markup1 = telebot.types.InlineKeyboardMarkup(row_width=1)
            all_nouts = telebot.types.InlineKeyboardButton(text=f"Все {message.text.lower()} со скидкой",
                                                           callback_data="Все")
            advantageous = telebot.types.InlineKeyboardButton(text="Самый выгодный", callback_data="Выгодный")
            markup1.add(all_nouts, advantageous)
            sev_msg = bot.send_message(message.chat.id, f"Всего нашлось {len(id_list)} товаров со скидкой!"
                                                        f" Как мне тебе их вывести?", reply_markup=markup1)
            bot_idmsgs_list.append(sev_msg.id)
        else:
            ei_msg = bot.send_message(message.chat.id,
                                      f"Нашел эту категорию, но в ней сейчас нет скидок. Попробуй позже! ")
            bot_idmsgs_list.append(ei_msg.id)




    elif message.text == "Изменить город":
        markup3 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        mos = telebot.types.KeyboardButton("Москва")
        eka = telebot.types.KeyboardButton("Екатеринбург")
        kra = telebot.types.KeyboardButton("Краснодар")
        nov = telebot.types.KeyboardButton("Новосибирск")
        irk = telebot.types.KeyboardButton("Иркутск")
        ros = telebot.types.KeyboardButton("Ростов-на-Дону")
        markup3.add(mos, eka, kra, nov, irk, ros, back)
        tw_msg = bot.send_message(message.chat.id, f"Выбери город", reply_markup=markup3)
        bot_idmsgs_list.append(tw_msg.id)

    elif message.text in c_ids:
        cookies['MVID_REGION_SHOP'] = c_ids[message.text]
        start(message)
    elif message.text == "Начать сначала":
        start(message)
    elif message.text == "Очистить выдачу":
        if len(bot_vid_idmsgs_list) > 0:
            for i in bot_vid_idmsgs_list:
                try:
                    bot.delete_message(message.chat.id, i)
                except:
                    print("")
            fr_msg = bot.send_message(message.chat.id, "Выдача очищена!", reply_markup=markup_b)
            bot_idmsgs_list.append(fr_msg.id)
        else:
            th_msg = bot.send_message(message.chat.id, "Выдача и так пуста")
            bot_idmsgs_list.append(th_msg.id)
        bot_vid_idmsgs_list.clear()


    else:
        z = list()
        count = 0
        for i in categories.all_categories:
            if message.text.lower() in i.lower():
                z.append(i)
                count += 1
                if count == 5:
                    break
        if len(z) > 0:
            del_bot_msgs(bot_idmsgs_list, message.chat.id)
            ni_msg = bot.send_message(message.chat.id,
                                      "Не могу найти твою категорию, но я подобрал список схожих категорий:",
                                      reply_markup=markup_b)
            ten_msg = bot.send_message(message.chat.id, ", ".join(z))
            bot_idmsgs_list.append(ni_msg.id)
            bot_idmsgs_list.append(ten_msg.id)

        else:
            del_bot_msgs(bot_idmsgs_list, message.chat.id)
            el_msg = bot.send_message(message.chat.id, "Не могу найти такую категорию.", reply_markup=markup_b)
            bot_idmsgs_list.append(el_msg.id)


bot.polling(none_stop=True)
