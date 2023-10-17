import websocket
import _thread
from datetime import datetime
import json
from binance.client import Client
import time
import pickle
from ftplib import FTP
import os
import listetest
            
host = "..."
user = "..."
password = "..."

event_type="kline"
interval="1s"
numbersymbolsmin=0
numbersymbols=18
threshold=66
fee=0.001  #0.1% fee
budgetquant=1000

listchrono=[]   # liste des listsymbol
listalready=[]
listsymbol=[]	# liste de listes/symbols : 1 liste par symbol

listlock=_thread.allocate_lock()
list_lock_chrono=_thread.allocate_lock()
ftplock=_thread.allocate_lock()
filelock=_thread.allocate_lock()

def save_list(l):
	now = datetime.now()
	ttl="listsymbol_"+str(int(now.second%2))
	filelock.acquire()
	with open("tmpFile", 'wb') as f:
		pickle.dump(l, f)
		f.flush()
		os.fsync(f.fileno())
	os.replace("tmpFile",ttl)
	filelock.release()

def read_list(filpath):
    with open(filpath, 'rb') as fp:
        try:
            l = pickle.load(fp)
            #print(l)
        except:
            return 0
        return l

def create_list(lexcinfo):
	print("len(lexcinfo)",len(lexcinfo))
	global listsymbol
	try:
		for i in range(2):
			s="listsymbol_"+str(i)
			savedlistsymbol=read_list(s)
			if savedlistsymbol:break
	except:
		savedlistsymbol=0
	if savedlistsymbol:
		listsymbol=savedlistsymbol.copy()
		print("if savedlistsymbol")

def info_():
	lexcinfo=[]
	api_key = "..."
	api_secret = "..."
	client = Client(api_key, api_secret)
	exchange_info = client.get_exchange_info()
	linfo=[]
	i=0
	for s in exchange_info['symbols']:
		if s['symbol'].lower().endswith("usdt"):
			linfo.append(s['symbol'].lower())
			if i>=numbersymbolsmin: lexcinfo.append(s['symbol'].lower()+"@"+event_type+"_"+interval)
			if i>=(numbersymbols-1): break
			i+=1
	req_='{ "method": "SUBSCRIBE", "params": ' + str(lexcinfo).replace("'","\"") + ', "id": 1}'
	print("info_")
	create_list(lexcinfo.copy())  
	return req_
	
def alreadyin(tuplalready):
        for la in listalready:
            if la==tuple(tuplalready):
                return 1
        return 0

def ws_message (ws,message):
    m=json.loads(message)
    tuplalready=(m['e'],m['E'],m['s'])
    b9=alreadyin(tuplalready)
    if b9!=1:        
                listalready.append(tuplalready)
                if len(listalready)>numbersymbols*2:
                    del listalready[0]
                print(".")
                compute( m['e'],m['E'],m['s'],m['k']['t'],m['k']['T'],m['k']['s'], m['k']['i'],m['k']['f'],m['k']['L'],m['k']['o'],m['k']['c'],m['k']['h'],m['k']['l'],m['k']['v'],m['k']['n'],m['k']['x'],m['k']['q'],m['k']['V'],m['k']['Q'],m['k']['B'])
                #_thread.start_new_thread(compute,( m['e'],m['E'],m['s'],m['k']['t'],m['k']['T'],m['k']['s'], m['k']['i'],m['k']['f'],m['k']['L'],m['k']['o'],m['k']['c'],m['k']['h'],m['k']['l'],m['k']['v'],m['k']['n'],m['k']['x'],m['k']['q'],m['k']['V'],m['k']['Q'],m['k']['B'], ))
                _thread.start_new_thread(save_list,(listsymbol.copy(),))

def ws_open(ws):
	print(requete_)
	ws.send(requete_)

def ws_thread(*args):
	ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws", on_open = ws_open, on_message = ws_message)
	ws.run_forever()

