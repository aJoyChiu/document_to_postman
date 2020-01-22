echo "run readAllDataMd.py"
python3 readAllDataMd.py $1

echo "run drafter to parse data apib to json"
drafter -o save_by_drafter.json -f json temp.apib

echo "run readMD.py"
python3 readMD.py $2