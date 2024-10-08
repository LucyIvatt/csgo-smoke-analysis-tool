# CSGO-Utility-Analysis-Tool
Tool created as part of a dissertation at the University of York on analysing the quality of smoke grenade usage in CS:GO. 

Consists of 4 parts - Web scraping, parsing, analysis and visualisations​.
- Python logging module used throughout the scripts​
- Configuration file for file locations, visualisation colours etc.​

## Limitations
- Restricted only to mirage to reduce effort required for manual collection of doorways / common locations
- Inaccurate for one-way smokes

# Web Scraping
Python script utilising Selenium WebDriver (Browser automation)​ - Downloads every demo file from HLTV from 29/01/2020​

1. Navigates to HLTV events page with the correct filters on (LAN tournaments & Date range)​
2. Navigates to every event (using xPaths) and opens its results page and saves the URLs of all matches (unless the map mirage was not played).​
3. Clicks the GOTV button to download the file - Each match has a unique ID, this is saved after each download to ensure if the program closed unexpectedly, it would not try to redownload matches.​
4. Extracts downloaded demo files​
5. Extracts all demos into the same directory. Any that are not mirage are deleted. _Some other maps might be in there as if the match was a best of three and one of the maps was mirage, it will also download the 1-2 other maps that were played.​_

**Logging Example: **

<img width="698" alt="image" src="https://github.com/user-attachments/assets/9e530f72-f64d-4c95-94ab-b8920a024a31">

# Parsing
Python script utilising the [awpy python package](https://github.com/pnxenopoulos/awpy) (now updated for CS2). CS:GO demos use Google’s Protocol Buffers to serialize the game objects. The awpy package allows you to parse these files into python dictionaries or output to json files.​

The script generates an overall `dataset.json` file containing all the relevant information from every match. ​

Iterates through all `.demo` files extracted previously​ and for each one:
1. Parses them into a python dictionary using awpy​
2. Extracts only the relevant information about each smoke grenade used and discards the rest.​
3. Appends the smoke grenade information to the `dataset.json` file.​

**Final Dataset Breakdown:​**

| Demos (matches) | Rounds  | Smokes  | Players  | Teams |
|-----------------|---------|---------|----------|-------|
| 229             | 6,011   | 35,177  | 658      | 145   |

**Grenade Info Example**

```json
{
    "demoID": "BLAST-Premier-Fall-Final-2021-astralis-vs-faze-bo3-mirage",
    "throwerName": "karrigan",
    "throwerTeam": "FaZe Clan",
    "throwerSide": "T",
    "roundNum": 5,
    "throwTime": "01:54",
    "grenadeX": -224.5,
    "grenadeY": -503.5625,
    "grenadeZ": -165.875,
    "roundWon": false
}
```

# Analysis
Python script primarily utilising NumPy. The program uses a simplified 2D model, where smokes are circles and doorways are lines. The smokes’ locations have been collected using the web scraper and parser. The doorway locations were manually collected in game and stored in a separate json file. 2 classes were created - one for the Doorways and one for the Smokes.​

1. Loads smokes in by converting each smoke from the `dataset.json` file into the `Smoke` python object. ​
2. Loads doorways in by converting each doorway from the `doorway.json` file into the `Doorway` python object.​
3. Assigns the smoke grenades to the doorway they are within the detection area of (pre-determined size from a config file). Discards any not in any doorway’s range.​
4. Calculates the coverage for each of the valid smokes. Unit tests written for coverage calculations.

![AbstractRepresentationExample](https://github.com/user-attachments/assets/ab66d89b-9d25-4c31-8f1e-3b417f33ce6f)
![Smoke Doorway Cases](https://github.com/user-attachments/assets/effa6dc1-53bd-4c37-8ffc-476e74b65c16)

# Visualisations
Python script primarily utilising matplotlib, scipy and seaborn.​

Using the coverage statistics determined earlier, creates a set of different diagrams that can be used in different industry contexts.

## Collected Data
### Smoke Locations
![scatter plot heatmap](https://github.com/user-attachments/assets/9830a8b4-37a7-4b76-8acf-2b70e6839bf0)

### Doorway Locations
![doorway name locations drawio](https://github.com/user-attachments/assets/f8f47e28-0065-41b2-ba91-ca622ae1c186)

## Use Cases
### Match Example
- Possible application for post match analysis and visualisations of this nature e.g.

![FazeSmokes](https://github.com/user-attachments/assets/dc9e2ece-c00c-4c81-aab7-15a96221e0ec)

| Player      | Success Rate (%) |
|-------------|------------------|
| Twistzz     | 86.67            |
| olofmeister | 75.00            |
| broky       | 83.33            |
| rain        | 84.62            |
| karrigan    | 50.00            |
| **Team Success Rate (%)** | **80.00** |

### Player Averages
- Possible application for training / focusing on less accurate smoke locations
![BlameFPlayerViswpic](https://github.com/user-attachments/assets/5f7667bc-440a-4b14-8ae4-889c36a00c1d)






