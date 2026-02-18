# survey_ml_rso2024 -- Survey Mode: A Review of Machine Learning in Resident Space Object Detection and Characterization

**Authors:** Konstantinos Tsaprailis, George Choumos, Vaios Lappas, Charalampos Kontoes
**Venue:** AIAA SciTech Forum 2024 (AIAA 2024-2065)
**DOI:** https://doi.org/10.2514/6.2024-2065

---

## sec0 -- Abstract

[sec0_p1] The number of Resident Space Objects (RSO) in Earth's orbit has been rising steadily since the first satellite was launched. The need to protect functioning space assets from collisions with space debris is becoming more urgent as the number of debris has increased considerably partly due to a number of anti-satellite weapons tests which have created large debris clouds. Operational satellites have also been increasing exponentially due to the planned and already launched constellations. The field of Space Surveillance and Tracking (SST) has been established to try to mitigate the risks of collisions, using sensors such as radars and optical telescopes to detect, characterize, and catalog RSOs. This paper aims to provide a survey of the Machine Learning based methods that are being used to detect and characterize RSOs while also analyzing some non-machine learning approaches.

---

## sec1 -- Introduction

[sec1_p1] "Space," [the Hitchhiker's Guide to the Galaxy] says, "is big. Really big. You just won't believe how vastly hugely mindbogglingly big it is. I mean you may think it's a long way down the road to the chemist, but that's just peanuts to space." This vastness is now increasingly occupied by a growing number of Resident Space Objects (RSOs), a consequence of the continuous increase in space launches and anti-satellite weapon tests. Such an increase in Earth's orbit occupancy not only highlights the enormity of space but also underscores the escalating risks both to operational space assets (due to the increased risk of collision with other assets or debris that would render them unusable) but also to the space industry as a whole by increasing the probability of the Kessler Syndrome, a theoretical scenario where each RSO collision leads to the creation of more debris which in turn increases the number of collisions until the probability of collision is so high that would render the launch and operation of satellites impossible.

[sec1_p2] This growing population of RSOs presents significant challenges for the field of Space Situational Awareness (SSA), which tries to monitor and catalog this large number of objects in order to timely manage potential conjunctions. Space Surveillance and Tracking is the field of SSA that deals with artificial objects and encompasses a number of applications such as RSO detection and classification, RSO characterization, orbit determination, conjunction analysis, reentry prediction and RSO catalog creation and maintenance.

[sec1_p3] In this paper we will focus on two applications: RSO detection and RSO characterization. RSO detection is the application of identifying and tracking objects in space, while RSO characterization is the application of obtaining detailed information about the objects' physical properties and potential functionality. Machine learning and deep learning are fields that have shown great promise in improving the accuracy of algorithms in many different domains. Given this widespread adoption, the goal is for the paper to serve as an overview on the use of machine learning based techniques for these two applications by surveying the available literature and grouping them by the algorithms and datasets used so that researchers in the field interested in applying ML and DL based techniques in their work have a starting point in what has already worked and how they can expand on that.

[sec1_p4] The paper first presents the methodology used to query for published papers on the subjects, filtered for the subset of interest. Then an analysis is performed of the methods used in each application. Due to the nature of the applications, the majority of papers retrieved were found to use data from optical telescopes, hence the field of computer vision is dominating the methods used to detect and characterize RSOs. Traditional techniques of image processing were being used almost exclusively up to the last 6-7 years, while recently ML-based and more specifically methods utilizing artificial neural networks are beginning to eclipse the rest.

---

## sec2 -- Literature Survey Methodology

[sec2_p1] The survey of the literature was implemented by utilizing the advanced search options of the Google Scholar platform. Google Scholar is a search engine specifically for scholarly literature that allows the use of complex queries to retrieve very targeted results.

[sec2_p2] In our case we were interested in finding papers that were using machine learning or deep learning techniques and applications related to space surveillance and space situational awareness so we used broad terms to try to retrieve as many papers as possible. The actual terms and query that were used are the following: ("machine learning" OR "deep learning") AND ("satellite collision" OR "collision avoidance" OR "orbit prediction" OR "space situational awareness" OR "space surveillance" OR "kessler syndrome").

[sec2_p3] In order to improve the workflow an open source tool called sort-google-scholar was used which programmatically queries the Google Scholar API, fetches and sorts the results and saves them in comma separated values (csv) files. The tool also allows for a limit to the number of results that are returned, which we set to 300. The tool was run on a yearly basis starting in 2007 up until September 2023.

[sec2_p4] The results represent the evolution of interest in the field of SSA/SST over time. The number of papers before 2010 is very low while as the 2010s progress the number of papers steadily increase and after 2018 we have an almost exponential increase (true number of papers cannot be seen due to the 300 papers limit set in the sort-google-scholar tool).

[Figure 1: Number of papers related to SSA/SST and ML/DL.]

[sec2_p5] The next review step was going over each of the paper and by analyzing it, classify it in 5 categories from highly relevant/relevant (meaning that the paper is using machine learning methods in the context of an SSA/SST specific application) to review papers, a "maybe" category for papers that either don't use machine learning techniques or are using but it's not a relevant application (e.g. ML for predicting Space Weather) to finally an irrelevant category for papers that briefly mentioned one of the terms used in the query but are not related to the domain.

[Figure 2: Number of papers based on relevance to SSA/SST domains and ML/DL usage.]

[sec2_p6] Finally once the relevance sorting had been completed the list of very relevant/relevant papers was used to further group them by application. The popularity of each application highlights the different applications that have evolved over time in the field of SSA/SST. From this list RSO characterization and RSO detection were chosen for this paper for their closely related thematic.

[Figure 3: A ranking of SSA/SST applications by the number of papers found.]

---

## sec3 -- RSO Detection

[sec3_p1] RSO detection is the process of identifying and locating objects in space, such as satellites, debris, and other celestial bodies. This involves using ground-based or space-based sensors, like radar and optical telescopes, to continuously monitor the space environment and track the positions and trajectories of RSOs. The primary goal of RSO detection is to locate and segment the part of the sensor output that contains space objects. This review focuses on the detection of space objects in optical telescope images and specifically when objects are non-resolved (meaning the satellite features cannot be distinguished from the image as they span only a few pixels).

[sec3_p2] Detecting the space objects is the first task in a series of processing steps in order to maintain an up-to-date catalog of space objects, which is essential for providing the necessary SST services such as collision avoidance, fragmentation and reentry analysis, satellite maneuvers and understanding the overall orbital congestion.

---

### sec3.1 -- Non-Machine Learning Processing Methods

[sec3.1_p1] As a first step we will aggregate all the methods for detecting RSOs that don't use machine learning techniques. It should be noted that this should not be treated as an exhaustive list of all classical image processing methods since the query that was performed included specifically the terms machine learning or deep learning, so the papers that will be presented here are a by-product of this search.

[sec3.1_p2] Starting with the first paper in 2005, Edith Stoveken et al. presented a few methods to specifically detect space debris in optical telescope images (vs stars and artifacts - hot/dead pixels and cosmic ray events). The first method is utilizing a star catalog to create a mask that removes the known stars in the captured image, then the objects of interest remain. A second method is using the object characteristics, to distinguish between point and streak like objects. The use of a series of images from the same region of the sky can be used to calculate the mean value of all images in each pixel position which can create a mask that only highlights stars. Subtracting this mask from the following images removes stars and moving objects of interest remain. A final method is presented which requires a sequence of at least three images, where the apparent velocity is calculated from the apparent shift in the object from the first to the second, then it is extrapolated to where it is expected in the third image. If that object is found it can be considered an object of interest.

[sec3.1_p3] Li, K. et al in 2009 introduced the concept of using Mathematical Morphology (MM) in space debris detection which is a set of four basic operators (erosion, dilation, opening and closing) that can be applied at images to process geometrical structures. The idea behind these operators is the use of a secondary matrix (called "probe") that is then applied in each pixel of the telescope image, with each operator performing a task in the specific domain. For example applying the erosion operator in the telescope images can remove object effects that are smaller than the selected probe size. On the other hand applying the dilation operator will augment objects in the image that are smaller than the probe. Finally the opening and closing operators are used to remove a specific type of noise called salt and pepper that is present on binary images.

[sec3.1_p4] In 2013 Sun, R.-Y. et al capitalized on the Mathematical Morphology techniques by publishing a full pipeline of 5 steps to detect and localize space debris in optical telescope images: (1) Bias/dark/flat calibration (not usually needed in space debris detection as mentioned by authors); (3) Mathematical morphology filtering and enhancement (this is the core of the process, using the top-hat transformation operator a non-linear high-pass filter is created which removes the smear noise and improves the image quality); (4) Global thresholding (a threshold value is chosen and a bit mask is produced); (5) Subtraction and segmentation (the mask is subtracted from the image and segments are calculated in the resulting image by identifying areas with at least 8 connected pixels using the two pass union-finding algorithm); (6) Determining the image positions in pixel coordinates (using a point spread function (PSF) fitting technique).

[Figure 4: The effect of the top-hat transformation which removes the smear noise and improves the image quality. Work by Sun, R.-Y. et al. Left: The original image. Right: Image after it has been transformed with a structure element with size 7 x 1 pixels.]

[sec3.1_p5] Progressing further on the concept of a multi-step processing system using Mathematical Morphology operators, Xi, J. et al. proposed an algorithm that first removes the image background by using a low pass filter template (of size 6x6), then performs adaptive threshold segmentation in two consecutive images which produces binary images. Then the first image is subtracted from the second which removes stars and what remains is debris and some extra noise points around where stars were. The next step is the "twice morphologic filtering" where two successive "open" operators are applied, with a logic "AND" operation between the output of the first open operation and the initial binary image. The final step is the application of a Frame Correlative Debris Detection Algorithm to the candidate debris regions, which tries to detect the debris in three consecutive images, by calculating a velocity from a candidate debris in the first and the second images, then looking for the debris in the expected region in the third image based on the calculated velocity. This whole pipeline is also used as a tracking algorithm by also employing Kalman filtering.

[sec3.1_p6] The same scientific team followed up in 2015 with a new paper that proposes a new multi-step process for detecting debris. The method is based on 5 consecutive images of the sky region of interest. As a first step a maximum projection image is calculated where each pixel value is the maximum value of the five images in each pixel position. Then the mean intensity of the five images is calculated and removed from the maximum projection image to remove the stars and noise. Twice morphological filtering is applied to connect different debris candidate regions and eliminate noise points. A Hough Transformation converts all detected streaks to points and thus the start and end points of the streak are detected which calculates the debris region. Finally a Particle Filter based on Bayesian inferences and Monte Carlo simulations is used which locates the debris in the initial frames and is then used to detect the debris in the latter images, reducing the calculation cost.

[Figure 5: The maximum projection technique. Each pixel value is the maximum value of the five images in each pixel position. Then the mean intensity of the five images is calculated and removed from the maximum projection image to remove the stars and noise. Work by Xi, J. et al.]

[sec3.1_p7] In another work a team used a four step process based on Mathematical Morphology. First smear noise is eliminated using a TopHat operator, then artifacts - byproduct of the first operation - are removed by a second TopHat operation with a different orientation of the structural element (probe). The third step is the calculation of a median frame of consecutive images upon which a threshold (calculated as 3 background fluctuant levels above that of smoothed background) is used to highlight the candidate regions. Because the Mathematical Morphology processes produce a lot of noise which increases the number of false positives a specific binary morphological filter utilizing a-priori properties of object point shapes is used to reduce it. Finally groups with sets of 5 connected pixels are highlighted as candidates. The candidate objects are taken in the initial raw consecutive images, and false positives are further removed by comparing the candidate debris position vs the initial images and removing the ones who are in the neighborhood.

[sec3.1_p8] In the following work Nunez, J. et al. proposed using an image deconvolution technique, and specifically the iterative Richardson-Lucy (R-L) deconvolution method to clean up and enhance the stars and debris in optical images such that other debris detection algorithms can be applied more efficiently.

[sec3.1_p9] Feuge-Miller, B. et al used a statistical method for detecting and tracking objects (they reference them as Anthropogenic Space Objects) in telescope star images. The methodology is based on a-contrario analysis, stating that features in the images that cannot be attributed to noise from hardware, atmosphere or the background celestial environment should be (anthropogenic) space objects. The approach involves several steps: hypothesis testing, detection pipeline, astrometry, and orbit determination. The hypothesis testing is based on defining measurable regions and applying significance thresholds to control false positives. The detection pipeline involves evaluating derivative vector fields, removing likely star features, applying track association procedures, and filtering steps. Astrometry involves transforming image-frame coordinates into right ascension and declination angles for potential space objects. Finally orbit determination compares the precision and accuracy of measurements against known state ephemerides. The method is tested against real data.

---

### sec3.2 -- Machine Learning Based Methods

[sec3.2_p1] The papers that have been analyzed were classified in the following categories based on the method used: (1) Custom feature generation with additional ML model, (2) Custom Neural Networks either built from scratch, or with major architecture adaptations, (3) Existing Neural Network architectures used either as is or with small adaptations, (4) Dataset papers, and (5) Dataset re-labelling methods.

---

#### sec3.2.1 -- Custom Feature Generation with ML Model

[sec3.2.1_p1] The following list of papers contain methods which use a combination of methods for creating features from the raw images before feeding these features in an ML model. This is in contrast to the majority of papers using neural network based models where the feature extraction step is part of the model (especially when using convolutional neural networks).

[sec3.2.1_p2] The first paper that uses an ML method in our list was proposed in 2014 by Huang, T et al. They are using telescope images, which they break up into blocks. Then each block is processed and the following features are produced: a) overall expectation: the mean value of the pixel intensities in the image block, b) overall variance: measures how much the pixel intensities vary from the overall expectation, c) overall skewness: describes the asymmetry of the distribution of pixel intensities in an image block and d) duty ratio: the concept is derived from digital circuits theory and is defined as the ratio of the event duration to the total period of a signal. These features are used to train a Naive Bayes Classifier which is used to classify each block into categories (target, smear, or background). As an extra step a joint decision process is run which re-evaluates these classifications by considering the classifications of adjacent blocks, enhancing the accuracy and reliability of the target detection.

