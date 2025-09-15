import aiohttp
import asyncio
import json
from bs4 import BeautifulSoup
import sys

async def main():
    airports_data = {}
    try:
        with open('/home/admin/FlightTracker/atcs.json', 'r') as file:
            airports_data = json.load(file)
    except FileNotFoundError:
        pass

    if len(sys.argv) < 2 or len(sys.argv[1]) != 4:
        print("Please provide an airport code as a command-line argument.")
        return

    airport = sys.argv[1]  # Get the airport code from the command-line argument


    if airport in airports_data.get('airports', {}):
        # Fetch name and ID from the atcs.json file
        list = airports_data['airports'][airport]
        for it in list:
            print(f"{it['name']} : {it['id']}")
    else:
        url = f'https://www.liveatc.net/search/?icao={airport}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')
        onclick_elements = soup.find_all(attrs={"onclick": True})

        onclick_data = []
        for element in onclick_elements:
            name_element = element.find_previous('td', {'bgcolor': 'lightblue'})
            name = name_element.text.strip() if name_element else None
            onclick = element['onclick']
            if "myHTML5Popup" in onclick:
                onclick_data.append({
                    'onclick': onclick,
                    'name': name
                })
        dict = []
        for data in onclick_data:
            onclick = data['onclick']
            start_index = onclick.index("'") + 1
            end_index = onclick.index("'", start_index)
            value = onclick[start_index:end_index]
            name = data['name']
            bo = {
                'name': name,
                'id': value
            }
            dict.append(bo)
        airports_data["airports"][airport] = dict
            
        with open('/home/admin/FlightTracker/atcs.json', 'w') as file:
            json.dump(airports_data, file, indent=4)

        for it in dict:
            print(f"{it['name']} : {it['id']}")
        print()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())