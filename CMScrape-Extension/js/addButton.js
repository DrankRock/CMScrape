var titleDiv = document.querySelector("div.page-title-container.d-flex.align-items-center.text-break")
var itemTitleDiv = titleDiv.querySelector("div.flex-grow-1")
var reportAProblemDiv = titleDiv.querySelector("div.align-self-end.mb-md-1")
var helpA = titleDiv.querySelector("a.d-flex.align-items-center.justify-content-end")

console.log('helo'+reportAProblemDiv.outerHTML)

helpA.innerHTML = '<span class="fonticon-questionmark"></span>&nbsp;CMScrape - Add to list'
helpA.setAttribute("href", "#")
helpA.setAttribute("onclick","var ar = window.localStorage.getItem('CMScrape_LinksArray');(ar == null) ? ar = [] : ar = ar.split(', ');ar.push(window.location.href);window.localStorage.setItem('CMScrape_LinksArray', ar);")
var divAdd = helpA.outerHTML
var divClear = `<a href="#" class="d-flex align-items-center justify-content-end" onclick="window.localStorage.removeItem('CMScrape_LinksArray')"><span></span>&nbsp;-&nbsp;Clear</a>`
var divExport = `<a href="#" class="d-flex align-items-center justify-content-end" onclick="console.log('Exporting to txt ...');var data = window.localStorage.getItem('CMScrape_LinksArray').split(',').join('\\r\\n');fileName = 'cmscrape_list.txt';var a = document.createElement('a');var blob = new Blob([data], {type: 'octet/stream'}),url = window.URL.createObjectURL(blob);a.href = url;a.download = fileName;a.click();window.URL.revokeObjectURL(url);"><span />&nbsp;-&nbsp;Export</a>`

helpA.outerHTML = String(divAdd) + String(divClear) + String(divExport)