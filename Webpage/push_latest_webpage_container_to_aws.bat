aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 189212062998.dkr.ecr.eu-central-1.amazonaws.com
docker tag car_scraper_webpage:latest 189212062998.dkr.ecr.eu-central-1.amazonaws.com/car_scraper_webpage:latest
docker push 189212062998.dkr.ecr.eu-central-1.amazonaws.com/car_scraper_webpage:latest