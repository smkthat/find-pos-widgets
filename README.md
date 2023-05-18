# find-pos-widgets

___

### Multithread selenium webdriver parser

Finds installed POS widgets on the public page and checks their URLs for compliance with templates with UTM tags. The results are written on the fly to a file result.txt at the root of the project. The console progress bar displays information about processed links.


## Deployment:

Use scripts for deployment:

- [unix](unix) for Linux / MacOS
- [windows](windows) for Windows

or

1. Create **env**:
    ```
    # Linux/MacOS
    cd {{root_dir}}
    python -m venv venv
    ```
2. Install [requirements](source/requirements.txt)
    ```
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r source/requirements.txt
    deactivate
    ```
3. Provide target [VK](https://vk.com) public urls on **target.txt** file in root dir (example):
    ```
    https://vk.com/public12345
    https://vk.com/best_public_ever
    ...
    ```
4. Start parsing:
    ```
   source venv/bin/activate
   python source/main.py
    ```

## Requirements:

- [Python 3.11+]()
- [beautifulsoup4 4.12.2]()
- [html5lib 1.1]()
- [selenium 4.9.1]()
- [tqdm 4.65.0]()