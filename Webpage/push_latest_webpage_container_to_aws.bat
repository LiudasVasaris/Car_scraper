aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/o6e6h4k8
docker tag car_scraper_webpage:latest public.ecr.aws/o6e6h4k8/car_scraper_webpage:latest
docker push public.ecr.aws/o6e6h4k8/car_scraper_webpage:latest