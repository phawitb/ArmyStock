# ArmyStock

### 1.load data from sheet https://www.youtube.com/watch?v=r817RLqmLac
```
python load_data_from_sheet.py
```
### 2.run app
```
streamlit run app.py
```
### in code.gs
```
setup_tutorial :: https://www.youtube.com/watch?v=r817RLqmLac

sheet url :: https://docs.google.com/spreadsheets/d/1qjwfbjsITCQXcdYV88soR3xk-NBUKpjGTuQ57IWG2Dc/edit?usp=sharing

code.gs :: 
function doGet(e) {
  var action = e.parameter.action;

  if (action == 'getAllRifleData') {
    return getAllRifleData();  // Return all rifle data
  }
  
  if (action == 'getAllPersonData') {
    return getAllPersonData();  // Return all person data
  }
}

// Function to retrieve all rifle data
function getAllRifleData() {
  var sheet_rifle = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('rifle_data');
  var rows = sheet_rifle.getRange(2, 1, sheet_rifle.getLastRow() - 1, sheet_rifle.getLastColumn()).getValues();
  var data = [];

  // Loop through rows and build JSON object for each
  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];
    var record = {
      "rifle_barcode": row[0],
      "rifle_id": row[1],
      "person_id": row[2],
      "instock": row[3]
    };
    data.push(record);
  }

  var result = JSON.stringify(data);
  return ContentService.createTextOutput(result).setMimeType(ContentService.MimeType.JSON);
}

// Function to retrieve all person data
function getAllPersonData() {
  var sheet_person = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('person_data');
  var rows = sheet_person.getRange(2, 1, sheet_person.getLastRow() - 1, sheet_person.getLastColumn()).getValues();
  var data = [];

  // Loop through rows and build JSON object for each
  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];
    var record = {
      "person_barcode": row[0],
      "person_id": row[1],
      "name": row[2]
    };
    data.push(record);
  }

  var result = JSON.stringify(data);
  return ContentService.createTextOutput(result).setMimeType(ContentService.MimeType.JSON);
}

```
