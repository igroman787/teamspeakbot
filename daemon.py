import telnetlib
import os
import base64
import urllib.request
import time # time.strftime(init_time)
import subprocess
import sys
import threading
import math
import socket


debug = 1 # 1-Режим разработки
bot_name = 'scorpclub_bot' # Имя бота
bot_version = '1.5.014' # Версия бота
sgid_not_hold_corporation = '290' # Группа сервера "Корпорация не верна"
sgid_no_corporation = '292' # Группа сервера "Не состоит в корпорации"
sgid_wrong_nickname = '291' # Группа сервера "Никнейм не правильный"
sgid_pilot = '97' # Группа сервера "Пилот"


# Ввод дополнительных функций:
def launcher ():
	"""Создадим конфигурационный файл"""
	hostip = input('Введите IP адрес сервера: ').encode('utf-8');
	cod_passwd = base64.b64encode(input('Введите пароль для доступа ServerQuery: ').encode('utf-8'));
	sglist = input('Введите sgid всех корпораций, разделяя пробелами: ').encode('utf-8');
	inputfile = open(route+'inputfile.ini', 'wb');
	inputfile.write(hostip + b'|' + cod_passwd + b'|' + sglist);
	inputfile.close();
	input('Все данные сохранены. Спасибо.').encode('utf-8');
# end define

def loading():
	"""Ежесекундное обновление input файлов"""
	global inputfile, inputclan, lst, sglist_m
	while True:
		time.sleep(5)
		inputfile = (open(route+"inputfile.ini", 'r')).read()
		inputclan = (open(route+"inputclan.ini", 'r')).read()
		inputmsg = (open(route+"inputmsg.ini", 'r')).read()
		lst = inputfile.split("|")
		hostip =lst[0]
		cod_passwd =lst[1]
		passwd = (base64.b64decode(cod_passwd)).decode('utf-8')
		sglist_m =lst[2].split(" ") # Получили массив груп, которые нужно проверить
# end define

def logging():
	"""Ежесекундное обновление логов"""
	global logs, in_log_cycle
	while True:
		time.sleep(3)
		while True:
			if in_log_cycle == 0:
				in_log_cycle = 1
				logs_f = open(route+"logs.txt", 'a')
				logs_f.write(logs)
				logs_f.close()
				logs = ''
				in_log_cycle = 0
				break
			else:
				time.sleep(0.1)
# end define

def in_log(text):
	"""Запись логов"""
	global logs, in_log_cycle
	text = time.strftime(init_time) + 'Information. ' + text
	while True:
		if in_log_cycle == 0:
			in_log_cycle = 1
			print(text)
			logs = logs + text + '\n'
			in_log_cycle = 0
			break
		else:
			time.sleep(0.1)
# end define

def in_debug(text):
	"""Запись подробных логов Debag"""
	text = time.strftime(init_time) + 'Debag. ' + text
	global logs, in_log_cycle
	if debug == 1:
		global logs, in_log_cycle
		while True:
			if in_log_cycle == 0:
				in_log_cycle = 1
				print(text)
				logs = logs + text + '\n'
				in_log_cycle = 0
				break
			else:
				time.sleep(0.1)
# end define

def in_error(text):
	"""Запись логов"""
	global logs, in_log_cycle
	text = time.strftime(init_time) + 'Error. ' + text
	while True:
		if in_log_cycle == 0:
			in_log_cycle = 1
			print(text)
			MessageToTelegram('Server', text)
			logs = logs + text + '\n'
			in_log_cycle = 0
			break
		else:
			time.sleep(0.1)
# end define

def in_msg(user_online_id, text):
	"""Отправка сообщение пользователю TS"""
	text = text.replace(' ', '\s')
	in_tn1_comand('sendtextmessage targetmode=1 target=' + user_online_id + ' msg=' + text)
# end define

def good_nickname(user_nikname, user_database_id='no_data'):
	"""Выделяем никнейм и проверяем на нормальность"""
	# Выделяем ник
	brackets_cycle = 0
	while brackets_cycle < len(brackets):
		if brackets[brackets_cycle] in user_nikname:
			clients_nik_find_subname = user_nikname.find(brackets[brackets_cycle])
			user_nikname = user_nikname[:clients_nik_find_subname]
		brackets_cycle = brackets_cycle + 1
	# Проверяем на нормальность
	user_nikname_0 = list(user_nikname)
	nickname_cycle = 0
	while nickname_cycle < len(user_nikname_0):
		c_gn_1 = user_nikname_0[nickname_cycle]
		if c_gn_1 not in goodsign_s:
			in_log('Обнаружен неизвестный знак в никнейме №"' + user_database_id + '".')
			user_nikname = 'empty_result'
			break
		nickname_cycle = nickname_cycle + 1
	return user_nikname
# end define

def in_tn1_comand(comand):
	"""Вводим определенную команду в tn1"""
	global in_tn1_cycle
	while True:
		if server_connection_tn1 == 1:
			if in_tn1_cycle == 0:
				in_tn1_cycle = 1
				tn1.write((comand + '\n').encode('utf-8'))
				in_tn1_cycle = 0
				break
			else:
				time.sleep(0.1)
		else:
			time.sleep(0.1)
# end define

def in_tn2_comand(comand):
	"""Вводим определенную команду в tn2"""
	global in_tn2_cycle, tn2, server_connection_tn2
	while True:
		if server_connection_tn2 == 1:
			if in_tn2_cycle == 0:
				in_tn2_cycle = 1
				tn2.write((comand + '\n').encode('utf-8'))
				in_tn2_cycle = 0
				break
			else:
				time.sleep(0.1)
		else:
			time.sleep(0.1)
