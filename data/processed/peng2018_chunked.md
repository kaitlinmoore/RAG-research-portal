# peng2018 -- Artificial Neural Network-Based Machine Learning Approach to Improve Orbit Prediction Accuracy

**Authors:** Hao Peng, Xiaoli Bai
**Venue:** Journal of Spacecraft and Rockets, Vol. 55, No. 5 (AIAA) (2018)
**DOI:** https://doi.org/10.2514/1.A34171

---

## sec0 -- Abstract

[sec0_p1] A machine learning (ML) approach has been proposed to improve orbit prediction accuracy in previous studies. In this paper, the artificial neural network (ANN) model is investigated for the same purpose. The ANNs are trained by historical orbit determination and prediction data of a resident space object (RSO) in a simulated space catalog environment. Because of ANN's universal approximation capability and flexible network structures, it has been found that the trained ANNs can achieve good performance in various situations. Specifically, this study demonstrates and validates the generalization capabilities to future epochs and to different RSOs, which are two situations important to practical applications. A systematic investigation of the effect of the random initialization during the training and the ANN's network structure has also been studied in the paper. The results in the paper reveal that the ML approach using ANN can significantly improve the orbit prediction.

---

## sec1 -- Introduction

[sec1_p1] The number of space objects larger than 10 cm is presently approaching 29,000, the estimated population of objects between 1 and 10 cm is about 750,000, and for objects smaller than 1 cm the number exceeds 166 million. These objects distribute in different regions from low to very high Earth orbits, and threatens the safety of satellites in or crossing these regions. At the heart of the challenges for Space Situational Awareness (SSA) is to predict resident space object's (RSO's) orbit efficiently and accurately. Current orbit predictions that are solely grounded on physics-based models, however, fail to achieve required accuracy for collision avoidance and have already led to collisions. Several incidents have painfully demonstrated the limitations of our current orbit prediction capability, such as the February 2009 collision of a U.S. Iridium communications satellite and a Russian Cosmos 2251 communications satellite. In the coming decades, both the number of space objects and the number of conflicts between these objects will increase rapidly. Our ability to generate accurate and timely predictions of the trajectory of RSOs is the key factor of the SSA system.

[sec1_p2] The limitation of current prediction approach arises from the assumed dynamic models, measurement errors, orbit determination errors, and others. In reality, we can only get limited information from the physical world, while these limited information will be further twisted by various assumptions during the modeling process. For example, whatever accurate measurements or parameters we have about the solar activity, the model is only statistically approximating the data with limited variables that appear to be dominant. Another good example is the atmosphere drag model that usually causes great uncertainty for orbit predictions of LEO objects.

[sec1_p3] Considering that certain information embedded in historical data has not been used during the conventional orbit prediction process, we have proposed a machine learning (ML) approach to capture and extract these extra information in previous studies. The ML approach has presented a different modeling and prediction capability compared with the physical model based approach. The improvement on orbit prediction can be made without explicitly modeling forces or perturbations. Instead, models of orbit prediction errors are directly learned based on large amounts of historical data.

[sec1_p4] In one study, we have discovered that the information of the area-to-mass ratio (AMR) can be recovered from the consistent error between two estimated states in a catalog. In another study using a simulation-based space catalog environment as the test bed, we have discovered three types of generalization capability for the proposed ML approach. In the above studies, the support vector machine (SVM) method has been chosen as the specific ML algorithm. The SVM is a universal approximation method, which means that theoretically it could approximate any continuous function with arbitrary accuracy. We have found that the SVM can capture the underlying relationship between the available parameters and the prediction error, and can reduce the orbit prediction error greatly.

[sec1_p5] In this paper, as an extension to the previous studies, we have examined the artificial neural network (ANN) to improve orbit prediction accuracy. The ANN is basically multiple layers of neurons that connect to neurons at the previous layers, and the inputs are processed from the first to the last layer, by weighted summation and nonlinear mapping at each neuron.

[sec1_p6] Recently, as represented by the great achievement of AlphaGo, attentions have been drawn on a specialized kind of ANN, the deep neural network, which is good at tasks such as classification, decision making, or picture comprehensions. It is well-known that the ANN can be superior to human performance in various classification problems, where the outputs are discrete categories. The ANN has also been used in other fields dealing with continuous outputs, that is, the regression problem. The ANN has proven to be a powerful universal approximation method, able to approximate any smooth functions with adequate neurons and layers. In fact, it has been a long time since the function approximation capability of shallow ANNs with just one hidden layer has been applied to various problems in aerospace fields. Williams has trained a shallow neural network to predict the future solar activity based on historical data, and his experiment shows that using this technique the prediction of the lifetime of satellite is more accurate. Considerable improvements have been reported when compared with the conventional linear regression. Macpherson et al. have extended the method to predict both the solar and geomagnetic activity. They have used ANNs with just 1 hidden layer of no more than 10 neurons. Lu et al. have proposed a pruning learning strategy to find the minimal radial basis function neural network, which has been also used in control and function approximation problems. The ANN method has also been integrated into Kalman filters to improve the accuracy of GPS applications when there are model uncertainties. Recently, Sanchez-Sanchez and Izzo have used deep neural networks to learn the solution of an optimal landing problem, so that real-time on-board trajectory planning can be achieved. Mereta et al. have studied various machine learning methods, including the ANN, to provide initial guess of the optimal final mass for low-thrust trajectory design between asteroids.

