import urllib.request, urllib.error, socket, requests, multiprocessing, re, sys, random, time
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool

WEBPAGE = 'https://www.cardmarket.com/en'
TIMEOUT = 10

headers_list = [{
        'Host': 'www.cardmarket.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    },{
        'Host': 'www.cardmarket.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    },{
        'Host': 'www.cardmarket.com',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    },{
        'Host': 'www.cardmarket.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }]

class proxyClass():
    def __init__(self, nThreads, nProxyNeeded, proxyFile):
        if proxyFile == False:
            self.initWebScrape()
        else:
            self.initFileProxy(proxyFile)
        random.shuffle(self.proxyList)
        self.nThreads = nThreads
        self.needs = nProxyNeeded

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
            print("found {} proxies at https://free-proxy-list.net/".format(len(self.proxyList)))

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
            print("found {} proxies at {}".format(len(out),link))
        print("found {} proxies in total".format(len(self.proxyList)))

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
        pool = ThreadPool(self.nThreads)
        #pool = multiprocessing.Pool(processes=self.nThreads)
        vals = pool.imap(self.checkProxy, self.proxyList)
        iterator = 0
        working = 0
        output = []
        for result in vals:
            text = "Checking Proxies : [{}/{}] - Working : {}, Need : {}".format((iterator+1),len(self.proxyList), working, self.needs)
            print(text, end="\r", flush=True)
            if result != -1:
                output.append(result)
                working+=1
            if working >= self.needs:
                self.proxyList = output
                return output 
            iterator+=1
        self.proxyList = output
        return output 
