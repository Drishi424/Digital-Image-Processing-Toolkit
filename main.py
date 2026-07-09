import cv2
from Modules.enhancements import Enhancements
from Modules.noise_addition import Noise
from Modules.filtering import Filtering

enhancements = Enhancements()
noise = Noise()
filtering = Filtering()

image = cv2.imread("Images/sample.jpeg")



#Enhancements
negative_img = enhancements.negative(image)
cv2.imwrite("Images/output/negative.jpg", negative_img)

log_img = enhancements.log_transform(image)
cv2.imwrite("Images/output/log.jpg", log_img)

gamma_img = enhancements.gamma_transform(image, gamma=0.5)
cv2.imwrite("Images/output/gamma.jpg", gamma_img)

contrast_img = enhancements.contrast_stretch(image)
cv2.imwrite("Images/output/contrast.jpg", contrast_img)

equalized_img = enhancements.histogram_equalization(image)
cv2.imwrite("Images/output/equalized.jpg", equalized_img)

reference = cv2.imread("Images/reference.jpg")

if reference is None:
	print("Warning: reference image 'Images/reference.jpg' not found. Skipping histogram matching.")
else:
	matched_img = enhancements.histogram_matching(image, reference)
	cv2.imwrite("Images/output/matched.jpg", matched_img)



#Salt and paper
salt_img = noise.salt_pepper_noise(image, amount=0.05)
cv2.imwrite("Images/output/salt_pepper.jpg", salt_img)

gaussian_img = noise.gaussian_noise(image, mean=0, sigma=25)
cv2.imwrite("Images/output/gaussian.jpg", gaussian_img)



# Filters
mean_img = filtering.mean_filter(image, kernel_size=3)
cv2.imwrite("Images/output/mean_filter.jpg", mean_img)

median_img = filtering.median_filter(image, kernel_size=3)
cv2.imwrite("Images/output/median_filter.jpg", median_img)

gaussian_filter_img = filtering.gaussian_filter(image, kernel_size=5, sigma=1)
cv2.imwrite("Images/output/gaussian_filter.jpg", gaussian_filter_img)

print("All operations completed successfully!")