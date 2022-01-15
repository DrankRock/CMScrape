import urllib.request, urllib.error, socket, requests, multiprocessing, re, sys, random, time
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
from PyQt5 import QtWidgets

WEBPAGE = 'https://www.cardmarket.com/en'
TIMEOUT = 10
FINISH = False

class proxyClass():
    def __init__(self, proxyFile, nProxy, proxyPoolSize, consoleDisp):
        self.consoleDisp = consoleDisp
        self.needs = nProxy
        if proxyFile == False:
            self.initWebScrape()
        else:
            self.initFileProxy(proxyFile)
        random.shuffle(self.proxyList)
        self.nProcess = proxyPoolSize

    def initFileProxy(self, proxyFile):
        with open(proxyFile, 'r') as f:
            self.proxyList = [line.strip() for line in f]
            #print("\n".join(self.proxyList))
        print("successfully loaded {} proxies.\n".format(len(self.proxyList)))

    def initWebScrape(self):
        # I'm keeping this overly complicated version in case of needing to know if it's http or https
        def freeProxyListNet():
            page = requests.get("https://free-proxy-list.net/")
            soup = BeautifulSoup(page.content, "html.parser")

            name_uncut = soup.find("table", class_="table table-striped table-bordered")
            #print(name_uncut)
            name = re.findall(r'<td(?: class="(?:hm|hx)")?>(.*?)<\/td>',str(name_uncut))
            #print(name)
            current = 0
            temp = ""
            for elem in name:
                val = current%8
                if val == 0:
                    temp = elem
                elif val == 1:
                    temp = temp+":"+elem
                    self.proxyList.append(temp)
                current += 1
            self.consoleDisp.setPlainText("found {} proxies at https://free-proxy-list.net/".format(len(self.proxyList)))
            QtWidgets.QApplication.processEvents()

        self.proxyList = []
        freeProxyListNet()

        httpLinks = [
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
        ]
        for link in httpLinks:
            r = requests.get(link, allow_redirects=True)
            out = r.content.decode("utf8").splitlines()
            self.proxyList = self.proxyList+out
            self.consoleDisp.setPlainText(self.consoleDisp.toPlainText()+"\n"+"found {} proxies at {}".format(len(out),link))
            QtWidgets.QApplication.processEvents()
        self.consoleDisp.setPlainText(self.consoleDisp.toPlainText()+"\n"+"found {} proxies in total".format(len(self.proxyList)))
        QtWidgets.QApplication.processEvents()
    def getProxies(self):
        return self.proxyList

    def TheType(self, typeP):
        outlist = []
        for elem in self.proxyList:
            sp = elem.split(":")
            if len(sp) == 4:
                elem = "{}://{}:{}@{}:{}".format(typeP,sp[2],sp[3],sp[0],sp[1])
            else:
                elem = "{}://{}:{}".format(typeP,sp[0],sp[1])
            #print("{}".format(elem))
            outlist.append(elem)
        self.proxyList = outlist

    def randomProxy(self):
        return random.choice(self.proxyList)

    def checkProxy(self, pip):
        if not FINISH:
            try:
                proxy_handler = urllib.request.ProxyHandler({'http': pip,'https': pip})
                opener = urllib.request.build_opener(proxy_handler)
                opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                urllib.request.install_opener(opener)
                req=urllib.request.Request(WEBPAGE)  # change the URL to test here
                sock=urllib.request.urlopen(req)
            except:
                #print("ERROR:", detail)
                return -1
            return pip

    def checkProxies(self):
        startTime = time.time()
        socket.setdefaulttimeout(TIMEOUT)
        pool = ThreadPool(self.nProcess)
        #pool = multiprocessing.Pool(processes=self.nProcess)
        iterator = 0
        working = 0
        output = []
        prevText = self.consoleDisp.toPlainText()
        try:
            vals = pool.imap(self.checkProxy, self.proxyList)
            for result in vals:
                text = "Checking Proxies : [{}/{}] - Working : {} - Need : {}".format((iterator+1),len(self.proxyList), working, self.needs)
                if working >= self.needs:
                    self.proxyList = output
                    return output 
                self.consoleDisp.setPlainText(prevText+"\n"+text)
                QtWidgets.QApplication.processEvents()
                #print(text, end="\r", flush=True)
                if result != -1:
                    output.append(result)
                    working+=1
                iterator+=1
            self.proxyList = output
        except:
            global FINISH
            FINISH = True
        return output 


# This comes from : https://stackoverflow.com/a/765436

'''
# Enhanced version of what's from stackoverflow with multiprocessing
def main(nProcess, timeout):
    socket.setdefaulttimeout(int(timeout))
    if len(sys.argv) > 1:
        p = proxyClass(sys.argv[1])
    else:
        p = proxyClass(False)
    if len(sys.argv) > 2:
        typeP = sys.argv[2]
        p.TheType(typeP)
    
    proxyList = p.getProxies()
    pool = ThreadPool(nProcess)
    vals = pool.imap(is_bad_proxy, proxyList)
    iterator = 0
    working = 0
    output = []
    print("Checking which proxies are working ... (might take some time)\nThreads = {}\nTimeout = {}\nTesting url = {}".format(THREADS,TIMEOUT,WEBPAGE))
    for result in vals:
        print("[{}/{}] - Working : {}".format((iterator+1),len(proxyList), working), end="\r", flush=True)
        if result != -1:
            output.append(result)
            working+=1
        iterator+=1
    strOut = "\n".join(output)
    #print("Working Proxies : \n{}".format(strOut))
    return strOut

# Search for free proxies and check which one are working, on google, with a timeout of 5s, on 8 threads
'''