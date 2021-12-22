# CMScrape
Collectibles price tracker from Cardmarket links.

---
### README
This tool aims to **gain time** when checking a collection's price on CardMarket.  
The setup is quite long at the moment, you need to make a file containing all the cardmarket links to all the collectibles in your collection. You can find an example of a list [here](https://github.com/DrankRock/CMScrape/blob/main/CMScrape/myCards.txt). Once the list is created, the time gain starts. You just need to execute `python3 CMScrape.py`, then choose your links file in "Choose input file", then choose a type of output. Stat is a condensed output, containing only "Date, minPrice, mean30Price, TrendPrice", as a sum of all the prices of your collection. The output is a more precised version, with for each link, details about the collectible, and prices.  
The DBScrape part is currently not working. In Fine, I want it to scrape CardMarket as a whole to get all the cards in links, as  
"Name, Expansion, URL"  
Or something similar.  

#### About the prices.  
MinPrice is the minimum price observed on cardmarket **taking into account the parameters**, such as the condition, or the langage.  
Mean30 is the price as indicated on CardMarket, the mean selling/buying price of the last 30 days.  
TrendPrice is the trending price.  
Trend and mean do not take into account the parameters. In my opinion, they are thus less precise when checking prices for a collection, but more accurate when you are buying cards for playing.   
You will find below an example of the execution with the latest version.  

## Current state :
This project is currently in developpment. It works but was never intensly tested.
If you have any suggestions or any kind of feedback, you can contact me on discord on [the dedicated discord server](https://discord.gg/UR3R5C5Ehn).

Note : this project was developped on Ubuntu 16.04. If you face any issue witht he execution, please let me know.

## Current preoccupations :
I am currently trying to make the best possible GUI using PyQt5. I am also trying to get a full database of CardMarket links to facilitate the creation of the list of links. I would like to have it in a "Game-Expansion-Number-Name-URL" form, to create a Database in the future and facilitate the access of the data. 

## TODO :
Add MultiThreading
Improve the wobbly console output in the -g version
Find testers to have some feedback
Add a tool to create the list, using CM's database to add full expansions, search by names etc
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
`python3 CMScrape.py <parameters>`
By default, CMScrape will be launched in a new Application window, as it's more user-friendly. You can still use the `-t` options to launch the app in the terminal.

*example :*
`python3 CMScrape.py -i myGreatCollection.txt -o mySortedPricedCollection.csv -s someStats.csv -so`

### Parameters :
***`-i, --input :`***

Input file containing on each line a link to a cardmarket card. 

***`-o, --output :`***

Output file, preferably a .csv file because the output will be written in csv format. For each line from the inputfile will be written a line containing :

`game,item,extension,number,name,min_price,price_trend,mean30d_price,language,sellerType,minCondition,isSigned,isFirstEd,isPlayset,isAltered,isReverseHolo,isFoil,url`

If no information is found concerning a parameter, 'None' will be indicated.


***`-s, --stats :`***

Statistics file, preferably a csv file because the output will be written in csv format. At the end of the execution will be appended a line containing :

`current Time, sum of all the minimum prices, sum of all the trending prices, sum of all the "Mean 30 days" prices`

***`-so, --sort-outfile :`***

**/!\ this parameter takes no arguments**

When this parameter is chosen, the output csv file, given in argument of the --output parameter, is sorted alphabetically. It works exclusively on output, because the stat file is already sorted in crescent date order.

***`-g, --graphic :`***

**/!\ this parameter takes no arguments**

Executes CMScrape in an interactive application.


***`-t, --terminal :`***

**/!\ this parameter takes no arguments**

Executes CMScrape in the terminal (without graphic application)


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
