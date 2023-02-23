import time
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import time
import re
from datetime import datetime
from aiogram.utils.callback_data import CallbackData
from aiogram import Bot, Dispatcher, executor, types #, dispatcher
from aiogram.types import *
from aiogram.utils.deep_linking import get_start_link, decode_payload
from aiogram.utils.exceptions import *
import mysql.connector

ROOT_IDS = [# you should put the Roots Ids Here
  "2020886220",# kamal
]

# Bot Tken Should Be Here
Token = '6240755718:AAHFBfLlqWXKjnmKjH1egI7thS32PgFvKbI'

bot = Bot(token=Token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage);

CASHOUT_REQUESTS = {}

class AdMessage1(StatesGroup):
  ad_msg = State()

class AdMessage2(StatesGroup):
  ad_msg = State()

class Broadcast(StatesGroup):
  conf = State()
  msg_type = State()
  photo = State()
  caption = State()
  text = State()

class Cashout(StatesGroup):
  cashout = State()

class CashoutData(StatesGroup):
  data = State()

class ConfirmData(StatesGroup):
  confirm = State()

class CashoutWorldWide(StatesGroup):
  action = State()

# DB connection
try:
  conn = mysql.connector.connect(host="localhost", user="root", passwd="", database="kamal-bot")
  cursor = conn.cursor(dictionary=True)
  print("Connected To DB Successfuly")
except Exception as e:
  print("Error :", e)

cursor.execute("SELECT * FROM options WHERE id = 1")
options = cursor.fetchall()[0]

ADMINS_IDS = []
cursor.execute("SELECT telegram_id FROM users WHERE is_admin = 1")
for admin in cursor.fetchall():
  ADMINS_IDS.append(admin["telegram_id"])

CHANNELS_IDS = []
cursor.execute("SELECT tel_id FROM channels")
for chnl in cursor.fetchall():
  CHANNELS_IDS.append(chnl["tel_id"])

BOT_LINK    = "https://t.me/salahnewbotforme_bot"
BOT_CHANNEL = "https://t.me/+h6I-N_eYKMRhNTRk"
support_service = "@kamal_private"
BOT_EXPLAIN = "https://t.me/explainwork"

inviting_gift   = 5
min_cashout     = options['min_cashout']# min_cashout   = 1000
max_cashout     = options['max_cashout']# max_cashout   = 20000

calc_profits_cb = CallbackData("calc", "action", "currency")
cashout_bank_cb = CallbackData("bank", "cashout")
cashout_data_cb = CallbackData("cashout_data", "bank_data")

welcome_msg_1 = "🔝القائمة الرئيسية"
welcome_msg_2 = "مرحباً انت الان في قائمة البوت الرئيسية"
auth_err_msg  = "❌ لم يتم العثور على المستخدم الذي قام بإنشاء هذا الرابط أو تم حذفه."
already_registered = "ℹ️ أنت مستخدم هذا البوت بالفعل."
sub_msg       = f"""
  يجب عليك الاشتراك في قناة البوت الرسمية لكي تتمكن من استخدام البوت.


  قناة البوت الرسمية 
  🔗 {BOT_CHANNEL}

  بعد الإشتراك اضغط /start
  """

""" Buttons Names And Values """
profits       = "أرباحي 💵"
daily_gift    = "المكافأة اليومية ⏰"
invite_link   = "رابط الدعوة 🔗"
more_options  = "📥المزيد 📥"
this_bot      = "ما هذا البوت ⁉️"
cash_out      = "سحب الارباح 💰"
contact_us    = "أتصل بنا 📧"
confirm       = "✅ تأكيد"
decline       = "🚫 إلغاء"
western_union = "ويسترن يونيون 🌏"
moneygram     = "موني جرام 🌏"
payer         = "باير 🅿️"
bitcoin       = "بيتكوين 💰"
paypal        = "PayPal 💸"
usdt          = "USDT 💵"

""" Messages Values """
home_page     = "🔝 القائمة الرئيسية"
back_page     = "🔙 رجوع"
cashout_bank  = "🏦 سحب بنكي 🏦"
cashout_elec  = "🌐 سحب إلكتروني 🌐"
world_countries  = "🌏 جميع دول العالم 🌏"

""" world countries """
countries = {
  "bh": "البحرين 🇧🇭",
  "ae": "الإمارات 🇦🇪",
  "jo": "الأردن 🇯🇴",
  "sd": "السودان 🇸🇩",
  "sa": "السعودية 🇸🇦",
  "dz": "الجزائر 🇩🇿",
  "kw": "الكويت 🇰🇼",
  "iq": "العراق 🇮🇶",
  "so": "الصومال 🇸🇴",
  "tn": "تونس 🇹🇳",
  "ye": "اليمن 🇾🇪",
  "ma": "المغرب 🇲🇦",
  "om": "عمان 🇴🇲",
  "sy": "سوريا 🇸🇾",
  "dj": "جيبوتي 🇩🇯",
  "lb": "لبنان 🇱🇧",
  "qa": "قطر 🇶🇦",
  "ps": "فلسطين 🇵🇸",
  "mr": "موريتانيا 🇲🇷",
  "eg": "مصر 🇪🇬",
  "ly": "ليبيا 🇱🇾"
}

