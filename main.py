import cv2
import numpy as np
import torch
import torch.nn.functional as F
from skimage.filters import threshold_otsu
from skimage.morphology import binary_opening, disk

from Unet import UNet

model = UNet(2)
model.load_state_dict(torch.load(
    'Model.pth', map_location='cpu'
)['state_dict'])
for parameter in model.parameters():
    parameter.requires_grad = False
model.eval()


def resize(image):
    return cv2.resize(image, dsize=(512, 512), interpolation=cv2.INTER_CUBIC)


def evaluate(image):
    '''
    input  : RGB (png, jpg, etc.) image of neuron
    output : B&W image of segmentation, B&W image of soma
    '''
    cv2.normalize(image,  image, 0, 255, cv2.NORM_MINMAX)
    input = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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


# test_image = cv2.imread('test_img.jfif')
# output_1, output_2 = evaluate(test_image)
# plt.figure()
# plt.imshow(output_1)
# plt.figure()
# plt.imshow(output_2)
# plt.show()
