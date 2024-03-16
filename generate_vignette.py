import cv2
import numpy as np

# Скрипт для генерации виньетки на экране

rows, cols = 135, 240
color = 5, 9, 20, 255
vignette = np.array(color * (rows * cols)).reshape((rows, cols, 4))
X_resultant_kernel = cv2.getGaussianKernel(cols, 125)
Y_resultant_kernel = cv2.getGaussianKernel(rows, 125)
resultant_kernel = Y_resultant_kernel * X_resultant_kernel.T
mask = -resultant_kernel / resultant_kernel.min()
vignette[:, :, 3] = vignette[:, :, 3] * mask * 1.1 + 510

cv2.imwrite("assets/sprite/vignette.png", vignette)
