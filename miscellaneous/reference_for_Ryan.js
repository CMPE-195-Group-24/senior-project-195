/* Do not maniplate any of the code in this file yet.
 * Assigned to Ryan only */

function addRow(tableID) {
    var table = document.getElementById(tableID); // identifying table based on parameter (ID) is passed
 
    var rowCount = table.rows.length; // row count
    var row = table.insertRow(rowCount);
 
    ///////////// FIRST CELL /////////////
    var cell1 = row.insertCell(0); // creating new first cell on the new row
    // HTML contents of first cell
 
    cell1.innerHTML = `
       <input type="text" placeholder="Assignment Name" id="assignment" name="assignment[]"/>
       <input type="text" style="width: 100px;" placeholder="Score" id="score" name="score[]"/>
       <input type="text" style="width: 100px;" placeholder="Total Points" id="totalpoints" name="totalpoints[]"/>
    `;
 
    // ///////////// SECOND CELL /////////////
    // var cell2 = row.insertCell(1); // creating new second cell on the new row
    // // HTML contents of second cell
    // var element1 = document.createElement("input"); // In HTML, <input></input>
    // element1.type = "text0"; // In HTML, <input type="text0"></input>
    // element1.placeholder = "text0"; // In HTML, <input placeholder="text0"></input>
    // element1.name="txt1[]"; // In HTML, <input name="txt1[]"></input>
    // cell2.appendChild(element1);
 
    // ///////////// THIRD CELL /////////////
    // var cell3 = row.insertCell(2); // creating new third cell on the new row
    //    // HTML contents of third cell
    // var element2 = document.createElement("input"); // In HTML, <input></input>
    // element2.type = "txt0";
    // element2.name = "txt0[]";
    // cell3.appendChild(element2);
 
    // alert("Cell added.")
 }
 
 // function addColumn(tableID) {
 //    var table = $('#'+tableID);
 //    var iter = 0;
 //    $('#test').click(function() {
 //       table.find('tr').each(
 //          function() {
 //             var trow = $(this);
 //             if (trow.index() === 0) {
 //                trow.append("<th>Test" + iter + "</th>");
 //             } else {
 //                trow.append('<td>\
 //                <input type="text" placeholder="Assignment Name" id="assignment" name="assignment[]"/>\
 //                <input type="text" style="width: 100px;" placeholder="Score" id="score" name="score[]"/>\
 //                <input type="text" style="width: 100px;" placeholder="Total Points" id="totalpoints" name="totalpoints[]"/>\
 //                </td>');
 //             }
 //          }
 //       );
 //      iter += 1;
 //    });
 // }
 
 function rowCount(tableID) {
    var rowCount = 0;
    var table = document.getElementById(tableID);
    var rows = table.getElementsByTagName("tr");
 
    for (var i = 0; i < rows.length; i++) {
       rowCount++;
    }
 
    document.querySelector("#rowCount").innerHTML =
    `${rowCount-1}`;
 
    return rowCount;
 }
 
 function columnCount(tableID) {
    var columnCount = 0;
    var table = document.getElementById(tableID);
    var columns = table.getElementsByTagName("th");
 
    for (var i = 0; i < columns.length; i++) {
       columnCount++;
    }
 
    document.querySelector("#columnCount").innerHTML =
    `${columnCount}`;
 
    return columnCount;
 }
 
 var table = $('#dataTable');
 var iter = 2; // starts creating at 2nd column
 $('#addColumn').click(function() {
    table.find('tr').each(
       function() {
          var trow = $(this);
          if (trow.index() === 0) {
             trow.append('<th>Course ' + (iter) + '<input style="position: relative; float: right;" type="text" placeholder="Weight" id="weight"/></th>');
          } else {
             trow.append('<td>\
             <input type="text" placeholder="Assignment Name" id="assignment" name="assignment[]"/>\
             <input type="text" style="width: 100px;" placeholder="Score" id="score" name="score[]"/>\
             <input type="text" style="width: 100px;" placeholder="Total Points" id="totalpoints" name="totalpoints[]"/>\
             </td>');
          }
       }
    );
    iter += 1;
 });
 
 $('#addRow').click(function() {
    var first_row = $('#firstBodyRow');
    first_row.clone().appendTo('#dataTable');
 });
 
 
 
         /*
         function deleteRow(tableID) {
             try {
             var table = document.getElementById(tableID);
             var rowCount = table.rows.length;
 
             for(var i=0; i<rowCount; i++) {
                 var row = table.rows[i];
                 var chkbox = row.cells[0].childNodes[0];
                 if(null != chkbox && true == chkbox.checked) {
                     table.deleteRow(i);
                     rowCount--;
                     i--;
                 }
 
 
             }
             }catch(e) {
                 alert(e);
             }
         }
         */