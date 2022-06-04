from pyobigram.utils import sizeof_fmt,nice_time
import datetime
import time
import os

def text_progres(index,max):
	try:
		if max<1:
			max += 1
		porcent = index / max
		porcent *= 100
		porcent = round(porcent)
		make_text = ''
		index_make = 1
		make_text += '\n['
		while(index_make<20):
			if porcent >= index_make * 5: make_text+= '✦'
			else: make_text+= '✧'
			index_make+=1
		make_text += ']\n'
		return make_text
	except Exception as ex:
			return ''

def porcent(index,max):
    porcent = index / max
    porcent *= 100
    porcent = round(porcent)
    return porcent

def createDownloading(filename,totalBits,currentBits,speed,time,tid=''):
    msg = '📥DESCARGANDO📡... \n\n'
    msg+= '🏷️ NAME: ' + str(filename)+'\n'
    msg+= '📦 TOTAL SIZE: ' + str(sizeof_fmt(totalBits))+'\n'
    msg+= '📥 DOWNLOADED: ' + str(sizeof_fmt(currentBits))+'\n'
    msg+= '📶 SPEED: ' + str(sizeof_fmt(speed))+'/s\n'
    msg+= '⏲️ TIME LEFT: ' + str(datetime.timedelta(seconds=int(time))) +'\n\n'

    msg = '📥DESCARGANDO ARCHIVO📡...\n\n'
    msg += '📦 Archivo: '+filename+'\n'
    msg += text_progres(currentBits,totalBits)+'\n'
    msg += '📊 PERCENTAGE: '+str(porcent(currentBits,totalBits))+'%\n\n'
    msg += '📦 TOTAL SIZE: '+sizeof_fmt(totalBits)+'\n\n'
    msg += '📥 DOWNLOADED: '+sizeof_fmt(currentBits)+'\n\n'
    msg += '📶 SPEED: '+sizeof_fmt(speed)+'/s\n\n'
    msg += '⏲️ TIME LEFT: '+str(datetime.timedelta(seconds=int(time)))+'s\n\n'

    if tid!='':
        msg+= '/cancel_' + tid
    return msg
def createUploading(filename,totalBits,currentBits,speed,time,originalname=''):
    msg = '📤UPLOADING☁️... \n\n'
    msg+= '🏷️ FILE: ' + str(filename)+'\n'
    if originalname!='':
        msg = str(msg).replace(filename,originalname)
        msg+= '📤 UPLOADING: ' + str(filename)+'\n'
    msg+= '📦 TOTAL SIZE: ' + str(sizeof_fmt(totalBits))+'\n'
    msg+= '📤 UPLOADED: ' + str(sizeof_fmt(currentBits))+'\n'
    msg+= '📶 SPEED: ' + str(sizeof_fmt(speed))+'/s\n'
    msg+= '⏲️ TIME LEFT: ' + str(datetime.timedelta(seconds=int(time))) +'\n'

    msg = '📤UPLOADING☁️...\n\n'
    msg += '🏷️ NAME: '+filename+'\n'
    if originalname!='':
        msg = str(msg).replace(filename,originalname)
        msg+= '📚 PART: ' + str(filename)+'\n'
    msg += text_progres(currentBits,totalBits)+'\n'
    msg += '📊 PERCENTAGE: '+str(porcent(currentBits,totalBits))+'%\n\n'
    msg += '📦 TOTAL SIZE: '+sizeof_fmt(totalBits)+'\n\n'
    msg += '📤 UPLOADED: '+sizeof_fmt(currentBits)+'\n\n'
    msg += '📶 SPEED: '+sizeof_fmt(speed)+'/s\n\n'
    msg += '⏲️ TIME LEFT: '+str(datetime.timedelta(seconds=int(time)))+'s\n\n'

    return msg