# end define

def tn2_connect():
	"""Создание второго тунеля для server query команд"""
	global tn2, server_connection_tn2
	in_debug('run_tn2_connect')
	while True:
		if server_connection_tn1 == 1:
			tn2=telnetlib.Telnet(host=hostip, port=10011, timeout=2)
			time.sleep(ping)
			buffer = (tn2.read_very_eager()).decode('utf-8')
			if 'Welcome to the TeamSpeak 3 ServerQuery interface' in buffer:
				server_connection_tn2 = 1
				in_tn2_comand('login serveradmin '+ passwd)
				time.sleep(ping)
				buffer = (tn2.read_very_eager()).decode('utf-8')
				if 'error id=0 msg=ok' in buffer:
					in_tn2_comand('use sid=1')
					time.sleep(ping)
					buffer = (tn2.read_very_eager()).decode('utf-8')
					if 'error id=0 msg=ok' in buffer:
						in_tn2_comand('clientupdate client_nickname=' + bot_name + '_info')
						time.sleep(ping)
						buffer = (tn2.read_very_eager()).decode('utf-8')
						in_debug('tn2_connect_info resalt=ok')
						while True:
							time.sleep(30)
							in_tn2_comand('version')
							time.sleep(0.1)
							buffer = (tn2.read_very_eager()).decode('utf-8')
		else:
			time.sleep(1)
# end define

def star_conflict_detected(user_nikname, user_servergroups_m, user_online_id, user_database_id):
	"""Проверка пользователя Star Conflict"""
	in_debug('run_star_conflict_detected')
	star_conflict_detected_cycle = 0
	while star_conflict_detected_cycle < len(user_servergroups_m):
		in_debug('star_conflict_detected_cycle_info user_servergroups_m=' + str(user_servergroups_m[star_conflict_detected_cycle]) + ' sglist_m=' + str(sglist_m))
		if user_servergroups_m[star_conflict_detected_cycle] in sglist_m:
			# Проверка пользователя
			in_debug('run_user_verification_for ' + user_nikname)
			uv_code, user_clanname_across_sc_api = user_verification_across_sc_api(user_nikname)
			# Начинаем сравнивать user_clanname и input_clanname
			if user_clanname_across_sc_api in inputclan:
				clan_sgid = inputclan[:inputclan.find(user_clanname_across_sc_api)]
				clan_sgid = clan_sgid[clan_sgid.rfind('sgid') + len('sgid'):clan_sgid.rfind('=')]
				in_debug('star_conflict_detected_info nikname=' + user_nikname + ' clan_sgid=' + clan_sgid)
				if clan_sgid in user_servergroups_m:
					uv_code = 1 # Приветствие пользователя
				else:
					uv_code = 2 # Корпорация не верна
			elif uv_code == 3:
				in_debug('error_star_conflict_detected ' + 'Пользователь не состоит в корпорации')
			else:
				in_debug('error_star_conflict_detected ' + 'Данная корпорация не найдена в inputclan')
				uv_code = 2
			break
		else:
			uv_code = 9 # unknown_error
		star_conflict_detected_cycle = star_conflict_detected_cycle + 1
	# Реакция на любой код uv_code
	if uv_code == 1: # Приветствие пользователя
		in_msg(user_online_id, 'Привет ' + user_nikname + ' :)')
		return_to_normal(uv_code, user_database_id, user_servergroups_m)
		offline_messenger_output(user_nikname, user_online_id)
		RandWise(user_online_id)
	elif uv_code == 2: # Корпорация не верна
		in_msg(user_online_id, 'Привет ' + user_nikname + '. К твоему сожалению твоя информация о корпорации не верна. ' + 'Твоя настоящая корпорация [b]' + user_clanname_across_sc_api + '[/b] :(')
		time.sleep(ping)
		in_tn1_comand('servergroupaddclient sgid=' + sgid_not_hold_corporation + ' cldbid=' + user_database_id)
	elif uv_code == 3: # Не состоит в корпорации
		in_msg(user_online_id, 'Привет ' + user_nikname + '. К твоему сожалению твоя информация о корпорации не верна. ' + 'В данный момент [b]ты не состоишь в какой либо корпорации[/b] :(')
		time.sleep(ping)
		in_tn1_comand('servergroupaddclient sgid=' + sgid_no_corporation + ' cldbid=' + user_database_id)
	elif uv_code == 4: # Никнейм не найден
		in_msg(user_online_id, 'Привет ' + user_nikname + '. К твоему сожалению твой [b]никнейм не найден[/b] в базе данных Star Conflict. Скорее всего ты просто неправильно написал свой никнейм :(')
		time.sleep(ping)
		in_tn1_comand('servergroupaddclient sgid=' + sgid_wrong_nickname + ' cldbid=' + user_database_id)
	elif uv_code == 5: # Не правильный никнейм
		in_msg(user_online_id, 'Привет. К твоему сожалению твой никней не правильный. Убедись, что он состоит только из [b]цифр и букв латинского алфавита[/b], например "Andrey1989" :(')
		time.sleep(ping)
		in_tn1_comand('servergroupaddclient sgid=' + sgid_wrong_nickname + ' cldbid=' + user_database_id)
# end define