[sec1_p7] We make three contributions in this paper: 1) the ANN method is demonstrated to have good performance on reducing orbit prediction errors; 2) the effect of the number of neurons and hidden layers has been explored; and 3) ANN's generalization capabilities to future epochs and different RSOs have been rigorously investigated. Furthermore, combining the performance of the ANN method in this paper and that of the SVM method in our previous studies, we verify that the proposed ML approach is feasible and correct, with great potential to advance practical applications.

[sec1_p8] This paper is organized as follows. In Sec. II, we briefly summarize the previously proposed ML approach, and introduce the basic concept of the ANN. In Sec. III, we present the generalization capability study of the trained ANN models onto orbit predictions at future epochs, and the effect of randomness and network structure are investigated. In Sec. IV, the generalization capability of the trained ANN models to different RSOs are investigated. At last, in Sec. V, we summarize the paper and provide insights and suggestions on future research.

---

## sec2 -- Backgrounds

[sec2_p1] In this section, we first briefly review the ML approach to improve orbit prediction accuracy using a simulated space catalog environment. More details can be found in our previous studies. Next, design of learning variables and the dataset structure are presented. Last, basic concepts of the ANN are introduced.

---

### sec2.1 -- Machine Learning Approach for Orbit Prediction Problem

[sec2.1_p1] The concept of the proposed ML approach to directly modify the orbit prediction is illustrated in Fig. 1. When the RSO enters the detection range of the ground station, we will generate an estimate of the state of the RSO at a certain epoch using a conventional orbit determination method. This estimated state will deviate from the true state, which is usually referred to as an estimation error. Then the estimated state is propagated, usually under the same dynamics to the determination process, to a future epoch to generate the predicted state, which will further deviate from the true state because of the error propagation. In practice, the atmosphere drag force, the solar radiation pressure, and the shape and attitude motion of the RSO are difficult to be accurately modeled.

[Figure 1: Illustration of machine learning approach to directly improve the orbit prediction.]

[sec2.1_p2] With the speculation that the effect of these unmodeled factors is hidden in the historical data of measurements, estimations, and orbit predictions, the ML approach is proposed to discover the hidden relationship between the available variables and the orbit prediction error from historical data. Once the ML model has been well trained, as shown in Fig. 1, the ML-modified state is generated by eliminating the ML-generated error from the original predicted state. This ML-modified orbit prediction is expected to be closer to the true state. We note that the ML approach is not restricted to specific dynamic models or underlying relationships, but can be applied to different catalogs and embedded in current procedures.

---

### sec2.2 -- Simulation Environments

[sec2.2_p1] The flowchart of our simulation environment for the machine learning approach is demonstrated in Fig. 2. The top four blocks show the sequential simulations of the conventional orbit prediction: 1) The true orbit of an RSO in the "truth" dynamics models; 2) The measurement of the RSO from ground stations; 3) The estimation process in an assumed dynamic model different from the "truth"; 4) The orbit predictions are generated. The bottom three blocks show the machine learning enhancement procedure.

[Figure 2: Flowchart of the simulation environment for the machine learning approach.]

[sec2.2_p2] This simulation environment is established with the goal that the simulated "truth" dynamic models can capture not only main factors contributing to the orbit prediction error in reality, but also the difference between the assumed models and the truth models.

[sec2.2_p3] [Table 1: Parameters of the "truth" model used to generate orbits and measurements, and the assumed model used in estimation and prediction. Truth model uses WGS84 Earth shape, 40x40 harmonic gravity field, third-body perturbation from Sun plus solar planets plus Pluto plus the Moon, DTM2000 atmosphere model, and MSAFE solar activity. Assumed model uses WGS84 Earth shape, 10x10 harmonic gravity field, third-body perturbation from Sun plus Jupiter plus the Moon, NRLMSISE-00 atmosphere model, and constant solar activity values F10.7=150.0 and Kp=3.0.]