[Figure 6: Flow diagram of the joint decision and Naive Bayes algorithm (JD-NB) for object detection.]

[sec3.2.1_p3] Xi, J., et al. tried a different approach of using image preprocessing techniques (such as maximum projection) for hot pixel and background removal, but also for star removal (using star detection and segmentation) and space debris candidate region proposal. Then a dedicated neural network called SDdecNet (based on the LeNet5 architecture) has been developed to detect and classify the candidate regions. Finally this SDdecNet model infers every candidate region on whether it's space debris or not.

[sec3.2.1_p4] Du, Y. et al. tried another combined approach of using classical image processing techniques with machine learning methods. The background and smear effect are removed with specific thresholds, then in the specific application the stars vs debris (appearing as streaks) are identified using a machine learning model based on Support Vector Machines (SVMs).

[sec3.2.1_p5] Montanaro A. et al proposed a new object detection method that uses a stacking method before the images are processed by a simple neural network with three convolutional layers. Specifically, the stacking method improves the signal over background ratio (SBR) by overlapping many frames shifted by a specific number of pixels depending on the speed and direction of the observed object. The model was trained using simulated data generation by the EUSO Simulation and Analysis Framework (ESAF).

[sec3.2.1_p6] Zhang, X. et al created a model that tries to detect weak debris targets against a background of dense stars with long tails resulting from long exposure times. They are using simulated data and processing them initially with a rectangular fitting technique to aggregate trailing images and reduce noise influence. This fitting is based on the predictable angle and length of the star trails. Once the star tails are aggregated, the next step involves recognizing semi-occluded targets. This is done by analyzing the occluded state of the target and using a fully connected network (FCN) to classify the semi-occluded scenes and extract the semi-occluded images. The final step integrates traditional multi-frame association with the processed single-frame images.

