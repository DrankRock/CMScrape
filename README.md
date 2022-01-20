# CMScrape
Collectibles price tracker from Cardmarket links.

---
### README
This tool aims to **gain time** when checking a collection's price on CardMarket.  
The setup is quite long at the moment, you need to make a file containing all the cardmarket links to all the collectibles in your collection. You can find an example of a list [here](https://github.com/DrankRock/CMScrape/blob/main/CMScrape/myCards.txt). Once the list is created, the time gain starts. You just need to execute `python3 CMScrape.py`, then choose your links file in "Choose input file", then choose a type of output. Stat is a condensed output, containing only "Date, minPrice, mean30Price, TrendPrice", as a sum of all the prices of your collection. The output is a more precised version, with for each link, details about the collectible, and prices.  

This tool contains options for multithreaded execution, and an auto proxies scraper/checker/rotator to avoid getting ip-blocked by CardMarket.

#### About the prices.  
*MinPrice* is the minimum price observed on cardmarket **taking into account the parameters**, such as the condition, or the langage.  
*Mean30* is the price as indicated on CardMarket, the mean selling/buying price of the last 30 days.  
*TrendPrice* is the trending price.  
Trend and mean do not take into account the parameters. In my opinion, they are thus less precise when checking prices for a collection, but more accurate when you are buying cards for playing.   

### Demo :
You will find below an example of the execution with the latest version. If needed, a youtube version is available [here](https://www.youtube.com/watch?v=3Wjy0_205oI).
/!\ This demo is obsolete, it's way faster now. Will make a new one later.

![Demo](.github/images/CMScrape_Demo.gif)

## Current state :
This project is currently in developpment. It works and is tested on ubuntu 16.04 and windows 10, mostly on yugioh and pokemon cards.
If you have any suggestions or any kind of feedback, you can contact me on discord on [the dedicated discord server](https://discord.gg/UR3R5C5Ehn).

Note : this project was developped on Ubuntu 16.04. If you face any issue with the execution, please let me know.

## Current preoccupations :
I'm curretly working on a Firefox extension to create the list of links faster. 
I will also extend the sources for the proxy scraper, and add a language option to CMScrape.
I need to update the terminal version for a lighter execution.

## TODO :
Create a tool to add lots of cards to the list of links easily. I'm still in the thinking part.
Create a card scanner using OpenCV (this is a distant todo, as I have near to no experience in opencv)  

## Download :
```shell
# clone the repo
$ git clone https://github.com/DrankRock/CMScrape.git
# change the working directory to CMScrape
$ cd CMScrape/
# download required packages
$ python -m pip install -r requirements.txt
```

## Usage :
`python3 CMScrape.py`

## How to :
As soon as you launch CMScrape, you will be greeted by the main window.
Use the three buttons on the left to choose an input file, and either a Statistic file, an output file, or both.

### Files :
The **input** file should be a .txt file containing, on each line, a URL to a specific collectible from CardMarket. This can be cards, decks, boosters, deck boxes etc. As long as it's a collectible with a variable price, it will work. The input is enough to run the app, and if no outputs are given, the total prices will be written on the console. 
The **output** file must be a .csv file. If it doesn't exist, it will be created. If it does exist, it will be overwritten. For each url contained in the input file, the output file will contain a line with the informations : 
`game,item,extension,number,name,min_price,price_trend,mean30d_price,language,sellerType,minCondition,isSigned,isFirstEd,isPlayset,isAltered,isReverseHolo,isFoil,url`
in a coma separated form. The price and the url will be surrounded by `"`, which needs to be set as the String Delimiter in your csv viewer. (Libreoffice works well).
The **statistics** file must be a .csv file. If it doesn't exist, it will be created. If it does exist, the content of the file won't be overwritten, but a new line will be added at the end containing the informations. The statistics option outputs a single file with the informations :
`current Time, sum of all the minimum prices, sum of all the trending prices, sum of all the "Mean 30 days" prices`
in a coma separated form. This output aims to check the evolution of the collection as a whole.

### Parameters :
You can and should select parameters to precise the behavior of the application. You can open the preferences menu in `Settings -> Preferences` or by pressig `Ctrl+P`.
**Number of Threads** is the number of cardmarket pages you want to check simultaneously. A bigger number generally means more speed, but you are limited by the quality of your connexion, and the power of your computer. The default value, 50, gives good results. If you are going to check n url, putting more than n threads adds nothing.
**Number of Threads in ProxyCheck** is the number of Proxies you want to check simultaneously. The need for proxies is explained in the next section.
**Number of Proxies** is the maximum number of proxies you need.
**Use a file containing proxies** is self-explanatory. Instead of searching online for proxies, put the path to a file containing your proxies (Https or Http) and it will be used. You can then choose if you want to use this file, and if you want CMScrape to check which proxies are working. 

All these options are saved in the `.cmscrape` file and will be loaded in the next execution.

### RUN :
To explain what happens when CMScrape runs, I need to answer a question. If you understand the need for auto-rotating proxies, no need to read this subsection.

#### What are proxies, and why do we need them ?
A proxy is like a mask that your connection puts on, to make the website think it's a different person. It's not as secure as a VPN, it really is just like a mask, where a VPN would be a complete false identity and modification of your face. We need to disguise our identity because most websites protect themselves from people making too many requests. From my tests, Cardmarket accepts that a single user make 32 requests per minute. Above that, the request will return an error, and CMScrape will not work.
When using on single thread, so one url by one, this limit is not reached. But once we go multithreaded, so checking many urls at once, cardmarket sees how fast we go and knows it's not a human doing that, and blocks the IP adress.
This is why we need proxies. 

Because this tool might be used by people who are not familiar with these technologies, I added a way to do this automatically. Instead of having to buy, or find proxies, CMScrape will go on various pages online and find free proxies, then check them. 
Proxies need to be checked, because they will not always work. They depend on servers, etc. Non-working proxies will waste time and efficiency, so testing which ones work is necessary. With free proxies like the ones I'm scraping online, around 1 proxy in 10 is working.

#### The running :
As soon as the run button is clicked, if you did not put a proxy file, CMScrape will dowload free proxies on various sources, then check them.
When enough working proxies are found (as specified in the preferences, or when all the proxies were checked), the scraping phase starts for all the links in the input file. For each link, the page is downloaded, informations are extracted and put in the selected output.

When it's done, an information dialog will open, and some general informations will appear on the console. 

### Terminal's arguments :
#### The current terminal version is obsolete, hasn't been maintained for a while. I will update it in the near future, and put all the options back on the README.md. I apologize for the inconvenience. I only left the -h / --help option as it will only work in terminal anyways, and still works. 

***`-h :`***

**/!\ this parameter takes no arguments**

Shows the help :
```
-- Python CardMarket Scraper --
usage: CMScrape.py -i <input file or link> -o <outputfile> -s <statFile(optional)>
Precisions about the results :
 _____________________
|     minCondition    |
|_____________________|
| None = Poor         |
| 6    = Played       |
| 5    = Light Played |
| 4    = Good         |
| 3    = Excellent    |
| 2    = Near Mint    |
| 1    = Mint         |
|_____________________|
|      language       |
|_____________________|
| None = None         |
| 1    = English      |
| 2    = French       |
| 3    = German       |
| 4    = Spanish      |
| 5    = Italian      |
| 6    = S-Chinese    |
| 7    = Japanese     |
| 8    = Portuguese   |
| 9    = Russian      |
| 10   = Korean       |
| 11   = T-Chinese    |
| 12   = Dutch        |
| 13   = Polish       |
| 14   = Czech        |
| 15   = Hungarian    |
|_____________________|
```

---
## Example :
<ins>*input*</ins>

![picture alt](https://github.com/DrankRock/PokeScraper/blob/main/gitRessources/Screenshot%20from%202021-11-20%2019-00-58.png "links.txt")

<ins>*command*</ins>

![picture alt](https://github.com/DrankRock/PokeScraper/blob/main/gitRessources/Screenshot%20from%202021-11-20%2019-03-22.png "command")

<ins>*links.csv*</ins>

![picture alt](https://github.com/DrankRock/PokeScraper/blob/main/gitRessources/Screenshot%20from%202021-11-20%2019-05-10.png "links.csv")

<ins>*linksStat.csv*</ins>

![picture alt](https://github.com/DrankRock/PokeScraper/blob/main/gitRessources/Screenshot%20from%202021-11-20%2019-05-50.png "linksStat.csv")

## Exceptions :
Be careful, this script doesn't work with everything buyable on CardMarket.
Below is an example of a not working example, because it does not contain trend/mean prices. It's not a collectible, as opposed to the other version of the same kind of item below it.

#### This doesn't work
![picture alt](https://github.com/DrankRock/CMScrape/blob/main/gitRessources/doesntWork.png "doesntWorkExample")

#### This works
![picture alt](https://github.com/DrankRock/CMScrape/blob/main/gitRessources/works.png "workingExample")

### Thanks to :
The logo was created from another one created by Gregor Cresnar from the Noun Project.