[sec2.2_p4] The nonspherical effect of the Earth gravity is modeled using spherical harmonic functions, with coefficients provided by the EIGEN-6S model. Third-body perturbations of all major solar system bodies are considered, including the Sun, all the planets, the Pluto, and the Moon. The position of these bodies are provided by DE430 data file from the JPL. The Drag Temperature Model 2000 (DTM2000) model is used to approximate the atmosphere, where the Marshall Solar Activity Future Estimate Solar (MSAFE) data from NASA are used to provide solar activity information, which has significant effect on the density and the speed of the atmosphere. A different atmosphere model, NRLMSISE-00, is used for the assumed model. We note that we just use the two different models to mimic the differences between the empirical atmosphere model and the truth. The solar radiation pressure is calculated with the reference value as 4.56 x 10^-6 N/m^2 at 1 AU (149,597,870.0 km) from the Sun. And the effects of the penumbra and eclipse are considered. During the generation of true orbit, a spherical RSO with a constant area-to-mass ratio of 0.05 is assumed, and the drag coefficient Cd and single-parameter reflection coefficient Cr are assumed to be constant.

[sec2.2_p5] [Table 2: Ground-based radar stations modeled in the paper. Three stations: Eglin, FL (latitude 30.57 deg, longitude -86.21 deg, altitude 34.7 m); Clear, AK (latitude 64.29 deg, longitude -149.19 deg, altitude 213.3 m); Kaena Point, HI (latitude 21.57 deg, longitude -158.27 deg, altitude 300.2 m). Each station has specified max range, elevation range, and measurement noise standard deviations for range, azimuth, and elevation.]

[sec2.2_p6] Three ground radar stations are simulated using topocentric frames to generate tracks of measurement of an RSO, with their parameters summarized in Table 2. The stations will generate discrete measurements, including the azimuth alpha, the elevation eta, and the range rho, at each step of the measurement gap, when the target RSO is visible to the ground stations. A series of consecutive measurements are organized as a track, and one track can include measurements collected from different stations if they could all detect the RSO. The measurement errors are simulated as normal distributions with zero biases and standard deviations for the azimuth, elevation, and range, respectively, as summarized in Table 2. The batch Least Square (LS) estimator is used to estimate the state of the RSO at the beginning of each track. In this study, all tracks in the past 12 h are used as the input of the LS estimator. The output of the LS estimator includes the orbit state X and drag coefficient parameter Cd. Then the prediction process is carried out in the same assumed dynamic model. The prediction error is generated by comparing the predicted state and the recorded true state at the same epoch.

[sec2.2_p7] A maximum prediction duration of 7 days (1 week) is used in this paper, which is suitable for general surveillance and conjunction analysis of LEO objects. We note that all the simulations are implemented using the Orekit, which is a low-level space dynamics library written in Java.

---

### sec2.3 -- Dataset Structure of Machine Learning Approach

[sec2.3_p1] At first, we define the notations that will be used throughout the following paper. We use the symbol X(t) to denote the state of the RSO at time t, without expressing it in a coordinate frame. The state X(t) can be expressed in the classical orbital element (COE) form as [a, e, i, omega, Omega, nu], or in the Earth-centered inertial (ECI) frame as [X, Y, Z, VX, VY, VZ]. The difference between two states at the same epoch t will be expressed in the RSW frame as [delta_x, delta_y, delta_z, delta_vx, delta_vy, delta_vz], where x axis (radial) is the radial direction, the y axis (along-track) is perpendicular to the x axis in the orbital plane and points to the inertial velocity direction, and the z axis (cross-track) is along the angular momentum direction. The above symbols without any modifier indicate that they are true value of the orbit, such as the true state X(ti). The hat over a symbol is used to indicate that it is an estimated value. We use an additional time variable after a semicolon to indicate that this value is based on a previous estimate, such as (tj; ti) in X_hat(tj; ti), which indicates that this state is predicted at tj based on X_hat(ti).

[sec2.3_p2] The choice of learning variables is identical to our previous study on SVM's limits. To be self-consistent, this is briefly summarized here. With above notations, all learning variables at the current epoch ti are collected and represented as the vector Lambda(ti), whose components include the following: 1) Prediction duration delta_t = tj - ti to the future epoch tj (ti < tj); 2) Estimated state X_hat(ti) at the current epoch ti, expressed as both COE and ECI forms; 3) Estimated drag coefficient Cd_hat(ti) at the current epoch ti; 4) Maximal measured elevation in the current ith track eta, and the corresponding range rho and azimuth alpha at that epoch, denoted by theta_i = [rho, alpha, eta]; 5) Predicted state X_hat(tj; ti) at the future epoch tj, based on the current epoch X_hat(ti), expressed as both COE and ECI forms.

[sec2.3_p3] Then, all the target variables are: 6) True predicted error e(tj; ti) at the future epoch tj, expressed as RSW components [ex, ey, ez, evx, evy, evz]. Because the RSW error has six components, totally six ANN models will be trained for each component. We note that these learning variables are chosen through a trial-and-error process, and the result is not meant to be optimal.