[sec3.2.1_p7] Lin, B. et al created a mixed classic method and CNN based pipeline for small target detection against real star image data. The pipeline starts by preprocessing the images to remove the background by splitting the image into smaller grids. For each grid the histogram of pixel values is clipped using a custom method with the median and mean values. A binarization step is followed to separate the background from the foreground (stars and objects). Then a region proposal search is executed using the foreground segments to create candidate regions around the points of interest with variable sizes for further processing. Finally these candidate regions are input into a custom CNN (called SF-CNN) which performs the final classification. As a last step to remove redundant targets in the same proposal a non-maximum suppression operation is performed.

---

#### sec3.2.2 -- Custom Neural Networks

[sec3.2.2_p1] The second category includes models that have been built from scratch or that are using an established architecture but is augmented with new modules and components to adapt them to the space object detection task.

[sec3.2.2_p2] Xiang, Y. et al. used a custom convolutional neural network architecture named FGBNN which processes images by splitting them into a 14x14 pixel grid, then detects whether there's debris in each grid cell. The authors highlight the fast training and inference speed of the model as the main advantage due to the smaller number of parameters compared to similar detection models.

[Figure 7: The pipeline of the FGBNN. The image split into 14x14 grids by the FGBNN and for each grid predict the class probabilities. If the grid with space debris, the predicted value is one. The grids with space debris labeled with red. Work by Xiang, Y. et al.]

[sec3.2.2_p3] Guo, X. et al created a CNN model for space target segmentation based on an encoder-decoder structure incorporating channel and spatial attention modules to enhance the feature fusion and focus on the relevant parts of the image. The method also performs a post processing to calculate the centroid of the detected targets. The model has been trained in a simulated dataset that was created by the authors by adding target blocks to images, with a variety of signal-to-noise ratios (SNR).

[Figure 8: The proposed encoder-decoder structure architecture with the segmentation networks. Each cube represents a multi-channel feature map. CAM and SAM are channel attention module and spatial attention module respectively.]

[sec3.2.2_p4] Kyselica, D. et al tackled the problem of trying to predict the current position of a space object in an image sequence, given the previous positions. The model is based on a Long Short-Term Memory (LSTM) neural network. It was trained on synthetic data generated by the authors and validated with real telescope images.

