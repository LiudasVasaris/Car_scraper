#!/bin/bash
bucket_name="s3://car-scraper-vu-bucket/code/"

zip -r "ETL" ETL
zip -r "Scraper" Scraper

aws s3 cp ETL.zip $bucket_name
aws s3 cp Scraper.zip $bucket_name

rm -rf ETL.zip
rm -rf Scraper.zip