[sec2.3_p4] With the chosen learning and target variables, the illustration of the training and testing process of the ML approach is demonstrated in Fig. 3. During the collection of training data, each estimated state is propagated to the epoch of all following estimates with delta_t < delta_t_max; then the learning variable Lambda(ti) and the true prediction error e(tj; ti) are collected as a data point. The total dataset will be used to train ANN models to approximate e(tj; ti) based on Lambda(ti). After the ANN model has been trained, it can generate the ML-predicted error e_hat_ML(tj; ti). In the ideal situation, e_hat_ML(tj; ti) should be equal to e(tj; ti), leading to that the residual error e_res(tj; ti) = e(tj; ti) - e_hat_ML(tj; ti) becomes zero. In practice, the statistical properties of e_res(tj; ti) will be analyzed to evaluate the performance of the trained ANN model.

---

[Figure 3: Illustration of learning and target variables for ANN models.]

### sec2.4 -- Artificial Neural Network

[sec2.4_p1] The artificial neural network (ANN) can approximate any smooth transfer functions with adequate neurons and layers. In this subsection, a brief summary of ANN is presented.

[sec2.4_p2] Figure 4 shows a neural network with L layers. The first layer with the learning variables a1 = Lambda(ti) is the input layer, and the last layer that generates the output aL is the output layer. Intermediate layers from l = 2 to L - 1 are usually referred to as hidden layers. The network will be trained to generate outputs aL as close as possible to the corresponding target variable e(tj; ti) for each data point in the training data. In other words, the ANN is trained to capture the underlying relationship of (Lambda(ti, tj), e(tj; ti)).

[Figure 4: Illustration of an artificial neural network (ANN) with L layers.]

[sec2.4_p3] [Equation 1: The output of each neuron is computed as the activation function applied to the weighted sum of all outputs from the previous layer plus a bias term.]

[sec2.4_p4] The activation function F can be chosen from many functions, while different choices will affect the capability and performance of the resulted ANN. Depending on the activation functions used at each layer, the ANN model can be used for both classification and regression problems. The orbit prediction problem in this paper is modeled as a regression problem; the log-sigmoid transfer function is chosen for the hidden layers (layers 2 to L - 1), and the pure linear function is chosen for the output layer (the Lth layer).

[sec2.4_p5] [Equation 2: The log-sigmoid activation function maps any real-valued input to a value between 0 and 1.] [Equation 3: The pure linear activation function passes the input through unchanged.] [Equation 4: The cost function is defined as the mean squared error over all training data points, computed as the average of the squared 2-norms of the differences between true and ANN-generated errors.]

[sec2.4_p6] The goal of a training algorithm is to minimize the cost function. In this study, the back propagation technique is used to solve for the gradient of the cost function with respect to all the weights and the biases. And the Levenberg-Marquardt optimization method is used to update the weights and biases of the ANN.

[sec2.4_p7] The great flexibility of the ANN also implies that it is very likely to overfit the training data. To avoid the potential overfitting, the training data are divided into a validation data set and a real training data set. The validation data are not used for training. Instead, during the training, the performance of the ANN on the validation data is monitored so that an early stop of the training will be triggered when overfitting is detected according to some criterion. A common indication of overfitting is that the cost function keeps decreasing but that on the validation data starts to increase, which is the criterion used in this paper.

---

## sec3 -- Generalization Capability at Future Epochs

[sec3_p1] As has been proposed and discussed in our previous study, for the orbit prediction problem, there exist three types of generalization capabilities of the ML approach: Type I: Generalization capability within the same dataset. The total dataset is divided randomly into a training set and a testing set. The testing data are within the same time interval as the training set. This is the common practice in machine learning area. Type II: Generalization capability to future epochs. The testing data are restricted to be in the future epoch with respect to the training data. This reflects the realistic orbit prediction problem. Type III: Generalization capability to different but nearby RSOs in future epochs. This is a generalization type that can be very important for SSA. Basically, this capability means learning some patterns from a limited number of RSOs, and then applying the knowledge onto other RSOs.

[sec3_p2] According to our previous results, the Type I generalization is relatively easy to achieve by the ML approach, and so we will focus on the Type II and III generalization capabilities in this paper. In this section, the Type II generalization capability will be investigated. Besides of the performance of the ANN, the effect of random initialization and the number of neurons and hidden layers are also systematically explored.

---

### sec3.1 -- Simulation Parameters and Performance Metric

[sec3.1_p1] The RSO ENVISAT, which has a Sun-synchronous orbit (SSO), is chosen as the study object in this paper. General information and parameters of ENVISAT are summarized in Table 3.

[sec3.1_p2] [Table 3: Parameters of ENVISAT. Name: ENVISAT; NORAD ID: 27386; Orbit: SSO; Launch date: 1 March 2002; Altitude: approximately 796 km; Period: approximately 100 min; Weight: approximately 8211 kg; Inclination: approximately 98.54 deg; Eccentricity: approximately 0.001165.]