def compute(e,E,s,kt,kT,ks,ki,kf,kL,ko,kc,kh,kl,kv,kn,kx,kq,kV,kQ,kB):
	open = float(ko)
	close = float(kc)
	high  = float(kh)
	low = float(kl)
	
	evenement=""
	
	initlist = [e,E,s,kt,kT,ks,ki,kf,kL,float(ko),float(kc),float(kh),float(kl),kv,kn,kx,kq,kV,kQ,kB]
	
	worklist = [e,E,s,kt,kT,ks,ki,kf,kL,float(ko),float(kc),float(kh),float(kl),kv,kn,kx,kq,kV,kQ,kB]
	
	for i in range(80):
		worklist.append(0)
	listlock.acquire()  # zone critique, peut-être à agrandir et supprimer worklist
	for l in reversed(listsymbol):
		if s in l:
			worklist=l.copy()
			#print("______",l)
			break
	listlock.release()
	#print (worklist)
	closeprev=worklist[10]
	sma7sprev=worklist[30]
	sma8sprev=worklist[31]
	sma9sprev=worklist[32]
	sma1hprev=worklist[33]
	sma2hprev=worklist[34]
	sma12hprev=worklist[35]
	sma24hprev=worklist[36]
	ranksma1h=worklist[37]
	ranksma12h=worklist[38]
	ranksma24h=worklist[39]
	rankcloseprev=worklist[40]
	breakoutprocess=worklist[41]
	breakoutcountdown=worklist[43]
	sma2high=worklist[50]
	
	if worklist[45] is not None : sma12prev=worklist[45]
	else : sma12prev=close
	if worklist[46] is not None : sma20prev=worklist[46]
	else : sma20prev=close
	if worklist[47] is not None : sma50prev=worklist[47]
	else : sma50prev=close
	if worklist[48] is not None : sma200prev=worklist[48]
	else : sma200prev=close
	
	if worklist[49] is not None : sma2prev=worklist[49]
	else : sma2prev=close

	if worklist[42] is not None : breakouthigh=worklist[42]
	else : breakouthigh=close
	if worklist[50] is not None : sma2highprev=worklist[50]
	else : sma2highprev=close

	if worklist[44] is not None : evenement=worklist[44]
	else : evenement=""
	if evenement=="breakout":evenement=""

    # sma
	sma7s=round((sma7sprev*6+close)/7,6)
	sma8s=round((sma8sprev*7+close)/8,6)
	sma9s=round((sma9sprev*8+close)/9,6)
	sma1h=round((sma1hprev*3599+close)/3600,6)            #3600
	sma2h=round((sma2hprev*7199+close)/7200,6)            #7200
	sma12h=round((sma12hprev*43199+close)/43200,6)        #43200
	sma24h=round((sma24hprev*86399+close)/86400,6)        #86400
	
	#print(sma12prev,sma20prev,sma50prev,sma200prev)
	sma12=round((sma12prev*11+close)/12,6)
	sma20=round((sma20prev*19+close)/20,6)
	sma50=round((sma50prev*49+close)/50,6)
	sma200=round((sma200prev*199+close)/200,6)

	sma2=round((sma2prev+close)/2,6)
	
    # breakout screener_______________________________________

	ev=0

	#print((sma12-sma20)*(sma12prev-sma20prev), (sma12>sma20) , (sma20<sma50) , (sma50<sma200))

	if (((sma12-sma20)*(sma12prev-sma20prev))<0) and (sma12>sma20) and (sma20<sma50) and (sma50<sma200) : 
		#evenement="1_0_0_sma12_cross_up_sma20"
		evenement="1_0_1_sma12_cross_up_sma20"
		print(evenement)
		breakouthigh=close

	if evenement=="1_0_1_sma12_cross_up_sma20":
		if (((sma20-sma50)*(sma20prev-sma50prev))<0) and (sma20>sma50) and (sma50<sma200) :
			#evenement="1_1_0_sma20_cross_up_sma50"
			evenement="1_1_1_sma20_cross_up_sma50"
			print(evenement)
			breakouthigh=close

	if evenement=="1_1_1_sma20_cross_up_sma50":
		if (((sma20-sma200)*(sma20prev-sma200prev))<0) and (sma20>sma200):
			evenement="1_2_0_sma20_cross_up_sma200"
			print(evenement)
			breakouthigh=close

	if evenement=="1_2_0_sma20_cross_up_sma200":
		if (((sma50-sma200)*(sma50prev-sma200prev))<0) and (sma50>sma200) and (sma20>sma50) and (sma50>sma200) : 
			#evenement="2_1_0_sma50_cross_up_sma200"
			evenement="2_2_0_sma50_cross_up_sma200"
			print(evenement)

	if evenement=="2_2_0_sma50_cross_up_sma200":
		if (((sma20-sma50)*(sma20prev-sma50prev))<0) and (sma20<sma50) and (sma50>sma200) :
			#evenement="3_1_0_sma20_cross_down_sma50"
			evenement="3_1_1_sma20_cross_down_sma50"
			print(evenement)

	if evenement=="3_1_1_sma20_cross_down_sma50":
		if (((sma20-sma50)*(sma20prev-sma50prev))<0) and (sma20>sma50) and  (sma50>sma200) :
			#evenement="3_2_0_sma20_cross_up_sma50"
			evenement="3_2_1_sma20_cross_up_sma50"
			print(evenement)
	
	# acheter
	if evenement == "3_2_1_sma20_cross_up_sma50":
		if close > breakouthigh:
			evenement="breakout"
			print(evenement)
			ev=1
				
	# sortir du breakout : 12 crossdown 50
	"""if (((sma12-sma50)*(sma12prev-sma50prev))<0) and (sma12<sma50):
		evenement="leave_breakout_12crossdown50"
		print(evenement)"""
		
	# déterminer prix achat = high
	if evenement!="" and evenement != "3_1_1_sma20_cross_down_sma50" and evenement != "3_2_1_sma20_cross_up_sma50":
		if close > breakouthigh :
			breakouthigh=close
			print(breakouthigh)

	sma2high=round((sma2highprev+breakouthigh)/2,6)

	"""# breakout_______________________________________________
	
	ranklist=[0,0,0,0]
	rankdict={}
	rankdict.update({0: close})                # worklist[40]
	rankdict.update({1: sma1h})                # worklist[37]
	rankdict.update({2: sma12h})               # worklist[38]
	rankdict.update({3: sma24h})               # worklist[39]
	rankdict_=dict(sorted(rankdict.items(), key=lambda item: float(item[1])))
	rr=0
	for r in rankdict_:
		#print(ranklist[r],int(rr))
		ranklist[r]=int(rr)
		rr+=1
	rankclose=ranklist[0]
	ranksma1h=ranklist[1]
	ranksma12h=ranklist[2]
	ranksma24h=ranklist[3]
	#print(rankclose,ranksma1h,ranksma12h,ranksma24h)

	if rankclose > rankcloseprev and rankclose >= 3:
		#print(s,"rankclose > rankcloseprev",rankclose,rankcloseprev)
		if breakoutprocess == 0 or breakoutcountdown <= 0 :
			#breakoutcountdown=60 	# compte à rebours
			breakouthigh=close
			breakoutprocess=1  	# chercher un high du close_price, 
		                		# booléen 1 du high, 2 de la descente et remontée
		
	if breakoutprocess==1 :
		#print(s,"breakoutprocess==1",breakoutcountdown)
		#breakoutcountdown-=1
		if close > closeprev :
			#print("breakouthigh=close",close,closeprev)
			breakouthigh=close
		else:
			breakoutprocess=2
			
	if breakoutprocess==2 :
		#print(s,"breakoutprocess==2",breakoutcountdown)
		#breakoutcountdown-=1
		if sma7s < sma7sprev and close > breakouthigh :
			#print("sma7s < sma7sprev and close > breakouthigh",close,breakouthigh)
			breakoutprocess=0
			evenement="breakout"
		elif breakoutcountdown<0 or rankclose<=1 : 
			breakoutprocess=0"""
			
	for i in range(20):
		worklist[i]=initlist[i]
	worklist[30]=sma7s
	worklist[31]=sma8s
	worklist[32]=sma9s
	worklist[33]=sma1h
	worklist[34]=sma2h
	worklist[35]=sma12h
	worklist[36]=sma24h
	"""worklist[37]=ranksma1h
	worklist[38]=ranksma12h
	worklist[39]=ranksma24h
	worklist[40]=rankclose"""
	worklist[41]=breakoutprocess
	worklist[42]=breakouthigh
	#print("breakouthigh out",worklist[42])
	worklist[43]=breakoutcountdown
	worklist[44]=evenement
	worklist[45]=sma12
	worklist[46]=sma20
	worklist[47]=sma50
	worklist[48]=sma200
	worklist[49]=sma2
	worklist[50]=sma2high
	
	
	# mise à jour de listsymbol
	listlock.acquire()
	if len(listsymbol)>7200:
		listsymbol.pop(0)
	#print("before",len(listsymbol))
	listsymbol.append(worklist.copy())
	#print("after",len(listsymbol))
	listlock.release()

	# send
	if evenement=="breakout":
		ev=0
		print(evenement)
		title=str(s)+"-"+str(E)+"-"+evenement+"-test"
		_thread.start_new_thread(sendlistcsv,(worklist.copy(),title))	# envoie de worklist csv
		
		listftp=[]
		list_lock_chrono.acquire()
		listlock.acquire()
		j=0
		for l in (listsymbol):
			if s in l:
				listftp.append(l.copy())
				if len(listftp)>200:break
				j+=1
		print("j : ",j)
		listlock.release()
		list_lock_chrono.release()
		title=str(s)+"-"+str(E)+"-"+evenement+"-test"
		_thread.start_new_thread(sendlistgraph,(listftp.copy(),title))
		#if evenement=="leave_breakout_12crossdown50":evenement=""		
		if evenement=="breakout":evenement=""

	#_thread.exit()
		
