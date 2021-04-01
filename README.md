##


### Instructions:
1. Copy and Paste the list of Institutes in data/input_lists/{country_name}. (200 max)
2. Run ```scrapy crawl scholars -o {output_json_lines}.jl > output.txt -a country={country} --logfile {logFile}.txt``` repetitevely.

### To run
```bash 
scrapy crawl scholars -o oup_india.jl > output.txt -a country=india --logfile log.txt
```

- Stop when there are no more requests made by the scrapy 

#### Repetively
- Change IP address in VPN. Then rerun.


### Example:
- America
```bash
scrapy crawl scholars -o oup_america.jl > output.txt -a country=america --logfile log.txt
```

- Britain
```bash
scrapy crawl scholars -o oup_britain.jl > output.txt -a country=britain --logfile log.txt
```
- When the program ends, change IP, re-run the command.

- In short 
```bash
cat oup_temp.jl >> oup_america.jl ; rm -rf oup_temp.jl log_temp.txt; scrapy crawl scholars -o oup_temp.jl > output.txt -a country=america --logfile log_temp.txt
```


### Install Requirements:
- ```pip3 install scrapy```

### After running:
- Remove the duplicate records in the output json lines.



## Run Scrapoxy:
### Installation:
```
sudo apt-get install build-essential
sudo npm install -g scrapoxy
pip3 install scrapoxy
```

### Instructions:
- Generate "accessKeyId" and "secretAccessKey", from AWS credentials.
- Put those values in the `conf.json` file.

- Run 
```bash
scrapoxy start conf.json -d   
```

In other terminal, run
```bash
scrapy crawl scholars -o oup_america.jl > output.txt -a country=america --logfile log.txt
```

- Can access the Scrapoxy GUI working at: `localhost:8889/`. Password is set to "jujutsu". (Yes, Its from that over-hyped dope anime Jujutsu Kaisen).
- The region is set to Mumbai in conf.json.
- Currently max instances are set to 3, change as per your aws credits.
