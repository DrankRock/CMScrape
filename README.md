# PokeScraper
pokemon cards price tracker from cardmarket links

---
## Current state :
This project is currently in developpment. It currently works if used in commande line. 
#### TODO :
->Make it work for all types of cards from CardMarket (Yu-Gi-Oh, Magic, etc). 

---
## Download :
```
# clone the repo
$ git clone https://github.com/DrankRock/PokeScraper.git
# change the working directory to PokeScraper
$ cd PokeScraper/
# download required packages
$ python -m pip install -r requirements.txt
```
---
## Usage :
`python3 pokeScrap.0.1.py -i <inputFile> -o <outputFile> -s <statFile>`
### Parameters :
***`-i or --input :`***

Input file containing on each line a link to a cardmarket card. 

***`-o or --output :`***

Output file, preferably a .csv file because the output will be written in csv format. For each line from the inputfile will be written a line containing :

`extension,number,name,min_price,price_trend,mean30d_price,language,sellerType,minCondition,isSigned,isFirstEd,isPlayset,isAltered,url`

***`-s or --stats :`***

Statistics file, preferably a csv file because the output will be written in csv format. At the end of the execution will be appended a line containing :

`current Time, sum of all the minimum prices, sum of all the trending prices, sum of all the "Mean 30 days" prices`

***`-h or --help :`***

Shows the help :
```
-- Pokemon CardMarket Scraper --
usage: pokeScrap.0.2.py -i <input file or link> -o <outputfile> -s <statFile(optional)>
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