cashout_ways = {
  "bh": ["الشامل 🇧🇭", "الرافدين 🇧🇭"],
  "ae": ["إتش إس بي سي 🇦🇪", "الشارقة 🇦🇪"],
  "jo": ["البنك الاهلي الأردني 🇯🇴", "بنك القاهرة عمان 🇯🇴", "بنك صفوة الإسلامي 🇯🇴"],
  "sd": ["بنك الخرطوم 🇸🇩", "بنك ام درمان الوطني 🇸🇩", "البنك السوداني الاهلي 🇸🇩", "بنك فيصل الاسلامي 🇸🇩", "bankak 🇸🇩"],
  "sa": ["بنك الراجحي 🇸🇦", "بنك الاهلي السعودي 🇸🇦", "فوري 🇸🇦"],
  "dz": ["البنك الوطني الجزائري 🇩🇿", "البنك الوطني الجزائري 🇩🇿", "بنك البركة الجزائري 🇩🇿"],
  "kw": ["البنك الاهلي المتحد 🇰🇼", "برقان 🇰🇼"],
  "iq": ["اسياسيل 🇮🇶", "زين كاش 🇮🇶", "إيلاف 🇮🇶"],
  "so": ["بنك دار السلام 🇸🇴", "Amana Bank 🇸🇴"],
  "tn": ["يوباف 🇹🇳", "الامان 🇹🇳"],
  "ye": ["بنك الكريمي 🇾🇪", "الحزمي 🇾🇪", "النجم 🇾🇪", "القطيبي للحوالات 🇾🇪", "بنك التضامن 🇾🇪", "بنك الامل 🇾🇪"],
  "ma": ["وفا كاش 🇲🇦", "Cashplus 🇲🇦", "CIH Bank 🇲🇦"],
  "om": ["البنك الوطني العماني 🇴🇲", "بنك مسقط 🇴🇲"],
  "sy": ["إم تي إن كاش 🇸🇾", "الهرم 🇸🇾", "مصرف سوريا المركزي 🇸🇾", "سيرتيل كاش 🇸🇾"],
  "dj": ["بنك سبأ الافريقي 🇩🇯", "بنك السلام 🇩🇯"],
  "lb": ["بنك البركة اللبناني 🇱🇧", "بنك لبنان والمهجر 🇱🇧", "مصرف لبنان المركزي 🇱🇧", "OMT 🇱🇧"],
  "qa": ["المشرق 🇶🇦", "الريان 🇶🇦"],
  "ps": ["بنك الاستثمار الفلسطيني 🇵🇸", "بنك فلسطين 🇵🇸"],
  "mr": ["البنك الإسلامي الموريتاني 🇲🇷", "البنك الشعبي الموريتاني 🇲🇷"],
  "eg": ["فودافون كاش 🇪🇬", "تيليكوم 🇪🇬", "اتصالات كاش 🇪🇬", "اورنج 🇪🇬", "بنك الإسكندرية 🇪🇬", "بنك الاهلي المصري 🇪🇬", "بنك فيصل الاسلامي 🇪🇬"],
  "ly": ["دينار باي 🇱🇾", "مدار 🇱🇾"]
}

all_cashout_options = []

for i in cashout_ways.values():
  for y in i:
    all_cashout_options.append(y)

error_msg = """
  ❌ أمر غير معروف!

  لقد قمت بإرسال رسالة مباشرة إلى دردشة بوت أو
  تم تعديل بنية القائمة من قبل المسؤول.

  ℹ️ لا ترسل رسائل مباشرة إلى البوت أو
  أعد تحميل القائمة بالضغط /start
  """

btn1 = KeyboardButton(profits)
btn2 = KeyboardButton(daily_gift)
btn3 = KeyboardButton(more_options)
btn4 = KeyboardButton(invite_link)
btn5 = KeyboardButton(this_bot)
btn6 = KeyboardButton(cash_out)
btn7 = KeyboardButton(contact_us)
key_main = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(btn1).add(btn2).row(btn3, btn4).row(btn5, btn6).add(btn7)

async def home_panel(chat_id):

  btn1 = InlineKeyboardButton("قناة اثباتات السحب", url=BOT_CHANNEL)
  btn2 = InlineKeyboardButton("🔰 شرح طريقة استخدام البوت", url=BOT_EXPLAIN)
  key_1 = InlineKeyboardMarkup().add(btn1).add(btn2)

  await bot.send_message(chat_id, welcome_msg_1, reply_markup=key_main)
  await bot.send_message(chat_id, welcome_msg_2, reply_markup=key_1)

async def is_sub(user_id):

  for channel in CHANNELS_IDS:
    response = await bot.get_chat_member(channel, user_id)
    if not (response.status in ["member", "creator"]) and not (user_id in ADMINS_IDS):
      return False
  return True

async def get_ad_msg(text_col='ad_msg', image_col='ad_msg_img'):
  cursor.execute(f"SELECT {text_col}, {image_col} FROM options")
  result = cursor.fetchone()
  return result

async def set_ad_msg(text, image_id=None, text_col='ad_msg', image_col='ad_msg_img'):

  img = f"'{image_id}'" if bool(image_id) and len(str(image_id)) > 0 else "NULL"

  cursor.execute(f"UPDATE options SET {text_col} = '{text}', {image_col} = {img}")
  conn.commit()
  pass

async def insert_user(user_id, full_name=None):
  cursor.execute(f"INSERT INTO users (telegram_id, username, last_gift) VALUES ('{user_id}', '{full_name}', DATE_SUB(now(), INTERVAL 10 DAY))")
  res = conn.commit()
  print(f"insert into db Try")
  pass

async def get_user(user_id):
  cursor.execute(f"SELECT * FROM users WHERE telegram_id = '{user_id}'")
  result = cursor.fetchone()
  return result

async def get_all_users():
  cursor.execute(f"SELECT telegram_id FROM users WHERE is_admin = 0")
  result = cursor.fetchall()
  return result

