# Automation-Part-Scraper

Simple script to automatically load in google sheet with automation part numbers and scrape sites to get stock/availability info


An example of what the google sheet could look like is below:


| Component        | Description          | Vender            | BaseURL     | Discount | Price | In Stock| Expected In Stock Date
| ---------------- |:--------------------:| -----------------:|------------:|---------:|------:|--------:|------------------------:|
| c0-00dd1-d       | PLC                  | Automation Direct |See Below    |    0     |       |         |                         |
| DTI515           | RFID Reader          | IFM               |Not Required |    5     |       |         |                         |

The BaseURL is required for Automation Direct parts and should look like the following:
https://www.automationdirect.com/adc/shopping/catalog/programmable_controllers/click_plcs_(stackable_micro_brick)/plc_units/

After running, the file might look like below:

| Component        | Description          | Vender            | BaseURL     | Discount | Price | In Stock| Expected In Stock Date
| ---------------- |:--------------------:| -----------------:|------------:|---------:|------:|--------:|------------------------:|
| c0-00dd1-d       | PLC                  | Automation Direct |See Below    |    0     |  88   |  228    |                         |
| DTI515           | RFID Reader          | IFM               |Not Required |    5     |   120 |    0    |  03/17/2023             |
