import sys,json,ssl,urllib.request,urllib.error,time
mode=sys.argv[1];assert mode in ('direct','proxy')
proxy={}if mode=='direct'else{'https':'http://127.0.0.1:7890','http':'http://127.0.0.1:7890'}
opener=urllib.request.build_opener(urllib.request.ProxyHandler(proxy),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
start=time.monotonic()
try:
    with opener.open(urllib.request.Request('https://github.com',method='HEAD'),timeout=15)as response:
        print(json.dumps({'mode':mode,'verified_tls_http_status':response.status,'elapsed_seconds':round(time.monotonic()-start,3),'credentials_sent':False}))
except Exception as error:
    print(json.dumps({'mode':mode,'type':type(error).__name__,'message':str(error),'elapsed_seconds':round(time.monotonic()-start,3),'credentials_sent':False}))
