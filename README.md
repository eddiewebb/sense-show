# Sense Show

Simple python script to visual Sense Energy consumption & solar generation on an LED matrix.

Uses a raspberry 3 and python.

## Running it
`SENSE_USER="email" SENSE_PASSWD='5ecr!ts' sudo -E python3 main.py`

## Output

stdout will see progess bars showing usage

```
From Solar:  -0%|          | -7.00/8.00k [00:00<-1:59:59, -7.09kwatts/s]
Consumption:  12%|█▏        | 1.74k/15.0k [00:00<00:00, 1.40Mwatts/s]
From Grid:  12%|█▏        | 1.75k/15.0k [00:00<00:00, 1.67Mwatts/s]
```

## Leds

If wired to an LED strip you'll also visualize it. I bought a cheap serial style one on amazon.
[8x32 LED Panel - Individually Addressable
![8x32 led panel](https://ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&ASIN=B07P5TSKX8&Format=_SL160_&ID=AsinImage&MarketPlace=US&ServiceVersion=20070822&WS=1&tag=eddiewebb-20&language=en_US)](https://amzn.to/2RoNRGH)

### Objects
- Grid - depicted with tower on left
- House - depicted with blue house in center
- Panels - depicted by blue stripes on right
- Sun - Small yellow dot abov panels
- Energy Flow Green, Yellow or Red leds flow in the direction of energy, sized base on total watts.

### Overproducing

Orange/Yellow LEDs will flow from panels, through house (reduced by usage) and back to grid. Shown here, these yellow LEDs are moving right (solar) to left (grid)

![Overproducing](/assets/overproduce.jpg)

### Consumption

Red LEDs will flow from grid to house, and feeding panels during shade/night.  For instance here my idle house is using minimum electricity and feeding about 8 watts to panels at night. Lights are moving left (grid) to right( house and panels)

![NIghtly consumption](/assets/night.jpg)


<a href="https://www.amazon.com/gp/product/B07P5TSKX8/ref=as_li_ss_il?ie=UTF8&psc=1&linkCode=li2&tag=eddiewebb-20&linkId=e9e436b17c7329ee86c5811a60a6fb9c&language=en_US" target="_blank"><img border="0" src="//ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&ASIN=B07P5TSKX8&Format=_SL160_&ID=AsinImage&MarketPlace=US&ServiceVersion=20070822&WS=1&tag=eddiewebb-20&language=en_US" ></a><img src="https://ir-na.amazon-adsystem.com/e/ir?t=eddiewebb-20&language=en_US&l=li2&o=1&a=B07P5TSKX8" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />