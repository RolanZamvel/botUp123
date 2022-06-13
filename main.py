from cProfile import run
import pstats
from pyobigram.utils import sizeof_fmt,get_file_size,createID,nice_time
from pyobigram.client import ObigramClient,inlineQueryResultArticle
from MoodleClient import MoodleClient

from JDatabase import JsonDatabase
import zipfile
import os
import infos
import xdlink
import mediafire
import datetime
import time
import youtube
import NexCloudClient
from pydownloader.downloader import Downloader
from ProxyCloud import ProxyCloud
import ProxyCloud
import socket
import tlmedia
import S5Crypto
import asyncio
import aiohttp
from yarl import URL
import re
from draft_to_calendar import send_calendar

def sign_url(token: str, url: URL):
    query: dict = dict(url.query)
    query["token"] = token
    path = "webservice" + url.path
    return url.with_path(path).with_query(query)

def downloadFile(downloader,filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        thread = args[2]
        if thread.getStore('stop'):
            downloader.stop()
        downloadingInfo = infos.createDownloading(filename,totalBits,currentBits,speed,time,tid=thread.id)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

def uploadFile(filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        originalfile = args[2]
        thread = args[3]
        downloadingInfo = infos.createUploading(filename,totalBits,currentBits,speed,time,originalfile)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

def processUploadFiles(filename,filesize,files,update,bot,message,thread=None,jdb=None):
    try:
        bot.editMessageText(message,'📦𝙿𝚛𝚎𝚙𝚊𝚛𝚒𝚗𝚐 𝚏𝚘𝚛 𝚞𝚙𝚕𝚘𝚊𝚍☁️...')
        evidence = None
        fileid = None
        user_info = jdb.get_user(update.message.sender.username)
        cloudtype = user_info['cloudtype']
        proxy = ProxyCloud.parse(user_info['proxy'])
        if cloudtype == 'moodle':
            client = MoodleClient(user_info['moodle_user'],
                                  user_info['moodle_password'],
                                  user_info['moodle_host'],
                                  user_info['moodle_repo_id'],
                                  proxy=proxy)
            loged = client.login()
            itererr = 0
            if loged:
                if user_info['uploadtype'] == 'evidence':
                    evidences = client.getEvidences()
                    evidname = str(filename).split('.')[0]
                    for evid in evidences:
                        if evid['name'] == evidname:
                            evidence = evid
                            break
                    if evidence is None:
                        evidence = client.createEvidence(evidname)

                originalfile = ''
                if len(files)>1:
                    originalfile = filename
                draftlist = []
                for f in files:
                    f_size = get_file_size(f)
                    resp = None
                    iter = 0
                    tokenize = False
                    if user_info['tokenize']!=0:
                       tokenize = True
                    while resp is None:
                          if user_info['uploadtype'] == 'evidence':
                             fileid,resp = client.upload_file(f,evidence,fileid,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                          elif user_info['uploadtype'] == 'draft':
                                fileid,resp = client.upload_file_draft(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                                draftlist.append(resp)
                          elif user_info['uploadtype'] == 'perfil':
                                fileid,resp = client.upload_file_perfil(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                                draftlist.append(resp)
                          elif user_info['uploadtype'] == 'blog':
                                fileid,resp = client.upload_file_blog(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                                draftlist.append(resp)
                          elif user_info['uploadtype'] == 'calendar':
                                fileid,resp = client.upload_file_calendar(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                                draftlist.append(resp)
                          iter += 1
                          if iter>=10:
                              break
                    os.unlink(f)
                if user_info['uploadtype'] == 'evidence':
                    try:
                        client.saveEvidence(evidence)
                    except:pass
                return draftlist
            else:
                bot.editMessageText(message,'⚠️𝙲𝚕𝚘𝚞𝚍 𝚎𝚛𝚛𝚘𝚛⚠️')
        elif cloudtype == 'cloud':
            tokenize = False
            if user_info['tokenize']!=0:
               tokenize = True
            bot.editMessageText(message,'🚀𝚄𝚙𝚕𝚘𝚊𝚍𝚒𝚗𝚐 ☁️ 𝚙𝚕𝚎𝚊𝚜𝚎 𝚠𝚊𝚒𝚝...😄')
            host = user_info['moodle_host']
            user = user_info['moodle_user']
            passw = user_info['moodle_password']
            remotepath = user_info['dir']
            client = NexCloudClient.NexCloudClient(user,passw,host,proxy=proxy)
            loged = client.login()
            if loged:
               originalfile = ''
               if len(files)>1:
                    originalfile = filename
               filesdata = []
               for f in files:
                   data = client.upload_file(f,path=remotepath,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                   filesdata.append(data)
                   os.unlink(f)
               return filesdata
        return None
    except Exception as ex:
        bot.editMessageText(message,f'⚠️𝙴𝚛𝚛𝚘𝚛 {str(ex)}⚠️')


def processFile(update,bot,message,file,thread=None,jdb=None):
    file_size = get_file_size(file)
    getUser = jdb.get_user(update.message.sender.username)
    max_file_size = 1024 * 1024 * getUser['zips']
    file_upload_count = 0
    client = None
    findex = 0
    if file_size > max_file_size:
        compresingInfo = infos.createCompresing(file,file_size,max_file_size)
        bot.editMessageText(message,compresingInfo)
        zipname = str(file).split('.')[0] + createID()
        mult_file = zipfile.MultiFile(zipname,max_file_size)
        zip = zipfile.ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
        zip.write(file)
        zip.close()
        mult_file.close()
        client = processUploadFiles(file,file_size,mult_file.files,update,bot,message,jdb=jdb)
        try:
            os.unlink(file)
        except:pass
        file_upload_count = len(zipfile.files)
    else:
        client = processUploadFiles(file,file_size,[file],update,bot,message,jdb=jdb)
        file_upload_count = 1
    bot.editMessageText(message,'📦𝙿𝚛𝚎𝚙𝚊𝚛𝚒𝚗𝚐 𝚏𝚒𝚕𝚎📄...')
    evidname = ''
    files = []
    if client:
        if getUser['cloudtype'] == 'moodle':
            if getUser['uploadtype'] == 'evidence':
                try:
                    evidname = str(file).split('.')[0]
                    txtname = evidname + '.txt'
                    evidences = client.getEvidences()
                    for ev in evidences:
                        if ev['name'] == evidname:
                           files = ev['files']
                           break
                        if len(ev['files'])>0:
                           findex+=1
                    client.logout()
                except:pass
            if getUser['uploadtype'] == 'draft' or getUser['uploadtype'] == 'blog' or getUser['uploadtype'] == 'calendar' or getUser['uploadtype'] == 'perfil':
               for draft in client:
                   files.append({'name':draft['file'],'directurl':draft['url']})
        else:
            for data in client:
                files.append({'name':data['name'],'directurl':data['url']})
        bot.deleteMessage(message.chat.id,message.message_id)
        finishInfo = infos.createFinishUploading(file,file_size,max_file_size,file_upload_count,file_upload_count,findex)
        filesInfo = infos.createFileMsg(file,files)
        bot.sendMessage(message.chat.id,finishInfo+'\n'+filesInfo,parse_mode='html')
        if len(files)>0:
            txtname = str(file).split('/')[-1].split('.')[0] + '.txt'
            sendTxt(txtname,files,update,bot)
        try:

            import urllib

            user_info = jdb.get_user(update.message.sender.username)
            cloudtype = user_info['cloudtype']
            proxy = ProxyCloud.parse(user_info['proxy'])
            if cloudtype == 'moodle':
                client = MoodleClient(user_info['moodle_user'],
                                    user_info['moodle_password'],
                                    user_info['moodle_host'],
                                    user_info['moodle_repo_id'],
                                    proxy=proxy)
            host = user_info['moodle_host']
            user = user_info['moodle_user']
            passw = user_info['moodle_password']
            if getUser['uploadtype'] == 'calendar' or getUser['uploadtype'] == 'draft':
                nuevo = []
                #if len(files)>0:
                    #for f in files:
                        #url = urllib.parse.unquote(f['directurl'],encoding='utf-8', errors='replace')
                        #nuevo.append(str(url))
                fi = 0
                for f in files:
                    separator = ''
                    if fi < len(files)-1:
                        separator += '\n'
                    nuevo.append(f['directurl']+separator)
                    fi += 1
                urls = asyncio.run(send_calendar(host,user,passw,nuevo))
                loged = client.login()
                if loged:
                    token = client.userdata
                    modif = token['token']
                    client.logout()
                nuevito = []
                for url in urls:
                    url_signed = (str(sign_url(modif, URL(url))))
                    nuevito.append(url_signed)
                loco = '\n'.join(map(str, nuevito))
                fname = str(txtname)
                with open(fname, "w") as f:
                    f.write(str(loco))
                #fname = str(randint(100000000, 9999999999)) + ".txt"
                bot.sendMessage(message.chat.id,'📅𝙲𝚊𝚕𝚎𝚗𝚍𝚊𝚛 𝚍𝚒𝚛𝚎𝚌𝚝 𝚕𝚒𝚗𝚔/𝚜🔗')
                bot.sendFile(update.message.chat.id,fname)
            else:
                return
        except:
            bot.sendMessage(message.chat.id,'💢𝙲𝚘𝚞𝚕𝚍 𝚗𝚘𝚝 𝚖𝚘𝚟𝚎 𝚝𝚘 𝚌𝚊𝚕𝚎𝚗𝚍𝚊𝚛💢')
    else:
        bot.editMessageText(message,'⚠️𝙲𝚕𝚘𝚞𝚍 𝚎𝚛𝚛𝚘𝚛⚠️')

def ddl(update,bot,message,url,file_name='',thread=None,jdb=None):
    downloader = Downloader()
    file = downloader.download_url(url,progressfunc=downloadFile,args=(bot,message,thread))
    if not downloader.stoping:
        if file:
            processFile(update,bot,message,file,jdb=jdb)

def sendTxt(name,files,update,bot):
                txt = open(name,'w')
                fi = 0
                for f in files:
                    separator = ''
                    if fi < len(files)-1:
                        separator += '\n'
                    txt.write(f['directurl']+separator)
                    fi += 1
                txt.close()
                bot.sendFile(update.message.chat.id,name)
                os.unlink(name)

def onmessage(update,bot:ObigramClient):
    try:
        thread = bot.this_thread
        username = update.message.sender.username
        tl_admin_user = os.environ.get('tl_admin_user')

        #set in debug
        tl_admin_user = 'manzanatg'

        jdb = JsonDatabase('database')
        jdb.check_create()
        jdb.load()

        user_info = jdb.get_user(username)

        if username == tl_admin_user or user_info:  # validate user
            if user_info is None:
                if username == tl_admin_user:
                    jdb.create_admin(username)
                else:
                    jdb.create_user(username)
                user_info = jdb.get_user(username)
                jdb.save()
        else:
            mensaje = "𝚈𝚘𝚞 𝚍𝚘 𝚗𝚘𝚝 𝚑𝚊𝚟𝚎 𝚊𝚌𝚌𝚎𝚜𝚜.\n𝙲𝚘𝚗𝚝𝚊𝚌𝚝 𝚠𝚒𝚝𝚑 𝚖𝚢 𝚘𝚠𝚗𝚎𝚛: @manzanatg\n"
            intento_msg = "💢𝚃𝚑𝚎 𝚞𝚜𝚎𝚛 @"+username+ " 𝚑𝚊𝚜 𝚝𝚛𝚒𝚎𝚍 𝚝𝚘 𝚊𝚌𝚌𝚎𝚜𝚜 𝚠𝚒𝚝𝚑𝚘𝚞𝚝 𝚙𝚎𝚛𝚖𝚒𝚜𝚜𝚒𝚘𝚗💢"
            bot.sendMessage(update.message.chat.id,mensaje)
            bot.sendMessage(1137219031,intento_msg)
            return
        


        msgText = ''
        try: msgText = update.message.text
        except:pass

        # comandos de admin
        if '/add' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_user(user)
                    jdb.save()
                    msg = '✅𝚃𝚑𝚎 𝚞𝚜𝚎𝚛 @'+user+' 𝚑𝚊𝚜 𝚋𝚎𝚒𝚗𝚐 𝚊𝚍𝚍𝚎𝚍 𝚝𝚘 𝚝𝚑𝚎 𝚋𝚘𝚝!'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,f'⚠️𝙲𝚘𝚖𝚖𝚊𝚗𝚍 𝚎𝚛𝚛𝚘𝚛 /add 𝚞𝚜𝚎𝚛𝚗𝚊𝚖𝚎')
            else:
                bot.sendMessage(update.message.chat.id,'👮𝚈𝚘𝚞 𝚍𝚘 𝚗𝚘𝚝 𝚑𝚊𝚟𝚎 𝚊𝚍𝚖𝚒𝚗𝚒𝚜𝚝𝚛𝚊𝚝𝚘𝚛 𝚙𝚎𝚛𝚖𝚒𝚜𝚜𝚒𝚘𝚗𝚜👮')
            return
        if '/admin' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_admin(user)
                    jdb.save()
                    msg = '✅𝙽𝚘𝚠 @'+user+' 𝚒𝚜 𝚊 𝚋𝚘𝚝 𝚊𝚍𝚖𝚒𝚗 𝚝𝚘𝚘!'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,f'⚠️𝙲𝚘𝚖𝚖𝚊𝚗𝚍 𝚎𝚛𝚛𝚘𝚛 /admin 𝚞𝚜𝚎𝚛𝚗𝚊𝚖𝚎⚠️')
            else:
                bot.sendMessage(update.message.chat.id,'👮𝚈𝚘𝚞 𝚍𝚘 𝚗𝚘𝚝 𝚑𝚊𝚟𝚎 𝚊𝚍𝚖𝚒𝚗𝚒𝚜𝚝𝚛𝚊𝚝𝚘𝚛 𝚙𝚎𝚛𝚖𝚒𝚜𝚜𝚒𝚘𝚗𝚜👮')
            return

        if '/preview' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_user_evea_preview(user)
                    jdb.save()
                    msg = '✅𝚃𝚑𝚎 𝚞𝚜𝚎𝚛 @'+user+' 𝚗𝚘𝚠 𝚒𝚜 𝚒𝚗 𝚝𝚎𝚜𝚝 𝚖𝚘𝚍𝚎.'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,f'⚠️𝙲𝚘𝚖𝚖𝚊𝚗𝚍 𝚎𝚛𝚛𝚘𝚛 /preview 𝚞𝚜𝚎𝚛𝚗𝚊𝚖𝚎⚠️')
            else:
                bot.sendMessage(update.message.chat.id,'👮𝚈𝚘𝚞 𝚍𝚘 𝚗𝚘𝚝 𝚑𝚊𝚟𝚎 𝚊𝚍𝚖𝚒𝚗𝚒𝚜𝚝𝚛𝚊𝚝𝚘𝚛 𝚙𝚎𝚛𝚖𝚒𝚜𝚜𝚒𝚘𝚗𝚜👮')
            return 
        if '/ban' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    if user == username:
                        bot.sendMessage(update.message.chat.id,'⚠️𝚈𝚘𝚞 𝚌𝚊𝚗 𝚗𝚘𝚝 𝚋𝚊𝚗 𝚢𝚘𝚞𝚛𝚜𝚎𝚕𝚏⚠️')
                        return
                    jdb.remove(user)
                    jdb.save()
                    msg = '𝚃𝚑𝚎 𝚞𝚜𝚎𝚛 @'+user+' 𝚑𝚊𝚜 𝚋𝚎𝚒𝚗𝚐 𝚋𝚊𝚗𝚗𝚎𝚍 𝚏𝚛𝚘𝚖 𝚝𝚑𝚎 𝚋𝚘𝚝!'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'⚠️𝙲𝚘𝚖𝚖𝚊𝚗𝚍 𝚎𝚛𝚛𝚘𝚛 /ban user⚠️')
            else:
                bot.sendMessage(update.message.chat.id,'👮𝚈𝚘𝚞 𝚍𝚘 𝚗𝚘𝚝 𝚑𝚊𝚟𝚎 𝚊𝚍𝚖𝚒𝚗𝚒𝚜𝚝𝚛𝚊𝚝𝚘𝚛 𝚙𝚎𝚛𝚖𝚒𝚜𝚜𝚒𝚘𝚗𝚜👮')
            return
        if '/obtenerdb' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                sms1 = bot.sendMessage(update.message.chat.id,'𝚂𝚎𝚗𝚍𝚒𝚗𝚐 𝚍𝚊𝚝𝚊𝚋𝚊𝚜𝚎...')
                sms2 = bot.sendMessage(update.message.chat.id,'𝙳𝚊𝚝𝚊𝚋𝚊𝚜𝚎:')
                
                bot.editMessageText(sms1,sms2)
                bot.sendFile(update.message.chat.id,'database.jdb')
            else:
                bot.sendMessage(update.message.chat.id,'👮𝚈𝚘𝚞 𝚍𝚘 𝚗𝚘𝚝 𝚑𝚊𝚟𝚎 𝚊𝚍𝚖𝚒𝚗𝚒𝚜𝚝𝚛𝚊𝚝𝚘𝚛 𝚙𝚎𝚛𝚖𝚒𝚜𝚜𝚒𝚘𝚗𝚜👮')
            return
        if '/leerdb' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                database = open('database.jdb','r')
                bot.sendMessage(update.message.chat.id,database.read())
                database.close()
            else:
                bot.sendMessage(update.message.chat.id,'👮𝚈𝚘𝚞 𝚍𝚘 𝚗𝚘𝚝 𝚑𝚊𝚟𝚎 𝚊𝚍𝚖𝚒𝚗𝚒𝚜𝚝𝚛𝚊𝚝𝚘𝚛 𝚙𝚎𝚛𝚖𝚒𝚜𝚜𝚒𝚘𝚗𝚜👮')
            return
        if '/useradm' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                message = bot.sendMessage(update.message.chat.id,'🦾')
                message = bot.sendMessage(update.message.chat.id,'🦾𝚈𝚘𝚞 𝚊𝚛𝚎 𝚋𝚘𝚝 𝚊𝚍𝚖𝚒𝚗𝚒𝚜𝚝𝚛𝚊𝚝𝚘𝚛, 𝚜𝚘 𝚢𝚘𝚞 𝚑𝚊𝚟𝚎 𝚝𝚘𝚝𝚊𝚕 𝚌𝚘𝚗𝚝𝚛𝚘𝚕 𝚘𝚟𝚎𝚛 𝚒𝚝𝚜𝚎𝚕𝚏✅')
            else:
                message = bot.sendMessage(update.message.chat.id,'🙁')
                message = bot.sendMessage(update.message.chat.id,'🙁𝚈𝚘𝚞 𝚊𝚛𝚎 𝚓𝚞𝚜𝚝 𝚊𝚗 𝚞𝚜𝚎𝚛, 𝚏𝚘𝚛 𝚗𝚘𝚠 𝚢𝚘𝚞 𝚑𝚊𝚟𝚎 𝚕𝚒𝚖𝚒𝚝𝚊𝚝𝚎𝚍 𝚌𝚘𝚗𝚝𝚛𝚘𝚕❎')
            return
        # end

        # comandos de usuario
        if '/help' in msgText:
            message = bot.sendMessage(update.message.chat.id,'𝚄𝚜𝚎𝚛 𝚐𝚞𝚒𝚍𝚎:')
            tuto = open('tuto.txt','r')
            bot.sendMessage(update.message.chat.id,tuto.read())
            tuto.close()
            return
        if '/xdlink' in msgText:

            try: 
                urls = str(msgText).split(' ')[1]
                channelid = getUser['channelid']
                xdlinkdd = xdlink.parse(urls, username)
                msg = f'**Aquí está su link encriptado en xdlink:** `{xdlinkdd}`'
                msgP = f'**Aquí está su link encriptado en xdlink protegido:** `{xdlinkdd}`'
                if channelid == 0:
                    bot.sendMessage(chat_id = chatid, parse_mode = 'Markdown', text = msg)
                else: 
                    bot.sendMessage(chat_id = chatid, parse_mode = 'Markdown', text = msgP)
            except:
                msg = f'》*El comando debe ir acompañado de un link moodle*'
                bot.sendMessage(chat_id = chatid, parse_mode = 'Markdown', text = msg)
            return

        if '/xdon' in msgText:
            getUser = user_info
            if getUser:
                getUser['xdlink'] = 1
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
            return
            
        if '/xdoff' in msgText:
            getUser = user_info
            if getUser:
                getUser['xdlink'] = 0
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
            return

        if '/channelid' in msgText:
            channelId = str(msgText).split(' ')[1]
            getUser = user_info
            try:
                if getUser:
                    getUser['channelid'] = str(msgText).split(' ')[1]
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                msg = f'》*El comando debe ir acompañado de un id de canal*\n\n*Ejemplo: -100XXXXXXXXXX*'
                bot.sendMessage(chat_id = chatid, parse_mode = 'Markdown', text = msg)
            return

        if '/delChannel' in msgText:
            getUser = user_info
            if getUser:
                getUser['channelid'] = 0
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
            return
        if '/about' in msgText:
            message = bot.sendMessage(update.message.chat.id,'📄')
            información = open('información.txt','r')
            bot.sendMessage(update.message.chat.id,información.read())
            información.close()
            return
        if '/commands' in msgText:
            message = bot.sendMessage(update.message.chat.id,'🙂𝙵𝚘𝚛 𝚊𝚍𝚍 𝚝𝚑𝚒𝚜 𝚌𝚘𝚖𝚖𝚊𝚗𝚍𝚜 𝚝𝚘 𝚝𝚑𝚎 𝚚𝚞𝚒𝚌𝚔 𝚊𝚌𝚌𝚎𝚜𝚜 𝚖𝚎𝚗𝚞 𝚢𝚘𝚞 𝚖𝚞𝚜𝚝 𝚜𝚎𝚗𝚍 𝚝𝚑𝚎 𝚌𝚘𝚖𝚖𝚊𝚗𝚍 /setcommands 𝚝𝚘 @BotFather 𝚊𝚗𝚍 𝚝𝚑𝚎𝚗 𝚜𝚎𝚕𝚎𝚌𝚝 𝚢𝚘𝚞𝚛 𝚋𝚘𝚝, 𝚊𝚏𝚝𝚎𝚛 𝚘𝚗𝚕𝚢 𝚛𝚎𝚖𝚊𝚒𝚗𝚐𝚜 𝚛𝚎𝚜𝚎𝚗𝚍 𝚝𝚑𝚎 𝚖𝚎𝚜𝚜𝚊𝚐𝚎 𝚠𝚒𝚝𝚑 𝚝𝚑𝚎 𝚗𝚎𝚡𝚝 𝚌𝚘𝚖𝚖𝚊𝚗𝚍𝚜 𝚊𝚗𝚍... 𝚍𝚘𝚗𝚎😁.')
            comandos = open('comandos.txt','r')
            bot.sendMessage(update.message.chat.id,comandos.read())
            información.close()
            return
        if '/myuser' in msgText:
            getUser = user_info
            if getUser:
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
                return
        if '/zips' in msgText:
            getUser = user_info
            if getUser:
                try:
                   size = int(str(msgText).split(' ')[1])
                   getUser['zips'] = size
                   jdb.save_data_user(username,getUser)
                   jdb.save()
                   msg = '🗜️𝙿𝚎𝚛𝚏𝚎𝚌𝚝 𝚗𝚘𝚠 𝚝𝚑𝚎 𝚣𝚒𝚙𝚜 𝚠𝚒𝚕𝚕 𝚋𝚎 𝚘𝚏 '+ sizeof_fmt(size*1024*1024)+' 𝚝𝚑𝚎 𝚙𝚊𝚛𝚝𝚜📚'
                   bot.sendMessage(update.message.chat.id,msg)
                except:
                   bot.sendMessage(update.message.chat.id,'⚠️𝙲𝚘𝚖𝚖𝚊𝚗𝚍 𝚎𝚛𝚛𝚘𝚛 /zips 𝚣𝚒𝚙𝚜_𝚜𝚒𝚣𝚎⚠️')    
                return
        if '/gen' in msgText:
            pass444
        if '/acc' in msgText:
            try:
                account = str(msgText).split(' ',2)[1].split(',')
                user = account[0]
                passw = account[1]
                getUser = user_info
                if getUser:
                    getUser['moodle_user'] = user
                    getUser['moodle_password'] = passw
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️𝙲𝚘𝚖𝚖𝚊𝚗𝚍 𝚎𝚛𝚛𝚘𝚛 /acc 𝚞𝚜𝚎𝚛,𝚙𝚊𝚜𝚜𝚠𝚘𝚛𝚍⚠️')
            return

        if '/host' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                host = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['moodle_host'] = host
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️𝙲𝚘𝚖𝚖𝚊𝚗𝚍 𝚎𝚛𝚛𝚘𝚛 /host 𝚌𝚕𝚘𝚞𝚍_𝚞𝚛𝚕⚠️')
            return
        if '/repo' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = int(cmd[1])
                getUser = user_info
                if getUser:
                    getUser['moodle_repo_id'] = repoid
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️𝙲𝚘𝚖𝚖𝚊𝚗𝚍 𝚎𝚛𝚛𝚘𝚛 /repo 𝚖𝚘𝚘𝚍𝚕𝚎_𝚛𝚎𝚙𝚘_𝚒𝚍⚠️')
            return
        if '/encrypt_on' in msgText:
            try:
                getUser = user_info
                if getUser:
                    getUser['tokenize'] = 1
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'🔒𝙴𝚗𝚌𝚛𝚢𝚙𝚝 𝚍𝚘𝚠𝚗𝚕𝚘𝚊𝚍 𝚕𝚒𝚗𝚔𝚜.')
            except:
                bot.sendMessage(update.message.chat.id,'⚠️𝙲𝚘𝚖𝚖𝚊𝚗𝚍 𝚎𝚛𝚛𝚘𝚛 /encrypt_on 𝚎𝚗𝚌𝚛𝚢𝚙𝚝_𝚜𝚝𝚊𝚝𝚎⚠️')
            return
        if '/encrypt_off' in msgText:
            try:
                getUser = user_info
                if getUser:
                    getUser['tokenize'] = 0
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'🔒𝙽𝚘 𝚎𝚗𝚌𝚛𝚢𝚙𝚝 𝚍𝚘𝚠𝚗𝚕𝚘𝚊𝚍 𝚕𝚒𝚗𝚔𝚜.')
            except:
                bot.sendMessage(update.message.chat.id,'⚠️𝙲𝚘𝚖𝚖𝚊𝚗𝚍 𝚎𝚛𝚛𝚘𝚛 /encript_off 𝚎𝚗𝚌𝚛𝚢𝚙𝚝_𝚜𝚝𝚊𝚝𝚎⚠️')
            return
        if '/cloud' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['cloudtype'] = repoid
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️𝙲𝚘𝚖𝚖𝚊𝚗𝚍 𝚎𝚛𝚛𝚘𝚛 /cloud (𝚖𝚘𝚘𝚍𝚕𝚎 𝚘𝚛 𝚌𝚕𝚘𝚞𝚍)⚠️')
            return
        if '/uptype' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                type = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['uploadtype'] = type
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️𝙲𝚘𝚖𝚖𝚊𝚗𝚍 𝚎𝚛𝚛𝚘𝚛 /uptype (𝚎𝚟𝚒𝚍𝚎𝚗𝚌𝚎,𝚍𝚛𝚊𝚏𝚝,𝚋𝚕𝚘𝚐,𝚌𝚊𝚕𝚎𝚗𝚍𝚊𝚛)⚠️')
            return

        if '/search_proxy' in msgText:
            msg_start = 'Buscando proxy, esto puede tardar de una a dos horas...'
            bot.sendMessage(update.message.chat.id,msg_start)
            print("Buscando proxy...")
            for port in range(3029,3032):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                result = sock.connect_ex(('152.206.139.117:',port))  

                if result == 0: 
                    print ("Puerto abierto!")
                    print (f"Puerto: {port}")  
                    proxy = f'152.206.139.117:{port}'
                    proxy_new = S5Crypto.encrypt(f'{proxy}')
                    msg = 'Su nuevo proxy es:\n\nsocks5://' + proxy_new
                    bot.sendMessage(update.message.chat.id,msg)
                    break
                else: 
                    print ("Error...Buscando...")
                    print (f"Buscando en el puerto: {port}")
                    sock.close()
            
            return
        if '/proxy' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                proxy = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['proxy'] = proxy
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    msg = '🧬𝙿𝚎𝚛𝚏𝚎𝚌𝚝, 𝚙𝚛𝚘𝚡𝚢 𝚎𝚚𝚞𝚒𝚙𝚙𝚎𝚍 𝚜𝚞𝚌𝚌𝚎𝚜𝚜𝚏𝚞𝚕𝚢.'
                    bot.sendMessage(update.message.chat.id,msg)
            except:
                if user_info:
                    user_info['proxy'] = ''
                    statInfo = infos.createStat(username,user_info,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'🧬𝙴𝚛𝚛𝚘𝚛 𝚎𝚚𝚞𝚒𝚙𝚙𝚒𝚗𝚐 𝚙𝚛𝚘𝚡𝚢.')
            return
        if '/encrypt' in msgText:
            proxy_sms = str(msgText).split(' ')[1]
            proxy = S5Crypto.encrypt(f'{proxy_sms}')
            bot.sendMessage(update.message.chat.id, f'🧬𝙿𝚛𝚘𝚡𝚢 𝚎𝚗𝚌𝚛𝚢𝚙𝚝𝚎𝚍:\n{proxy}')
            return
        if '/decrypt' in msgText:
            proxy_sms = str(msgText).split(' ')[1]
            proxy_de = S5Crypto.decrypt(f'{proxy_sms}')
            bot.sendMessage(update.message.chat.id, f'🧬𝙿𝚛𝚘𝚡𝚢 𝚍𝚎𝚌𝚛𝚢𝚙𝚝𝚎𝚍:\n{proxy_de}')
            return
        if '/off_proxy' in msgText:
            try:
                getUser = user_info
                if getUser:
                    getUser['proxy'] = ''
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    msg = '🧬𝙰𝚕𝚛𝚒𝚐𝚑𝚝, 𝚙𝚛𝚘𝚡𝚢 𝚞𝚗𝚎𝚚𝚞𝚒𝚙𝚙𝚎𝚍 𝚜𝚞𝚌𝚌𝚎𝚜𝚜𝚏𝚞𝚕𝚢.\n'
                    bot.sendMessage(update.message.chat.id,msg)
            except:
                if user_info:
                    user_info['proxy'] = ''
                    statInfo = infos.createStat(username,user_info,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'🧬𝙴𝚛𝚛𝚘𝚛 𝚍𝚎𝚌𝚛𝚢𝚙𝚝𝚒𝚗𝚐 𝚙𝚛𝚘𝚡𝚢.')
            return
        if '/view_proxy' in msgText:
            try:
                getUser = user_info
                if getUser:
                    proxy = getUser['proxy']
                    message = bot.sendMessage(update.message.chat.id,'🧬𝚃𝚑𝚎 𝚙𝚛𝚘𝚡𝚢 𝚝𝚑𝚊𝚝 𝚢𝚘𝚞 𝚊𝚛𝚎 𝚞𝚜𝚒𝚗𝚐 𝚗𝚘𝚠 𝚒𝚜:')
                    bot.sendMessage(update.message.chat.id,proxy)
            except:
                message = bot.sendMessage(update.message.chat.id,'🧬𝚃𝚑𝚎 𝚙𝚛𝚘𝚡𝚢 𝚝𝚑𝚊𝚝 𝚢𝚘𝚞 𝚊𝚛𝚎 𝚞𝚜𝚒𝚗𝚐 𝚗𝚘𝚠 𝚒𝚜:')
                bot.sendMessage(update.message.chat.id,proxy)
            return
        if '/dir' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['dir'] = repoid + '/'
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️𝙲𝚘𝚖𝚖𝚊𝚗𝚍 𝚎𝚛𝚛𝚘𝚛 /dir 𝚍𝚎𝚜𝚝𝚒𝚗𝚢_𝚏𝚘𝚕𝚍𝚎𝚛⚠️')
            return
        if '/cancel_' in msgText:
            try:
                cmd = str(msgText).split('_',2)
                tid = cmd[1]
                tcancel = bot.threads[tid]
                msg = tcancel.getStore('msg')
                tcancel.store('stop',True)
                time.sleep(3)
                bot.editMessageText(msg,'🚫𝚃𝚊𝚜𝚔 𝚌𝚊𝚗𝚌𝚎𝚕𝚕𝚎𝚍🚫')
            except Exception as ex:
                print(str(ex))
            return
        #end

        message = bot.sendMessage(update.message.chat.id,'🔬𝙰𝚗𝚊𝚕𝚢𝚣𝚒𝚗𝚐...🔬')

        thread.store('msg',message)

        if '/start' in msgText:
            start_msg = '   🌟𝔹𝕠𝕥 𝕚𝕟𝕚𝕔𝕚𝕒𝕥𝕖𝕕🌟\n'
            start_msg+= '✥ ------✥◈✥------ ✥\n'
            start_msg+= '🤖𝐻𝑒𝓁𝓁𝑜 @' + str(username)+'\n'
            start_msg+= '🙂𝒲𝑒𝓁𝓁𝒸𝑜𝓂𝑒 𝓉𝑜 𝒻𝓇𝑒𝑒 𝒹𝑜𝓌𝓃𝓁𝑜𝒶𝒹 𝒷𝑜𝓉 𝒮𝓊𝓅𝑒𝓇𝒟𝑜𝓌𝓃𝓁𝑜𝒶𝒹 𝑜𝓃 𝒾𝓉𝓈 𝒾𝓃𝒾𝓉𝒾𝒶𝓁 𝓋𝑒𝓇𝓈𝒾𝑜𝓃 𝟣.𝟢 𝒫𝓁𝓊𝓈𝐸𝒹𝒾𝓉𝒾𝑜𝓃🌟!\n'
            start_msg+= '🦾𝒟𝑒𝓋𝑒𝓁𝑜𝓅𝑒𝓇: > @Luis_Daniel_Díaz <\n\n'
            start_msg+= '🙂𝐼𝒻 𝓎𝑜𝓊 𝓃𝑒𝑒𝒹 𝒽𝑒𝓁𝓁𝓅 𝑜𝓇 𝒾𝓃𝒻𝑜𝓇𝓂𝒶𝓉𝒾𝑜𝓃 𝓊𝓈𝑒:\n'
            start_msg+= '/help\n'
            start_msg+= '/about\n'
            start_msg+= '🙂𝐼𝒻 𝓎𝑜𝓊 𝓌𝒾𝒸𝒽 𝒶𝒹𝒹 𝓉𝒽𝑒 𝒸𝑜𝓂𝓂𝒶𝓃𝒹 𝒷𝒶𝓇 𝓉𝑜 𝓉𝒽𝑒 𝓆𝓊𝒾𝒸𝓀 𝒶𝒸𝒸𝑒𝓈𝓈 𝒷𝑜𝓉 𝓂𝑒𝓃𝓊 𝓈𝑒𝓃𝒹 /commands.\n\n'
            start_msg+= '😁𝐸𝓃𝒿𝑜𝓎 𝑔𝓇𝑒𝒶𝓉𝓁𝓎 𝓎𝑜𝓊𝓇 𝓈𝓉𝒶𝓎 𝒾𝓃 𝒽𝑒𝓇𝑒😁.\n'
            bot.editMessageText(message,start_msg)
            message = bot.sendMessage(update.message.chat.id,'🦾')
        elif '/files' == msgText and user_info['cloudtype']=='moodle':
             proxy = ProxyCloud.parse(user_info['proxy'])
             client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],proxy=proxy)
             loged = client.login()
             if loged:

                List = client.getEvidences()
                List1=List[:45]
                total=len(List)
                List2=List[46:]
                info1 = f'<b>Archivos: {str(total)}</b>\n\n'
                info = f'<b>Archivos: {str(total)}</b>\n\n'
                
                i = 0
                for item in List1:
                    info += '<b>/del_'+str(i)+'</b>   /txt_'+str(i)+'\n'
                    #info += '<b>'+item['name']+':</b>\n'
                    for file in item['files']:                  
                        info += '<a href="'+file['directurl']+'">\t'+file['name']+'</a>\n'
                    info+='\n'
                    i+=1
                    bot.editMessageText(message, f'{info}',parse_mode="html")
                
                if len(List2)>0:
                    bot.sendMessage(update.message.chat.id,'⏳Conecting with the list number 2...')
                    for item in List2:
                        
                        info1 += '<b>/del_'+str(i)+'</b>   /txt_'+str(i)+'\n'
                        #info1 += '<b>'+item['name']+':</b>\n'
                        for file in item['files']:                  
                            info1 += '<a href="'+file['url']+'">\t'+file['name']+'</a>\n'
                        info1+='\n'
                        i+=1
                        bot.editMessageText(message, f'{info1}',parse_mode="html")
        elif '/txt_' in msgText and user_info['cloudtype']=='moodle':
             findex = str(msgText).split('_')[1]
             findex = int(findex)
             proxy = ProxyCloud.parse(user_info['proxy'])
             client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],proxy=proxy)
             loged = client.login()
             if loged:
                 evidences = client.getEvidences()
                 evindex = evidences[findex]
                 txtname = evindex['name']+'.txt'
                 sendTxt(txtname,evindex['files'],update,bot)
                 client.logout()
                 bot.editMessageText(message,'𝚃𝚇𝚃 𝚑𝚎𝚛𝚎📃')
             else:
                bot.editMessageText(message,'🤔')
                message = bot.sendMessage(update.message.chat.id,'⚠️𝙴𝚛𝚛𝚘𝚛 𝚊𝚗𝚍 𝚙𝚘𝚜𝚜𝚒𝚋𝚕𝚎 𝚌𝚊𝚞𝚜𝚎𝚜:\n𝟷-𝙲𝚑𝚎𝚌𝚔 𝚘𝚞𝚝 𝚢𝚘𝚞𝚛 𝚊𝚌𝚌𝚘𝚞𝚗𝚝\n𝟸-𝚂𝚎𝚛𝚟𝚎𝚛 𝚍𝚒𝚜𝚊𝚋𝚕𝚎𝚍: '+client.path)
             pass
        elif '/token' in msgText:
            message2 = bot.editMessageText(message,'🤖𝙶𝚎𝚝𝚝𝚒𝚗𝚐 𝚝𝚘𝚔𝚎𝚗, 𝚙𝚕𝚎𝚊𝚜𝚎 𝚠𝚊𝚒𝚝🙂...')

            try:
                proxy = ProxyCloud.parse(user_info['proxy'])
                client = MoodleClient(user_info['moodle_user'],
                                      user_info['moodle_password'],
                                      user_info['moodle_host'],
                                      user_info['moodle_repo_id'],proxy=proxy)
                loged = client.login()
                if loged:
                    token = client.userdata
                    modif = token['token']
                    bot.editMessageText(message2,'🤖𝚈𝚘𝚞𝚛 𝚝𝚘𝚔𝚎𝚗 𝚒𝚜: '+modif)
                    client.logout()
                else:
                    bot.editMessageText(message2,'⚠️𝚃𝚑𝚎 𝚖𝚘𝚘𝚍𝚕𝚎 '+client.path+' 𝚍𝚘𝚎𝚜 𝚗𝚘𝚝 𝚑𝚊𝚟𝚎 𝚝𝚘𝚔𝚎𝚗⚠️')
            except Exception as ex:
                bot.editMessageText(message2,'⚠️𝚃𝚑𝚎 𝚖𝚘𝚘𝚍𝚕𝚎 '+client.path+' 𝚍𝚘𝚎𝚜 𝚗𝚘𝚝 𝚑𝚊𝚟𝚎 𝚝𝚘𝚔𝚎𝚗 𝚘𝚛 𝚌𝚑𝚎𝚌𝚔 𝚘𝚞𝚝 𝚝𝚑𝚎 𝚊𝚌𝚌𝚘𝚞𝚗𝚝⚠️')       
        elif '/del_' in msgText and user_info['cloudtype']=='moodle':
            findex = int(str(msgText).split('_')[1])
            proxy = ProxyCloud.parse(user_info['proxy'])
            client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],
                                   proxy=proxy)
            loged = client.login()
            if loged:
                evfile = client.getEvidences()[findex]
                client.deleteEvidence(evfile)
                client.logout()
                bot.editMessageText(message,'𝙵𝚒𝚕𝚎 𝚍𝚎𝚕𝚎𝚝𝚎𝚍🗑️')
            else:
                bot.editMessageText(message,'🤔')
                message = bot.sendMessage(update.message.chat.id,'⚠️𝙴𝚛𝚛𝚘𝚛 𝚊𝚗𝚍 𝚙𝚘𝚜𝚜𝚒𝚋𝚕𝚎 𝚌𝚊𝚞𝚜𝚎𝚜:\n𝟷-𝙲𝚑𝚎𝚌𝚔 𝚘𝚞𝚝 𝚢𝚘𝚞𝚛 𝚊𝚌𝚌𝚘𝚞𝚗𝚝\n𝟸-𝚂𝚎𝚛𝚟𝚎𝚛 𝚍𝚒𝚜𝚊𝚋𝚕𝚎𝚍: '+client.path)
        elif '/delall' in msgText and user_info['cloudtype']=='moodle':
            proxy = ProxyCloud.parse(user_info['proxy'])
            client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],
                                   proxy=proxy)
            loged = client.login()
            if loged:
                evfiles = client.getEvidences()
                for item in evfiles:
                    client.deleteEvidence(item)
                client.logout()
                bot.editMessageText(message,'𝙵𝚒𝚕𝚎𝚜 𝚍𝚎𝚕𝚎𝚝𝚎𝚍🗑️')
            else:
                bot.editMessageText(message,'🤔')
                message = bot.sendMessage(update.message.chat.id,'⚠️𝙴𝚛𝚛𝚘𝚛 𝚊𝚗𝚍 𝚙𝚘𝚜𝚜𝚒𝚋𝚕𝚎 𝚌𝚊𝚞𝚜𝚎𝚜:\n𝟷-𝙲𝚑𝚎𝚌𝚔 𝚘𝚞𝚝 𝚢𝚘𝚞𝚛 𝚊𝚌𝚌𝚘𝚞𝚗𝚝\n𝟸-𝚂𝚎𝚛𝚟𝚎𝚛 𝚍𝚒𝚜𝚊𝚋𝚕𝚎𝚍: '+client.path)
        elif 'http' in msgText:
            url = msgText
            ddl(update,bot,message,url,file_name='',thread=thread,jdb=jdb)
        else:
            #if update:
            #    api_id = os.environ.get('api_id')
            #    api_hash = os.environ.get('api_hash')
            #    bot_token = os.environ.get('bot_token')
            #    
                # set in debug
            #    api_id = 7386053
            #    api_hash = '78d1c032f3aa546ff5176d9ff0e7f341'
            #    bot_token = '5124841893:AAH30p6ljtIzi2oPlaZwBmCfWQ1KelC6KUg'

            #    chat_id = int(update.message.chat.id)
            #    message_id = int(update.message.message_id)
            #    import asyncio
            #    asyncio.run(tlmedia.download_media(api_id,api_hash,bot_token,chat_id,message_id))
            #    return
            bot.editMessageText(message,'⚠️𝙴𝚛𝚛𝚘𝚛, 𝚒𝚝 𝚌𝚘𝚞𝚕𝚍 𝚗𝚘𝚝 𝚊𝚗𝚊𝚕𝚒𝚣𝚎 𝚌𝚘𝚛𝚛𝚎𝚌𝚝𝚕𝚢⚠️')
    except Exception as ex:
           print(str(ex))
  

def main():
    bot_token = '5326988358:AAGw7SHWE0IiDVmDEFJsUtbmygkeH4Xv0yI'
    

    bot = ObigramClient(bot_token)
    bot.onMessage(onmessage)
    bot.run()
    asyncio.run()

if __name__ == '__main__':
    try:
        main()
    except:
        main()