[sec3.2.2_p5] Fitzgerald, G. et al created a custom model to detect and track GEO satellites in wide field of view (WFOV) imaging systems. The problem with images produced by these systems is the small footprint of the object in the image as well as the inherent noise of the sensor. The system is composed of two models, the HARP-Net and LOC-Net. The High Area Region Proposal Network (HARP-Net) is the first stage, which uses a 2D convolutional neural network (CNN) with stacked temporal frames. HARP-Net generates a heatmap of Regions of Interest (ROIs) by leveraging the temporal features in the sequential frames. The LOC-Net, which incorporates elements of YOLOv5, uses the heatmap to predict bounding boxes of the RSOs. It works on the cropped areas from the heatmap that contain high-value ROI pixels.

[Figure 9: Various RSOs of different orbital regimes and resulting morphology. A cluster of GEO RSOs are annotated in (A), a low-light MEO RSO is highlighted in (B), and a bright streaking LEO RSO is shown in (C). Taken from work by Fitzgerald, G. et al.]

[sec3.2.2_p6] Ibele, A. et al also created a method to detect space objects in wide field of view (WFOV) imaging systems. The authors used a custom CNN based on the ResNet architecture with modifications to focus on the highest-resolution feature map in the feature pyramid, simplify the architecture, and optimize it for faster training and inference.

[sec3.2.2_p7] Tao, J. et al created a custom CNN based model called SDebrisNet to detect space debris in telescope video sequences. The model is composed of several modules, a spatial and a temporal feature extraction module, a spatial feature enhancement module and finally a spatial-temporal feature fusion module. The Spatial Feature Extraction module is based on the MobileNetV3 architecture and as the name suggests it extracts spatial features from the image. Then the Spatial Feature Enhancement module includes four spatial feature enhancement networks designed to strengthen the spatial details of small objects. Then after the spatial features have been enhanced the Temporal Feature Extraction module receives the high-level feature maps of each frame, and processes them with a self-attention method to learn spatiotemporal coherence from consecutive frames, outputting temporal salient high-level features. Finally the Spatial-Temporal Feature Fusion module fuses the enhanced spatial features and temporal features, resulting in saliency images for each frame in the video clip. The last step involves the centroid calculation of the detected object by calculating the weighted centroid coordinate of each pixel in the salient region based on its intensity. The model has been trained and tested in 45 synthetic and 2 real telescope videos.

[Figure 10: Detailed illustration of the proposed saliency detection network (SDebrisNet), which consists of the spatial feature extraction module, spatial feature enhancement module, temporal feature extraction module, and saliency prediction module. Work by Tao, J. et al.]

[sec3.2.2_p8] Yuan, Y. et al proposed an enhanced version of the YOLOv5 architecture to detect small and weak space objects in simulated telescope images. The proposed version has the following added modules: a) The Cross-Layer Context Fusion Module (CCFM) enhances the feature information and network identification ability. It operates through multiple parallel branches to learn context information at different scales, b) The Adaptive Weighting Module (AWM) is designed to map small-scale features sequentially to the features of the previous layer, assisting the CCFM in further enhancing the expression of features and c) The Spatial Information Enhancement Module (SIEM) is key in capturing multi-directional spatial environmental information, particularly vital for small object detection where spatial information is easily lost. Finally they are also utilizing a new data augmentation technique (Contrast Mosaic) to enhance data complexity and diversity.

[Figure 11: The framework of the CS-YOLOv5 model for small and weak. Yuan, Y. et al.]

---

#### sec3.2.3 -- Existing Neural Network Architectures

[sec3.2.3_p1] In the third category, the authors of the papers have used the established architectures from computer vision models and either used them as-is or with minimal changes.

[sec3.2.3_p2] In 2019 Varela, L. et al. explored the usage of convolutional neural networks (CNN), which are a type of neural network architecture that has shown great success in image processing tasks. The main advantage of the CNNs lies in the fact that handcrafting features are no longer necessary for creating an algorithm, but rather the training process itself produces these features which are usually detected by the first layers of the network. An even more useful type of CNNs are Region Based CNNs (R-CNNs) which also output the region in the image where the object of interest lies, by iteratively searching all parts of the image and feeding each part in a dedicated CNN that can apply a label to the frame-part. This architecture has the disadvantage of having to check the image versus multiple sizes which significantly increases the performance required. A third architecture is the YOLO architecture, which instead of looking at the image multiple times, instead tries to predict bounding boxes in the areas of the image that seem relevant. By looking at the image only once, it increases the performance of the system. The system proposed uses the v2 of the YOLO architecture which has a number of improvements compared to the first one.

[sec3.2.3_p3] Similarly Temple, D. in 2019 used the v3 of the YOLO architecture for detecting RSOs in a vast network of sensors owned by the company. Additionally a Kalman filter is used to track the RSOs over time in different images.

[sec3.2.3_p4] Another team also used the YOLO v2 architecture with a dataset from the Pulkovo Observatory to detect objects in two types of images: a) fixed camera -- constant background and b) moving camera -- changing background.

[sec3.2.3_p5] De Vittori, A. et al created a system that aims to predict and extract the position and shape of space object tracklets from telescope images, focusing on real-time processing with high accuracy. The system was trained on both synthetic images and real images. Synthetic images were created with a new Python application developed in-house. The app uses TLE (Two-Line Element) files of known Low Earth Orbit (LEO) space objects to simulate their transits across a simulated night sky. The output is dual-tone (black and white) images representing the night sky with white tracklets. In addition to the synthetic, real images were also used to test the system. The model at the heart of the system is a neural network based on the U-Net architecture which performs the image segmentation to highlight the detected tracklets.

[Figure 12: The U-Net image segmentation architecture.]

[sec3.2.3_p6] Mastrofini, M. et al created a new algorithm called Brightest Objects Sky Segmentation (BOSS) designed to focus on the brightest objects in optical sensor images, which can be stars for attitude determination or resident space objects (RSOs) for space surveillance tasks. The dataset was created from three different sources. Real night sky acquisition campaigns, simulated images using the Stellarium software and images obtained from a high fidelity star tracker image simulator which leads to strong model generalization abilities. The BOSS algorithm is utilizing a U-Net based neural network which is trained to output the probability of each pixel in the image being a foreground object (star, RSO etc). Finally a custom clustering algorithm groups the pixels and prioritizes the most significant clusters based on their dimension, energy, and maximum energy value.

