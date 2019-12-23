echo "run read_all_data_md.py"
python3 read_all_data_md.py

echo "run drafter to parse data apib to json"
drafter -o save_by_drafter.json -f json temp.apib

# echo "run readMD.py"
# python3 readMD.py