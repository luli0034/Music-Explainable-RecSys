#!/bin/sh
DATA_DIR="./data"
SOURCE_DATA_DIR="$DATA_DIR/source"
echo "$DATA_DIR $SOURCE_DATA_DIR"
[ ! -d "$DATA_DIR" ] && mkdir -p "$DATA_DIR"
if [ -d "$SOURCE_DATA_DIR" ]; then
    echo "1. Source folder exist, remove all files then create"
    rm -rf "$SOURCE_DATA_DIR"
    mkdir "$SOURCE_DATA_DIR"
else
    echo "1. Create source folder"
    mkdir "$SOURCE_DATA_DIR"
fi
echo "2. Start downloading data from Kaggle competitions..."
kaggle competitions download -c kkbox-music-recommendation-challenge -p "$SOURCE_DATA_DIR"

echo "3. Unzip downloaded data and clean..."
unzip "$SOURCE_DATA_DIR/kkbox-music-recommendation-challenge" -d "$SOURCE_DATA_DIR"
rm "$SOURCE_DATA_DIR/kkbox-music-recommendation-challenge.zip"

echo "4. Uncompross 7z files"
for filename in $SOURCE_DATA_DIR/*.csv.7z; do
    7z x "$filename" -o"$SOURCE_DATA_DIR"
    rm "$filename"
done