[Figure 13: Real vs synthetic data comparison: real night sky image (on the left) and Stellarium-generated night sky (on the right). Work by Mastrofini, M. et al.]

[sec3.2.3_p7] Su, S. et al used a custom convolutional neural network inspired by the Faster RCNN architecture to detect dim and small space objects in star images, and a k-means clustering algorithm to locate the centroid of the detected objects. The clustering algorithm involves bilinear interpolation to increase the target's pixel count, segmentation of the target and background, and iterative target region window adjustment to minimize noise-induced errors. The model was trained on simulated data, semi-real data (simulated mixed with real) and fully real data.

[sec3.2.3_p8] Jordan, J. et al created a CNN model based around the MobileNetV2 architecture for efficient object detection. They created a custom synthetic dataset to train the model, and was tested on real and synthetic data. The focus of the method is to create a model that is efficient to be potentially used in mobile ground telescopes.

[sec3.2.3_p9] Dai, Y. et al created an object detection model based on the YOLOv2 architecture specifically for GEO objects which tend to be fainter in optical images. The method works on image sequences and leverages a post processing step called the CFS technique which utilizes the principle of moving continuity and trajectory consistency of space objects across frames. Specifically space objects are expected to move with uniform speed along a straight-line trajectory. The CFS method utilizes this characteristic to filter and supplement the detection results. The model was trained on data collected from the Kelvins SpotGEO Challenge.

[Figure 14: An example of image sequence of GEO objects: (a-e) five frame images within a sequence that contain six objects; (f) the source positions are shown by the cross symbols in different colors. Dataset from the work by Dai, Y. et al.]

---

#### sec3.2.4 -- Dataset Papers

[sec3.2.4_p1] During our search the following paper was found which created new datasets specifically for space object detection. Fletcher J. et al. named the dataset SatNet which includes 104,100 annotated images captured in rate-track mode against GEO targets. The authors mention some of the shortcomings (especially due to human annotation biases such that results in a large distribution of brighter objects, objects that are shown better in a dimmer background, or objects that occur more often) and have created a new simulation software and with it a new dataset called SatSim which includes 50,000 images from each of 20 simulated sensors. The authors also trained a neural network based on the YOLO v3 model architecture and compared it with a popular open source software called SExtractor that also supports object detection in sky images.

[sec3.2.4_p2] Chen, Z. et al created a new framework called simulation-augmented benchmarking framework for RSO detection (SAB-RSOD). They used a simulation system to create data (stars and streaks of RSO) using real sensor parameters. Then the dataset was augmented with real world images from a star tracker (Swarm star tracker). The dataset is used to train a YOLO and a Faster RCNN model as well as their own model based around the U-Net architecture.

---

#### sec3.2.5 -- Relabelling Methods

[sec3.2.5_p1] Finally the following two papers were found which include innovative methods to tackle the problem of unlabeled or noisy data. Data annotation requires time, money and expertise which makes it hard and expensive to create high quality datasets. With the following work the authors tried to find ways to overcome these obstacles.

[sec3.2.5_p2] Dimitrescu, F. et al created a novel system which recursively re-annotates incomplete astronomical data (i.e. not all visible objects are annotated). They used a two model system with a first object detection module based on the Faster R-CNN architecture with a ResNet-18 backbone and the second is a custom CNN classifier. The method works by parsing the image through the detection phase for candidate region generation, which are then fed into the classifier. Objects with a high classification confidence are added into the training dataset to enhance the model performance.

[Figure 15: Overview of the re-annotation model by Dimitrescu, F. et al. It consists of 3 stages: the detection stage, in which the object detection model is trained and the objects of interest are detected on the validation set; the cropping stage, in which crops for the classifier are extracted based on the detections from the previous stage; the re-annotations stage in which the classifier is trained on the extracted crops of the objects of interest from the train set, as well as noise, and then used to detect which objects found in the detection stage are valid. In the last stage, the valid detected objects are also saved to be used in the next re-annotation step.]

[sec3.2.5_p3] Li, H. et al created a method to relabel noisy data in space debris detection datasets (such as stars miss-labeled as debris). The method begins by denoising and smoothing the background (removing hot pixels, flicker noise, and evening out uneven background). Then two identical CNNs are trained on the same dataset. They make their predictions on the same samples. Then each network's predictions are used as extra information to correct the noisy labels of the other network, thus refining it during training. The method was tested on a mix of real and simulated data.

---

## sec4 -- RSO Characterization

[sec4_p1] Resident Space Object (RSO) characterization is the process of obtaining detailed information about the physical properties, functional capabilities, and potential behaviors of objects orbiting Earth, such as satellites and space debris. This process helps maintain the safety and operational efficiency of space assets by determining an object's size, shape, mass, orientation, reflectivity, and material composition. RSO characterization may also assess the operational status of objects, such as differentiating between active satellites, non-functional satellites, or space debris.

---

### sec4.1 -- Classical Image Processing Methods

[sec4.1_p1] In this part, similar to the classical image processing methods of the RSO detection application, we present general image processing methods used in RSO characterization which do not use machine learning based techniques.

[sec4.1_p2] Starting in 2011, Chaudhary, A. et al created a technique for characterizing RSOs called RSO fingerprinting using time series of brightness data in multiple wavelengths. It represents an RSO (specifically working with satellites) as a model being composed of two separate facets, the body and the solar panels. Then it uses the Lx technique, which works on the hyperspectral brightness data by trying to match features and extract information about the RSO in more detail in each level. For L0 it tries to match features such as overall size, type, gross brightness, and the basic shape and position of principal specular glints (bright spots due to reflection). L1 features comprise the geometric shape of the signature brightness, color indices, and variations due to the angle of sunlight (sub-solar angle). The Level 2 level distinguishes the light contributions of the solar panel and the main body of the RSO. It looks at the sloping regions or bifurcations in the signature brightness and color, helping to separate and identify the contributions of different components of the RSO. Finally Level 3 tracks the temporal evolution of the fractional abundance of the solar panel and the body of the RSO. This level provides insights into the mechanical stability and attitude of the RSO.

