var linksArray = localStorage.getItem('linksArray')

if (linksArray == null){
  linksArray = []
} else {
  linksArray = linksArray.split(',') 
}


var saveData = (function () {
var a = document.createElement("a");
// document.body.appendChild(a);
// a.style = "display: none";
return function (data, fileName) {
      var blob = new Blob([data], {type: "octet/stream"}),
        url = window.URL.createObjectURL(blob);
    a.href = url;
    a.download = fileName;
    a.click();
    window.URL.revokeObjectURL(url);
};
}());

// The above code comes from : https://stackoverflow.com/a/43135989

document.addEventListener("click", function(e) {
  if (!e.target.classList.contains("select-this-url")) {
    return;
  }
  
  var clicked_id = e.target.id
  if(clicked_id == "Add"){
    chrome.tabs.query({'active': true, 'lastFocusedWindow': true}, function(tabs) {
      var url = tabs[0].url;
      linksArray.push(url)
      console.log("Start ...")
      console.log(linksArray)
      localStorage.setItem('linksArray', linksArray)
      var newText =  ""+linksArray.length+" links in list !"
      document.getElementById("Add").innerHTML = newText;
    });

  } else if (clicked_id == "Export"){
    console.log("Exporting to txt ...")
    var data = linksArray.join('\r\n');
    fileName = "cmscrape_list.txt";
    saveData(data, fileName);

  } else if (clicked_id == "Clear"){
    var result = confirm("Do you want to continue?");
    if(result)  {
        localStorage.removeItem('linksArray')
        localStorage.setItem('linksArrayDeleted', true)
        console.log("List deleted.")
    } else{
      console.log("List not deleted.")
    }
  }
  

});