def user_verification_across_sc_api(user_nikname):
	"""Проверка пользователя по базе данных Star Conflict"""
	url = 'http://gmt.star-conflict.com/pubapi/v1/userinfo.php?nickname='
	user_clanname_across_sc_api = 'no_clan'
	webform = ''
	uv_code = 9 # unknown_error
	if 'empty_result' in user_nikname:
		uv_code = 5 # Не правильный никнейм
	else:
		in_debug('run_user_verification_across_sc_api')
		try:
			webform = (urllib.request.urlopen(url + user_nikname).read(1000)).decode('utf-8')
		except:
			in_debug('Warning! SC API block with me!!!')
		if 'Invalid username/nickname' in webform:
			uv_code = 4 # Никнейм не найден
		elif '"result":"ok"' in webform and '"clan"' not in webform:
			uv_code = 3 # Не состоит в корпорации
		elif '"clan"' in webform:
			user_clanname_across_sc_api = webform[webform.find('"clan":{"name"') + len('"clan":{"name":"'):]
			user_clanname_across_sc_api = user_clanname_across_sc_api[:user_clanname_across_sc_api.find('",')]
			uv_code = 0 # Все норм
		else:
			in_debug('error_user_verification_across_sc_api unknown_error')
	in_debug('user_verification_across_sc_api_info nikname=' + user_nikname + ' uv_code=' + str(uv_code) + ' clanname=' + user_clanname_across_sc_api)
	return uv_code, user_clanname_across_sc_api
# end define

def return_to_normal(uv_code, user_database_id, user_servergroups_m):
	"""Снимаем предупреждение, если все в порядке"""
	if uv_code == 1:
		if sgid_not_hold_corporation in user_servergroups_m:
			in_tn1_comand('servergroupdelclient sgid=' + sgid_not_hold_corporation + ' cldbid=' + user_database_id)
		if sgid_no_corporation in user_servergroups_m:
			in_tn1_comand('servergroupdelclient sgid=' + sgid_no_corporation + ' cldbid=' + user_database_id)
		if sgid_wrong_nickname in user_servergroups_m:
			in_tn1_comand('servergroupdelclient sgid=' + sgid_wrong_nickname + ' cldbid=' + user_database_id)
# end define

def rights_checking(user_nikname, user_database_id, user_servergroups_m):
	"""Проверка прав пользователя - есть ли группа корпорации, если есть права пилота"""
	in_debug('run_rights_checking')
	in_debug('rights_checking_info sgid_pilot=' + sgid_pilot + ' user_servergroups_m=' + str(user_servergroups_m))
	if sgid_pilot in user_servergroups_m:
		inputclan_m = inputclan.split(';')
		rc_code = 0
		for items in inputclan_m:
			items = items[items.find('sgid')+len('sgid'):items.find('=')]
			in_debug('rights_checking_cycle_info items=' + items + ' inputclan_m=' + str(inputclan_m))
			if items in user_servergroups_m:
				rc_code = 1
				break
		if rc_code == 0:
			uv_code, user_clanname_across_sc_api = user_verification_across_sc_api(user_nikname)
			if user_clanname_across_sc_api in inputclan:
				sgid_clan = inputclan[:inputclan.find(user_clanname_across_sc_api)]
				sgid_clan = sgid_clan[sgid_clan.rfind('sgid')+len('sgid'):]
				in_tn1_comand('servergroupaddclient sgid=' + sgid_clan + ' cldbid=' + user_database_id)
			else:
				in_debug('rights_checking_error Корпорация ' + user_clanname_across_sc_api + ' не найдена в inputclan')
		in_debug('rights_checking_info rc_code=' + str(rc_code))

def msg_adaptation(user_incoming_messages_info):
	"""Обрабатываем входящие команды"""
	in_debug('run_working_with_incoming_messages')
	incoming_messages_user_online_id = user_incoming_messages_info[user_incoming_messages_info.find('invokerid=')+len('invokerid='):]
	incoming_messages_user_online_id = incoming_messages_user_online_id[:incoming_messages_user_online_id.find(' ')]
	incoming_messages_user_global_id = user_incoming_messages_info[user_incoming_messages_info.find('invokeruid=')+len('invokeruid='):]
	incoming_messages_user_global_id = incoming_messages_user_global_id[:incoming_messages_user_global_id.find('\n')]
	incoming_messages_user_nikname = user_incoming_messages_info[user_incoming_messages_info.find('invokername=')+len('invokername='):]
	incoming_messages_user_nikname = incoming_messages_user_nikname[:incoming_messages_user_nikname.find(' ')]
	incoming_messages_msg = user_incoming_messages_info[user_incoming_messages_info.find('msg=')+len('msg='):]
	incoming_messages_msg = incoming_messages_msg[:incoming_messages_msg.find(' ')]
	response_msg = ''
	if 'server' not in incoming_messages_user_global_id:
		in_debug('working_with_incoming_messages_info online_id=' + incoming_messages_user_online_id + ' msg=' + incoming_messages_msg + ' globalid=' + incoming_messages_user_global_id)
		in_log('Обработка входящего сообщения от ' + incoming_messages_user_nikname)
		if '/' in incoming_messages_msg[0:1]:
			response_msg = response_msg + ' ' + 'Запрос успешно принят.'
		elif '!' in incoming_messages_msg[0:1]:
			response_msg = response_msg + ' ' + MessageToTelegram(incoming_messages_user_nikname, incoming_messages_msg)
		elif '#' in incoming_messages_msg[0:1]:
			offline_messenger_input(incoming_messages_user_online_id, incoming_messages_user_global_id, incoming_messages_user_nikname, incoming_messages_msg)
		elif 'URL=client:' in incoming_messages_msg:
			user_nikname = incoming_messages_msg[incoming_messages_msg.find(']') + len(']'):]
			user_nikname = user_nikname[:user_nikname.find('[')]
			user_nikname = good_nickname(user_nikname, incoming_messages_user_global_id)
			in_debug('run_working_with_URL_response_for ' + user_nikname)
			uid, karma, effRating, prestigeBonus, gamePlayed, gameWin, totalAssists, totalBattleTime, totalDeath, totalDmgDone, totalHealingDone, totalKill, totalVpDmgDone, clanname, clantag, sc_code = sc_api(user_nikname)
			if sc_code == 0:
				response_msg = response_msg + ' ' + 'Результат по запросу: nikName:[b]' + user_nikname + '[/b] uid:[b]' + uid + '[/b] karma:[b]' + karma + '[/b] effRating:[b]' + effRating + '[/b] prestigeBonus:[b]' + prestigeBonus + '[/b] gamePlayed:[b]' + gamePlayed + '[/b] gameWin:[b]' + gameWin + '[/b] totalAssists:[b]' + totalAssists + '[/b] totalBattleTime:[b]' + totalBattleTime + '[/b] totalDeath:[b]' + totalDeath + '[/b] totalDmgDone:[b]' + totalDmgDone + '[/b] totalKill:[b]' + totalKill + '[/b] totalVpDmgDone:[b]' + totalVpDmgDone + '[/b] clan:[b]' + clanname + ' [' + clantag + '][/b]'
			if sc_code == 4:
				response_msg = response_msg + ' ' + 'Неверный никнейм. Данный никнейм не найден в базе данных игры Star Conflict'
				
			#response_msg = response_msg + ' ' + 
		else:
			response_msg = response_msg + ' ' + 'Моя нейронная сеть еще не дописана. Поэтому в данный момент я не смогу тебе ответить :( Но ты можешь связаться с главным администратором сервера, для этого напиши мне сообщение, начав с восклицательного знака, например: "!Тут один тип хочет пожертвовать на наш проект пару биткойнов. Срочно дуй сюда!!!"'
		in_msg(incoming_messages_user_online_id, response_msg)