[sec4.1_p3] In 2014, Linares, R. et al used light curves and angle data (which are time series produced by optical telescope observations, the light curves representing the time series of the brightness and angles representing the time series of topocentric azimuth and elevation of the RSO) to identify the most probable shape of an unknown resident space object along with its associated rotational and translational states. They used two techniques, a multiple-model adaptive estimation (MMAE) and an Unscented Kalman Filter (UKF). MMAE was used to estimate the most probable shape of the space object (from a bank of possible shapes, but can choose the best model that fits the actual shape when the true shape is not in the bank). The Unscented Kalman Filter was used to estimate the rotational and translational states based on fusing angles and light curve data, along with their associated models. Simulated data were used to verify the method.

---

### sec4.2 -- Machine Learning Based Methods

[sec4.2_p1] The papers using ML based techniques have been classified into the following categories based on the type of characterization performed: (1) Behaviour and intent classification, (2) Shape classification, (3) Spin/state/attitude/pose estimation and classification, (4) Space object type classification / target recognition, (5) Material identification, and (6) Future lightcurve prediction.

---

#### sec4.2.1 -- Behaviour / Intent Classification

[sec4.2.1_p1] The first characterization application is trying to predict the behaviour or event of the target space object. This involves the classification of the maneuvers that the space object performs to classes such as expected space keeping ones, or anomalous (which may indicate a malfunction or malicious intent).

[sec4.2.1_p2] The first paper in 2016 by Furfaro, R. et al aims to predict and understand the behavior of Resident Space Objects (RSOs) with a goal of developing a decision support system for space domain awareness. Specifically, by using Extreme Learning Machines (ELM) and convolutional neural networks (CNN), the aim is to infer critical parameters of RSOs from sensor measurements. These parameters include aspects like the object's energy state, momentum, and other physical characteristics. Then the characteristics are used for clustering RSOs in the feature space, which helps in identifying different types of behaviors exhibited by these space objects, such as standard operational patterns, anomalous behaviors, or patterns indicative of potential threats or malfunctions. By integrating Space Object Behavioral Ontologies (SOBO) with Bayesian Networks (BN), the study provides a probabilistic framework for predicting the behavior of RSOs. This prediction is based not only on the learned patterns from machine learning models but also incorporates expert knowledge and domain-specific information from the ontologies. The study used simulated data generated from physical models simulating the behavior of RSOs, including various energy and state parameters.

[Figure 16: The End-to-End Machine Learning and Ontology-based Bayesian Networks for Space Object Decision Support System developed by Furfaro, R. et al for behavior classification.]

---

#### sec4.2.2 -- Shape Characterization

[sec4.2.2_p1] The second characterization application, one of the most popular ones (in number of papers involving it), is the space object shape classification. Defining the shape of an RSO can be useful for SST applications such as orbit determination (because knowing the shape of the object can aid in calculating the effect of the solar wind or the atmospheric drag).

[sec4.2.2_p2] In 2019 Linares, R. et al presented a method for characterizing the shape of a space object using light curves. They generated simulated light curves using a physically-based forward model. Then they used the data to train a convolutional neural network to directly predict the object shape. The study focused around 4 classes of rocket bodies such as a) a cylinder with round top, b) a simple cylinder, c) a shape representative of an Atlas Upper Stage; and d) a shape representative of a Falcon 9 Upper Stage. Additionally the team also trained a variational autoencoder on the data in order to understand and visualize the latent distribution of light curve data.

[Figure 17: Models for Rocket Bodies used in the shape characterization work by Linares, R. et al.]

[Figure 18: VAE-learned light curves in the latent variable space work by Linares, R. et al.]

[sec4.2.2_p3] Yao, L. et al used lightcurve data and a 1-D CNN to characterize the space debris basic shape (specular cylinders, diffuse cylinders, box-wing satellites, and cube satellites are used as primary shapes). The model was trained on simulated data (generated using the Cook-Torrance Bidirectional Reflectance Distribution Function model, considering various shapes and materials for space debris) and compared against other ML models such as k-nearest-neighbors, Support Vector Machines, Random Forests and Decision Trees all of which it outperformed in accuracy. Additionally another dataset was created from observations extracted from the Mini-Mega TORTORA (MMT) database with two shapes (rocket body vs defunct satellite) training both the custom CNN model and a Random Forest model.

[sec4.2.2_p4] van Rooij, S. et al. used radar measurements (specifically Inverse Synthetic Aperture Radar (ISAR) images) to determine the size and shape of satellite solar panels and buses, using a custom CNN model based on the VGG19 architecture. The study used simulated radar images for training. The simulation covers five different satellites (Envisat, Grace, ICESat, Landsat7, and Landsat8) with various geometries, including different azimuth and elevation angles, and noise levels. The model works by segmenting the image into the different components (e.g. solar panel or bus) and thus their shape and size can be estimated.

[Figure 19: Examples of normalized ISAR images (not same scale, small satellites are zoomed), ground truth masks and model predictions for Envisat, Grace, IceSAT and Landsat8 satellites, using the Leave-one-out approach. Work by van Rooij, S. et al.]