[sec3.1_p3] For numerical simulations, the initial state of the orbit of ENVISAT is extracted from a TLE set using the standard SGP4 model. Using this initial state, the orbit of the RSO in the simulated environment for 4 weeks is demonstrated in Fig. 5 in the ECI frame. The orbit is colored by red at the beginning, and is seen to gradually change to blue at the end, which reveals the procession of the orbit due to the perturbation forces.

[Figure 5: Orbit of ENVISAT for 4 weeks in ECI frame.]

[sec3.1_p4] [Equation 5: The performance metric P_ML is defined as the total absolute residual error divided by the total absolute true error, expressed as a percentage. This metric shows the percentage of errors that remain after the ML modification.] We note that if the metric is computed using the training data, it actually reflects the learning capability of the ANN. More important, according to our experience, this definition can avoid numerical problems with small denominators and thus stably evaluate the average performance of the trained model in most situations.

---

### sec3.2 -- Generalization Performance at Future Epochs

[sec3.2_p1] In this subsection, 6 three-layer ANN networks with 1 hidden layer of 20 neurons are trained for each component of the true orbit prediction error e. The training data are the historical orbit prediction data of the RSO in the first 4 weeks, that is, weeks 1--4, and the testing data are the data in the following 1 week, that is, week 5. Additionally, the data in the last day of the training data are used as the validation data for the early stopping criterion, in order to guarantee a better generalization capability. This design leads to that the numbers of data points for the training, validation, and testing data are 39,979, 1633, and 6239, respectively. For simplicity, the similar choice of validation data will be used for the remaining paper without clarification. The early stop parameter is chosen as 20, which means that the training will be terminated if the cost function on the validation data has not been reduced in the following 20 consecutive iterations.

[sec3.2_p2] Figure 6 demonstrates the performance of the trained ANN on the training data of the radial axis error ex. The horizontal axis represents the prediction duration delta_t. The vertical axis shows true, ML-predicted, and residual along-track errors ex. The left plot shows the scatter plot, where black circles represent the true error, green dots represent the ML-predicted error, and red dots represent the residual error after ML modifications. The right plot shows the errorbar plot of the left scatter plot, where the center point represents the mean value of each clustered group of the error, and the length from the middle of the bar to the top (or the bottom) represents the standard deviation of the corresponding clustered group. For clarity, the three curves have been slightly displaced along the horizontal axis to avoid overlapping. The performance metric P_ML(ex) = 7.5% is shown above axes. Because these two plots reveal similar information in most time, for clarity, only the errorbar plot will be demonstrated in the following paper.

[Figure 6: Example of performance P_ML(ex) of ANN on the training data (weeks 1--4).]

[sec3.2_p3] About the residual errors for all experiments, we conjecture that they are possibly due to, but not limited to, the following factors: 1) the intrinsic randomness of the data that cannot be completely removed, such as the measurement noise; 2) limited information of errors captured by the current choice of available learning variables; 3) the early stopping criterion introduced to guarantee a better generalization capability; and 4) the theoretical limits of the ANN model, such as the approximation capability with chosen finite number of neurons and layers. Therefore, these factors may not be completely overcome theoretically.

[sec3.2_p4] Figure 7 demonstrates the performance of ANNs for all the position and velocity error components on the training data (weeks 1--4), which reveals the learning capability of the ANNs. The mean values of residual error e_res have all been reduced to almost zero, and the standard deviations have also been significantly reduced. The result reveals that the ANN has captured the underlying relationship between learning and target variables in the training data. However, the generalization capability onto future data remains to be examined.

[Figure 7: Performance of ANNs for different components on the training data (weeks 1--4).]

[sec3.2_p5] Figure 8 demonstrates the performance of the trained ANN that has been generalized onto the testing data (week 5). For ex, ey, evx, and evy, both the mean values and the standard deviations have been significantly reduced. The metric P_ML are slightly larger than corresponding metric on training data in Fig. 7. This is expected because the testing data have not been used during the training and also may contain information different from the training data. For ez and evz, the metrics are 55.9% and 60.0%, respectively. It is clear in the figure that the biases and standard deviations have also been reduced to some extent, although the performances are not as good as that of the other four components.

[Figure 8: Performance of ANNs for different components on the testing data (week 5).]

[sec3.2_p6] To have a clearer impression of the capability of the trained ANNs, a comparison of the true (left) and residual (right) errors is presented in Fig. 9. The vertical axes are in logarithmic scale. It is clear that among the magnitudes of three true position errors, we have ey > ex > ez, and after the modification using ANNs, e_res_x and e_res_y have been significantly reduced, and e_res_x and e_res_z have come to the same magnitude. It is also interesting to note that the residual velocity errors e_res_vx, e_res_vy, and e_res_vz have been reduced to almost the same magnitude.

