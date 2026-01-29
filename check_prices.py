import json

data = json.load(open('etc/equipment.json'))
print(f'Total items: {len(data)}')

zero_price = [d for d in data if d['price'] == '0 gp' or d['price'] == '0']
print(f'Items with 0 price: {len(zero_price)}')
print('\nExamples:')
for d in zero_price[:10]:
    print(f"  {d['name']}: '{d['price']}'")