# end define

def MessageToTelegram(clientNameFromMsg, inputText):
	"""Отправка сообщения в Телеграм"""
	in_debug('run_MessageToTelegram')
	clientNameToMsg = 'Igroman787'
	clientDbidFromMsg = '0'
	clientNameFromMsg_old = clientNameFromMsg
	clientNameFromMsg = good_nickname(clientNameFromMsg)
	
	# Узнать dbid отправителя
	in_tn2_comand('clientlist')
	time.sleep(0.1)
	buffer = (tn2.read_very_eager()).decode('utf-8')
	clientlist_m = buffer.split('|')
	serchText = 'client_nickname=' + clientNameFromMsg_old
	for item in clientlist_m:
		if serchText in item:
			clientDbidFromMsg = item[item.find('client_database_id=') + len('client_database_id='):]
			clientDbidFromMsg = clientDbidFromMsg[:clientDbidFromMsg.find(' ')]
			break
	if clientDbidFromMsg == '0':
		return 'Error SB748R. Critical error.'
	if clientNameFromMsg == 'empty_result':
		clientNameFromMsg = clientNameFromMsg_old
	msgText = inputText[1:]
	msgText = msgText.replace('\s', ' ')
	sendText = '<clientNameFromMsg>' + clientNameFromMsg + '</clientNameFromMsg>' + '<msgText>' + msgText + '</msgText>' + '<clientDbidFromMsg>' + clientDbidFromMsg + '</clientDbidFromMsg>' + '<clientNameToMsg>' + clientNameToMsg + '</clientNameToMsg>'
	outputText = InTelegramService('<sendText>' + sendText + '</sendText>')
	return outputText
#end define

def InTelegramService(inputText):
	"""Отправка данных службе отправки сообщений Telegram"""
	in_debug('run_InTelegramService')
	try:
		sock = socket.socket()
		host = 'localhost'
		outputLocalPort = 3080
		sock.connect((host, outputLocalPort)) # Открываем соединение
		sock.send(inputText.encode()) # Отправляем данные
		data = sock.recv(4096) # Получаем данные
		sock.close()
		outputText = data.decode()
		outputText = Parsing(outputText, '<result>', '</result>')
	except:
		outputText = 'Error SF49N9. Служба доставки сообщений Telegram не отвечает.'
	return outputText
#end define

def Parsing(inputText, startScan, endScan):
	text_0 = inputText[inputText.find(startScan) + len(startScan):]
	outputText = text_0[:text_0.find(endScan)]
	return outputText
#end define

def InputHostTeamSpeakService():
	"""Служба приема сообщений с последующей трансляйие в TeamSpeak"""
	in_debug('run_InputHostTeamSpeakService')
	sock = socket.socket()
	host = 'localhost'
	inputLocalPort = 3081
	sock.bind((host, inputLocalPort)) # Создаем входящее соединение
	sock.listen(1) # Устанавливаем максимальное количество одновременных соединений
	while True:
		conn, addr = sock.accept()
		in_debug('Есть входящее соединение от LocalhostTelegramService: ' + str(addr))
		try:
			LocalhostTeamSpeakServiceConnect(conn)
		except ConnectionResetError:
			in_debug('Клиент принудительно разорвал соединение (LocalhostTelegramService): ' + str(addr))
#end define

