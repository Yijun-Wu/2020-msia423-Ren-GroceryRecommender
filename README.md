# MSiA423 Grocery Recommender    
Author: Jing Ren, QA: Aakanksha Sah

## Project Charter
### Vision
With coronavirus impact and Stay-at-Home order, even though you can still shop for food at the grocery store while keeping social distancing, you might find some items are in short supply or hesitant to go out at the first place. Many times people forget about what they intend to buy, specially when they’re not physically in grocery stores, as stores normally put bundled item together in same shopping aisle. However, Amazon Fresh and Instacart got very limited delivery slots which are hard to find these days, so it's not easy to get the missing items in time. This application aims to help complete your grocery list by recommending bundled items so as to save your time and trouble, as well as meeting your shopping needs.

### Mission
To generate grocery lists, this application will first prompt users to input one item on their current grocery list, and then make top 5 recommendations based on market basket analysis (association rules via apriori), which is derived from customer orders dataset from instacart. The items selected from recommendation list will also have corresponding recommendations. With more data input, the list generated will become a closer match to user's wish list items, and it also provides option of starting over by resetting the basket. Hopefully users will find the app save their time and maintain a healthy diet during the COVID-19 pandemic.

### Success criteria
Machine Learning Criteria: The success of this application will be examined by robustness of recommendations given, we mainly consider recommender’s ability to capture user’s preferences in this case. Therefore, we define score as fraction of n recommendations are “good”. One example could be mothers buy baby products such as milk and diapers together. So, we define score as fraction of n recommendations that are “good”. We start by recommend what can be bought with the first product in current order, and we will give 5 recommendations, then compare the next 4 actually bought products with this 5 recommendations. If there's a match, we will add 1 to the total score, so on so forth, and take total score divided by total number of recommendations.
We aim to have score > 0.3, so that at least 30% of recommendations are matching actually ordered items.

Business Success Criteria: This application will be deemed successful if 50% of new users come back to the app, and average session frequency reaches twice per month, showing user engagement. We would also consider customer satisfaction survey, level from 0 to 5, to get average user ratings as feedback.


## Planning
### Initiative 1: Data Preprocessing
Epic 1
- Story 1: Make sure to understand the dictionary of data. 
- Story 2: Clean the data, check format, and handle missing values if needed.
- Story 3: Store data in cloud platform (icebox)

### Initiative 2: Model Building
Epic 1
- Story 1: Choose set of features to include in model development.
- Story 2: Evaluate models based on performance and calculation results.

Epic 2
- Story 1: Train the chosen model on dataset and check its robustness.
- Story 2: Set up test cases to evaluate functionality.
### Initiative 3: App Development
Epic 1
- Story 1: Develop scripts for user input layout.
- Story 2: Build the front end app.

Epic 2
- Story 1: Connect modeling part to recommendation result display.
- Story 2: Create user satisfactory survey.
### Backlog
I1E1 - 2 point

I2E1 - 2 point

### Icebox
I2E2 - 8 point

I3E1 - 4 point

I3E2 - 3 point


## Midterm Checkpoint
## Running the app
### Step 1: Download the dataset

- Data Source: https://www.instacart.com/datasets/grocery-shopping-2017
- File Name: order_products__prior.csv, orders.csv, products.csv

The file needs to be manually downloaded, you need to first download `instacart_online_grocery_shopping_2017_05_01.tar.gz`, then unzip the compressed file folder to locate the files. 
It is already downloaded and moved into `data/external` folder.
**Note that, we need to connect to Northwestern VPN for following steps.**


### Step 2. Upload raw dataset into or download it from S3 bucket

*1. Add Configuration for AWS S3 bucket*

Replace access key id and secret access key with your own key from AWS account, by exporting environmental variables beforehand running these commands in terminal:

```
export AWS_ACCESS_KEY_ID=<Your Access Key ID>

export AWS_SECRET_ACCESS_KEY=<Your Secret Key ID>
```

Or make these changes in `.mys3config` and run command `source .mys3config`. Both work in the same way.

In addition, make sure your IP address is added in inbound rules and consistent with RDS setting, even if connected to Northwestern VPN, there might still be differences between IP addresses when you connect several times.


*2a. Upload Raw Data to S3*

Here's a list of args in commands,

- `--s3bucket`: add the name of your S3 bucket where you will store the data file. 
- `--input1` / `--output1`: path to prior orders dataframe.
- `--input2` / `--output2`: path to orders dataframe.
- `--input3` / `--output3`: path to products dataframe.

By running command below, the raw data will be uploaded to your S3 bucket successfully.

```
python3 run.py upload --config=config/recommendation.yaml --s3bucket=nw-jren-s3-1 --input1=data/external/order_products__prior.csv --input2=data/external/orders.csv --input3=data/external/products.csv
```


*2b. Download Raw Data to S3*

By running command below, the raw data will be downloaded from your S3 bucket successfully.

