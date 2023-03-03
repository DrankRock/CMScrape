import requests, re
from bs4 import BeautifulSoup


def lineToInfo(line):
    line = f"{line}"
    soup2 = BeautifulSoup(line, "html.parser")

    # # # # SELLER INFOS BLOCK # # # #
    seller_infos = soup2.find('span', class_='seller-info d-flex align-items-center')

    seller_country_pattern = r'data-toggle="tooltip" title="(.*?)">'
    seller_country = re.findall(seller_country_pattern, str(seller_infos))[1]
    seller_country = seller_country.split(": ")[1]

    seller_name_pattern = r'/Users/(.*?)">'
    seller_name = re.findall(seller_name_pattern, str(seller_infos))[0]

    seller_type_pattern = r'data-original-title="(.*?)"'
    try:
        seller_type = re.findall(seller_type_pattern, str(seller_infos))[0]
    except:
        seller_type = "Amateur"  # that is dirty, but it works (if nothing found, it's an amateur

    # # # # PRODUCT INFORMATIONS # # # #
    product_infos = soup2.find('div', class_='product-attributes col')
    badge_pattern = r'<span class="badge">(.*?)</span>'
    badge = re.findall(badge_pattern, str(product_infos))[0]

    infos_pattern = r'data-original-title="(.*?)"'
    infos = re.findall(infos_pattern, str(product_infos))
    info_str = ""
    for info in infos :
        info_str += str(info).replace(","," ")+" - "
    info_str = info_str[:-3]

    # # price / avail # #
    input = soup2.find('div', class_='col-offer')

    price_pattern = r'<span class="font-weight-bold color-primary small text-right text-nowrap">(.*?)</span>'
    price = re.findall(price_pattern, str(input))[0]
    price = price.replace(",", ".")

    number_pattern = r'<span class="item-count small text-right">(.*?)</span>'
    number = re.findall(number_pattern, str(input))[0]

    # print(seller_country, seller_name, seller_type, badge, infos_str, price, number)
    out = [seller_country, seller_name, seller_type, badge, info_str, price, number]
    return out


# Set the URL of the webpage you want to parse
url = 'https://www.cardmarket.com/fr/Pokemon/Products/Singles/Neo-Destiny/Dark-Feraligatr-NDE5?language=5&isFirstEd=Y'


def soupToTopXSellers(soup, number_of_sellers):
    table_body = soup.find('div', class_='table-body')
    article_divs = table_body.find_all('div',
                                       {'class': 'row no-gutters article-row', 'id': lambda x: x.startswith('article')})
    outList = []
    # Loop through the matching div elements and do something
    i = 0
    for div in article_divs:
        # Do something with the div element
        if i >= number_of_sellers:
            break
        outList.append(lineToInfo(div))
        i += 1
    return outList


'''
<div class="row no-gutters article-row" id="articleRow1434423798"><div class="d-none col"></div><div class="col-sellerProductInfo col"><div class="row no-gutters"><div class="col-seller col-12 col-lg-auto"><span class="seller-info d-flex align-items-center"><span class="seller-name d-flex"><span class="badge d-none d-sm-inline-flex has-content-centered mr-1 badge-faded sell-count" data-html="true" data-placement="bottom" data-toggle="tooltip" title="561 Sales | 11768 Available items">561</span><span class="icon d-flex has-content-centered mr-1" data-html="true" data-placement="bottom" data-toggle="tooltip" title="Item location: Switzerland"><span class="icon" style="display: inline-block; width: 16px; height: 16px; background-image: input_url('//static.cardmarket.com/img/89f7303ef70095797975a067832c9792/spriteSheets/ssMain.png'); background-position: -80px -70px;"></span></span><span class="d-flex has-content-centered mr-1"><a href="/en/YuGiOh/Users/Constantin-Trading">Constantin-Trading</a></span><span class="d-flex text-nowrap ml-lg-auto"><span class="d-flex has-content-centered mr-1 proFaded"><span class="icon" data-html="true" data-original-title="Professional" data-placement="bottom" data-toggle="tooltip" onmouseout="hideMsgBox()" onmouseover="showMsgBox(this,`Professional`)" style="display: inline-block; width: 16px; height: 16px; background-image: input_url('//static.cardmarket.com/img/f8d806e6267c7c859592cba11335f3d6/spriteSheets/ssMain2.png'); background-position: -464px -16px;" title=""></span></span></span></span></span></div><div class="col-product col-12 col-lg"><div class="row no-gutters"><div class="product-attributes col"><a class="article-condition condition-nm mr-1" data-html="true" data-placement="bottom" data-toggle="tooltip" href="/en/YuGiOh/Help/CardCondition" title="Near Mint"><span class="badge">NM</span></a><span class="icon mr-2" data-html="true" data-original-title="German" data-placement="bottom" data-toggle="tooltip" onmouseout="hideMsgBox()" onmouseover="showMsgBox(this,`German`)" style="display: inline-block; width: 16px; height: 16px; background-image: input_url('//static.cardmarket.com/img/f8d806e6267c7c859592cba11335f3d6/spriteSheets/ssMain2.png'); background-position: -80px -0px;" title=""></span><span class="icon st_SpecialIcon mr-1" data-html="true" data-original-title="First Edition" data-placement="bottom" data-toggle="tooltip" onmouseout="hideMsgBox()" onmouseover="showMsgBox(this,`First Edition`)" style="display: inline-block; width: 16px; height: 16px; background-image: input_url('//static.cardmarket.com/img/f8d806e6267c7c859592cba11335f3d6/spriteSheets/ssMain2.png'); background-position: -112px -16px;" title=""></span></div><div class="mobile-offer-container d-flex d-md-none justify-content-end col"><span class="small item-count-mobile mr-3">1 avail.</span><div class="d-flex flex-column"><div class="d-flex align-items-center justify-content-end"><span class="font-weight-bold color-primary small text-right text-nowrap">2,35 €</span></div></div></div></div></div></div></div><div class="col-offer"><div class="price-container d-none d-md-flex justify-content-end"><div class="d-flex flex-column"><div class="d-flex align-items-center justify-content-end"><span class="font-weight-bold color-primary small text-right text-nowrap">2,35 €</span></div></div></div><div class="amount-container d-none d-md-flex justify-content-end mr-3"><span class="item-count small text-right">1</span></div><div class="actions-container d-flex align-items-center justify-content-end col pl-2 pr-0"><a class="btn btn-sm btn-grey" data-html="true" data-placement="bottom" data-toggle="tooltip" href="/en/YuGiOh/Login" role="button" title="You have to be logged in to be able to buy items."><span class="fonticon-cart"></span></a></div></div></div>
'''