def LocalhostTeamSpeakServiceConnect(conn):
	"""обработка входящего соединения localhost telegram service"""
	in_debug('run_LocalhostTeamSpeakServiceConnect')
	while True:
		data = conn.recv(4096) # Получаем данные
		in_debug('get packet (LocalhostTeamSpeakServiceConnect) ' + str(len(data)))
		if len(data) < 1:
			return
		try:
			inputText = data.decode('UTF-8')
		except UnicodeDecodeError:
			in_debug("Ошибка. Пакет не является текстовым (LocalhostTeamSpeakServiceConnect)")
			return
		inputMode = Parsing(inputText, '<mode>', '</mode>')
		in_debug('Получаем данные (LocalhostTeamSpeakServiceConnect): ' + inputText)
		if inputMode == 'msg':
			outputText = MsgFromTelegramToTeamSpeak(inputText)
		elif inputMode == 'request':
			outputText = RequestFromTelegramToTeamSpeak(inputText)
		else:
			outputText = 'Error G141FS. Mod wrong.'
		in_debug('Отправляем ответ (LocalhostTeamSpeakServiceConnect): ' + outputText)
		outputText = '<result>' + outputText + '</result>'
		conn.send(outputText.encode())
#end define

def MsgFromTelegramToTeamSpeak(inputText):
	"""Отправка входящего сообщения клиенту TeamSpeak"""
	in_debug('run_MsgFromTelegramToTeamSpeak')
	msgClientOnlineId = '0'
	
	msgClientDbid = Parsing(inputText, '<msgClientDbid>', '</msgClientDbid>')
	msgText = Parsing(inputText, '<msgText>', '</msgText>')
	clientNameFromMsg = Parsing(inputText, '<clientNameFromMsg>', '</clientNameFromMsg>')
	
	# Узнать msgClientName и msgClientOnlineId
	in_tn2_comand('clientlist')
	time.sleep(0.1)
	buffer = (tn2.read_very_eager()).decode('utf-8')
	clientlist_m = buffer.split('|')
	serchText = 'client_database_id=' + msgClientDbid + ' '
	for item in clientlist_m:
		if serchText in item:
			msgClientName = item[item.find('client_nickname=') + len('client_nickname='):]
			msgClientName = msgClientName[:msgClientName.find(' ')]
			msgClientOnlineId = item[item.find('clid=') + len('clid='):]
			msgClientOnlineId = msgClientOnlineId[:msgClientOnlineId.find(' ')]
			break
	if msgClientOnlineId == '0':
		response_msg = clientNameFromMsg + ': ' + msgText
		offline_messenger_input('0', '0', 'FromTelegram', response_msg)
		outputText = 'Отправка оффлайн сообщения.' + '\n' + '[' + msgClientDbid + '] Вы >> ' + msgClientName + ': ' + msgText
	else:
		response_msg = clientNameFromMsg + ': ' + msgText
		in_msg(msgClientOnlineId, response_msg)
		outputText = '[' + msgClientDbid + '] Вы >> ' + msgClientName + ': ' + msgText
	return outputText
#end define

def RequestFromTelegramToTeamSpeak(inputText):
	"""Выполнение запроса к серверу TeamSpeak"""
	in_debug('run_RequestFromTelegramToTeamSpeak')
	tsCmd = Parsing(inputText, '<tsCmd>', '</tsCmd>')
	in_tn2_comand(tsCmd)
	time.sleep(0.1)
	outputText = (tn2.read_very_eager()).decode('utf-8')
	return outputText
#end define

