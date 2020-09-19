# Weed Detection in a Jetson Nano Device
Code to deploy Artificial Intelligence algorithm in the Edge to detect weed in the field and spray herbicides just on it.

This repository will show all steps to create an algorithm and assemble a device to spray herbicides on the field.

It's a complete pipeline to detect, spray herbicides, check it and calibrate. Also there will be another camera to identify and count just the SugarCane plant.

![pipeline](/files/field_printer.png)

Inference on my trained algorithm to identify SugarCane plant and weeds with Long and short leaves:

[![Weed Detection](/files/image.png)](https://youtu.be/RE5kCkVsjOo)

For inference:
```
python3 pipeline.py
```
