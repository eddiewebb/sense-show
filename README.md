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

If wired to an LED strip you'll also visualize it.

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