def sc_api(user_nikname):
	"""Пробиваем по базе данных SC пользователя и выдаем данные на русском языке"""
	url = 'http://gmt.star-conflict.com/pubapi/v1/userinfo.php?nickname='
	webform = (urllib.request.urlopen(url + user_nikname).read(1000)).decode('utf-8')
	if 'Invalid username/nickname' in webform:
		sc_code = 4 # Никнейм не найден
		uid = karma = effRating = prestigeBonus = gamePlayed = gameWin = totalAssists = totalBattleTime = totalDeath =totalDmgDone = totalHealingDone = totalKill = totalVpDmgDone = clanname = clantag = 'empty_result'
	elif '"result":"ok"' in webform:
		# Начинаем подсчеты
		sc_code = 0 # Все норм
		uid = webform[webform.find('"uid":') + len('"uid":'):]
		uid = uid[:uid.find(',')]
		if webform.find('"uid":') < 0:
			uid = 'no_data'
		karma = webform[webform.find('"karma":') + len('"karma":'):]
		karma = karma[:karma.find(',')]
		if webform.find('"karma":') < 0:
			karma = 'no_data'
		effRating = webform[webform.find('"effRating":') + len('"effRating":'):]
		effRating = effRating[:effRating.find(',')]
		if webform.find('"effRating":') < 0:
			effRating = 'no_data'
		prestigeBonus = webform[webform.find('"prestigeBonus":') + len('"prestigeBonus":'):]
		prestigeBonus = prestigeBonus[:prestigeBonus.find(',')]
		if webform.find('"prestigeBonus":') < 0:
			prestigeBonus = 'no_data'
		gamePlayed = webform[webform.find('"gamePlayed":') + len('"gamePlayed":'):]
		gamePlayed = gamePlayed[:gamePlayed.find(',')]
		if webform.find('"gamePlayed":') < 0:
			gamePlayed = 'no_data'
		gameWin = webform[webform.find('"gameWin":') + len('"gameWin":'):]
		gameWin = gameWin[:gameWin.find(',')]
		if webform.find('"gameWin":') < 0:
			gameWin = 'no_data'
		totalAssists = webform[webform.find('"totalAssists":') + len('"totalAssists":'):]
		totalAssists = totalAssists[:totalAssists.find(',')]
		if webform.find('"totalAssists":') < 0:
			totalAssists = 'no_data'
		totalBattleTime = webform[webform.find('"totalBattleTime":') + len('"totalBattleTime":'):]
		totalBattleTime = totalBattleTime[:totalBattleTime.find(',')]
		if webform.find('"totalBattleTime":') < 0:
			totalBattleTime = 'no_data'
		totalDeath = webform[webform.find('"totalDeath":') + len('"totalDeath":'):]
		totalDeath = totalDeath[:totalDeath.find(',')]
		if webform.find('"totalDeath":') < 0:
			totalDeath = 'no_data'
		totalDmgDone = webform[webform.find('"totalDmgDone":') + len('"totalDmgDone":'):]
		totalDmgDone = totalDmgDone[:totalDmgDone.find(',')]
		if webform.find('"totalDmgDone":') < 0:
			totalDmgDone = 'no_data'
		totalHealingDone = webform[webform.find('"totalHealingDone":') + len('"totalHealingDone":'):]
		totalHealingDone = totalHealingDone[:totalHealingDone.find(',')]
		if webform.find('"totalHealingDone":') < 0:
			totalHealingDone = 'no_data'
		totalKill = webform[webform.find('"totalKill":') + len('"totalKill":'):]
		totalKill = totalKill[:totalKill.find(',')]
		if webform.find('"totalKill":') < 0:
			totalKill = 'no_data'
		totalVpDmgDone = webform[webform.find('"totalVpDmgDone":') + len('"totalVpDmgDone":'):]
		totalVpDmgDone = totalVpDmgDone[:totalVpDmgDone.find(',')]
		totalVpDmgDone = totalVpDmgDone[:totalVpDmgDone.find('}')]
		if webform.find('"totalVpDmgDone":') < 0:
			totalVpDmgDone = 'no_data'
		clanname = webform[webform.find('"clan":{"name":"') + len('"clan":{"name":"'):]
		clanname = clanname[:clanname.find('",')]
		if webform.find('"clan":{"name":"') < 0:
			clanname = 'Не состоит в корпорации'
		clantag = webform[webform.find('"tag":"') + len('"tag":"'):]
		clantag = clantag[:clantag.find('"}}}')]
		if webform.find('"tag":"') < 0:
			clantag = ''
	else:
		sc_code = 9 # unknown_error
		uid = karma = effRating = prestigeBonus = gamePlayed = gameWin = totalAssists = totalBattleTime = totalDeath =totalDmgDone = totalHealingDone = totalKill = totalVpDmgDone = clanname = clantag = 'empty_result'
	in_debug('sc_api_info uid=' + uid + ' karma=' + karma + ' effRating=' + effRating + ' prestigeBonus=' + prestigeBonus + ' gamePlayed=' + gamePlayed + ' gameWin=' + gameWin + ' totalAssists=' + totalAssists + ' totalBattleTime=' + totalBattleTime + ' totalDeath' + totalDeath + ' totalDmgDone=' + totalDmgDone + ' totalHealingDone=' + totalHealingDone + ' totalKill=' + totalKill + ' totalVpDmgDone=' + totalVpDmgDone + ' clanname=' + clanname + ' clantag=' + clantag)
	return uid, karma, effRating, prestigeBonus, gamePlayed, gameWin, totalAssists, totalBattleTime, totalDeath, totalDmgDone, totalHealingDone, totalKill, totalVpDmgDone, clanname, clantag, sc_code
# end define

def world_of_tanks_detected(user_nikname, user_servergroups_m, user_online_id, user_database_id):
	"""Обнаружение пользователя World of Tanks"""
	in_debug('run_world_of_tanks_detected')
	world_of_tanks_detected_cycle = 0
	while world_of_tanks_detected_cycle < len(user_servergroups_m):
		in_debug('world_of_tanks_detected_cycle_info ')
		# А вот тут уже нужно подумать
	
	
	
	
	
	
	
# end define

def offline_messenger_input(incoming_messages_user_online_id, incoming_messages_user_global_id, incoming_messages_user_nikname, incoming_messages_msg):
	"""Прием офлайн сообщения"""
	in_debug('run_offline_messenger_input')
	client_name_s = incoming_messages_msg[incoming_messages_msg.find('#')+len('#'):]
	client_name_s = client_name_s[:client_name_s.find('\s')]
	client_name_s_m = client_name_s.split(',')
	offline_msg = incoming_messages_msg[incoming_messages_msg.find('#')+len(client_name_s)+len('#')+len('\s'):]
	offline_msg = offline_msg.replace(';','.')
	offline_msg = offline_msg.replace('#','№')
	offline_msg = offline_msg.replace('|-|','-')
	offline_msg = offline_msg.replace('|=|','=')
	for client_name in client_name_s_m:
		if len(client_name) > 2 and len(offline_msg) > 0:
			incoming_messages_user_nikname = good_nickname(incoming_messages_user_nikname)
			if 'empty_result' in incoming_messages_user_nikname:
				break
			url = 'http://gmt.star-conflict.com/pubapi/v1/userinfo.php?nickname='
			webform = (urllib.request.urlopen(url + client_name).read(1000)).decode('utf-8')
			if '"result":"ok","code":0' not in webform:
				break
			user_url = '[URL=client://0/' + incoming_messages_user_global_id + '=~' + incoming_messages_user_nikname + ']' + incoming_messages_user_nikname + '[/URL]'
			in_debug('offline_messenger_input_info '+'#'+client_name+'|-|'+offline_msg+'|=|'+incoming_messages_user_nikname+';')
			offline_msg_file = open(route+"offline_msg.txt", 'a')
			offline_msg_file.write('#'+client_name+'|-|'+offline_msg+'|=|'+user_url+';'+'\n')
			offline_msg_file.close()
			in_msg(incoming_messages_user_online_id, 'Ваше сообщение "' + offline_msg + '" отправлено пользователю "' + client_name + '". Он получит его при следующем подключении')
