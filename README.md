# find-pos-widgets

##### Finds installed POS widgets on the public vk page and checks their URLs for compliance with templates with UTM tags. The results are written on the fly to a file result.csv at the root of the project.

#### The console progress bar displays information about processed links:

```
Processing: 100%|████████████| 3319/3319 [00:37<00:00, 88.23url/s, CORRECT=963, INVALID=1968, MISSING=388, TIMEOUT=0, ERROR=0]
```

### POS result types:

- `CORRECT` - Correct urls
- `INVALID` - Contain NOT valid urls
- `LINKS_COUNT` - Incorrect number of urls
- `MISSING` - Urls NOT exists
- `TIMEOUT` - Can't get public data from request, connection timeout
- `ERROR` - NOT valid public url or parsing errors

### POS link statuses:

- `VALID` - Correct url
- `NOT_MATCH` - Invalid, url don't match pattern
- `UTM_INVALID` - Invalid UTM code value
- `SPACER` - Invalid, url contains spaces

## Deployment:

##### 1. Create `env`:
```
cd {{project_dir}}
python -m venv venv
```

##### 2. Install [requirements](requirements.txt):
For Windows:
```
# cmd.exe
venv\Scripts\activate.bat
# PowerShell
venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt
deactivate
```
For Linux / MacOS:
```
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

##### 3. Provide target [VK](https://vk.com) public urls on `target.txt` file in root dir (example):
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
# Linux / MacOS
source venv/bin/activate

python main.py
```

##### 5. For stop parsing use keys: `ctrl` + `c`

##### 6. For close venv use command:
```
deactivate
```

## Configurations:
##### Default [config.yaml](config.yaml):
```
vk_api:
  access_token: 'Put your token'
  version: 5.131
parsing:
  max_links_per_widget: 2
  skip_correct: false
  save_public_data: true
  public_data_fields: [ menu, activity, city, contacts, description, members_count, status ]
progressbar:
  min_interval_per_unit: 0
display:
  csv_delimiter: ';'
  public_display_fields: [pos_result, url, id, name, screen_name, pos_links, description]
  status_types:
    pattern: '{name}'
    items:
      VALID: { name: '✅', value: 'Correct urls' }
      NOT_MATCH: { name: '❌', value: 'Invalid, url dont match pattern' }
      UTM_INVALID: { name: '⚠️', value: 'Invalid UTM code value' }
      SPACER: { name: '⚠️', value: 'Invalid, url contains spaces' }
  result_types:
    pattern: '{name}: {value}'
    items:
      CORRECT: { name: '✅', value: 'Correct urls' }
      INVALID: { name: '⚠️', value: 'Contain NOT valid urls' }
      LINKS_COUNT: { name: '❗', value: 'Widgets links count not pass tests' }
      MISSING: { name: '❌', value: 'Urls NOT exists' }
      TIMEOUT: { name: '⌛️', value: 'Timeout when getting url page data' }
      ERROR: { name: '🆘', value: 'NOT valid url or data parsing errors' }
paths:
  log_file: 'runtime.log'
  target_file: 'target.txt'
  result_file: 'result.csv'
  save_public_data_dir: 'publics_data'
exceptions:
  connection:
    max_tries: 5
    timeout: 5
```
##### vk_api:
- `access_token` - (str) Your VK API token. For provide access_token you can [create app](https://vk.com/editapp?act=create) and get token in settings.

    ![img.png](info/img.png)

    ![img1.png](info/img1.png)

- `version` - (int) VK API version.

##### parsing:
- `max_links_per_widget` (**int**) - Checking for the number of POS widgets, if `0` - the check is skipped
- `skip_correct` - (bool) Skip URLs with correct pos widgets
- `save_public_data` - (bool) If we need to save datas of publics in folder
- `public_data_fields` - Fields for request from VK API:
  * `menu` - (Default) Widgets data
  * `activity` - Public activity type
  * `city` - City of the public
  * `description` - Public description
  * `members_count` - Public total members
  * `status` - Current public status
  * ... - Find more fields in [dev.vk.com](https://dev.vk.com/method/groups.getById)

##### progressbar:
- `min_interval_per_unit` - min_interval [0-0.1] for the update progress indicator (_!!! do not increase more than 0.1 !!!_)

##### display:
- `csv_delimiter` - Delimiter for result csv file
- `public_display_fields` - Select fields to display in result csv file (with the preservation of order):
  * `pos_result` - (Default) POS widgets parsing result type
  * `url` - (Default) Target public url
  * `name` - (Default) Parsed public name
  * `pos_links` - (Default) POS links checking status
  * `id` - Parsed public id
  * `screen_name` - Parsed public screen_name
  * ... - Include more from `parsing.public_data_fields`

- `status_types` and `status_types` - Here you can specify the values to display in the pattern results file

  ##### output result csv file example:
  
  ```
  pos_result;url;name;pos_link1;pos_link1_status;pos_link2;pos_link2_status;id;screen_name
  ✅;https://vk.com/public123;Public 123;https://pos.gosuslugi.ru/og/org-activities?.....;✅: Correct urls;https://pos.gosuslugi.ru/form/?.....;✅: Correct urls;32242414124;public123
  ⚠️;https://vk.com/best_public_ever;Best public ever;https://pos.gosuslugi.ru/og/org-activities?.....;⚠️: Invalid UTM code value;https://pos.gosuslugi.ru/abcdf/?.....;❌: Invalid, url dont match pattern;98127468127;best_public_ever
  ❗;https://vk.com/club321;Clubbers 321;https://pos.gosuslugi.ru/form/?.....;✅: Correct urls;;;667678689;public667678689
  ❌;https://vk.com/club12345678;Club 12345678;;;;12345678;club12345678
  ...
  ```

##### paths:
- `log_file` - Path to runtime log file
- `target_file` - Path to target file with urls
- `result_file` - Path to result file
- `save_public_data_dir` - The path to the directory when saving the parsed data of the vkontakte group to a json file, if `parsing.save_public_data` is `false` - do not been saved

##### exceptions:
- `max_tries` - Number of attempts to get data
- `timeout` - Waiting between attempts (multiplied by the number of _max_tries_)

## Widget check regexes:
- Not provided UTM codes: `REG-CODE|OGRN|ID|MUN-CODE`
- Spacers: `\s|%20`
- Template:
  ```
  https://pos\.gosuslugi\.ru/(?:form/\?(opaId=\d+)|og/org-activities\?(?:(reg_code=\d{2,8})|(mun_code=\d{8})))&(utm_source=vk|utm_source=vk[12])&(utm_medium=\d{2,4})&(utm_campaign=\d{13})
  ```

## Requirements:

- **Python** >= 3.8
- **omegaconf** == 2.3.0
- **tqdm** == 4.65.0
- **vk** == 3.0