async def check_user(sender, upline='2020886220'):
  user = await get_user(sender.id)

  if (user != None and user["telegram_id"] != None):
    print("---------------------")
    print(f"Get From DB => ( {user['username']} : {user['telegram_id']} )")
    print("---------------------")
    return user
  else:
    
    await insert_user(sender.id, f"{sender.first_name} {sender.last_name if bool(sender.last_name) else ''}")
    user = await get_user(sender.id)
    print("---------------------")
    print(f"insert user => ( {user['username']} )")
    print("---------------------")

    if (user != None and user["telegram_id"] != None):
      upline_user = await get_user(upline)
      if (bool(upline_user["id"]) and int(upline_user["id"]) > 0):
        cursor.execute(f"UPDATE users SET invitees = invitees + 1, profits = profits + {inviting_gift} WHERE telegram_id = '{upline}'")
        res = conn.commit()
        await bot.send_message(upline, f"انضم {sender.first_name} عن طريق رابطك. \n تمت اضافة {inviting_gift}$ الى مجموع ارباحك.")
        print("---------------------")
        print(f"Add One To invitees To User ( {upline} )")
        print("---------------------")
        return user
      else:
        await bot.send_message(sender.id, auth_err_msg)
        print("---------------------")
        print(f"Error On Getting Upline From link Paylod Of new user => ({sender.id})")
        print("---------------------")
    else:
      print("---------------------")
      print("Error On Getting user After Insertation")
      print("---------------------")

async def update_options():
  global options
  cursor.execute("select * from options where id = 1")
  options = cursor.fetchall()[0]

async def update_admins():
  global ADMINS_IDS
  cursor.execute("select telegram_id from users where is_admin = 1")
  ADMINS_IDS = []
  for admin in cursor.fetchall():
    ADMINS_IDS.append(admin["telegram_id"])
  print(f"===================")
  print(f"ADMINS_IDS is Updated => ( {ADMINS_IDS} )")
  print(f"===================")

async def update_channels():
  global CHANNELS_IDS
  CHANNELS_IDS = get_channels()
  
  print(f"===================")
  print(f"CHANNELS_IDS is Updated => ( {CHANNELS_IDS} )")
  print(f"===================")
  pass

def get_channels():
  
  cursor.execute("SELECT tel_id FROM channels")
  channels = []
  
  for chnl in cursor.fetchall():
    print(chnl)
    channels.append(chnl["tel_id"])
  return channels


@dp.message_handler(commands=['start'])
async def welcome_handler(message: types.Message):

  user_id = message.from_user.id
  chat_id = message.chat.id

  upline = message.get_args()# you can use => get_start_link(message.from_id) <= to get a link with paylod
  user_db = await check_user(message.from_user, upline) # paylod => upline

  if await is_sub(user_id):
    
    # await bot.send_message(chat_id, "nice")
    await home_panel(chat_id)
  
  else:
    await bot.send_message(chat_id, sub_msg)

@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):

  if await is_sub(message.from_user.id):
      
    await message.answer(f"""
      • عند دعوتك لشخص واحد عبر رابطك الخاص سوف تحصل على مكافأة موضحة بالدولار.
      والدفع تلقائي وفوري.

      تستطيع الحصول على رابط الخاص عن طريق /invite_link

      📌قناة البوت: 
      🔗 {BOT_CHANNEL}
      """)
  else:
    await bot.send_message(message.chat.id, sub_msg)

@dp.message_handler(commands=['invite_link'])
async def invite_handler(message: types.Message):
  if await is_sub(message.from_user.id):
    link = await get_start_link(message.from_id)
    await message.answer(link)
  else:
    await bot.send_message(chat_id, sub_msg)

@dp.message_handler(commands=['admin'])
async def admin_handler(message: types.Message):

  user_id = message.from_id

  if str(user_id) in ROOT_IDS:
    await message.answer(f"""
      اهلا بك في لوحة الادمن
      =======--------=======
      /daily_gift <قيمة المكافئة> لتحديد قيمة المكافئة اليومية
      /gift_time <الساعات> لتحديد المدة الزمنية بين الجوائز (بالساعات)
      /gift_ad لتحديد الرسالة الاساسية المرسلة مع المكافئات
      /gift_ad_2 لتحديد الرسالة الفرعية المرسلة مع المكافئات
      /admin لعرض لوحة الادمن
      /add_admin <admin id> لإضافة ادمن فرعي
      /delete_admin <admin id> لحذف ادمن فرعي
      /list_admins لعرض الادمن المتواجدين
      /add_channel <channel id> لاضافة قناة
      /delete_channel <channel id> لحذف قناة
      /list_channels لعرض القنوات المتواجدة
      /send_broadcast لإذاعة رسالة لكافة الاعضاء
      """)
  
  elif await is_sub(user_id) and str(user_id) in ADMINS_IDS:
    await message.answer(f"""
      اهلا بك في لوحة الادمن
      =======--------=======
      /daily_gift لتحديد قيمة المكافئة اليومية
      /gift_time لتحديد المدة الزمنية بين الجوائز (بالساعات)
      """)

  else:
    await message.answer(error_msg)

@dp.message_handler(commands=['daily_gift'])
async def daily_gift_handler(message: types.Message):

  user_id = message.from_id

  if await is_sub(user_id) and str(user_id) in ADMINS_IDS:

    value = message.get_full_command()[1]
    if (bool(re.search(r'\d', value)) and int(value) > 0):

      cursor.execute(f"UPDATE options SET gift_amount = {value}")
      conn.commit()
      await message.answer(f"✅ المكافئة اليومية هي {value}")
    else:
      await message.answer(f"❌ لا يمكن للمكافئة اليومية ان تكون {value}. \n الرجاء تحديد قيمة صالحة")

  else:
    await message.answer(error_msg)

@dp.message_handler(commands=['gift_time'])
async def gift_time_handler(message: types.Message):

  user_id = message.from_id

  if await is_sub(user_id) and str(user_id) in ADMINS_IDS:
    
    value = message.get_full_command()[1]
    if (bool(re.search(r'\d', value)) and int(value) > 0):

      cursor.execute(f"UPDATE options SET gift_time = {value}")
      conn.commit()
      await message.answer(f"✅ الفترة بين المكافئات هي: {value} ساعات")
      await update_options()

    else:
      await message.answer(f"❌ لا يمكن للفترة بين المكافئات ان تكون :\n ( {value} ) \n الرجاء تحديد قيمة صالحة")

  else:
    await message.answer(error_msg)

