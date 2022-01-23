# Music-Explainable-RecSys

We build an end-to-end Recommendation System as Services to provide a RestAPI that can be query not only recommended items but also their explanation.

You can reproduce the whole pipeline on your own dataset in minutes if you’re familiar with:

- **Knowledge Graph Embedding** → *TransE, Link-Prediction*
- **Recommendation System**
- **Microservices** → *FastAPI, Docker, Kubenetes*
- **Database** → *PostgresSQL, MongoDB, SQLAlchemy (ORM)*

Also, you can deploy the services on cloud such as AWS, GCP, etc.

- **Cloud Concept →** *Amazon DynamoDB, Amazon RDS, Serverless Services*

# 📽️ Quick Demo

# 📚 Basic Concepts

Using Knowledge Graph to build Recommender System has attracted considerable interest due to some of its strengths.

1. **Heterogeneity**, KG can blend the user-item interaction, side information of users and items in the same graph.
2. **Explainability**, KG provides a way to analyze data from a relational perspective, many explainable recommendation methods have been proposed.

## About The Project

### KG x RecSys

A common way to build a RecSys is Knowledge Graph Embedding, It projects entities and relations into a lower dimension, representing these entities and relations with a dense vector.

Knowledge graph embedding methods can simply divide into two parts

1. **Translation-based** : TransE, TransH, TransR
2. **Semantic-based** : DistMult

If we want to recommend some movies to a user, and we define a relation `like` between users and movies.***

Once we trained the Knowledge Graph Embeddings, we can predict has any link (`like`) between a user and all recommended items (***link prediction***). 

Then, we can recommend the movies which have the highest scores to the user.

### Our Knowledge Graph

The **WSDM** dataset, provided by KKBOX, consists of information of the first observable listening event for each unique user-song pair within a specific time duration. And metadata of each song and user is also provided. We can simply split the data into three parts:

1. **User’s information :** User’s basic information such as age, gender, etc.
2. **Song’s information :** Song’s information such as artist name, composer, etc.
3. **User Behavior :** User’s behavior such as a user’s recurring listening event(s).

<details>
        <summary> Show KG Schema in details </summary>
    
### Song’s Info

- `song` → *song’s length* → `length`
- `song` → *song’s genre* → `genre`
- `song` → *sing by* → `artist`
- `song` → *written by* → `composer`
- `song` → *written by* → `lyricist`
- `song` → *language is* → `language`
- `song` → *publish in* → `country`
- `song` → *reference year* → `year`

### Member’s Info

- `user` → *reference year* → `year`
- `user` → *located in* → `city`
- `user` → *age is* → `age`
- `user` → *gender is* → `gender`
- `user` → *registered via* → `registered way`
- `user` → *registered in* → `year`

### User behavior

- `user` → *has interest* → `song`
- `user` → *top 3 listening (country)* → `country`
- `user` → *top 3 listening (reference year)* → `year`
- `user` → *top 3 listening (genre)* → `genre`
- `user` → *top 3 listening (composer)* → `compose`
- `user` → *top 3 listening (lyricist)* → `lyricist`

</details>

## How to be “Explainable”

The paths, which in Knowledge Graph, represent a reality in real world. Therefore, we can simply choose one of those paths which can connect `A` to `B`, as our explanation.

For example, if the RecSys predict that a user named `Luli` will love the song named `Faded` , there are two paths can walk from `Luli` to `Faded`:

***Path 1*** : ( `Luli` ) - [ `listen` ] → ( `Spectre` ) - [ `sing by` ] → ( `Alan  Walker` ) ← [ `sing by` ] - ( `Faded` )

***Explanation : `Luli`, recommend `Faded` to you, it’s seem like you like `Alan Walker`’s songs.***

***Path 2*** : ( `Luli` ) - [ `top 3 listen composer` ] → ( `Anders Froen` ) - [ `written by` ] → ( `Anders Froen` ) ← [ `sing by` ] - ( `Faded` )

***Explanation*** : `Luli`, recommend `Faded` to you, it’s seem like you like the songs which are written by `Anders Froen`.

# 🚀 Usage

## Preparing Data

1. Download the data from [Kaggle.com](https://www.kaggle.com/c/kkbox-music-recommendation-challenge), and process the downloaded data into KG-format.
    <details>
      <summary> Let's get the data!</summary>

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
    
    <details>
        <summary> Show Dockerfile</summary>
        
        
        
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
        

    </details>
    
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
