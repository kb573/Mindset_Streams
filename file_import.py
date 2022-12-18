import json
import jsonschema
import pandas as pd

def validate_json(json_data):
    """Check that a JSON object has the structure expected of a association object.

       Parameters
       ----------
       json_data : JSON Object : JSON object

       Returns
       ----------
       True/False : Boolean : True if structures matches schema False otherwise
    """
    
    association_schema = {
      "type": "object",
      "patternProperties": {
        "^.*$": {
          "anyOf": [
            {"type": "string", "pattern": "^[^\\s]*$",},
          ]
        }
      },
       "additionalProperties": False
    }
    
    try:
        jsonschema.validate(instance=json_data, schema=association_schema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True

def file_to_df(file_path):
    """Import association JSON file and validate its structure is correct.

       Parameters
       ----------
       file_path : String : system path to JSON file

       Returns
       ----------
       df : Pandas dataframe : contains assocation data
    """
    
    data = []
    with open(file_path) as f:
        json_objects = json.load(f)
    for json_object in json_objects:
        if validate_json(json_object) == True:
            data.append(list(json_object.values()))
            continue
        else:
            print('ValidationError: Invalid JSON object found ' + str(json_object))
            return
    df = pd.DataFrame(data, columns = ['word 1', 'word 2'])
    df = df.apply(lambda x: x.astype(str).str.lower())
    return df

def attach_sentiment(df, valence_file_path):
    """Attach sentiment valence labels to association data.

       Parameters
       ----------
       df : Pandas dataframe : contains sentiment attached assocation data
       valence_file_path : string : file path to JSON file containing sentiment valence data

       Returns
       ----------
       df : Pandas dataframe : contains sentiment attached assocation data
    """
    
    valence_dict = {}
    
    with open(valence_file_path) as f:
        json_objects = json.load(f)
    for d in tuple(json_objects):
        valence_dict[list(d.values())[0]] = list(d.values())[1]
    df['word 1 valence']= df['word 1'].map(valence_dict)
    df['word 2 valence']= df['word 2'].map(valence_dict)
    df.rename(columns={'column1': 'word 1', 'column2': 'word 2'}, inplace=True)
    df = df.apply(lambda x: x.astype(str).str.lower())
    return df