@dp.message_handler(commands=['gift_ad'])
async def gift_ad_handler(message: types.Message):

  user_id = message.from_id

  if str(user_id) in ROOT_IDS:
    
    await AdMessage1.ad_msg.set()
    await message.reply("أرسل الرسالة المرفقة مع المكافئات\n تستطيع الالغاء باستخدام /cancel")

  else:
    await message.answer(error_msg)

@dp.message_handler(commands=['gift_ad_2'])
async def gift_ad_2_handler(message: types.Message):

  user_id = message.from_id

  if str(user_id) in ROOT_IDS:
    
    await AdMessage2.ad_msg.set()
    await message.reply("أرسل الرسالة المرفقة مع المكافئات\n تستطيع الالغاء باستخدام /cancel")

  else:
    await message.answer(error_msg)

@dp.message_handler(commands=['add_admin'])
async def add_admin_handler(message: types.Message):

  user_id = message.from_id

  if str(user_id) in ROOT_IDS:
    
    value = message.get_full_command()[1]
    if (bool(re.search(r'\d', value)) and len(str(value)) == 10):

      cursor.execute(f"UPDATE users SET is_admin = 1 WHERE telegram_id = {value}")
      conn.commit()
      await message.answer(f"✅ تمت اضافة الادمن ( {value} )")
      await update_admins()
      await list_admins_handler(message)

    else:
      await message.answer(f"❌ لا يمكن ل(id) الادمن ان يكون:\n ( {value} ) \n الرجاء تحديد قيمة صالحة")

  else:
    await message.answer(error_msg)

@dp.message_handler(commands=['delete_admin'])
async def delete_admin_handler(message: types.Message):

  user_id = message.from_id

  if str(user_id) in ROOT_IDS:
    
    value = message.get_full_command()[1]
    if (bool(re.search(r'\d', value)) and len(str(value)) == 10):

      cursor.execute(f"UPDATE users SET is_admin = 0 WHERE telegram_id = {value}")
      conn.commit()
      await message.answer(f"✅ تم حذف الادمن ( {value} ) بنجاح.")
      await update_admins()

    else:
      await message.answer(f"❌ لا يمكن ل(id) الادمن ان يكون:\n ( {value} ) \n الرجاء تحديد قيمة صالحة")

  else:
    await message.answer(error_msg)

@dp.message_handler(commands=['add_channel'])
async def add_channel_handler(message: types.Message):

  user_id = message.from_id

  if str(user_id) in ROOT_IDS:
    
    value = message.get_full_command()[1]
    if (bool(re.search(r'\-\d{13}', value)) and len(str(value)) == 14):

      cursor.execute(f"INSERT INTO channels (tel_id) VALUES ({value})")
      conn.commit()
      await message.answer(f"✅ تمت اضافة القناة ( {value} ) بنجاح")
      await update_channels()
      print(CHANNELS_IDS)
      msg = f"القنوات الحالية:\n"
      for value in CHANNELS_IDS:
        msg += f"\n- {value}"
      await bot.send_message(message.chat.id, msg)

    else:
      await message.answer(f"❌ لا يمكن ل(id) القناة ان يكون:\n ( {value} ) \n الرجاء تحديد قيمة صالحة")

  else:
    await message.answer(error_msg)

@dp.message_handler(commands=['list_admins'])
async def list_admins_handler(message: types.Message):

  user_id = message.from_id

  if str(user_id) in ROOT_IDS:
    
    update_admins()
    
    print(f"listing all admins => ( {ADMINS_IDS})")
    
    msg = f"الادمن الحاليين:\n"
    for value in ADMINS_IDS:
      msg += f"\n*  {value}"
    await bot.send_message(message.chat.id, msg)

  else:
    await message.answer(error_msg)

@dp.message_handler(commands=['list_channels'])
async def list_channels_handler(message: types.Message):

  user_id = message.from_id

  if str(user_id) in ROOT_IDS:
    
    update_channels()
    
    print(f"listing all channels => ( {CHANNELS_IDS})")
    
    msg = f"القنوات الحالية:\n"
    for value in CHANNELS_IDS:
      msg += f"\n*  {value}"
    await bot.send_message(message.chat.id, msg)

  else:
    await message.answer(error_msg)

@dp.message_handler(commands=['delete_channel'])
async def delete_channel_handler(message: types.Message):

  user_id = message.from_id

  if str(user_id) in ROOT_IDS:
    
    value = message.get_full_command()[1]
    if (bool(re.search(r'-\d{13}', value)) and len(str(value)) == 14):

      cursor.execute(f"DELETE FROM channels WHERE tel_id = {value}")
      conn.commit()
      await message.answer(f"✅ تم حذف القناة ( {value} ) بنجاح.")
      
      await update_channels()
      print(f"CHANNELS_IDS Is Updated => ( {CHANNELS_IDS} )")
      msg = f"القنوات الحالية:\n"
      for value in CHANNELS_IDS:
        msg += f"\n- {value}"
      await bot.send_message(message.chat.id, msg)

    else:
      await message.answer(f"❌ لا يمكن ل(id) القناة ان يكون:\n ( {value} ) \n الرجاء تحديد قيمة صالحة")

  else:
    await message.answer(error_msg)

@dp.message_handler(commands=['send_broadcast'])
async def send_broadcast_handler(message: types.Message):

  user_id = message.from_user.id
  
  if str(user_id) in ROOT_IDS:

    await Broadcast.msg_type.set()
    await bot.send_message(user_id, "ارسل الرسالة التي سيتم اذاعتها :")

  else:
    await message.answer(error_msg)