---

[Figure 9: Comparisons between the true (left) and residual (right) orbit prediction error using trained ANNs.]

### sec3.3 -- Effect of Random Initialization

[sec3.3_p1] There is randomness in most of the training algorithms for ANN. Before the training, all the weights of the network have to be initialized. The training result depends on the initialization of weights and is usually different for each initialization, which is due to many local optimal solutions of ANN. So a practical guideline is that the performance of ANN should not be evaluated by a single experiment. In fact, it is a common practice to improve the performance of an existing trained ANN by trying different initializations, until the performance is acceptable.

[sec3.3_p2] In our experiments, the Nguyen-Widrow initialization algorithm is used to initialize the weights at each layer. By setting various random seeds for the global random stream of MATLAB, we can achieve different initializations. For all the trainings of ANNs in this paper, 10 random seeds are used and then fixed to explore the effect of randomness. All the trainings of the ANN in the following study, either with different network structures or for different components, will be carried out 10 times using these 10 seeds.

[sec3.3_p3] For the ANNs in the previous subsection, which have 1 hidden layer of 20 neurons, the results of 10 tests are summarized in Fig. 10. The dashed line with circles represents the training results, and the solid line with asterisks represents the testing results. The results reveal that the trained ANN have captured the underlying relationship between the learning and target variables, regardless of a particular initialization. The training results are more consistent, whereas the testing results are relatively more sensitive to the initialization. There are some cases where the performance is obviously worse than others, for example, case 4 of ex and case 6 of evy. From a practical point of view, a proper initialization of the ANN can always be found through a trial-and-error process, and a random initialization will usually not lead to too bad performance.

---

[Figure 10: Performances of ANNs initialized with different random seeds, trained with the same training data in weeks 1--4 and tested with the same testing data in week 5.]

### sec3.4 -- Effect of Network Structure

[sec3.4_p1] In this subsection, we investigate the effect of network structure of ANN on the generalization capability, by varying both the number of neurons at each layer and the number of layers. We note that having more neurons and layers will introduce more weights to be adjusted in the network, therefore more flexibility. This provides the ANN model more powerful approximation capability. However, as we have mentioned in Sec. II, more flexibility also means that it is more likely to overfit the training data, which will lead to a bad generalization performance.

[sec3.4_p2] First, we varied the number of neurons at all the layers from 10 to 30 with a step of 5. The results of the trained ANNs are summarized in Fig. 11. The horizontal axis represents the number of neurons at each hidden layer. The circles represent the training results for each random seed, and the asterisks represent the testing results. The dashed and solid lines represent medians of each set of results corresponding to the 10 random seeds. Note that the minimum P_ML among all the random initialization represents the best performance of the ANN, and the maximum P_ML reflects the capability of the ANN in the worst situation. Because we are more interested in the expectation of the performance, we have chosen the median of the metric P_ML to represent the performance of the ANN with a certain structure.

[Figure 11: Performance of trained ANNs with different numbers of neurons on the same testing data (week 5).]

[sec3.4_p3] In Fig. 11, a general trend is that the performance on training data (dashed lines) of ANN is becoming better when more neurons are used. However, this is not exactly the same for the performance on the testing data (solid lines). For ex, ez, and evy, the metrics P_ML on testing data tend to decrease with respect to neuron numbers. But for other components, the performance only changes slightly. This in fact is good, revealing that ANN is actually learning the underlying relationship, rather than just fitting particular data patterns. If on the contrary, better performance on the training data corresponds to worse generalization results, it will imply the overfitting. On the other hand, this phenomenon also shows that the early stop criterion works well.

[sec3.4_p4] Second, the number of hidden layers is varied from 1 to 3 to explore relatively deeper networks, while the number of neurons is still varied from 10 to 30. We note that incorporating even more hidden layers requires longer computation time and also more training data to avoid overfitting, but the performance improvement can be limited. The results are summarized in Fig. 12. For clarity, only the median metrics P_ML are demonstrated. Different markers are used to represent the results of ANNs with different hidden layers, where circles, asterisks, and triangles correspond to one, two, and three hidden layers, respectively.

[Figure 12: Performance metrics P_ML of different components on the training data, using different network structures.]

[sec3.4_p5] In Fig. 12, the metrics P_ML on training data (dashed lines) are almost monotonously decreasing as both layers and neurons increases. So, generally, more hidden layers and more neurons will lead to better learning capability. Comparing the dashed curves horizontally, it is shown that an ANN with fewer layers but more neurons can have learning capability equivalent to an ANN with more layers but fewer neurons. For example, for ex, the case with 1 hidden layer with 20 neurons and the case with 2 hidden layers with 10 neurons both have P_ML of about 8%. Such phenomena are expected from the theory about ANN but it is still helpful and interesting to be discovered for the orbit prediction problem for the first time.

