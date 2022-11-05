import pyrogram
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaDocument
from pyrogram import enums
import os
import back
import threading
import asyncio
import time


# bot
from info import TOKEN, HASH, ID
from info import CID, MID, OWNER
bot_token = TOKEN
api_hash = HASH
api_id = ID
app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)


# bot code
HELP_TEXT = "__🆕 /start - to check if i am alive\n\
🆘 /help - this message\n\
🖌️ /create - email::username::password - to create new account and login\n\
👨‍💻 /login username::password - to login to your account (to check statistics)\n\
📊 /stats - to check statistics of your account\n\
✔️ /check - to check of login info\n\
ℹ️ /info url - to check stats of the file\n\
📠 /logout - to logout__"


# start
@app.on_message(filters.command(["start"]))
def send_welcome(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):    
    app.send_message(message.chat.id, f"__👋 Hi {message.from_user.mention}, i am a interface bot working for softdrives.in, just send me any file to upload it for you.\nuse /help to know how to use me.__", reply_to_message_id=message.id,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Help", callback_data="help")], [InlineKeyboardButton("🌐 WebSite", url="https://softdrives.in")]]))
    if not manage.db.is_user_exist(message.from_user.id):
        message.reply("__🔍 Looks like you don't have account logged in, use **/login** or **/create**__", reply_to_message_id=message.id)
    

# help
@app.on_message(filters.command(["help"]))
def send_help(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    app.send_message(message.chat.id, HELP_TEXT, reply_to_message_id=message.id)


# brodcast
@app.on_message(filters.command(["broadcast"]))
def broadcast(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    if message.from_user.id == OWNER:
        mid = message.reply_to_message_id
        if mid == None:
            return
            
        msg = app.send_message(OWNER, "__in Progress...__" , reply_to_message_id=message.id)
        for ele in manage.db.get_all_telegramid():
            try:
                app.copy_message(ele[0], OWNER, mid)
                time.sleep(5)
            except Exception as e:
                print("error", ele[0], e)
                time.sleep(2)
        app.edit_message_text(OWNER, msg.id, "__Done__")


# create
@app.on_message(filters.command(["create"]))
def create(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    if manage.db.is_user_exist(message.from_user.id):
        app.send_message(message.chat.id, "__⚠️ You are already logged in with account. use /logout before creating new account.__", reply_to_message_id=message.id)
        return

    try:
        data = message.text.split("/create ")[1]
        email = data.split("::")[0]
        username = data.split("::")[1]
        password = data.split("::")[2]
    except:
        app.send_message(message.chat.id, "__⚠️ Invalid Format\n**/create email::username::password**__", reply_to_message_id=message.id)
        return
    
    msg = app.send_message(message.chat.id, "__🔄 Processing, Don't send it Again__", reply_to_message_id=message.id)
    flag = manage.create_new_user(message.from_user.id,username,email,password)

    if flag.code == 1:
       app.edit_message_text(chat_id=message.chat.id, message_id=msg.id, text=f"__☑️ Created and Logged in with account__\n**{username}:{password}**")
       app.edit_message_media(CID,MID, InputMediaDocument("users.db", caption=time.asctime(time.localtime(time.time()))))
    else:
        app.edit_message_text(chat_id=message.chat.id, message_id=msg.id, text=f"__❌ {flag.msg}__")


# login
@app.on_message(filters.command(["login"]))
def login(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    if manage.db.is_user_exist(message.from_user.id):
        app.send_message(message.chat.id, "__⚠️ You are already logged in with account. use /logout before logging in with another account.__", reply_to_message_id=message.id)
        return

    try:
        data = message.text.split("/login ")[1]
        username = data.split("::")[0]
        password = data.split("::")[1]
    except:
        app.send_message(message.chat.id, "__⚠️ Invalid Format\n**/login username::password**__", reply_to_message_id=message.id)
        return
    
    msg = app.send_message(message.chat.id, "__🔄 Processing__", reply_to_message_id=message.id)
    flag = manage.login_old_user(message.from_user.id,username,password).code

    if flag == 1:
        app.edit_message_text(chat_id=message.chat.id, message_id=msg.id, text=f"__☑️ Logged in with account__\n**{username}:{password}**")
        app.edit_message_media(CID,MID, InputMediaDocument("users.db", caption=time.asctime(time.localtime(time.time()))))
    else:
        app.edit_message_text(chat_id=message.chat.id, message_id=msg.id, text=f"__❌ Invalid Credentials__")
    

# check
@app.on_message(filters.command(["check"]))
def check(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    if manage.db.is_user_exist(message.from_user.id):
        app.send_message(message.chat.id, "__✅ You are logged in with account__", reply_to_message_id=message.id)
    else:
        app.send_message(message.chat.id, "__❎ You have not logged in with account__", reply_to_message_id=message.id)


# logout
@app.on_message(filters.command(["logout"]))
def logout(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    if manage.db.is_user_exist(message.from_user.id):
        manage.delete_user_from_database(message.from_user.id)
        app.send_message(message.chat.id, "__⭕ You are logged out from account__", reply_to_message_id=message.id)
        app.edit_message_media(CID,MID, InputMediaDocument("users.db", caption=time.asctime(time.localtime(time.time()))))
    else:
        app.send_message(message.chat.id, "__❎ You have not logged in with account__", reply_to_message_id=message.id)


# stats
@app.on_message(filters.command(["stats"]))
def stats(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    if manage.db.is_user_exist(message.from_user.id):
        msg = app.send_message(message.chat.id, "__🔄 Processing, Don't send it Again__", reply_to_message_id=message.id)
        info = manage.user_info(message.from_user.id).res
        info = f'**Total Files**: __{info["Total Files"]}__\n**Size Used**: __{info["Size Used"]}__\n**Size Available**: __{info["Size Available"]}__\n\
**Percentage Of Used**: __{info["Percentage Of Used"]}__\n**Balance**: __{info["Balance"]}__\n**Paid**: __{info["Paid"]}__\n\
**Pending Payment**: __{info["Pending Payment"]}__\n**Traffic Available Today**: __{info["Traffic Available Today"]}__'
        app.edit_message_text(chat_id=message.chat.id, message_id=msg.id, text=info)
    else:
        app.send_message(message.chat.id, "__❎ You have not logged in with account__", reply_to_message_id=message.id)


# info
@app.on_message(filters.command(["info"]))
def info(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    if manage.db.is_user_exist(message.from_user.id):
        try:
            data = message.text.split("/info ")[1]
            if "https://softdrives.in/" in data:
                fileid = data.split("https://softdrives.in/")[1]
            else:
                fileid = data
        except:
            app.send_message(message.chat.id, "__⚠️ Invalid Format\n**/info url** or **/info file-unique-id**__", reply_to_message_id=message.id)
            return
        
        msg = app.send_message(message.chat.id, "__🔄 Processing, Don't send it Again__", reply_to_message_id=message.id)
        info,images = manage.file_info(message.from_user.id,fileid).res
        dates = ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 12 Months"]
       
        i = 0 
        app.delete_messages(message.chat.id, msg.id)
        for ele in images:
            msg = app.send_photo(message.chat.id, ele, caption=f'**{dates[i]}**', reply_to_message_id=message.id)
            app.send_message(message.chat.id, info[i], reply_to_message_id=msg.id)
            os.remove(ele)
            i += 1
    else:
        app.send_message(message.chat.id, "__❎ You have not logged in with account__", reply_to_message_id=message.id)


# upload thread
async def uplodthread(message):
    if manage.db.is_user_exist(message.from_user.id):
        msg = await app.send_message(message.chat.id, "__⬇️ Downloading__", reply_to_message_id=message.id)
        file = await app.download_media(message)
        await app.edit_message_text(chat_id=message.chat.id, message_id=msg.id, text="__⬆️ Uploading__")
        info = manage.upload_file(message.from_user.id,file)
        os.remove(file)
        if info.code == 0:
            await app.edit_message_text(chat_id=message.chat.id, message_id=msg.id, text="__⭕ Failed__")
        else:
            info = info.res
            fileid = info[0].split("/")[-1]
            info = f'**URL** : __{info[0]}__\n\n**File Unique ID** : __{info[0].split("/")[-1]}__\n\n**File ID** : __{info[1]}__\n\n**Shareable Link** : __{info[2]}__'
            await app.edit_message_text(chat_id=message.chat.id, message_id=msg.id, text=info,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📊 Stats", callback_data=fileid)]]))
    else:
        await app.send_message(message.chat.id, "__❎ You have not logged in with account__", reply_to_message_id=message.id)


# upload
# @app.on_message(filters.voice)
# @app.on_message(filters.video_note)
# @app.on_message(filters.sticker)
# @app.on_message(filters.animation)
# @app.on_message(filters.audio)
@app.on_message(filters.photo)
@app.on_message(filters.document)
@app.on_message(filters.video)
async def uplod(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    try:
        filesize = message.document.file_size
    except:
        try:
            filesize = message.video.file_size
        except:
            filesize = message.photo.file_size

    if filesize > 133500000:
        await app.send_message(message.chat.id, "__📁 File is Too Big, Limit is 133.50 MB__", reply_to_message_id=message.id)
    else:
        await uplodthread(message)
   
    
# call back
@app.on_callback_query()
def answer(client: pyrogram.client.Client, call: pyrogram.types.CallbackQuery):
    

    if call.data == "help":
        app.answer_callback_query(call.id)
        app.edit_message_text(call.message.chat.id, call.message.id, HELP_TEXT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]]))
        return

    if call.data == "back":
        app.answer_callback_query(call.id)
        app.edit_message_text(call.message.chat.id, call.message.id, f"__I am a interface bot working for softdrives.in, just send me any file to upload it for you.\nuse /help to know how to use me.__",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Help", callback_data="help")], [InlineKeyboardButton("🌐 WebSite", url="https://softdrives.in")]]))
        return

    else:
        message = call.message
        if manage.db.is_user_exist(call.from_user.id):
            app.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
            fileid = call.data
            info,images = manage.file_info(call.from_user.id,fileid).res

            for ele in images:
                os.remove(ele)

            datas = info[1].split("\n")
            alertmsg = f'{datas[0].replace("*","").replace("_","")}\n\n{datas[1]}\n{datas[2]}\n{datas[3]}'
            app.answer_callback_query(call.id, text=alertmsg, show_alert=True)
            app.send_chat_action(message.chat.id, enums.ChatAction.CANCEL)
        else:
            app.answer_callback_query(call.id, text="❎ You have not logged in with account", show_alert=True)


# bot start and db restore
def main():
    time.sleep(5)
    msg = app.get_messages(CID,MID)
    if not os.path.exists("users.db"):
        app.download_media(msg,"./users.db")
    
    global manage
    manage = back.Manager()
    app.send_message(OWNER,"__Bot Started__")

strt = threading.Thread(target=lambda: main(), daemon=True)
strt.start()


# infinty polling
app.run()