@dp.message_handler(state='*', commands=['cancel'])
async def cancel_handler(message: types.Message, state: FSMContext):
  """Allow user to cancel action via /cancel command"""

  user_id = message.from_id

  cashout_memory = f"{str(user_id)[:3]}{str(user_id)[-3:]}"

  if cashout_memory in CASHOUT_REQUESTS:
    del CASHOUT_REQUESTS[cashout_memory]

  current_state = await state.get_state()
  if not current_state is None:
    await state.finish()

  await bot.send_message(message.chat.id, 'تم الالغاء !')
  time.sleep(0.5)
  await home_panel(message.chat.id)

@dp.message_handler()
async def kb_answer(message: types.Message):

  user_id = message.from_user.id
  user_db = await get_user(user_id)
  print("---------------------")
  print(f"user_db for message handler => ( {user_db} )")
  print("---------------------")
  
  if (bool(user_db) and user_db["id"] != None):
    if message.text == profits:

      btn_egp = InlineKeyboardButton(text="🇪🇬حساب أرباحك بالجنيه المصري EGP", callback_data=calc_profits_cb.new(action="calc_profits", currency='egp'))
      btn_sl  = InlineKeyboardButton(text="🇸🇾 حساب أرباحك بالليرة السورية", callback_data=calc_profits_cb.new(action="calc_profits", currency='sl'))
      btn_ry  = InlineKeyboardButton(text="🇾🇪حساب أرباحك بالريال اليمني  YER", callback_data=calc_profits_cb.new(action="calc_profits", currency='ry'))
      key_calculate_profits = InlineKeyboardMarkup().add(btn_egp).add(btn_sl).add(btn_ry)
      link = await get_start_link(user_id)
      await message.answer(f"""
        ✅ مرحبا بك عزيزي. {message.from_user.first_name}

        • عدد دعواتك {user_db['invitees']} شخص 
        • ارباحك  {user_db['profits']} دولار

        رابطك الخاص :
        🔗 {link}
        """, reply_markup=key_calculate_profits)
    elif message.text == daily_gift:
      
      cursor.execute(f"SELECT last_gift FROM users WHERE id = {user_db['id']}")
      res = cursor.fetchone()

      data1 = res["last_gift"]
      data2 = datetime.now()

      diff = data2 - data1

      days, seconds = diff.days, diff.seconds
      hours = days * 24 + seconds // 3600
      minutes = (seconds % 3600) // 60
      seconds = seconds % 60

      if (hours >= options["gift_time"]):

        cursor.execute(f"UPDATE users SET profits = profits + {options['gift_amount']}, last_gift = NOW() WHERE id = {user_db['id']}")
        conn.commit()

        link = await get_start_link(user_id)
        await message.answer(f"""
          🎉 لقد حصلت على مكافأة  {options["gift_amount"]} دولار 

          ✅ رصيدك الان اصبح {user_db["profits"] + options["gift_amount"]} دولار 

          لربح المزيد من المال شارك هذا الرابط لأصدقائك 👇 
          {link}

          💎 كل شخص يدخل عن طريق هذا الرابط سوف تحصل على {inviting_gift} دولار
          """)
        
        ad_msg = await get_ad_msg()
        msg, img = ad_msg.values() # str(ad_msg["ad_msg"]), str(ad_msg["ad_msg_img"])
        
        print("---------------")
        print(f"firest ad's message => {msg}")
        print(f"firest ad's Image => {img}")
        print("---------------")
        if (bool(msg) and len(msg) > 0 and bool(img) and len(img) > 0):
          await bot.send_photo(message.from_user.id, img, msg)
        elif (bool(msg) and len(msg) > 0):
          await bot.send_message(message.from_user.id, msg)

        ad_msg_2 = await get_ad_msg("ad_msg_2", "ad_msg_2_img")
        msg_2, img_2 = ad_msg_2.values()
        print("---------------")
        print(f"seconde ad's message => {msg_2}")
        print(f"seconde ad's Image => {img_2}")
        print("---------------")

        if (bool(msg_2) and len(msg_2) > 0 and bool(img_2) and len(img_2) > 0):
          await bot.send_photo(message.from_user.id, img_2, msg_2)
        elif (bool(msg_2) and len(msg_2) > 0):
          await bot.send_message(message.from_user.id, msg_2)

      else:

        link = await get_start_link(user_id)
        await message.answer(f"""
          ❌ عذراً عزيزي المكافأة اليومية متاحة كل {options["gift_time"]} ساعات.

          المكافأة القادمة بعد {options["gift_time"] - (hours + 1)} ساعات و {60 - (minutes + 1)} دقيقة و {60 - (seconds + 1)} ثانية

          -------------------------------------------------------------------------
          لربح المزيد من المال شارك هذا الرابط لأصدقائك 👇 
          {link}

          💎 كل شخص يدخل عن طريق هذا الرابط سوف تحصل على {inviting_gift} دولار
        """)
    elif message.text == invite_link:
      link = await get_start_link(user_id)
      await message.answer(f"""
        ✅ سوف تكسب  {inviting_gift} دولار  مكافأة  من كل شخص تقوم بدعوته عبر رابطك الخاص.


        🤴 رابطك الخاص : 
        🔗 {link}

        الحد الادنى للسحب {min_cashout} دولار فقط
        """)
    elif message.text == more_options:
      await message.answer(f"""
        ☑️ قريبا: 
        🔜• الربح من مشاهدة الاعلانات 
        🔜• الربح عبر أداء المهام 
        🔜• الربح من قناتك 

        ✉️ فريق الدعم الفني: {support_service}
        """)
    elif message.text == this_bot:
      await message.answer(f"""
        • عند دعوتك لشخص واحد عبر رابطك الخاص سوف تحصل على مكافأة موضحة بالدولار.
        والدفع تلقائي وفوري.
        
        تستطيع الحصول على رابطك الخاص عن طريق /invite_link

        📌قناة البوت: 
        🔗 {BOT_CHANNEL}
        """)
    elif message.text == cash_out:

      msg = """
        🔰 الرجا اختيار البلد الذي تقيم فيه ثم تحديد طريقة السحب من القائمة في الاسفل.

        ✅ طرق سحب متوفرة لجميع الدول العربية 
        ✅ سحب بنكي لاي دولة في العالم.
        ✅ سحب للمحافظ والبنوك الكترونية.
        """ 
      btn_bank = KeyboardButton(cashout_bank)
      btn_cryp = KeyboardButton(cashout_elec)
      btn_world = KeyboardButton(world_countries)
      btn_back = KeyboardButton(back_page)
      btn_home = KeyboardButton(home_page)

      btns = {}
      i = 0
      for country in countries.values():
        btns[i] = KeyboardButton(country) 
        i = i + 1

      key_countries = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(btn_bank).add(btn_cryp, btn_world).add(*btns.values()).row(btn_back, btn_home)
      await message.answer(msg, reply_markup=key_countries)
    elif message.text == home_page or message.text == back_page:
      await home_panel(message.chat.id)
    elif message.text == contact_us:
      await message.answer(f"✉️ فريق الدعم الفني: {support_service}")
    elif message.text == cashout_bank:

      key_cashout = InlineKeyboardMarkup().add(InlineKeyboardButton(cashout_bank, callback_data=cashout_bank_cb.new(cashout="true")))

      await bot.send_message(message.chat.id, f"""
        🏦 سحب بنكي 🏦

        ✅ يمكنك الان سحب اموالك عبر اي حساب بنكي لاي دولة في العالم . 

        ✅ الحد الادنى للسحب: {min_cashout}$
        ✅ الحد الاقصى للسحب: {max_cashout}$
        """, reply_markup=key_cashout)
    elif message.text == world_countries:

      cashout_ww_btn_1 = KeyboardButton(western_union)
      cashout_ww_btn_2 = KeyboardButton(moneygram)
      cashout_ww_btn_3 = KeyboardButton(decline)
      key_cashout_ww = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(cashout_ww_btn_1).add(cashout_ww_btn_2).add(cashout_ww_btn_3)

      await message.answer(f"""✅ الان يرجى اختيار طريقة السحب من القائمة في الأسفل:👇""", reply_markup=key_cashout_ww)

    elif message.text == cashout_elec:

      cashout_elec_btn_1 = KeyboardButton(payer)
      cashout_elec_btn_2 = KeyboardButton(bitcoin)
      cashout_elec_btn_3 = KeyboardButton(paypal)
      cashout_elec_btn_4 = KeyboardButton(usdt)
      cashout_elec_btn_5 = KeyboardButton(decline)
      key_cashout_elec = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(cashout_elec_btn_1).add(cashout_elec_btn_2).add(cashout_elec_btn_3).add(cashout_elec_btn_4).add(cashout_elec_btn_5)

      await message.answer(f"""✅ الان يرجى اختيار طريقة السحب من القائمة في الأسفل:👇""", reply_markup=key_cashout_elec)

    elif message.text in countries.values():

      ww_btn_1 = KeyboardButton(western_union)
      ww_btn_2 = KeyboardButton(moneygram)
      cancel_btn = KeyboardButton(decline)

      btns = {}
      i = 0
      for code, country in countries.items():
        if (country == message.text):
          print(f"code => {code} || country => {country}")
          for way in cashout_ways[code]:
            print(way)
            btns[i] = KeyboardButton(way)
            i = i + 1

      key_cashout_ww = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1).add(*btns.values(), ww_btn_1, ww_btn_2, cancel_btn)

      await message.answer(f"""✅ الان يرجى اختيار طريقة السحب من القائمة في الأسفل:👇""", reply_markup=key_cashout_ww)

    elif message.text in [western_union, moneygram, payer, bitcoin, paypal, usdt, *all_cashout_options]:

      cancel_btn = KeyboardButton(decline)
      key_cancel = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(cancel_btn)

      cashout_memory = f"{str(message.from_user.id)[:3]}{str(message.from_user.id)[-3:]}"
      CASHOUT_REQUESTS[cashout_memory] = {"amount": None, "way": message.text}

      await Cashout.cashout.set()
      
      await message.answer(f"""
        🔰 الان يرجى ادخال مبلغ السحب بالارقام فقط: 
        • الحد الادنى للسحب:  {min_cashout}$
        • الحد الاقصى للسحب: {max_cashout}$
        • ارباحك المتاحة للسحب: {user_db['profits']}$
        :👇""", reply_markup=key_cancel)
      
    elif message.text == contact_us:
      await message.answer(f"✉️ فريق الدعم الفني: {support_service}")

    else:
      await message.answer(error_msg)
      print("---------------------")
      print("unknown message has been sent")
      print("---------------------")
  else:
    await message.answer(error_msg)
    print("---------------------")
    print("user_db is not found for message handler")
    print("---------------------")

