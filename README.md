# find-pos-widgets

#### <div><a href="#en">🇬🇧 Eng</a> | <a href="#ru">Рус 🇷🇺</a></div>

<details>
  <summary>Table of contents</summary>
  <ol>
    <li>
      <a href="#en-about">About</a>
      <ul>
        <li><a href="#en-result-types">POS result types</a></li>
        <li><a href="#en-url-statuses">POS url statuses</a></li>
      </ul>
    </li>
    <li>
      <a href="#en-deployment">Deployment</a>
      <ul>
        <li><a href="#en-windows">Windows</a></li>
        <li><a href="#en-linux-macos">Linux / MacOS</a></li>
      </ul>
    </li>
    <li>
      <a href="#en-configurations">Configurations</a>
      <ul>
        <li><a href="#en-vk-api">VK API</a></li>
        <li><a href="#en-parsing">Parsing</a></li>
        <li><a href="#en-progressbar">Progressbar</a></li>
        <li><a href="#en-display">Display</a></li>
        <li><a href="#en-exceptions">Exceptions</a></li>
      </ul>
    </li>
    <li>
      <a href="#en-widget-regexes">Widget url regexes</a>
    </li>
    <li>
      <a href="#en-requirements">Requirements</a>
    </li>
  </ol>
</details>

---
<a name="en-about"></a>

## About

Finds installed POS widgets on the public vk page and checks their URLs for compliance with templates with UTM tags.
<br/>The results are written on the fly to the file specified in the configuration file.

<a name="en-result-types"></a>

### POS result types

- `CORRECT` - Correct urls
- `INVALID` - Contain NOT valid urls
- `LINKS_COUNT` - Incorrect number of urls
- `MISSING` - Urls NOT exists
- `TIMEOUT` - Can't get public data from request, connection timeout
- `ERROR` - NOT valid public url or parsing errors

The console displays information about processed links:

```shell
Clearing resources ...
Reading file ...
Prepare publics from links ...
Number of links found: 3319
Start processing:
Processing: 100%|████████████| 3319/3319 [00:37<00:00, 88.23url/s, CORRECT=963, INVALID=1968, MISSING=388, TIMEOUT=0, ERROR=0]
Processing complete! See results in './result.csv'
```

<a name="en-url-statuses"></a>

### POS url statuses

- `VALID` - Correct url
- `NOT_MATCH` - Invalid, url don't match pattern
- `UTM_INVALID` - Invalid UTM code value
- `SPACER` - Invalid, url contains spaces

---
<a name="en-deployment"></a>

## Deployment

<a name="en-windows"></a>

### OS Windows

1. Go to the project directory
    ```shell
    cd find-pos-widgets
    ```

2. Create Python env
    ```shell
    python -m venv venv
    ```
3. Run env
    ```shell
    # for cmd.exe
    venv\Scripts\activate.bat
    ```
    ```shell
    # for PowerShell
    venv\Scripts\Activate.ps1
    ```

4. Upgrade pip (this command may be skipped)
    ```shell
    pip install --upgrade pip
    ```

5. Install requirements
    ```shell
    pip install -r requirements.txt
    ```

6. Start script
    ```shell
    python main.py
    ```

<a name="en-linux-macos"></a>

### OS Linux / MacOS

1. Go to the project directory
    ```bash
    cd find-pos-widgets
    ```
2. Create Python env
    ```bash
    python -m venv venv
    ```
3. Run env
    ```bash
    source venv\Scripts\activate
    ```
4. Upgrade pip (this command may be skipped)
    ```bash
    pip install --upgrade pip
    ```
5. Install requirements
    ```bash
    pip install -r requirements.txt
    ```
6. Start script
    ```bash
    python main.py
    ```

#### Stopping:

1. For stopping script use keys:
   <br>`ctrl` + `c`
2. For close env use command:
   <br>`deactivate`

---
<a name="en-configurations"></a>

## Configurations

Provided in [config.yaml](config.yaml) file:

```yaml
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
  public_display_fields: [ pos_result, url, id, name, screen_name, pos_links, description ]
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

<a name="en-vk-api"></a>

### VK API

|     Param      |   Type   | Default | Description                                                                                                                               |
|:--------------:|:--------:|:-------:|-------------------------------------------------------------------------------------------------------------------------------------------|
|   `version`    | `float`  | `5.131` | VK API version                                                                                                                            |
| `access_token` | `string` |    -    |  Your VK API token.<br/><br/>_For provide access_token you can [create app](https://vk.com/editapp?act=create) and get token in settings_ |

<details>
  <summary>(See screenshots)</summary>
  <img src="info/img.png" alt="img"/>
  <img src="info/img1.png" alt="img1"/>
</details>

<a name="en-parsing"></a>

### Parsing

|         Param          |   Type    | Default  | Description                                                                                                                                                                                                                                                                                                                                                                                                           |
|:----------------------:|:---------:|:--------:|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `max_links_per_widget` | `intager` |   `2`    | Checking for the number of POS widgets, if `0` - the check is skipped                                                                                                                                                                                                                                                                                                                                                 |
|     `skip_correct`     | `boolean` | `false`  | Skip URLs with correct pos widgets                                                                                                                                                                                                                                                                                                                                                                                    |
|   `save_public_data`   | `boolean` |  `true`  | If we need to save datas of publics in folder                                                                                                                                                                                                                                                                                                                                                                         |
|  `public_data_fields`  |  `list`   | [`menu`] | Fields for request from VK API.<br/><br/>**Variables**:<br/><ul><li>`menu` - (Default) Widgets data</li><li>`activity` - Public activity type</li><li>`city` - City of the public</li><li>`description` - Public description</li><li>`members_count` - Public total members</li><li>`status` - Current public status</li><li>... find more fields in [dev.vk.com](https://dev.vk.com/method/groups.getById)</li></ul> |

<a name="en-progressbar"></a>

### Progressbar

|          Param          |   Type    | Default | Description                                                                                             |
|:-----------------------:|:---------:|:-------:|---------------------------------------------------------------------------------------------------------|
| `min_interval_per_unit` | `intager` |    0    | min_interval [`0`-`0.1`] for the update progress indicator<br/><br/>(_Do NOT increase more than `0.1`_) |

<a name="en-display"></a>

### Display

|                   Param                   |     Type     |                             Default                             | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|:-----------------------------------------:|:------------:|:---------------------------------------------------------------:|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|              `csv_delimiter`              |   `string`   |                               `;`                               | Delimiter for result csv file                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|          `public_display_fields`          |    `list`    | [`pos_result`, `url`, `name`, `pos_links`, `id`, `screen_name`] | Select fields to display in result csv file (with the preservation of order)<br/><br/>**Variables**:<br/><ul><li>`pos_result` - (Default) POS widgets parsing result type</li><li>`url` - (Default) Target public url</li><li>`name` - (Default) Parsed public name</li><li>`pos_links` - (Default) POS links checking status</li><li>`id` - Parsed public id</li><li>`screen_name` - Parsed public screen_name</li><li>... include more from `parsing.public_data_fields`</li></ul> |
| `result_types`<br/>and<br/>`status_types` | `dictionary` |                                -                                | Here you can specify the values to display in the pattern results file<br/><br/>Use any variables, such as `name`, `value`, or others. Then provide a `pattern` to determine how it will be provided<br/><br/>**Example for `status_type`:**<br/><pre>{"name": "✅", "value": "Correct urls"}<br/>pattern = "{name}: {value}"</pre>display: `✅: Correct urls`                                                                                                                    |

##### Output result csv file example:

  ```
  pos_result;url;name;pos_link1;pos_link1_status;pos_link2;pos_link2_status;id;screen_name
  ✅;https://vk.com/public123;Public 123;https://pos.gosuslugi.ru/og/org-activities?.....;✅: Correct urls;https://pos.gosuslugi.ru/form/?.....;✅: Correct urls;32242414124;public123
  ⚠️;https://vk.com/best_public_ever;Best public ever;https://pos.gosuslugi.ru/og/org-activities?.....;⚠️: Invalid UTM code value;https://pos.gosuslugi.ru/abcdf/?.....;❌: Invalid, url dont match pattern;98127468127;best_public_ever
  ❗;https://vk.com/club321;Clubbers 321;https://pos.gosuslugi.ru/form/?.....;✅: Correct urls;;;667678689;public667678689
  ❌;https://vk.com/club12345678;Club 12345678;;;;12345678;club12345678
  ...
  ```

<a name="en-paths"></a>

### Paths

|         Param          | Type     |    Default     | Description                                                                                                                                                       |
|:----------------------:|----------|:--------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|       `log_file`       | `string` | `runtime.log`  | Path to runtime log file                                                                                                                                          |
|     `target_file`      | `string` |  `target.txt`  | Path to target file with urls                                                                                                                                     |
|     `result_file`      | `string` |  `result.csv`  | Path to result file                                                                                                                                               |
| `save_public_data_dir` | `string` | `publics_data` |  The path to the directory when saving the parsed data of the VK group to a json file<br/><br/>_If `parsing.save_public_data` is `false` - data don't been saved_ |

<a name="en-exceptions"></a>

### Exceptions

|    Param    | Type      | Default | Description                                                              |  
|:-----------:|-----------|:-------:|--------------------------------------------------------------------------|  
| `max_tries` | `intager` |   `5`   | Number of attempts to get data                                           |  
|  `timeout`  | `float`   |   `5`   | Waiting between attempts<br/>_(multiplied by the number of `max_tries`)_ |  

---
<a name="en-widget-regexes"></a>

## Widget url regexes

#### Not provided UTM codes

```pythonregexp
REG-CODE|OGRN|ID|MUN-CODE
```

#### Spacers

```pythonregexp
\s|%20
```

#### Template

```pythonregexp
https://pos\.gosuslugi\.ru/(?:form/\?(opaId=\d+)|og/org-activities\?(?:(reg_code=\d{2,8})|(mun_code=\d{8})))&(utm_source=vk|utm_source=vk[12])&(utm_medium=\d{2,4})&(utm_campaign=\d{13})
```

---
<a name="en-requirements"></a>

## Requirements

1. Python 3.8+
2. Installed python env [requirements](requirements.txt)
    ```
    omegaconf==2.3.0
    tqdm==4.65.0
    vk==3.0
    ```

<br>
<br>
<br>