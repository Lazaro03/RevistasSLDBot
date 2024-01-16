from genericpath import exists
import os
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message

from src.cfgs.bot_conf import NAME, HASH, ID, BOT_TK, ZIPS, ALLOWED
from freeapi import Freeapi
from src.modules.aiodl import aio
from src.modules.makezip import compress

bot: Client = Client(
    name=NAME,
    api_hash=HASH,
    api_id=ID,
    bot_token=BOT_TK
)

@bot.on_message(filters.command("start", prefixes="/"))
async def start(client: Client, message: Message):
    print("Uso el bot "+client.name)
    if message.from_user.id in ALLOWED:
        await message.reply("Hola {} bienvenido al bot para subir a pediatria :v".format(message.from_user.first_name))
    else:
        await message.reply("No tiene autorizacion")


@bot.on_message(filters.regex(".*https://.*") | filters.regex(".*http://.*"))
async def download(client: Client, message: Message):
    
    if message.from_user.id in ALLOWED:
        print("Uso el bot "+client.name)
        Free_API = Freeapi()
    
        msg = await message.reply("Link directo Detectado")
        filename = ''
        size = 0
        try :
         filename = await aio(message.text, msg)
         size = Path(filename).stat().st_size
        except:

            filename = message.text.split('/')[3]
 
            size = 10000

    

        await msg.edit("Descargado ```{}```\nTamaño: ```{:.2f} MB```".format(filename, size / 1000000))
        
        try:
            if size > ZIPS * 1024 * 1024:

                comp_msg = await message.reply("El archivo pesa mas de lo esperado, se comprimira")
                file_list = compress(filename, part_size=ZIPS)
                fin_msg = await comp_msg.edit("Archivo Comprimido en partes de {} MB\n\nAhora subiendo".format(ZIPS))
                
                for files in file_list:

                    print("Subiendo "+ files)
                    link = Free_API.upload_file(files)

                    with open(filename+".txt", "a") as txt:
                        txt.write({'name':files,'url':link}+"\n")
                    os.remove(files)

                await message.reply_document(filename+".txt", caption="Archivo de [{}](https://t.me/{})".format(message.from_user.first_name, message.from_user.username))
                # os.remove(filename)
                os.remove(filename+".txt")

                await fin_msg.delete()
                await message.reply("Subido ```{}```".format(filename))

            else:
                file_link = Free_API.upload_file(filename)
                await message.reply(str(filename))
                await message.reply(file_link)


        except Exception as e:
            await message.reply(e)
            # os.remove(filename)
            pass
    else:
        await message.reply("No tiene autorizacion")

if __name__ == "__main__":
    # print("Iniciando Bot")
    # bot.start()
    # print("Bot Iniciado")
    # bot.loop.run_forever()
    print("Bot iniciado")
    bot.run()