[sec3.4_p6] In Fig. 12, the generalization performance on testing data (solid lines) shows different trends. For ez and evz, the metrics P_ML are decreasing with respect to the number of both hidden layers and neurons. But for ex, ey, evx, and evy, the ANN with one hidden layer either has the best performance in most cases or appears most stable with respect to the neuron number. We note again that a good learning performance does not always guarantee a good generalization capability, especially for orbit predictions at future epochs. And the results indicate that introducing more layers does not always lead to a better performance for all the components of the orbit prediction error. Therefore, in order to make the best use of historical data, it is helpful to design different structures for different error components. It remains for future studies to develop a systematic procedure to design optimal structures of ANN.

---

## sec4 -- Generalization onto Different RSOs

[sec4_p1] In this section, the type III generalization capability of ANN from the training RSO onto other RSOs is investigated. First, a coverage analysis procedure to check learning variables for the ML approach is presented. Then, we demonstrate and analyze the performance of the trained ANNs on RSOs with different altitudes or right ascension of ascending nodes (RAANs).

[sec4_p2] We have varied the semi-major axis deviation delta_a from -100 to 100 km with a step size of 10 km, and the RAAN deviation delta_Omega from -45 degrees to 45 degrees with a step size of 5 degrees. Figure 13 shows all the orbits for 1 day in the ECI frame.

---

[Figure 13: Orbits of RSOs with varying semi-major axis and RAAN based on ENVISAT for 1 day in the ECI frame.]

### sec4.1 -- Coverage Analysis of Learning Variables

[sec4.1_p1] As has been discovered in our earlier study, checking the range of the learning variables is critical. This is because the range of the variables on the generalized RSOs can be significantly different from those of the training RSO. Here, a brief review is included.

[sec4.1_p2] Take a new RSO, which has an altitude deviations of 10 km from the training RSO, ENVISAT, as an example. The coverage analysis of the learning variables is demonstrated in Fig. 14. Each vertical bar represents the range of a learning variable in the training data, normalized to the range of [0, 1] by its minimum and maximum values. The dots represent the variables in the testing data that have been well-covered by the range of the training data. And the crosses represent the variables, for which at least 10% of data are out of the range [-0.1, 1.1]. This criterion has been chosen through a trial-and-error process. The badly covered variables are also marked with a cross symbol at the bottom of the axis.

[Figure 14: Coverage analysis example of learning variables in training and testing data.]

[sec4.1_p3] Therefore, in this example for ANNs trained by the ENVISAT and then generalized to the new RSO, variables labeled as {2, 4, 18, 20, 22, 27} should be excluded from the learning variables. This procedure will be applied for all the experiments of the Type III generalization.

---

### sec4.2 -- Varying Semi-Major Axis

[sec4.2_p1] In this section, we study the case with different semi-major axes, or the altitude, which is one of the important parameters for RSOs in SSO. As demonstrated in Fig. 13b, the altitude has been varied -100 to 100 km with a step size of 10 km.

[sec4.2_p2] We simulate each new RSO for 5 weeks. The ANNs will be trained by the data of ENVISAT in weeks 1--4, and then the data of the new RSO in week 5 will be used to test the Type III generalization capability of the trained ANNs. Considering that the altitude of the RSO ENVISAT is just about 800 km, as shown in Table 3, a maximum variation of 100 km is relatively large.

[sec4.2_p3] The variables that are badly covered for at least one of the new RSOs with varied semi-major axis will be removed from the redesigned learning variables. In this way, the redesigned learning variables are the same for all RSOs, and so we can compare the performance of ANNs on different RSOs. As a result, the variables labeled as {2, 4, 18, 20, 22, 24, 27} are excluded for the redesigned ANNs. Based on the results in the previous section in Fig. 12, for ex and evx, the network structure is chosen to be 1 hidden layer with 25 neurons, which gives the best performance on the testing data; for ey and evy, the chosen structure is 1 hidden layer with 20 neurons, because its performance is similar compared with those with more neurons and is better or more stable with respect to the neuron number than those with more layers; for ez and evz, the chosen structure is 2 hidden layers with 20 neurons as a compromise between performance and computational burden.

[sec4.2_p4] The performance metrics for all the cases are summarized in Fig. 15. The horizontal axis is the changes of altitude, or semi-major axis, delta_a. As expected, the metrics P_ML on new RSOs increases as |delta_a| increases, which means that fewer orbit prediction errors can be removed when the new RSO has larger semi-major axis difference. When P_ML is larger than 100%, the average residual error after ML modification has not been reduced compared with the original error. For such cases, we will claim the generalization capability as invalid. For other cases with P_ML < 100%, we shall claim the generalization capability as valid. However, we remark that because the performance metric P_ML is defined as the average performance of all data points, and due to the probabilistic nature of the ML approach, orbit prediction errors of some data points can be increased even when P_ML is smaller than 100%.