@dp.callback_query_handler(calc_profits_cb.filter(action="calc_profits")) # to filter you can use => calc_profits_cb.filter(currency="egp")
async def choice_registr_method(call: CallbackQuery, callback_data):

  user_db = await get_user(call.from_user.id)
  currency = callback_data["currency"]
  print("---------------------")
  print(f"Calculate Profits Price For ( {call.from_user.first_name} )")
  print("---------------------")

  if (currency == 'egp'):

    msg = f"""ارباحك {user_db['profits']} دولار وتساوي بالجنيه المصري 🇪🇬 : {round(user_db['profits'] * 30.48, 2)} EGP
      قد يختلف سعر الصرف هذا عند السحب اختلاف طفيف وذالك اعتماداً على سعر صرف الجنيه المصري"""
    await bot.answer_callback_query(call.id, msg, show_alert=True)

  elif (currency == 'sl'):

    msg = f""" ارباحك {user_db['profits']} دولار وتساوي بالليرة  السورية 🇸🇾 : {round(user_db['profits'] * 7175, 2)} ليرة
      قد يختلف سعر الصرف هذا عند السحب اختلاف طفيف وذالك اعتماداً على سعر صرف اللحظة """
    await bot.answer_callback_query(call.id, msg, show_alert=True)

  elif (currency == 'ry'):

    msg = f"""أرباحك  {user_db['profits']} دولار وتساوي 
      • بحسب سعر صرف الريال (ص) تساوي {round(user_db['profits'] * 560, 2)} ريال 
      • بحسب سعر صرف الريال (ع) تساوي {round(user_db['profits'] * 1140, 2)} ريال"""
    await bot.answer_callback_query(call.id, msg, show_alert=True)
  
  print("---------------------")
  print(currency)
  print("---------------------")

