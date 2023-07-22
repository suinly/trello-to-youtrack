# Trello to YouTrack

## Instructions

### Clone repository with script

```bash
git clone https://github.com/suinly/trello-to-youtrack.git
```

### Set script options

```bash
cd trello-to-youtrack
cp config.example.py config.py
vim config.py
```

### Run script for getting list of Trello boards

```bash
python convert.py
```

### Run script with board

```bash
python convert.py --board <BOARD_ID_FROM_LIST>
```

A csv file will be created in the script directory. Upload the csv file to Google Drive and follow [the instructions](https://www.jetbrains.com/help/youtrack/server/import-from-google-sheets.html#create-new-import) for importing into YouTrack.