[sec4.2.2_p5] Balachandran, K. et al used an LSTM based neural network model in conjunction with a hidden Markov model to classify the shape (ellipsoidal asteroid, rocket upper-stage, CubeSat, torus, probe, and box-wing satellite) and spin rate (tumbling vs stabilized) of LEO RSOs using lightcurve data. They used simulated data to train and validate their model. They ran the lightcurve data against statistical tests for periodicity (Fisher's Exact Test for Periodicity) and aliasing (Augmented Dickey Fuller test) and implemented feature selection via wavelet decomposition.

---

#### sec4.2.3 -- Attitude/Pose Estimation and Classification

[sec4.2.3_p1] The task of attitude or pose estimation is also useful for use in SST applications such as orbit determination (because knowing the RSO attitude can help calculate the solar wind and atmospheric drag influence in the orbit evolution) but also to future missions aimed at active debris removal.

[sec4.2.3_p2] Phan, D. et al in 2019 developed a pipeline to characterize GEO objects into two categories: a) three-axis stabilized GEOs (TAGs) and b) tumbling objects (TOs), further sub-classifying TOs into rocket bodies or tumbling satellites. Also for TAGs, a sub-classification into signature types is implemented, aiding in assessing physical structures on the satellites. Using lightcurve data collected from partners the pipeline developed uses a number of statistical and ML methods to achieve the desired classification, namely: 1) a random forest (RF) classifier (utilizes statistical features derived from light curves for initial classification) 2) periodicity test (assesses the statistical significance of each period found in the light curve, distinguishing between TAGs and TOs) 3) aliasing test (evaluates whether residuals from a spline fit to the light curve are normally distributed, helping detect aliasing due to under-sampling) 4) quality of fit test (compares the coefficient of determination - R-squared - of the light curve's spline fit against empirical distributions, aiding in stability mode assessment) 5) hidden Markov model (HMM): Integrates the assessments from the above tests into a dynamic Bayesian network for the final classification.

[Figure 20: Example of a typical signature from a stable TAG satellite, work by Phan, D. et al in 2019.]

[Figure 21: Example of a sinusoidal signature from a tumbling TAG satellite, work by Phan, D. et al in 2019.]

[sec4.2.3_p3] Zhang, H. et al used Gaussian Process Regression on simulated satellite images (BUAA-SID dataset) to perform a) satellite recognition (the type of satellite observed) b) satellite pose/attitude estimation. Specifically for pose estimation a manifold constraint is introduced. It uses a manifold representation (e.g., normalized n-sphere in a n+1-dimensional space) to represent the degrees of freedom in pose variation, so that the model regression output is constrained in the possible satellite poses. Finally the model also provides an uncertainty measurement, by giving a confidence score with each prediction.

[sec4.2.3_p4] Afshar, R. et al also used the BUAA-SID dataset to create models for both target recognition and pose estimation. Their innovation lies in the use of transfer learning and data augmentation techniques, enhancing the classification accuracy under various space conditions, including noise and different illumination. A two-stage CNN architecture is used. The first stage involves a pre-trained network (Inception CNN) on the ImageNet dataset for feature extraction, a transfer learning technique. The second stage trains the network for classification and regression (for the tasks of satellite recognition and pose estimation respectively) on images of the dataset (which has been augmented by applying transformations like rotating, shifting, re-scaling, and zooming) to enhance classification accuracy making it more robust against different noise and lighting conditions.

[sec4.2.3_p5] Badura, G. in 2020 applied a CNN for the task of inferring an RSO's attitude from lightcurves. They tried to improve upon the issue of bidirectional reflectance distribution function (BRDF) mixing, sensor noise, and atmospheric turbulence, by generating a synthetic dataset that realistically incorporates BRDF signatures and environmental parameters. They generated the dataset by using the Beard-Maxwell model of reflectance, but adapted it for materials like silicon solar panels, glossy paint, and aluminum. Finally they used a CNN model based on the LeNet architecture to estimate four different maneuvers: a) tumbling, b) accelerating in rotational rate, c) stabilizing, and d) inactive.

[sec4.2.3_p6] Paulete, C. et al used data from radar measurements called Radar Cross Section (RCS). It is analogous to a lightcurve in the sense that it represents the radar reflectivity of an object (from the point of view of the radar installation) over a time span. This dataset was used to train two ML models to perform a) Attitude stability classification (in four classes, Earth pointing, inertia pointing, geodetic and tumbling) and b) Direct Object Identification (44 classes representing various satellites and a class for unknown object). Additionally the azimuth and elevation in the ITRF and GCRF reference frames is provided for each radar measurement. The model is a neural network using a Long Short-Term Memory (LSTM) layer (which can work with timeseries data) which is connected to a feedforward layer.

[sec4.2.3_p7] McNally, K. et al created a lightcurve simulator to produce generated lightcurve data due to the lack of open source datasets. Then they also used real lightcurves to both verify the validity of the generator but also test the model trained on simulated data. They predicted two different variables: a) attitude (2 classes stable or spinning satellite but additionally where the satellite antenna is pointing at) and b) satellite (6 different satellites are used for identification). The model was a feedforward neural network which is using the following features generated from the raw lightcurves: a) the maximum and minimum values of the apparent magnitude b) the coefficients of a third order polynomial regression fitting the lightcurve c) the first two most representative frequency amplitudes of the fourier transform of the lightcurve.

[sec4.2.3_p8] Qashoa, R. et al worked to classify LEO RSOs by object type and spin rate (stable satellite, tumbling satellite, rocket body) using light curves. Using a dataset of real light curves, features were extracted using a Wavelet Scattering Transformation (WST), which were then used as input to an SVM and an LSTM-based model to compare the accuracy of the two models.

[Figure 22: Example of 3D embedding of Wavelet Scattering Transformation coefficients using Euclidean distance in work by Qashoa, R. et al.]

[sec4.2.3_p9] Also the work by Balachandran, K. et al which was described in the Shape Characterization subsection also includes the task of spin rate (tumbling vs stabilized) classification.

---

#### sec4.2.4 -- Space Object Type Classification / Target Recognition

[sec4.2.4_p1] The space object type or target recognition is one of the most basic tasks in characterizing RSOs as it tries to match unknown observed objects to a list of known targets either in general categories such as debris vs satellite, or more detailed by trying to detect the specific type of satellite or satellite component (e.g. satellite body, solar panel etc).

[sec4.2.4_p2] Chaudhary, S. et al used the SPARK dataset (which contains 150,000 RGB images of 10 spacecraft and 1 debris class with bounding boxes highlighting them, along with the corresponding depth images) to create a new classification pipeline. In their work first the depth images are de-noised using the morphological opening operation. Then using the de-noised depth image a mask is created highlighting the object of interest. Then the mask is applied to the RGB image, which helps keep only the object of interest. Finally this masked image is fed into a neural network model which is using the EfficientNet B4 architecture which performs the space object classification.