[Figure 15: Performance of ANNs trained by ENVISAT and tested by new RSOs with different semi-major axes.]

[sec4.2_p5] For ex and ey the generalization capability is valid to all negative delta_a and to positive delta_a until about 30 and 70, respectively. The scattering asterisks also reveal that this generalization capability is, to some extent, robust with respect to the initialization of ANN. The results of evx and evy are less exciting but still show good or at least feasible generalization capabilities for delta_a from about -60 to 20 km and -100 to 60 km, respectively.

[sec4.2_p6] The results of ez and evz in Fig. 15 show that the model cannot be used to correct errors for these two components. We investigate these cases further. First, taking the case with delta_a = 10 km and the random seed 42 as example, the detailed results are demonstrated in Fig. 16. We note that, for all the components except ez and evz, their standard deviations tend to increase with the prediction duration delta_t, and a main effect of ANNs is to reduce the standard deviations. However, the behavior of the standard deviations of ez and evz is different, almost constant, or only slightly increase with delta_t. A physical conjecture is provided here. The motion along z axis, the cross-section axis, reflects the procession of the orbit, which is mainly caused by the nonspherical shape of the Earth. Because the procession motion has already been accurately modeled in the assumed model, the orbit prediction error of ez and evz will mainly contain intrinsic random errors such as the measurement noise, which cannot be eliminated by the proposed ML approach.

[Figure 16: Example of Type III generalization capability to the new RSO with delta_a = 10 km.]

[sec4.2_p7] Using the same case as in Fig. 16, an experiment that considers only the J2 perturbation in the assumed model was carried out to verify the above conjecture. The results are summarized in Fig. 17, where the ANNs are trained by ENVISAT and the new RSO has a delta_a of 10 km. Now, as the orbit prediction errors are much larger due to the less accurate assumed models, the performance of ANNs for all components is significant, especially for ez and evz. Furthermore, the performance metrics when using only J2 perturbation in the assumed model is demonstrated in Fig. 18, which reveals that the trained ANNs have good Type III generalization capabilities to nearby RSOs with different semi-major axes for all the components.

---

[Figure 17: Example of Type III generalization capability to the new RSO with delta_a = 10 km, using J2 perturbation in assumed model.]

[Figure 18: Performance of ANNs trained by ENVISAT and tested by new RSOs with different semi-major axes, using J2 perturbation in assumed model.]

### sec4.3 -- Varying Right Ascension of Ascending Node

[sec4.3_p1] Another important parameter of RSOs in SSO we have examined is the right ascension of ascending node (RAAN). The variation of RAAN, delta_Omega, is varied from -45 degrees to 45 degrees with a step size of 5 degrees, as shown in Fig. 13a. The orbits are propagated for 5 weeks and the data in week 5 are used as the testing data. Because they are all SSOs, their relative geometries in Fig. 13a are constant during the propagation.

[sec4.3_p2] As before, for all the new RSOs with varied RAAN, all badly covered variables have been excluded in the redesigned ANNs, which are the variables labeled as {4, 6, 8, 11, 20, 22, 24, 27}. And the network structures for each component are the same as those in the previous subsection. The results are summarized in Fig. 19. Similar results are observed to show that ANNs have good generalization capabilities around the original RSO for all the components except ez and evz. The reason is similar to what we have discussed in the previous subsection.

---

[Figure 19: Performance of ANNs trained by ENVISAT and tested by RSOs with different RAANs.]

## sec5 -- Conclusions

[sec5_p1] In this paper, the ML approach using ANN to improve the orbit prediction accuracy has been examined and demonstrated with good performance. The ANN models for all the components of the orbit prediction error are trained by the historical data of an RSO in SSO. Two types of generalization capabilities of the trained ANNs have been studied. First, the generalization capability to future epochs is found to be good. And the effect of the random initialization and the network structure has been systematically studied. The initialization is critical to guarantee a good performance, and the best network structures are different for individual error components. Second, the generalization capability to other RSOs is studied, where the ANNs are trained by the same RSO but tested on new RSOs with different semi-major axes or right ascension of ascending nodes. The results reveal that the ANNs could be generalized to a relatively wide range of nearby RSOs that have not been used for training.

[sec5_p2] Together with our previous studies using the support vector machine algorithm, it is further demonstrated that the ML approach is a feasible and promising method in improving orbit prediction accuracy. Besides of the good performance, the results also raise questions for future research. For example, is there a way to find an optimal initialization algorithm or network structure? And how shall we interpret the relationship between trained ANNs (especially with multiple hidden layers) and the physical laws?
