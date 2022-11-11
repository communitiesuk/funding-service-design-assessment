document.querySelector('#application_search').addEventListener('keyup', myFunction, false);

function myFunction(e) {
  e.preventDefault();    
    var filter = e.target.value.toUpperCase();
    var rows = document.querySelector("#application_overviews_table tbody").rows;
    
    for (var i = 0; i < rows.length; i++) {
        var firstCol = rows[i].cells[0].textContent.toUpperCase();
        var secondCol = rows[i].cells[1].textContent.toUpperCase();
        if (firstCol.indexOf(filter) > -1 || secondCol.indexOf(filter) > -1) {
            rows[i].style.display = "";
        } else {
          if(filter.length >= 3){
            rows[i].style.display = "none";
          }
        }      
    }
  }