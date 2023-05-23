# find-pos-widgets

___

## Multithread selenium webdriver parser

Finds installed POS widgets on the public page and checks their URLs for compliance with templates with UTM tags. The
results are written on the fly to a file result.csv at the root of the project.

#### The console progress bar displays information about processed links:

```
Progress: 100%|██████████| 351/351 [04:26<00:00,  1.32it/s, CORRECT=246, NOT_MATCH=52, SPACER=3 COPY_PASTE=16, MISSING=34, TIMEOUT=0, ERROR=0]
```

#### output result.txt example:

```
correct https://vk.com/public12345
not_match https://vk.com/best_public_ever
```

### Result types:

- _**CORRECT**_ - Widgets exists and urls is correct
- _**NOT_MATCH**_ - Widgets exists and urls NOT valid
- _**SPACER**_ - Widgets exists and urls NOT valid (have spaces)
- _**COPY_PASTE**_ - Widgets exists and urls NOT valid (is copy/pasted from template)
- _**MISSING**_ - Widgets NOT exists
- _**TIMEOUT**_ - Can't get url page data
- _**ERROR**_ - NOT valid url or parsing errors

## Deployment:

#### Use scripts for deployment:

- [unix](unix) for Linux / MacOS
- [windows](windows) for Windows

or

1. Create _**env**_:
    ```
    cd {{root_dir}}
    python -m venv venv
    ```
2. Install [requirements](source/requirements.txt)
    ```
    # for Windows
    venv/bin/Script/activate.bat
    # for Linux/MacOS
    source venv/bin/activate
    
    cd source
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    ```
3. Provide target [VK](https://vk.com) public urls on _**target.txt**_ file in root dir (example):
    ```
    https://vk.com/public12345
    https://vk.com/best_public_ever
    ...
    ```
4. Start parsing:
    ```
    source venv/bin/activate
    cd source
    python main.py
    ```

## Requirements:

- [Python 3.11+]()
- [beautifulsoup4 4.12.2]()
- [html5lib 1.1]()
- [selenium 4.9.1]()
- [tqdm 4.65.0]()