def createCompresing(filename,filesize,splitsize):
    msg = '🗜️COMPRESSING🗜️... \n\n'
    msg+= '🏷️ NAME: ' + str(filename)+'\n'
    msg+= '📦 TOTAL SIZE: ' + str(sizeof_fmt(filesize))+'\n'
    msg+= '📚 PARTS SIZE: ' + str(sizeof_fmt(splitsize))+'\n'
    msg+= '📕 AMOUNT OF PARTS: ' + str(round(int(filesize/splitsize)+1,1))+'\n\n'

    return msg
def createFinishUploading(filename,filesize,split_size,current,count,findex):
    msg = '📌FINISHED PROCESS📌\n\n'
    msg+= '🏷️ NAME: ' + str(filename)+'\n'
    msg+= '📦 TOTAL SIZE: ' + str(sizeof_fmt(filesize))+'\n'
    msg+= '📚 PARTS SIZE: ' + str(sizeof_fmt(split_size))+'\n'
    msg+= '📤 UPLOADED PARTS: ' + str(current) + '/' + str(count) +'\n\n'
    msg+= '🗑️DELETE FILE🗑️: ' + '/del_'+str(findex)
    return msg

def createFileMsg(filename,files):
    import urllib
    if len(files)>0:
        msg= '<b>🔗LINKS🔗</b>\n'
        for f in files:
            url = urllib.parse.unquote(f['directurl'],encoding='utf-8', errors='replace')
            #msg+= '<a href="'+f['url']+'">🔗' + f['name'] + '🔗</a>'
            msg+= "<a href='"+url+"'>🔗"+f['name']+'🔗</a>\n'
        return msg
    return ''

def createFilesMsg(evfiles):
    msg = '📑FILES ('+str(len(evfiles))+')📑\n\n'
    i = 0
    for f in evfiles:
            try:
                fextarray = str(f['files'][0]['name']).split('.')
                fext = ''
                if len(fextarray)>=3:
                    fext = '.'+fextarray[-2]
                else:
                    fext = '.'+fextarray[-1]
                fname = f['name'] + fext
                msg+= '/txt_'+ str(i) + ' /del_'+ str(i) + '\n' + fname +'\n\n'
                i+=1
            except:pass
    return msg
def createStat(username,userdata,isadmin):
    from pyobigram.utils import sizeof_fmt
    msg = '⚙️USER CONFIGURATION⚙️\n\n'
    msg+= '👤 NAME: @' + str(username)+'\n'
    msg+= '👤 USER: ' + str(userdata['moodle_user'])+'\n'
    msg+= '🔑 PASSWORD: ' + str(userdata['moodle_password'])+'\n'
    msg+= '🌐 CLOUD URL: ' + str(userdata['moodle_host'])+'\n'
    if userdata['cloudtype'] == 'moodle':
        msg+= '🆔 CLOUD ID: ' + str(userdata['moodle_repo_id'])+'\n'
    msg+= '☁️ CLOUD TYPE: ' + str(userdata['cloudtype'])+'\n'
    msg+= '🔼 UPLOAD TYPE: ' + str(userdata['uploadtype'])+'\n'
    if userdata['cloudtype'] == 'cloud':
        msg+= '📁 DIRECTORY: /' + str(userdata['dir'])+'\n'
    msg+= '🗜️ ZIPS SIZE: ' + sizeof_fmt(userdata['zips']*1024*1024) + '\n\n'
    msgAdmin = '🔴'
    if isadmin:
        msgAdmin = '🟢'
    msg+= '👮 ADMIN : ' + msgAdmin + '\n'
    proxy = '🔴'
    if userdata['proxy'] !='':
       proxy = '🟢'
    tokenize = '🔴'
    if userdata['tokenize']!=0:
       tokenize = '🟢'
    msg+= '📡 PROXY: ' + proxy + '\n'
    msg+= '🔒 ENCRYPT: ' + tokenize + '\n\n'
    msg+= '⚙️CONFIGURE CREDENTIALS⚙️\n Example: /acc user,password'
    return msg
    
