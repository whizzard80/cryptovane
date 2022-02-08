# cryptovane gadget
raspberry pi zero2w 2.13in waveshare e-paper fear and greed index update display

The cryptocurrency **fear and greed index** is a daily updating measure of the mood of the crypto market.  There is a zero to 100 scale, and four basic moods.  Extreme greed, greed, fear, and extreme fear.  This little device updates from the api and displays the current mood as well as the previous mood.

**needed:**

- raspberry pi zero 2w
- 2.13inch waveshare e-paper hat (2in13b_V3) 2 color red/black

You can modify the code to work with other models without too much trouble.


Right now I am just testing and making sure the device will work over time.

## Installation:
- Install raspbian lite to your pi zero 2w and connect it to your wireless network.
- Install the required libraries for the waveshare using the guide on the waveshare website.
- Drop cryptovane.py script into the 'examples' folder that is downloaded from waveshare's github for the device.
- Run the cryptovane.py script after you run the waveshare test script and make sure the device works and is set up properly.
It is also set up to start and refresh itself as long as power is connected by adding the script to the pi's /etc/rc.local file.


**Data Source:**

Thanks to alternative.me for providing this data and api.

https://alternative.me/crypto/fear-and-greed-index/