def sendlistgraph(l,title):
	ftplock.acquire()
	filpath="./uploaddirgraph/"+title
	with open(filpath, 'wb') as fp:
		print(filpath)
		pickle.dump(l, fp)
	filserverpath="domain.com/hft/graphin/"+title
	with FTP(host, user, password) as ftp :
		with open(filpath, "rb") as f:
			print(filpath,filserverpath)
			ftp.storbinary("STOR " + filserverpath, f)
	os.remove(filpath)
	ftplock.release()
	
def sendlistcsv(l,title):
	filpath="./uploaddircsv/"+title
	filpathstats="./stats_breakout/"+title
	filserverpath="domain.com/hft/in/"+title
	with open(filpathstats, 'w') as fps:
		txt=str(l)
		fps.write(txt)
		
	with open(filpath, 'wb') as fp:
		print(filpath)
		pickle.dump(l, fp)
	
	ftplock.acquire()
	with FTP(host, user, password) as ftp :
		with open(filpath, "rb") as f:
			print(filpath,filserverpath)
			ftp.storbinary("STOR " + filserverpath, f)
	ftplock.release()
	
	os.remove(filpath)

requete_=info_()

i=0
for s in listetest.liste:
    #print(0,0,0,0,0,0,0,0,0,s,0,0,0,0,0,0,0,0,0)
    #compute(e,E,s,kt,kT,ks,ki,kf,kL,ko,kc,kh,kl,kv,kn,kx,kq,kV,kQ,kB)
    compute(0,i,"test", 0, 0, 0, 0, 0, 0, 0, s, 0, 0, 0, 0, 0, 0, 0, 0,0)
    i+=1
    #time.sleep(0.1)
pause=input("pause")
_thread.start_new_thread(ws_thread, ())

while True:
	yves=1
