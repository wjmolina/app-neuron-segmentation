
# Neuron Segmentation

A U-Net by Michela Marini that segments neurons and a web application by Wilfredo Molina.

# Setup

Create a virtual environment, activate it, and execute
```
$ pip install -r requirements.txt
```
To spin-up a local server, execute
```
$ set FLASK_APP=application
$ flask run
```

# Usage

The web application takes a PNG, JPG, JPEG, or GIF file and displays three 512×512 images:

 - the original image (resized),
 - the segmented image, and
 - the soma extraction.
