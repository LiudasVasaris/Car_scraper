bucket_name="s3://car-scraper-vu-bucket/"
package_name="car-scraper-etl-plotly.zip"

rm -rf packages || true
mkdir packages
cd packages || exit

python3 -m venv venv
source venv/bin/activate

mkdir python
cd python || exit

pip install plotly -t .

rm -rf ./*dist-info

cd ..

zip -r $package_name python

aws s3 cp $package_name $bucket_name

cd ..
rm -rf packages