# end define

def offline_messenger_output(user_nikname, user_online_id):
	"""Вывод офлайн сообщения"""
	in_debug('run_offline_messenger_output')
	offline_msg_file = (open(route+"offline_msg.txt", 'r')).read()
	offline_msg_text = offline_msg_file
	while True:
		if '#'+user_nikname in offline_msg_text:
			time.sleep(1)
			for_client = offline_msg_text[offline_msg_text.find('#'+user_nikname):]
			for_client = for_client[:for_client.find('\n')]
			for_client_name = for_client[len('#'):for_client.find('|-|')]
			for_client_msg = for_client[for_client.find('|-|')+len('|-|'):for_client.find('|=|')]
			for_client_from = for_client[for_client.find('|=|')+len('|=|'):for_client.find(';')]
			in_msg(user_online_id, 'Вам офлайн сообщение от ' + for_client_from + ': [b][COLOR=#005500]' + for_client_msg + '[/COLOR][/b]')
			offline_msg_text_01 = offline_msg_text[:offline_msg_text.find(for_client)]
			offline_msg_text_02 = offline_msg_text[offline_msg_text.find(for_client)+len(for_client)+len('\n'):]
			offline_msg_text = offline_msg_text_01 + offline_msg_text_02
			offline_msg_file = open(route+"offline_msg.txt", 'w')
			offline_msg_file.write(offline_msg_text)
			offline_msg_file.close()
			in_debug('offline_messenger_output_info '+str(len(offline_msg_text)))
		else:
			break
# end define

def RandWise(user_online_id):
	"""Генератор мудрости"""
	in_debug('run_RandWise')
	time.sleep(3)
	url = "http://randstuff.ru/saying/"
	try:
		webform = (urllib.request.urlopen(url).read())
		webform = webform.decode('utf-8')
		
		a1 = webform.find('<h1 id="caption" data-txt="Мудрость:">') + len('<h1 id="caption" data-txt="Мудрость:">')
		text_01 = webform[a1:]
		a2 = text_01.find('<table class="text">') + len('<table class="text">')
		text_02 = text_01[a2:]
		a3 = text_02.find('</table>') + len('</table>')
		text_03 = text_02[:a3]
		
		b1 = text_03.find('<tr><td>') + len('<tr><td>')
		b2 = text_03.find('<span class="author">')
		generalText = text_03[b1:b2]
		b3 = text_03.find('<span class="author">') + len('<span class="author">')
		b4 = text_03.find('</span></td></tr></table>')
		authorText = text_03[b3:b4]
		
		outputText = 'Мудрость: ' + generalText + ' ' + authorText
	except:
		outputText = "Error: RandWise is broken."
	
	in_msg(user_online_id, outputText)
#end define








# ---------------------------------------------------------------------------------------------------------------------------------------------- #
# Начало бота!!!
# ---------------------------------------------------------------------------------------------------------------------------------------------- #

# Определяем операционную систему
system_platform = sys.platform
if 'win' in system_platform:
	system_platform = 'Windows'
elif 'linux' in system_platform:
	system_platform = 'Linux'
else:
	print('Error! Система не опознана. Дальнешая работа программы невозможно.')
	input()
	exit()

# Укажим путь до нашего файла # Можно сделать более универсальным используя os.getcwd()
route = os.path.abspath('daemon.py')
route = route[:(route.find('daemon.py'))]

# Поищем конфигурационный файл
if os.path.exists(route+'inputfile.ini'):
	print('Information. Обнаружен конфигурационный файл. Ok.')
else:
	print('Видимо это первый запуск бота на данной машине.'+'\n'+'Сейчас мы установим конфигурационный фал.')
	launcher ()

# Загружаем необходимые переменные
url = 'http://gmt.star-conflict.com/pubapi/v1/userinfo.php?nickname='
brackets = '( ) [ ] { } \ | / - + _ = \s . ,'.split(' ')
goodsign_s = 'q w e r t y u i o p a s d f g h j k l z x c v b n m Q W E R T Y U I O P A S D F G H J K L Z X C V B N M 1 2 3 4 5 6 7 8 9 0 ! @ # $ % ^ & *'.split(" ")
init_time = '%d.%m.%Y, %H:%M:%S. '
init_bzs_time = '%H:%M'
server_connection_tn1 = 0
server_connection_tn2 = 0
in_tn1_cycle = 0
in_tn2_cycle = 0
in_log_cycle = 0
logs = ''
online_clid = ''

# Загружаем данные из файла
inputfile = (open(route+"inputfile.ini", 'r')).read()
inputclan = (open(route+"inputclan.ini", 'r')).read()
inputmsg = (open(route+"inputmsg.ini", 'r')).read()
lst = inputfile.split("|")
hostip =lst[0]
cod_passwd =lst[1]
passwd = (base64.b64decode(cod_passwd)).decode('utf-8')
sglist_m =lst[2].split(" ") # Получили массив груп, которые нужно проверить
in_log('===================================================')
in_log('Инициализирую запуск бота ' + bot_name + ' v' + bot_version)
in_log('Операционная система распознана как: ' + system_platform)
in_log('Все данные загружены.')


