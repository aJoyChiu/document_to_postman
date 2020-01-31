echo "run splitDataStructure.py"
python3 splitDataStructure.py $1 $2

echo "run drafter to parse data apib to json"
drafter -o save_by_drafter.json -f json temp.apib

echo "run readMD.py"
python3 readMD.py $2
