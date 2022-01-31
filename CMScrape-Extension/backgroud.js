chrome.webNavigation.onCompleted.addListener(closeTab, {
  url: [
    {urlPrefix: 'https://www.cardmarket.com/'}
  ]
});

function closeTab(e) {
  alert("Holy shit !")
}
