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
			if porcent >= index_make * 5: make_text+= '▰'
			else: make_text+= '▱'
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
    msg = '╭─📥Downloading📡... \n'+'│'+'\n'
    msg+= '├🏷️ File name: ' + str(filename)+'\n'
    msg+= '├📦 Total size: ' + str(sizeof_fmt(totalBits))+'\n'
    msg+= '├📥 Downloaded: ' + str(sizeof_fmt(currentBits))+'\n'
    msg+= '├⚡️ Speed: ' + str(sizeof_fmt(speed))+'/s\n'+'│'+'\n'
    msg+= '╰─⏲️ Time left: ' + str(datetime.timedelta(seconds=int(time))) +'\n\n'

    msg = '╭─📥Downloading file📡...\n'+'│'+'\n'
    msg += '╰─🏷️ File name: '+filename+'\n'
    msg += text_progres(currentBits,totalBits)+'\n'
    msg += '╭─🚦 Percentage: '+str(porcent(currentBits,totalBits))+'%\n'+'│'+'\n'
    msg += '├📦 Total size: '+sizeof_fmt(totalBits)+'\n'
    msg += '├📥 Downloaded: '+sizeof_fmt(currentBits)+'\n'
    msg += '├⚡️ Speed: '+sizeof_fmt(speed)+'/s\n'+'│'+'\n'
    msg += '╰─⏲️ Time left: '+str(datetime.timedelta(seconds=int(time)))+'s\n\n'

    if tid!='':
        msg+= '/cancel_' + tid
    return msg
def createUploading(filename,totalBits,currentBits,speed,time,originalname=''):
    msg = '╭─📤Uploading☁️... \n'+'│'+'\n'
    msg+= '├🏷️ File name: ' + str(filename)+'\n'
    if originalname!='':
        msg = str(msg).replace(filename,originalname)
        msg+= '╭─📤Uploading: ' + str(filename)+'\n'
    msg+= '├📦 Total size: ' + str(sizeof_fmt(totalBits))+'\n'
    msg+= '├📤 Uploaded: ' + str(sizeof_fmt(currentBits))+'\n'
    msg+= '├⚡️ Speed: ' + str(sizeof_fmt(speed))+'/s\n'+'│'+'\n'
    msg+= '╰─⏲️ Time left: ' + str(datetime.timedelta(seconds=int(time))) +'\n'

    msg = '╭─📤Uploading☁️...\n'+'│'+'\n'
    msg += '├🏷️ File name: '+filename+'\n'
    if originalname!='':
        msg = str(msg).replace(filename,originalname)
        msg+= '╰─📚 Part: ' + str(filename)+'\n'
    msg += text_progres(currentBits,totalBits)+'\n'
    msg += '╭─🚦 Percentage: '+str(porcent(currentBits,totalBits))+'%\n'
    msg += '├📦 Total size: '+sizeof_fmt(totalBits)+'\n'
    msg += '├📤 Uploaded: '+sizeof_fmt(currentBits)+'\n'
    msg += '├⚡️ Speed: '+sizeof_fmt(speed)+'/s\n'+'│'+'\n'
    msg += '╰─⏲️ Time left: '+str(datetime.timedelta(seconds=int(time)))+'s\n\n'

    return msg
def createCompresing(filename,filesize,splitsize):
    msg = '╭─🗜️Compressing🗜️... \n'+'│'+'\n'
    msg+= '├🏷️ File name: ' + str(filename)+'\n'
    msg+= '├📦 Total size: ' + str(sizeof_fmt(filesize))+'\n'
    msg+= '├📚 Parts size: ' + str(sizeof_fmt(splitsize))+'\n'+'│'+'\n'
    msg+= '╰─📕 Amount of parts: ' + str(round(int(filesize/splitsize)+1,1))+'\n\n'

    return msg
def createFinishUploading(filename,filesize,split_size,current,count,findex):
    msg = '╭─✅Completed✅\n'+'│'+'\n'
    msg+= '├🏷️ File name: ' + str(filename)+'\n'
    msg+= '├📦 Total size: ' + str(sizeof_fmt(filesize))+'\n'
    msg+= '├📚 Parts size: ' + str(sizeof_fmt(split_size))+'\n'
    msg+= '├📤 Uploaded parts: ' + str(current) + '/' + str(count) +'\n'+'│'+'\n'
    msg+= '╰─🗑️Delete file🗑️: ' + '/del_'+str(findex)
    return msg

def createFileMsg(filename,files):
    import urllib
    if len(files)>0:
        msg= '<b>🔗Link/s🔗</b>\n'
        for f in files:
            url = urllib.parse.unquote(f['directurl'],encoding='utf-8', errors='replace')
            #msg+= '<a href="'+f['url']+'">🔗' + f['name'] + '🔗</a>'
            msg+= "<a href='"+url+"'>🔗"+f['name']+'🔗</a>\n'
        return msg
    return ''

def createFilesMsg(evfiles):
    msg = '📑File/s ('+str(len(evfiles))+')📑\n\n'
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
    msg = '╭─ⓘUser dataⓘ─〄\n'+'│'+'\n'
    msg+= '├👤 Username: @' + str(username)+'\n'
    msg+= '├👤 User: ' + str(userdata['moodle_user'])+'\n'
    msg+= '├🔑 Password: ' + str(userdata['moodle_password'])+'\n'
    msg+= '├🌐 Cloud URL: ' +'\n'+'├─'+ str(userdata['moodle_host'])+'\n'
    if userdata['cloudtype'] == 'moodle':
        msg+= '├🆔 Cloud ID: ' + str(userdata['moodle_repo_id'])+'\n'
    msg+= '├☁️ Cloud type: ' + str(userdata['cloudtype'])+'\n'
    msg+= '├🔼 Upload type: ' + str(userdata['uploadtype'])+'\n'
    if userdata['cloudtype'] == 'cloud':
        msg+= '├📁 Directory: /' + str(userdata['dir'])+'\n'
    msg+= '├🗜️ Zips size: ' + sizeof_fmt(userdata['zips']*1024*1024) + '\n'
    msgAdmin = 'No'
    if isadmin:
        msgAdmin = 'Yes'
    msg+= '├👮 𝙰𝚍𝚖𝚒𝚗𝚒𝚜𝚝𝚛𝚊𝚝𝚘𝚛: ' + msgAdmin + '\n'
    proxy = 'No'
    if userdata['proxy'] !='':
       proxy = 'Yes'
    tokenize = 'Off'
    if userdata['tokenize']!=0:
       tokenize = 'On'
    msg+= '├📡 Proxy setted: ' + proxy + '\n'
    msg+= '├🔒 Encrypt links: ' + tokenize + '\n'+'│'+'\n'
    msg+= '╰─ⓘUser dataⓘ─⎔'
    return msg
    