# Выполняем подключение к серверу
def daemon():
	global tn1, ping, server_connection_tn1
	#ping = discover_ip (hostip)
	ping = 1
	in_log('Найдено значение Ping до сервера '+hostip+'. Ping=' + str(ping))
	in_log('Приступаю к подключению к серверу.')
	tn1=telnetlib.Telnet(host=hostip, port=10011, timeout=2)
	time.sleep(ping)
	buffer = (tn1.read_very_eager()).decode('utf-8')
	if 'Welcome to the TeamSpeak 3 ServerQuery interface' in buffer:
		server_connection_tn1 = 1
		in_log('Подключение к серверу выполнено успешно.')
		in_tn1_comand('login serveradmin '+ passwd)
		time.sleep(ping)
		buffer = (tn1.read_very_eager()).decode('utf-8')
		if 'error id=0 msg=ok' in buffer:
			in_log('Вход в систему выполнен успешно.')
			in_tn1_comand('use sid=1')
			time.sleep(ping)
			buffer = (tn1.read_very_eager()).decode('utf-8')
			if 'error id=0 msg=ok' in buffer:
				in_tn1_comand('clientupdate client_nickname=' + bot_name)
				time.sleep(ping)
				buffer = (tn1.read_very_eager()).decode('utf-8')
				in_log('Присоединение к первому серверу выполено успешно.')
				# Тут начинается вся хуйня
				abc=0
				time.sleep(ping)
				in_tn1_comand('servernotifyregister event=textprivate')
				time.sleep(ping)
				in_tn1_comand('servernotifyregister event=server')
				time.sleep(ping)
				while True:
					time.sleep(0.1)
					buffer = (tn1.read_very_eager()).decode('utf-8')
					while 'notifycliententerview' in buffer:
						user_connection_info = buffer[buffer.find('notifycliententerview'):]
						user_connection_info = user_connection_info[:user_connection_info.find('\n')] # Информация о подключенном клиенте
						buffer = buffer[len(user_connection_info):]
						user_nikname = user_connection_info[user_connection_info.find('client_nickname='):]
						user_nikname = user_nikname[len('client_nickname='):user_nikname.find(' ')] # Никнейм пользователя
						in_debug('--- --- --- --- --- --- ---')
						in_debug('client_enter ' + user_nikname)
						in_log('Обнаружен клиент ' + user_nikname)
						user_database_id = user_connection_info[user_connection_info.find('client_database_id='):]
						user_database_id = user_database_id[len('client_database_id='):user_database_id.find(' ')] # dbid пользователя
						in_debug('client_info dbid=' + user_database_id)
						user_servergroups = user_connection_info[user_connection_info.find('client_servergroups='):]
						user_servergroups = user_servergroups[len('client_servergroups='):user_servergroups.find(' ')] # Группы сервера пользователя
						user_servergroups_m = user_servergroups.split(',') # Массив групп сервера пользователя
						in_debug('client_info servergroups=' + user_servergroups)
						user_online_id = user_connection_info[user_connection_info.find('clid='):]
						user_online_id = user_online_id[len('clid='):user_online_id.find(' ')] # online_id пользователя
						in_debug('client_info online_id=' + user_online_id)
						
						# Тут начинается проверка пользователя
						def user_adaptation(user_nikname, user_database_id, user_online_id, user_servergroups_m):
							"""Обработка вошедшего пользователя"""
							user_nikname = good_nickname(user_nikname, user_database_id) # Выделяем и проверяем никнейм
							rights_checking(user_nikname, user_database_id, user_servergroups_m)
							star_conflict_detected(user_nikname, user_servergroups_m, user_online_id, user_database_id)
						# end define
						t_user_adaptation = threading.Thread(target=user_adaptation(user_nikname, user_database_id, user_online_id, user_servergroups_m))
						t_user_adaptation.run()
						
						# Запускаем процесс проверки нового пользователя
						
						
						
						
						# Тут заканчивается проверка пользователя
					while 'notifytextmessage' in buffer:
						# Отвечаем на запрос
						user_incoming_messages_info = buffer[buffer.find('notifytextmessage'):]
						user_incoming_messages_info = user_incoming_messages_info[:user_incoming_messages_info.find('\n')]
						in_debug('detected_new_message ' + user_incoming_messages_info)
						buffer = buffer[buffer.find('notifytextmessage') + len(user_incoming_messages_info):]
						
						# Запускаем процесс обработки сообщения
						t_msg_adaptation = threading.Thread(target=msg_adaptation(user_incoming_messages_info))
						t_msg_adaptation.run()
						
						
					# Каждые 300 раз отправляем сообщение, что мы еще в сети
					if (not abc%300):
						in_tn1_comand('version')
					abc=abc+1
				# Тут заканчивается вся хуйня, надеюсь я осилю эту хуйню xD
			else:
				in_log('Не удалось подключиться к первому виртуальному серверу.')
		else:
			in_log('Неправильный пароль!')
	else:
		in_log('Сервер ' + hostip + ' не отвечает!')
# end daemon define



# Многопоточность
t1 = threading.Thread(target=daemon)
t2 = threading.Thread(target=tn2_connect)
t3 = threading.Thread(target=loading)
t4 = threading.Thread(target=logging)
t5 = threading.Thread(target=InputHostTeamSpeakService)

t1.start()
t2.start()
t3.start()
t4.start()
t5.start()

t1.join()
t2.join()
t3.join()
t4.join()
t5.join()
