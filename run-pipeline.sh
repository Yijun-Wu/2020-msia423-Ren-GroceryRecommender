#!/usr/bin/env bash

# Download datasets from S3 bucket
python3 run.py acquire --config=config/recommendation.yaml --s3bucket=nw-jren-s3-1 --output1=data/external/order_products__prior.csv --output2=data/external/orders.csv --output3=data/external/products.csv

# Generate recommendation table based association rules of market basket analysis on all data
python3 run.py generate_rules --input1=data/external/order_products__prior.csv --input2=data/external/products.csv --output=data/external/recommendations.csv

# Evaluate scores of recommendation model on test data (after generating rules from train data)
python3 run.py get_scores --input1=data/external/order_products__prior.csv --input2=data/external/orders.csv --input3=data/external/products.csv --output=data/external/scores.txt

# Store generated recommendations into RDS
python3 run.py store_RDS --input=data/external/recommendations.csv --truncate=True --rds=True