@dp.callback_query_handler(cashout_bank_cb.filter(cashout="true"))
async def cashout_bank_method(call: CallbackQuery, callback_data):

  user_db = await get_user(call.from_user.id)

  cancel_btn = KeyboardButton(decline)
  key_cancel = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(cancel_btn)
  
  cashout_memory = f"{str(call.from_user.id)[:3]}{str(call.from_user.id)[-3:]}"
  CASHOUT_REQUESTS[cashout_memory] = {"amount": None, "way": cashout_bank}
  
  await Cashout.cashout.set()
  
  await bot.send_message(call.message.chat.id, f"""
    🔰 الان يرجى ادخال مبلغ السحب بالارقام فقط: 
    • الحد الادنى للسحب:  {min_cashout}$
    • الحد الاقصى للسحب: {max_cashout}$
    • ارباحك المتاحة للسحب: {user_db['profits']}$
    :👇""", reply_markup=key_cancel)

  print("---------------------")
  print(f"Receiving Cashout Price ...")
  print("---------------------")

@dp.message_handler(state=AdMessage1.ad_msg, content_types=ContentType.PHOTO)
async def gift_ad_img_handler(message, state):
  """Process ( set gift ad )"""
  
  await state.finish()
  await bot.send_message(message.chat.id, "سيتم ارفاق الرسالة مع المكافئات اليومية بالشكل التالي:")

  photo_text = message.caption if bool(message.caption) and len(message.caption) > 0 else None
  photo_id = message.photo[-1].file_id

  await set_ad_msg(photo_text, photo_id)
  db_msg = await get_ad_msg()
  await bot.send_photo(message.chat.id, db_msg['ad_msg_img'], db_msg['ad_msg']) # also you can use answer_photo() method 

  print("\n=================\n")
  print(f"Message image id => {photo_id}")
  print(f"Message text (caption) =>\n{photo_text}")

@dp.message_handler(state=AdMessage1.ad_msg, content_types=ContentType.TEXT)
async def gift_ad_text_handler(message, state):
  """Process ( set gift ad )"""
  
  await state.finish()
  await bot.send_message(message.chat.id, "سيتم ارفاق الرسالة مع المكافئات اليومية بالشكل التالي:")

  photo_text = message.text

  await set_ad_msg(photo_text, None)
  db_msg = await get_ad_msg()
  await bot.send_message(message.chat.id, db_msg['ad_msg']) # also you can use answer_photo() method 

  print("\n=================\n")
  print(f"Message image id => None")
  print(f"Message text (text only) =>\n{photo_text}")

@dp.message_handler(state=AdMessage2.ad_msg, content_types=ContentType.PHOTO)
async def gift_ad_2_img_handler(message, state):
  """Process ( set gift ad )"""
  
  await state.finish()
  await bot.send_message(message.chat.id, "سيتم ارفاق الرسالة مع المكافئات اليومية بالشكل التالي:")

  photo_text = message.caption if message.caption and len(message.caption) > 0 else None
  photo_id = message.photo[-1].file_id

  await set_ad_msg(photo_text, photo_id, "ad_msg_2", "ad_msg_2_img")
  db_msg = await get_ad_msg("ad_msg_2", "ad_msg_2_img")
  await bot.send_photo(message.chat.id, db_msg['ad_msg_2_img'], db_msg['ad_msg_2']) # also you can use answer_photo() method 

  print("\n=================\n")
  print(f"Message image id => {photo_id}")
  print(f"Message text (caption) =>\n{photo_text}")

@dp.message_handler(state=AdMessage2.ad_msg, content_types=ContentType.TEXT)
async def gift_ad_2_text_handler(message, state):
  """Process ( set gift ad )"""
  
  await state.finish()
  await bot.send_message(message.chat.id, "سيتم ارفاق الرسالة مع المكافئات اليومية بالشكل التالي:")

  await set_ad_msg(message.text, None, "ad_msg_2", "ad_msg_2_img")
  db_msg = await get_ad_msg("ad_msg_2", "ad_msg_2_img")
  await bot.send_message(message.chat.id, db_msg['ad_msg_2'])# also you can use message.reply("text")
  
  print("\n=================\n")
  print(f"Message text (caption) => {message.text}")

@dp.message_handler(state=Broadcast.msg_type, content_types=ContentType.PHOTO)
async def broadcast_photo_handler(message: types.Message, state:FSMContext):
  
  btn1 = KeyboardButton(confirm)
  btn2 = KeyboardButton(decline)
  key_confirm = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(btn1, btn2)

  await Broadcast.conf.set()

  async with state.proxy() as data:
    data['msg_type'] = 'photo'
    data['photo'] = message.photo[-1].file_id
    data['caption'] = message.caption

  await bot.send_message(message.chat.id, "سيتم ارسال الاذاعة بالشكل التالي :", reply_markup=key_confirm)
  print("Confirming Broadcaste Message (photo)")
  await bot.send_photo(message.chat.id, message.photo[-1].file_id, message.caption)

