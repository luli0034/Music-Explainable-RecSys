# Music-Explainable-RecSys

# 🚀 Usage

## Preparing Data

1. Download the data from [Kaggle.com](https://www.kaggle.com/c/kkbox-music-recommendation-challenge), and process the downloaded data into KG-format.
    <details>
      <summary> ⏬ Let's get the data!</summary>

    Data preprocessing includes downloading data from Kaggle, and processing those data into KG-format (*head → relation ← tail*). You can simply build a docker image with the following steps and run the container to get the training data.

    Make sure you have `kaggle.json` in the same directory, the download scripts will look for this token.

    If you’ve not:

    1. Go to the link: https://www.kaggle.com/{account}/account
    2. Click the button `Create New API Token`.
    3. Download the file named `kaggle.json`, the content will look like the following:

        ```python
        {"username":"{account}","key":"{hash_key}"}
        ```


    Change directory into folder: `data-preprocessing`, and build a docker image named `build_kg`:

    ```bash
    cd ./data-preprocessing
    docker build -t build_kg . --no-cache
    ```

    The content of Dockerfile show below:

    ```docker
    FROM python:3.7-slim

    WORKDIR /data-preprocessing

    COPY ./requirements.txt /data-preprocessing/requirements.txt

    RUN apt-get update \
        && apt-get install gcc -y \
        && apt-get clean \
        && apt-get install zip -y \
        && apt-get install p7zip-full -y

    RUN pip install --upgrade pip \
        && pip install -r /data-preprocessing/requirements.txt \
        && rm -rf /root/.cache/pip

    COPY ./kaggle.json /root/.kaggle/kaggle.json
    COPY ./src /data-preprocessing/src/

    CMD ["bash", "src/get_data.sh"]
    ```

    Run the container and mount the *output directory* to your *local directory*:

    ```powershell
    docker run -d -v {local_directory}:/data-preprocessing/src/output/ --name preprocessing build_kg
    ```

    Also, you can check the running progress with `docker logs`

    ```powershell
    docker logs -f preprocessing
    ```

    Once the container have done its works, the three `csv` files will show in the *local directory.*

    1. `kg_members.csv` : Member’s basic information such as gender, age, etc. 
    2. `kg_songs.csv` : Song’s information including basic and extending features such as artist name, composer, years, etc.
    3. `kg_user_interation.csv` : Members who has interest the song.

    </details> 
