""" 
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

"""

import os
import requests
import pandas as pd

RIFLE_DATA_PATH = 'data/rifle_data.csv'
PERSON_DATA_PATH = 'data/person_data.csv'

url = 'https://script.google.com/macros/s/AKfycbyODcsyYP4BF6Sdw01g4wOd0Mxs5ZNK5KSTFJhR7Rf0Px_xo4IQz2kcbeoqZzu0wwMpaQ/exec'

def fetch_data(action):
    
    params = {
        'action': action 
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data)
    else:
        print(f"Error fetching {action}: {response.status_code}")
        return None
    
def update_rifle_data():
    df_new_rifle = fetch_data('getAllRifleData')
    print('df_new_rifle:', df_new_rifle)

    if df_new_rifle is not None:
        if os.path.exists(RIFLE_DATA_PATH):

            df_existing = pd.read_csv(RIFLE_DATA_PATH)
            existing_rifle_ids = set(df_existing['rifle_id'])
            new_rows = []

            for index, row in df_new_rifle.iterrows():
                rifle_id = row['rifle_id']
                if rifle_id not in existing_rifle_ids:
                    row['instock'] = True
                    new_rows.append(row)
                else:
                    df_existing.update(df_new_rifle.set_index('rifle_id'))
            if new_rows:
                df_existing = pd.concat([df_existing, pd.DataFrame(new_rows)], ignore_index=True)

            df_existing.to_csv(RIFLE_DATA_PATH, index=False)
            print("rifle_data.csv updated successfully!")

        else:
            df_new_rifle['instock'] = True
            df_new_rifle.to_csv(RIFLE_DATA_PATH, index=False)
            print("rifle_data.csv created successfully!")

def update_person_data():
    df_new_person = fetch_data('getAllPersonData')
    print('df_new_person',df_new_person)

    if df_new_person is not None:
        if os.path.exists(PERSON_DATA_PATH):
            df_new_person.to_csv(PERSON_DATA_PATH, index=False)
            print("person_data.csv updated successfully!")
        else:
            df_new_person.to_csv(PERSON_DATA_PATH, index=False)
            print("person_data.csv created successfully!")

def main():
    update_rifle_data()
    update_person_data()

if __name__ == '__main__':
    main()



