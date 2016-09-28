# BUNT (Bot UNderstanding Testbed)


## What is BUNT ?

BUNT is a testbed for NLP engines, typically used uin chatbots.

Find out more about the story behind BUNT here : [https://medium.com/@zelros](https://medium.com/@zelros)


## What BUNT can do for you ?

BUNT can evaluate performance on:

- **languages**: French and English are supported. Other languages can be added through modules.
- **corpus**: Different default corpus of testing data are provided (small talk, misspellings, …) - other corpus can be added by the user
- **apis**: 3 NLP-as-a-service providers are supported: api.ai, luis.ai, and recast.ai. Other providers can be added through plugins


## How does BUNT work ?

- Put your credentials in ```credentials.py```:

```
LUIS_KEY = 'my_luis_key'
```

- Select your settings in ```settings.py```:

```
ACTION = 'comparator'
METRICS = ['accuracy', 'error_3_penalized']
CRITERIA = {
    'en': ['mails_en', 'misspellings_en'],
    'fr': ['mails_fr', 'misspellings_fr']
}
```

- Run ```run.py```:

```
python run.py
```


## How can I add my own NLP service ?

- Create a class Manager inheriting ApiManager from ```api.py```. (See ```api.py``` for more details):

```
class MyAPIManager(ApiManager):
    def __init__(self):
        pass
    
    def fit(self, df_train):
        pass
        
    def predict(self, x_list):
        pass
```

- Add the name of your API in the settings file (in API_HANDLED)

- In ```api_builder.py```, add a case with your api (in build_api function)


## How can I add my own metric ?

- Add your metric in score_metric method of ```scorer.py```:

```
if metric == 'your_metric_name':
    # this example is the accuracy metric
    n_all = n_found + n_fallback + n_error
    return n_found / float(n_all)
```

- Add your metric name in ```settings.py``` in METRICS_HANDLED:

```
METRICS_HANDLED = ['accuracy',..., 'your_metric_name']
```


## How can I add my own test set ?

- Create a csv file (tab-separated) containing 2 rows

    The utterances are in the row called **sentence** and the intents are in the other row called **intent**
    (you can see one of the files)
    
- Add your file in ```criteria/language``` folder.

- Add the name of your file (without the *.csv*) in CRITERIA in ```settings.py``` when you want to use it:

```
CRITERIA = {
    'en': ['smalltalk_en', ... 'your_english_file'],
    'fr': ['smalltalk_fr', 'mails_fr', 'your_french_file']
}
```
