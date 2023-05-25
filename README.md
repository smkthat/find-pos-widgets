# find-pos-widgets

##### Finds installed POS widgets on the public page and checks their URLs for compliance with templates with UTM tags. The results are written on the fly to a file result.csv at the root of the project.

#### The console progress bar displays information about processed links:

```
Processing: 100%|████████████████████████████████████| 3319/3319 [00:37<00:00, 88.23url/s, CORRECT=963, INVALID=1968, MISSING=388, TIMEOUT=0, ERROR=0]
```

#### output result.txt example:

```
pos_result;public_url;pos_link1;pos_link1_status;pos_link2;pos_link2_status
INVALID;https://vk.com/best_public_ever;'https://pos.gosuslugi.ru/og/org-activities?.....';<Status name='VALID', value='Correct url'>;'https://pos.gosuslugi.ru/form/?.....';<Status name='NOT_MATCH', value='Invalid, url dont match pattern'>
INVALID;https://vk.com/club12345678;'https://pos.gosuslugi.ru/form/?.....';<Status name='NOT_MATCH', value='Invalid, url dont match pattern'>;'https://pos.gosuslugi.ru/og/org-activities?.....';<Status name='VALID', value='Correct url'>
...
```

### POS result types:

- _**CORRECT**_ - Widgets exists and urls is correct
- _**INVALID**_ - Widgets exists and urls NOT valid
- _**MISSING**_ - Widgets NOT exists
- _**TIMEOUT**_ - Can't get url page data
- _**ERROR**_ - NOT valid url or parsing errors

### POS link statuses:

- _**VALID**_ - Correct url
- _**NOT_MATCH**_ - Invalid, url don't match pattern
- _**UTM_INVALID**_ - Invalid UTM code value
- _**SPACER**_ - Invalid, url contains spaces

## Deployment:

#### Use scripts for deployment:

- [unix](unix) for Linux / MacOS
- [windows](windows) for Windows

or

##### 1. Create _**env**_:
```
cd {{project_dir}}
python -m venv venv
```

##### 2. Install [requirements](source/requirements.txt):
For Windows:
```
# cmd.exe
venv\Scripts\activate.bat
# PowerShell
venv\Scripts\Activate.ps1

cd source
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```
For Linux / MacOS:
```
source venv/bin/activate
cd source
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

##### 3. Provide target [VK](https://vk.com) public urls on _**target.txt**_ file in root dir (example):
```
https://vk.com/public12345
https://vk.com/best_public_ever
...
```

##### 4. Start parsing:
```
# cmd.exe
venv\Scripts\activate.bat
# PowerShell
venv\Scripts\Activate.ps1

python main.py
```

##### 5. Stop parsing:
> Use keys: ctrl + c

## Configurations:
##### [Default](source/config.yaml) config:
```
vk_api:
  access_token: abc123456789de
  version: 5.131
parsing:
  skip_correct: false
  save_public_data_dir: '../publics_data'
  min_interval: 0
  fields: [menu, activity, city, contacts, description, members_count, status]
log:
  log_file_path: '../runtime.log'
  target_file_path: '../target.txt'
  result_file_path: '../result.csv'
exceptions:
  connection:
    max_tries: 5 # tries count to get data
    timeout: 5 # waiting between tries (multiplied on tries count)
```
##### vk_api:
- _**access_token**_ - Your VK API token. For provide access_token you can [create app](https://vk.com/editapp?act=create) and get token in settings.

    ![img.png](info/img.png)

    ![img1.png](info/img1.png)

- _**version**_ - VK API version.

##### parsing:
- _**skip_correct**_ - (Boolean) Skip URLs with correct pos widgets
- _**save_public_data_dir**_ - The path to the directory when saving the parsed data of the vkontakte group to a json file, if _false_ - do not save
- _**min_interval**_ - min_interval [0-0.1] for the update progress indicator (_!!! do not increase more than 0.1 !!!_)
- _**fields**_ - More fields in https://dev.vk.com/method/groups.getById

##### log:
- _**log_file_path**_ - Path to runtime log file
- _**target_file_path**_ - Path to target file with urls
- _**result_file_path**_ - Path to result file

##### exceptions.connection:
- _**max_tries**_ - Number of attempts to get data
- _**timeout**_ - Waiting between attempts (multiplied by the number of _max_tries_)

## Requirements:

- **Python** >= 3.11
- **omegaconf** == 2.3.0
- **tqdm** == 4.65.0
- **vk** == 3.0