[Figure 23: The processing steps for the space object characterization work by Chaudhary, S. et al.: (a) Depth Image (b) Depth image after applying opening operation (c) RGB image (d) Masked image.]

[sec4.2.4_p3] Krantz, H. et al created a model to classify the type (three types of Starlink satellites and one type of OneWeb satellites, 4 classes in total) of LEO satellites based on their photometric signatures. They use the concept of effective albedo of a satellite (a theoretic construct calculated by comparing the observed satellite to an ideal uniform diffuse sphere) as input feature to a gradient boosted decision trees classifier along with the elevation and azimuth angles. The images are collected with an all sky camera performing photometric survey.

[sec4.2.4_p4] Walker, L. et al generated hyperspectral data with the goal of predicting the proportions of materials in satellites and infer the presence of large components (like solar panels and antennas), and finally perform satellite classification. The dataset was generated using physics and sensors simulations of 3D models of satellites, their orbits and rotation state vectors. An artificial neural network (ANN) was created to predict the fraction of light due to each material at different time points, using simulated data. The output is then converted into statistical features (mean, standard deviation, correlation coefficients, etc.) to produce new features. These features are used in a gradient boosted decision tree model (XGBoost) which predicts the presence of large satellite components (solar arrays, antennas, etc.). Finally a k-Nearest Neighbours (kNN) algorithm performs the final classification into different satellite types (GNSS, Earth Observation, Communications, Rocket Bodies and CubeSats).

[sec4.2.4_p5] Additionally the works by Zhang, H. et al, Afshar, R. et al, Paulete, C. et al, McNally, K. et al and Qashoa, R. et al which were already described in the Attitude/Pose Estimation subsection have also contributed to the type/target classification task.

---

#### sec4.2.5 -- Material Identification

[sec4.2.5_p1] The material identification task is used for extracting RSO information that can help in space target recognition. To this end Li, N. et al created a new pipeline by combining a Graph Neural Network (GNN) with a convolutional neural network (CNN) on hyperspectral images. As a first step a superpixel segmentation is performed to group pixels with similar characteristics. Then global structure topological graphs are generated from these segmented superpixels. These graphs augment the original hyperspectral images and the combined data are fed into the joint GNN CNN model. The model outputs the probability for each pixel and each type of material.

[Figure 24: The architecture of the system designed by Li, N. et al for the task of material identification.]

[Figure 25: Examples of material identification results, work by Li, N. et al.]

---

#### sec4.2.6 -- Future Lightcurve Prediction

[sec4.2.6_p1] Future lightcurve prediction was one of the niche applications found in the review, as the prediction of the future lightcurve value of an RSO could aid in other characterization tasks which use lightcurve data. Dupree, W. et al used two neural network based models (a Feed Forward and an LSTM based) with lightcurve data trying to predict the future lightcurve, meaning the future magnitude one would measure while observing the object. They performed feature engineering to handle missing values in the data, created rolling window samples and created new features to handle the irregular time steps by tracking the difference between measurement values.

---

## sec5 -- Data

[sec5_p1] Finally we will perform a small analysis on the types of data used in each application.

[sec5_p2] Looking at the summarized data a few interesting points stand out. The first is the fragmented landscape of datasets. Most work studied is being done in datasets created by the authors, either from real collected data (13 papers for RSO detection, 7 for RSO characterization) or data generated by the authors to fit the demands of their work (9 papers for RSO detection, 9 for RSO characterization). Researchers are also using hybrid methods by incorporating real data with simulated ones or using real data as an extra validation set to measure the transferability of their methods.

[sec5_p3] With regards to the data type used, for RSO detection optical telescope images are the only type studied but that can also be attributed to the literature search criteria. For RSO characterization the type used depends more on the task. Optical, hyperspectral, lightcurve and angles (declination and right ascension coordinates) have all been used in different tasks showcasing the different approaches followed by various teams. The majority of the data types are (Optical, hyperspectral) or can be converted (lightcurve) to images so as to be exploited by Convolutional and other Neural Network architectures.

[sec5_p4] [Table 1: Types of datasets used in the RSO detection papers. Lists 33 papers with columns for Paper, Data Type, and Real vs Simulated Data. All papers use Optical Telescope Images. Data sources are distributed among Real data, Simulated data, and Both (real and simulated combined).]

[sec5_p5] [Table 2: Types of datasets used in the RSO Characterization papers. Lists 19 papers with columns for Paper, Data Type, Real vs Simulated Data, and Task. Data types include Hyperspectral images, Lightcurve (Magnitude) data, Lightcurve and Angles data, Inverse Synthetic Aperture Radar (ISAR) images, Optical images, and Radar Cross Section (RCS) data. Tasks span Attitude/Pose Estimation and Classification, Behaviour/Intent Classification, Shape Characterization, Space Object Type Classification/Target Recognition, Material Identification, and Future lightcurve prediction.]

---

## sec6 -- Conclusion

[sec6_p1] With this paper we aimed to provide a thorough survey on the use of Machine Learning and Deep Learning methods for the applications of RSO detection and characterization.

[sec6_p2] It has been shown that the field of optical telescope image processing has been served by classical image processing techniques up to a few years ago when computer vision models based on artificial neural networks have started to dominate the field. Researchers are using established neural network architectures (such as YOLO, Faster R-CNN and U-Net) either as-is or by adapting them for efficiency or augmenting them with additional modules to better perform on the RSO detection application. With regards to the datasets used, the lack of standardised big datasets seems to be contributing to a fragmented landscape where researchers are using either smaller amounts of real data, or larger simulated datasets, with some also exploring the fusion of the two.

[sec6_p3] For the RSO characterization application there exists a number of different tasks where research is being undertaken. Attitude/pose estimation and classification, shape characterization, material identification and future lightcurve prediction are some of the main ones that were retrieved from the literature. A sample of the papers that have been published for these tasks have been analyzed showing a strong emphasis on the use of machine learning based techniques, and specifically deep learning ones, with convolutional neural networks being the most common method. With regards to the datasets, similarly to the RSO detection application most of the work is being performed in individual ones, emphasizing the need for creating extensive, open datasets to serve as benchmarks, thereby enhancing characterization methods.