@dp.message_handler(state=Broadcast.msg_type, content_types=ContentType.TEXT)
async def broadcast_text_handler(message: types.Message, state:FSMContext):
  
  btn1 = KeyboardButton(confirm)
  btn2 = KeyboardButton(decline)
  key_confirm = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(btn1, btn2)

  await Broadcast.conf.set()
  async with state.proxy() as data:
    data['msg_type'] = 'text'
    data['text'] = message.text
  await bot.send_message(message.chat.id, "سيتم ارسال الاذاعة بالشكل التالي :", reply_markup=key_confirm)
  print("Confirming Broadcaste Message (text only)")
  await bot.send_message(message.chat.id, message.text)

@dp.message_handler(state=Broadcast.conf)
async def confirm_broadcast_handler(message: types.Message, state:FSMContext):

  print(f"Confirming Broadcast => ( {message.text} )")
  
  async with state.proxy() as data:
    print(f"Data is => ( {data} )")

    if (message.text == confirm):

      all_users = await get_all_users()
      
      
      if (data['msg_type'] == "photo"):
        for user in all_users:
          try:
            await bot.send_photo(user['telegram_id'], data['photo'], data['caption'])
          except BotBlocked as e:
            print(f"Error with user ( {user} ) => {e}")
      elif (data['msg_type'] == "text"):
        for user in all_users:
          try:
            await bot.send_message(user['telegram_id'], data['text'])
          except BotBlocked as e:
            print(f"Error with user ( {user} ) => {e}")
      

    else:
      await cancel_handler(message, state)
  await state.finish()
@dp.message_handler(state=Cashout.cashout, content_types=ContentType.TEXT)
async def cashout_handler(message, state):

  print("\n=================\n")
  print(f"Received Cashout Price Is => {message.text}")
  
  await state.finish()

  if (message.text == decline):
    await cancel_handler(message, state)
  else:

    check_val = int(re.search(r'\d+', message.text).group())
    cashout_amount = check_val if bool(check_val) and int(check_val) else 0
    if cashout_amount > 0:
      if cashout_amount < max_cashout:
        if cashout_amount > min_cashout:
          
          cashout_memory = f"{str(message.from_user.id)[:3]}{str(message.from_user.id)[-3:]}"
          CASHOUT_REQUESTS[cashout_memory]["amount"] = message.text
          await CashoutData.data.set()

          msg = "الان يرجى ادخال معلومات السحب"
          if (CASHOUT_REQUESTS[cashout_memory]["way"] == cashout_bank):
            msg += " مثلا البلد ورقم الحساب البنكي "
          elif (CASHOUT_REQUESTS[cashout_memory]["way"] in
          [world_countries, moneygram, western_union, payer, bitcoin, paypal, usdt]):
            msg += " الخاصة بك في رسالة واحدة:"

          await bot.send_message(message.chat.id, msg)

        else:
          await Cashout.cashout.set()
          await bot.send_message(message.chat.id, f"""
            ❌ القيمة التي تم إدخالها أقل من الحد الأدنى.
            ℹ️ أدنى قيمة هي {min_cashout}.
            🔄 حاول مرة أخرى…""")
          
      else:
        await Cashout.cashout.set()
        await bot.send_message(message.chat.id, f"""
          ❌ القيمة المدخلة أكبر من الحد الأقصى.
          ℹ️ القيمة القصوى هي {max_cashout}.
          🔄 حاول مرة أخرى…""")
      
    else:
      await Cashout.cashout.set()
      await message.reply(message.chat.id, """
        ❌ فشل تغيير القيمة ...
        القيمة التي أرسلتها ليست رقمًا.
        ℹ️ أدخل قيمة رقمية…
        🔄 حاول مرة أخرى…""")

@dp.message_handler(state=CashoutData.data, content_types=ContentType.TEXT)
async def cashout_data_handler(message, state):

  cashout_memory = f"{str(message.from_user.id)[:3]}{str(message.from_user.id)[-3:]}"

  print("\n=================\n")
  print(f"Asking For Approving To Cashout From {message.from_user.id}")
  print(f"Cashout Price => {CASHOUT_REQUESTS[cashout_memory]['amount']} And Message => {message.text}")

  msg = f"""
    ❗️هل انت متاكد من عملية السحب من حسابك؟

    المبلغ: {CASHOUT_REQUESTS[cashout_memory]['amount']} دولار 
    طريقة السحب: {CASHOUT_REQUESTS[cashout_memory]['way']}
    معلومات السحب:\n{message.text}
    """
    
  btn1 = KeyboardButton(confirm)
  btn2 = KeyboardButton(decline)
  key_confirm = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(btn1, btn2)

  await ConfirmData.confirm.set()
  await bot.send_message(message.chat.id, msg, reply_markup=key_confirm)

@dp.message_handler(state=ConfirmData.confirm, content_types=ContentType.TEXT)
async def confirm_data_handler(message, state):

  user_id = message.from_user.id

  print("\n=================")
  print(f"Confirming From {user_id}")

  user_db = await get_user(user_id)

  cashout_memory = f"{str(user_id)[:3]}{str(user_id)[-3:]}"
  CASHOUT_REQUESTS[cashout_memory]

  if (message.text == confirm):
    if (int(user_db["profits"]) >= int(CASHOUT_REQUESTS[cashout_memory]["amount"])):
      await state.finish()
      await message.reply("💳 يتم السحب الان", reply_markup=key_main)
    else:
      await bot.send_message(message.chat.id, f"""
        خطأ الحد الادنى للسحب {min_cashout}
        رصيدك  {user_db["profits"]}$
        لا يمكنك سحب المبلغ المطلوب !!""")
      await cancel_handler(message, state)

  elif (message.text == decline):
    await cancel_handler(message, state)
  else:
    await ConfirmData.confirm.set()
    await bot.send_message(message.chat.id, """
      نوع رسالة غير مدعومة.
      ❌ للإلغاء /cancel
      🔄 للتكرار حاول مرة أخرى…
      """)



print("Bot started")
print("===================")

executor.start_polling(dp)