```
python3 run.py acquire --config=config/recommendation.yaml --s3bucket=nw-jren-s3-1 --output1=data/external/order_products__prior.csv --output2=data/external/orders.csv --output3=data/external/products.csv
```

Downloaded data will be stored into `data/external/order_products__prior.csv`, `data/external/orders.csv `, and `data/external/products.csv` correspondingly, or user specified path.


### Step 3. Perform market basket analysis and generate recommendations on all data

Here's a list of args in commands,

- `--input1`: path to prior orders dataframe.
- `--input2`: path to products dataframe.
- `--output`: path to store generated recommendation table.

```
python3 run.py generate_rules --input1=data/external/order_products__prior.csv --input2=data/external/products.csv --output=data/external/recommendations.csv
```

Generated recommendation table will be stored into `data/external/recommendations.csv` or user specified path.


### Step 4. Evaluate scores of recommendation model on test data (after generating rules from train data)

Here's a list of args in commands,

- `--input1`: path to prior orders dataframe.
- `--input2`: path to orders dataframe.
- `--input3`: path to products dataframe.
- `--output`: path to store generated scores (txt file).

```
python3 run.py get_scores --input1=data/external/order_products__prior.csv --input2=data/external/orders.csv --input3=data/external/products.csv --output=data/external/scores.txt
```

Generated test scores will be stored into `data/external/scores.txt`, or user specified path.
With over 3 million lines, it could take hours to run the test score, so as to save your running time, we only take a sample of records at this moment to check test score.
This score roughly stabilizes around 0.4 with whole data, before cutting it down due to limited RAM memory.


### Step 5. Write association rules' recommendations into RDS database

*1. Add Configuration for creating database schema in RDS*

Export environmental variables beforehand by running these commands in terminal:

```
export MYSQL_USER=<enter your RDS host here>
export MYSQL_PASSWORD=<enter your RDS password here>
export MYSQL_HOST=<enter your RDS instance endpoint here>
export MYSQL_PORT=<enter your port here>
export DATABASE_NAME=<enter your database name here> 
```

Another option would be edit the file `.mysqlconfig` in root directory. Run this command from root directory,

```
vi .mysqlconfig
``` 

Update the following credentials which will be used to create the database:

- MYSQL_USER: default is `admin` when setting up RDS instance
- MYSQL_PASSWORD: password used to create database server
- MYSQL_PORT: 3306 
- DATABASE_NAME: msia423_db
- MYSQL_HOST: RDS instance endpoint (check console)

Save your file and set these environment variables in your setting by running:

```
echo 'source .mysqlconfig' >> ~/.bashrc
source ~/.bashrc
```


*2. Writing records into table in RDS database*

Here's a list of args in commands,

- `--input`: path to recommendation table generated.
- `--truncate`: indicates whether empty the recommendation table or not.
- `--rds`: indicates whether table is stored into local SQLite or RDS database.

```
python3 run.py store_RDS --input=data/external/recommendations.csv --truncate=True --rds=True
```

Change to `--rds=False` if you want the table stored in local SQLite database.
Change to `--truncate=False` if you don't need to delete table from database. It's set to True as default, so as to avoid issue of duplicate entry for primary key in sql database.


*3a. Checking content in table created in RDS*

Firstly, connect to RDS database,

```
sh run_mysql_client.sh
```

Then, select the database we're using, and display content of our current recommendation table,

```
use msia423_db;
select * from Recommendation;
```


*3b. Checking content in table created locally*

If you choose to create database schema locally, you can simply check `data/msia423_db.db`.


### Step 6. Running the entire model pipeline with docker command

Firstly, we need to export environmental variables into our environment by using these commands in terminal,

```
export AWS_ACCESS_KEY_ID=<Your Access Key ID>
export AWS_SECRET_ACCESS_KEY=<Your Secret Key ID>
export SQLALCHEMY_DATABASE_URI=<Your SQLALCHEMY DATABASE URI>
```

Then, running run-pipeline.sh by following lines (build docker image first):

```
docker build -t grocery_recommender .
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e SQLALCHEMY_DATABASE_URI --mount type=bind,source="$(pwd)/data",target=/app/data/ grocery_recommender run-pipeline.sh
```


### Step 7. Running unit tests

Unit test is run for `src/market_basket_analysis.py` and `src/scores.py`.

Other functions are for download / upload /database creation purpose, so we won't perform tests in this case.

```
docker build -t grocery_recommender .
docker run grocery_recommender pytest
```


### Step 8. Running the Flask app

To run the Flask app (first build docker image), run: 

```
docker build -f app/Dockerfile -t grocery_recommender .
docker run -e SQLALCHEMY_DATABASE_URI --mount type=bind,source="$(pwd)",target=/app -p 5000:5000 grocery_recommender python3 app.py
```

You should now be able to access the app at http://0.0.0.0:5000/ in your browser.


