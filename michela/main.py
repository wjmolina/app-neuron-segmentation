import numpy as np
import torch
import torch.nn.functional as F
from PIL import ImageOps
from skimage.filters import threshold_otsu
from skimage.morphology import binary_opening, disk

from michela.Unet import UNet

model = UNet(2)
model.load_state_dict(torch.load('michela/Model.pth'))
for parameter in model.parameters():
    parameter.requires_grad = False
model.eval()


def evaluate(image):
    '''
    input  : RGB (png, jpg, etc.) image of neuron
    output : B&W image of segmentation, B&W image of soma
    '''
    input = ImageOps.grayscale(image)
    input = np.reshape(input, (1, 1, 512, 512))
    input = torch.from_numpy(input)
    input = input.type(torch.FloatTensor)

    output = model(input)
    output = F.sigmoid(output).data.cpu().numpy()
    output[0, 1] = binary_opening(
        output[0, 1] > 0.8 * np.max(output[0, 1]), disk(1)
    ).astype(np.int)
    output[0, 0] = output[0, 0] > threshold_otsu(output[0, 0])

    return output[0, 0], output[0, 1]
