# vanslette2024 -- Rapid and Uncertainty Quantified Orbital Propagation using Uncertainty-Aware AI

**Authors:** Kevin Vanslette, Alexander Lay, David Kusterer, Kevin Schroeder
**Venue:** AMOS Conference (2024)
**URL:** https://amostech.com/TechnicalPapers/2024/Machine-Learning-for-SDA/Vanslette.pdf

---

## sec0 -- Abstract

[sec0_p1] Due to the proliferation of Resident Space Objects (RSOs) in Low Earth Orbit (LEO), the task of real-time orbital tracking, propagation, conjunction prediction, and Space Domain Awareness (SDA) over the entire LEO belt is computationally expensive using physics-based methods. Alternatively, traditional data-driven Artificial Intelligence (AI) methods, while being fast and able to produce state-of-the-art metric performance over complex data, can produce overly confident, yet wrong, predictions without warning. We demonstrate the utility of an augmented, covariance predicting, AI framework for scalable orbital propagation of RSOs in LEO. The relative size of the predictive covariance is an indicator of how well this "uncertainty-aware" AI approach understands a given RSO's orbit, and in outlier situations, it overtly predicts large amounts of uncertainty rather than silently producing wrong results. This is a key feature for robust and performant SDA applications because it enables down-stream decision systems to choose whether a given AI prediction should be trusted and utilized or ignored and replaced. Trained over a relatively small dataset, the method forecasts the orbital trajectories of 34K RSOs one day into the future (5-minute intervals) on a single Graphical Processing Unit (GPU) in 5.5 seconds with 46.6 km Root Mean Squared Error (RMSE). Single orbit forecasts maintained RMSEs as low as 5.8 km and were able to propagate 1 million ephemerides in 12.1 seconds. Thus, the method offers practitioners a solution in the trade space between computational speed and accuracy while dynamically quantifying expected performance in terms of predicted uncertainty. This preliminary work begins exploring the utility of uncertainty predicting AI for scalable space domain awareness.

---

## sec1 -- Introduction

[sec1_p1] It is no surprise that most Space Domain Awareness (SDA) applications have considerable functional dependence on the current and future position estimates of Resident Space Objects (RSOs). At the lowest level, and due to observation intermittence, RSO orbital track estimates need to be maintained so future observations can be properly correlated with them. Forecasts of these tracks are important decision variables in higher level SDA planning applications for space traffic management, conjunction and collision avoidance, higher level data fusion analytics, and space debris cleanup planning. Any error, uncertainty, and/or latency in the production of these track forecasts propagate to downstream SDA applications, which diminishes their utility. The community has expended significant modeling effort and computational resources create high fidelity and scalable solutions for maintaining and forecasting RSO tracks with uncertainty.

[sec1_p2] For applications like space traffic management in the Low Earth Orbit (LEO) regime, tracks and track forecasts need to be maintained to identify potential conjunctions and collisions so avoidance maneuvers can be scheduled. ESA's 2024 Space Environment Report estimates there are about 34K objects greater and 10cm in LEO and nearly 1 million between 1 and 10cm, both of which can create computational challenges for space traffic management. While physics-based parametric models for tracking and propagation have long-standing and proven high fidelity, reliability, explainability, and an ability to quantify and forecast track uncertainty, the methods themselves can require significant computational resources at this scale. Speed (or computational complexity) and accuracy can be traded off by choosing which special perturbations to use in a given model; however, there is a significant gap in the speed-accuracy trade space between simple Keplerian motion and J2 or other special perturbations.

[sec1_p3] Alternatively, there are many classes of non-parametric Artificial Intelligence (AI) models that may be able to populate useful regions within the speed-accuracy trade space to give more modeling flexibility to practitioners. AI models move the bulk of the computational heavy lifting into offline training phases which generates models that can be evaluated quickly and with relatively low computational complexity due to Graphical Processing Unit (GPU) parallelization.

[sec1_p4] AI modeling approaches, while being known for being able to make fast and accurate predictions over complex datasets, often still fail to meet the high reliability and robustness standards that would allow for their adoption into critical space domain applications. In particular, in outlier scenarios, traditional AI methods often and without warning produce overly confident, yet wrong, predictions. This is to say, it is not good enough to train models that make state-of-the-art accurate predictions over "inlier" training datasets if the model then fails to generalize appropriately in real world applications that may include "outliers". This is a major problem for AI-based SDA applications because not only is the prediction wrong, it is wrong without warning of possible errors, which could compromise the integrity of downstream processing and decision making.

[sec1_p5] Outlier scenarios arise when applying an AI model outside of the domain of the training data. Deviations from the domain of the training data may be driven dynamically by environmental non-stationary or may be due to induced scope/domain training and testing mismatches. For the problem of ephemeris propagation in LEO, the former would include things like increased drag in LEO due to solar maximum (11 year cycle), while the later would include expecting training a model on one orbital regime to generalize to another or expecting models trained on low fidelity simulators that do not reflect reality well and testing on real data.

[sec1_p6] We believe a subfield of AI called Uncertainty-Aware AI (UA-AI) could be of considerable interest to the SDA community. UA-AI models differ from traditional AI models in that they are trained not only to make point predictions (i.e. a mean or classification probability vector), but also to predict distributional parameters (e.g. the variance around a classification probability vector) as additional outputs from the neural network. While it is relatively straightforward for these models to learn the aleatoric (statistical) uncertainty of inlier dataset and model pair, an ongoing challenge is getting these models to reliably estimate their own predictive uncertainty when presented with outlier data, as is reviewed in [5]. However, training a small ensemble of uncertainty-aware networks (over the same data, about 5 models) and probabilistically combining their results has been shown to significantly improve uncertainty estimation in outlier data regions, that is, it reliably predicts large uncertainty there. This ensemble method exploits inter-model disagreement due to the differences in the learned high dimensional model parameters. UA-AI approaches exist for regression, classification, object detection and segmentation based on these concepts and UA-AI attempts to tackle the problem of outliers directly through predictive uncertainty and a variety of UA-AI modeling approaches exist.

[sec1_p7] To demonstrate the feasibility of this approach, we apply UA-AI techniques to the problem of ephemeris forecasting in LEO. The dataset consists of the ephemerides of about 19K RSOs simulated over a 3 day period (5 minute intervals) generated using a high fidelity numerical propagator. The data includes cartesian position and velocity, their complementary orbital elements, and relative positions from the RSO to the Moon and Sun. We trained a small ensemble of UA-AI feed forward neural networks (with convolutional layers) that jointly forecast entire ephemeris trajectories in a single pass as well as their multi-time covariance matrices. We performed two different forecasting cases, the first predicts ephemeris up to 100 minutes ahead ("single orbit") and the second predicts ephemeris up to 1 day ahead along with their covariance matrices. We explored performance gains and losses of predicting fully specified multi-time covariance matrices vs block diagonal covariance matrices that had no inter-time correlations modelled. We demonstrate that the approach is robust to outliers by training the model on ephemeris with small eccentricity but tested them on ephemeris with the largest eccentricity in our dataset. We also explored using a multi-modal multivariate Gaussian mixture model, which alone was less robust to outliers than the ensemble of unimodal Gaussian mixtures.

[sec1_p8] We introduce the data and simulation in Section 2, the UA-AI approached used in Section 3, experimental setup and results in Section 4, and we conclude with a discussion of applications and expansions of this work in Section 5.

---

## sec2 -- Data and Simulation

[sec2_p1] The propagation of the orbital states of RSOs within the LEO regime was conducted using a robust and precise numerical integrator. The scope of the simulation encompassed a total of 19,210 RSOs, across various orbital altitudes for a span of 3 days. The numerical propagator used was extracted from the REsponsive Space ObservatioN Analysis and Autonomous Tasking Engine (RESONAATE), previously developed by researchers at the Virginia Tech National Security Institute (VTNSI).

[sec2_p2] The RESONAATE tool is a discrete time Space Object Surveillance and Identification (SOSI) modeling and simulation tool with a verified turnkey orbital propagator built-in. A key feature of the tool is the modularity of the spacecraft dynamics; therefore, the dynamics can be as precise as the scenario requires. The model can incorporate whichever gravity model (e.g. WGS84, EGM96, EGM2008) is needed with precise Earth procession and nutation parameters included. Sun and Moon, as well as other third body perturbations can be toggled on or off depending on the scenario. Solar radiation pressure, Earth albedo, and relativistic effects are also included as options to provide high-fidelity state estimation and covariance.

[sec2_p3] The propagation of the RSOs was performed using the Special Perturbations (SP) method, a high-fidelity approach that computes the trajectory of each object by numerically integrating the full set of perturbative forces acting on it. Among the perturbative forces accounted for were the gravitational influences of third bodies, specifically the Sun and Moon. These third-body perturbations are critical for accurately modeling the long-term evolution of orbits in the LEO regime, where gravitational interactions with these celestial bodies can induce significant deviations from purely Keplerian motion.

[sec2_p4] In addition to third-body perturbations, the Earth's gravitational field was modeled using the EGM96 geopotential model, truncated at degree 4 and order 4. This truncation was chosen to balance computational efficiency with the need for accuracy in modeling the Earth's gravitational perturbations. The EGM96 model, with its detailed representation of the Earth's gravitational anomalies, is particularly suited for precise orbit determination and prediction in the LEO environment.

[sec2_p5] Notably, the simulation did not account for the effects of drag, solar radiation pressure, or solid dynamic tides. The exclusion of these perturbation was deemed acceptable given the relatively short duration of the propagation and the focus on gravitational perturbations. While these perturbations can be important in certain high-precision scenarios, and are especially import for very low orbits, they were considered negligible for the scope of this simulation.

[sec2_p6] The numerical integration of the equations of motion was carried out using the 'RK45' solver, a member of the Runge-Kutta family, implemented in the 'scipy.integrate' package. The 'RK45' method was selected for its adaptive step size control, which dynamically adjusts the step size to maintain the specified error tolerances. This adaptive approach is particularly advantageous when dealing with the varying dynamical conditions encountered in LEO, where orbital velocities and perturbative forces can change rapidly. To ensure a high level of numerical precision, the integration was performed with a relative tolerance of 10^-10 and an absolute tolerance of 10^-12. These stringent tolerances were essential for maintaining the accuracy of the propagation over the extended simulation period. The chosen tolerances also helped to mitigate the accumulation of numerical errors, which can become significant in long-term integrations of orbital systems.

[sec2_p7] The generated ephemerides were transformed and expressed using 6 cartesian coordinates, 6 classical orbital elements, plus 6 coordinates indicating relative position of the Moon and Sun:

[Equation 1: State vector x_t^(j) consisting of 18 components -- cartesian position and velocity (x, y, z, vx, vy, vz), classical orbital elements (a, e, i, Omega, omega, T), and relative positions to Moon and Sun (xm, ym, zm, xs, ys, zs) -- indexed by timestamp t and RSO identification number j]

all of which are indexed by timestamp t and RSO identification number j.

[sec2_p8] The computational resources allocated to each data run consisted of 32 CPU cores, allowing for parallel processing to optimize the computational efficiency. The hardware utilized in this simulation was based on AMD EPYC 7542 processors, part of the EPYC 7002 Series designed specifically for server applications. Each processor features 32 CPU cores and 64 threads, operating at an overclock speed of up to 3.4 GHz. The processors are equipped with 128 MB of L3 cache, providing ample memory bandwidth for the intensive calculations required by the simulation.

[sec2_p9] The data run was distributed across four independent nodes. Each data run was tasked with propagating approximately 4,800 RSOs. Given this hardware configuration, each data run completed in approximately 115.28 hours. The processing rate was approximately 0.625 times real-time, indicating that the simulation covered 72 hours of orbital evolution in 115.28 hours of wall-clock time. This ratio underscores the computational demand of accurately propagating many RSOs over extended periods while maintaining high precision. While neither the hardware nor the software was fully optimized for this application, the described system is representative of the computational expense of the traditional physics-based orbital propagators. Overall, the combination of high-performance computing resources, high-fidelity perturbation modeling, and precise numerical integration enabled the accurate propagation of a large and diverse set of RSOs in the LEO environment. The results from this simulation provide a detailed and reliable basis for subsequent analyses of orbital behavior and collision risk assessment in LEO.

---

## sec3 -- Uncertainty-Aware AI Approach

[sec3_p1] We introduce the proposed UA-AI approach for ephemeris forecasting. In particular, we propose treating the problem like a multi-dimensional regression problem with fixed input and output sizes rather than as a sequential timeseries problem using recurrent neural networks (RNNs) or long-short term memory (LSTM) models.

[sec3_p2] Many physics-based solutions in this domain are sequential in nature, which results in error profiles that grow nonlinearly in the number of propagation steps. Further, the sequential nature of these approaches creates a computational bottleneck is that the previous step needs to be computed before the next step can be computed. While the proposed multi-dimensional regression method has fixed input and output sizes, it makes predictions in parallel across the ephemeris, increasing speed, while also not having the characteristic nonlinear error profile of sequential methods.

### sec3.1 -- Deep Multivariate Gaussian Model

[sec3.1_p1] Let a sample of input feature data (past multi-dimensional window of orbital data) be represented by a kx dimensional vector x in R^kx and its corresponding label (future multi-dimensional window of positional ephemeris) be a represented by a ky dimensional vector y in R^ky. We model a deep multivariate Gaussian distribution following [9],

[Equation 2: Deep multivariate Gaussian distribution rho(y|mu(x), Sigma(x)) -- the probability density of label y given neural network outputs for the mean mu(x) and covariance matrix Sigma(x)]

where mu(x) is mu: R^kx to R^ky and Sigma(x) is Sigma: R^kx to R^(ky x ky) are outputs from a neural network. The data (x,y) is treated like a completely certain quantity and the mean and covariance parametrically model the expected uncertainty, or error, in the neural prediction as a multivariate Gaussian. The neural network is trained to minimize the negative log likelihood,

[Equation 3: Negative log likelihood loss L(x,y) consisting of a Mahalanobis distance term (y - mu(x))^T Sigma(x)^-1 (y - mu(x)) plus the log determinant of the covariance ln(|Sigma(x)|)]

which is averaged over batches of data samples. The covariance matrix Sigma(x) is forced to be is symmetric positive definite through Cholesky decomposition,

[Equation 4: Cholesky decomposition Sigma(x) = L(x) L(x)^T where L(x) is a real positive lower triangular matrix]

where L(x) is a real positive lower triangular matrix, which we guarantee through the choice of positive activation functions along the diagonal elements of L. It should be noted that the predictive covariance in this case represents the AI model's uncertainty in its prediction of the ephemeris (most similar to a quantification of expected error) and is not equal to the process noise driven state covariance matrices that would be generated as part of a Kalman Filter paradigm orbital propagator.

[sec3.1_p2] Because the data is normalized between [-1,1] prior to training and because ky is relatively large in this orbital propagation problem, direct computations of the determinant and matrix inverse are not numerically stable. This is because the computation of the determinant involves computing ky products of values < 1, which can become exponentially small. We largely circumvent this issue by using logarithm tricks while also forcing the neural model to directly predict the inverse covariance matrices,

[Equation 5: Redefinition of L(x)L(x)^T as the Cholesky decomposition of the inverse covariance matrix Sigma(x)^-1 instead of Sigma(x)]

where we redefine L(x) to be the Cholesky decomposition of the (also symmetric positive semidefinite) inverse covariance matrix Sigma(x)^-1 instead, for notational simplicity in all future equations. In addition to helping with numerical stability, this also speeds up training time by avoiding inverse matrix evaluations and back propagation gradients. The log of the determinant of the inverse covariance is then,

[Equation 6: Log determinant of the inverse covariance as 2 times the sum of the log of diagonal elements of L -- ln(|Sigma^-1(x)|) = 2 sum_i ln(Lii(x))]

where Lii(x) is the ith diagonal element of L due to the eigenvalue product determinant relationship |L| = product of eigenvalues lambda_i and because the eigenvalues of L, lambda_i = Lii(x), are equal to the diagonal elements of positive lower triangular matrices.

[sec3.1_p3] Using these relations, and the identity ln(|Sigma(x)|) = -ln(|Sigma^-1(x)|), we cast the negative log likelihood into a more numerically stable form in terms of L,

[Equation 7: Numerically stable negative log likelihood L(x,y) = 0.5 (y - mu(x))^T (L(x)L(x)^T)(y - mu(x)) minus sum_i ln(Lii(x)) plus constant]

We implemented a custom neural network layer to output mu(x) and L(x) given data x or neural transformations of x to f(x) from upstream neural layers. This approach is particularly well suited when applications only require inverse covariance matrices (such as for computing Mahalanobis distances), because computing numerically stable inverses of Sigma^-1(x) require using matrix exponentials and logarithms Sigma(x) = exp(-ln(Sigma^-1(x))) in extreme cases.

[sec3.1_p4] We perform a non-exhaustive random hyperparameter search as part of the training process.

[sec3.1_p5] [Table 1: Hyperparameter Search Space.] The hyperparameter search space includes: number of convolution layers [0,8], number of filters per convolutional layer [32,256], number of dense neural layers [0,15], number of neurons per dense layer [75,1500], and Scale L [1,200].

[sec3.1_p6] Because the negative log likelihood does not directly try to minimize the error between mu(x) and y, the optimization would sometimes get "lazy" in its prediction of mu(x) and use the prediction of large covariance matrices to "hide" what would be considered large predictive errors |mu(x) - y| in this domain. To combat this "laziness", we included hyperparameters that scale L, which generally encouraged the optimizer to find more precise mu(x) predictions while improving negative log likelihood. We also searched over a few activation functions, learning rates, and batch sizes. In addition to implementing a method for predicting fully populated covariance matrices, we also implemented a block diagonal covariance model using sparse tensors. As a final post processing step, covariance matrices are rescaled to reproduce mean squared errors in the training set.

### sec3.2 -- Ensembling UA-AI Models for Outlier Robustness

[sec3.2_p1] We use a deep ensembles approach, but generalized to the multivariate domain through the construction of "ensemble covariance" via the law of total covariance. Like to the law of total variance, the ensemble covariance decomposes into the inlier (learnable, aleatoric) covariance and the outlier (estimated, epistemic) covariance, respectively,

[Equation 8: Law of total covariance -- Cov[yi, yj] = E[Sigma_g^(i,j)(x)] (inlier covariance) + Cov[mu_g^i(x), mu_g^j(x)] (outlier covariance), defining the total covariance Sigma_T(x)]

Here, the superscripts i, j are the i, jth components of y, Sigma, and mu and G are the total number of models in the ensemble. We use uniform 1/G ensemble member mixing, and empirically, ensembling G approximately 5 models is typically sufficient. Letting the ensemble mean be mu_T(x) = (1/G) sum_{g=1}^{G} mu_g(x) and the ensemble (total) covariance be Sigma_T(x), the resultant ensemble model is a unimodal multivariate Gaussian distribution rho(y|mu_T(x), Sigma_T(x)).

[sec3.2_p2] Even if the G models are trained over the same data and have the same hyperparameters, the approach (tuned weights/parameter values sets) taken by stochastic training algorithms is to randomly initialize a set of parameters. This means, with great certainty, the learned solutions end up very far away from one another due to the very high dimensional parameter spaces of neural networks. However, in regions with sufficient training data, the training process causes the ensemble member mu predictions to corroborate with one another, leading to small (co)variances of the mu's. Alternatively, far outside this sufficient data region, and because the models are so far away from one another in parameter space, the ensemble members have no reason to agree with one another and tend to disagree, which leads to an increase in ensemble covariance.

### sec3.3 -- Deep Multivariate Gaussian Mixture Model

[sec3.3_p1] As an alternative to ensembling unimodal deep multivariate Gaussian models, we considered a deep multivariate Gaussian mixture model,

[Equation 9: Deep multivariate Gaussian mixture model rho(y|mu_{1:M}, Sigma_{1:M}, alpha_{1:M}) as a weighted sum of M Gaussian components with mode weights alpha_m(x) that normalize to 1]

where M is the number mixture modes and alpha_{1:M}(x) are positive mode weights, which normalize to 1 through the choice of an appropriate activation function. The negative log likelihood of the deep multivariate Gaussian mixture takes the form of the log-sum-exponential (LSE) function LSE(z1,...,zM) = ln(sum_{m=1}^{M} exp(zm)), which is a standard function in most scientific computing libraries and is numerically stable. The negative log likelihood of the mixture distribution is

[Equation 10: Negative log likelihood of the mixture distribution L(x,y,M) = -LSE(L'_1(x,y),...,L'_M(x,y)) where L'_m includes the negative log likelihood of mode m plus the log of its mode weight]

where L'_m(x,y) = -L_m(x,y) + ln(alpha_m(x)) is the negative log likelihood of the mth mode from (7), L_m(x,y), plus the log of its corresponding mode weight, ln(alpha_m(x)). The number of mixture modes M is a free variable in our custom neural network layer, where M = 1 reproduces the unimodal case from Section 3.1, that is, L(x,y,M = 1) = L(x,y).

[sec3.3_p2] As we are interested in comparing this model's performance on outlier data to the ensemble method from the previous subsection, we compute an analogous total covariance quantity from (8), but instead replace ensemble members with mixture modes. This "mixture total covariance" quantity is (8) given that ensemble members are replace by modes g to m and uniform ensemble averaging is replace by mode weight averaging. For instance, the predictive mixture mean is instead mu_T(x) = sum_{m=1}^{M} alpha_m(x) mu_m(x).

---

## sec4 -- Experiments and Results

[sec4_p1] We summarize the experimental setup and results of our approach.

### sec4.1 -- Data and Processing

[sec4.1_p1] The dataset was split multiple ways to test the approach against both inlier and outlier data. The dataset was first split into "outlier" testing data, which consists of orbits having the largest 1% eccentricity values, e_1% in [0.061, 0.22], which we use for testing the method is robust to outliers. The remaining "inlier" data was randomly split into training and testing datasets such that 15% of this dataset is reserved for testing the fidelity and compute speed of the models. It should be noted that, in a sense, what makes the "outlier" testing data an outlier in the context of AI modeling is that these large eccentricity values were not included in the training data. If instead they were included, then the AI training method would be forced to learn how to handle these cases statistically.

[sec4.1_p2] In our problem, we let the input features be a concatenation of Tx time steps of ephemeris data from equation (1), x = [x^(j)_{t=1},...,x^(j)_{t=Tx}], which is kx = 18*Tx dimensional, and let the labels to be predicted be the concatenation of Ty three future dimensional position coordinates of the RSO, y = [(x, y, z)^(j)_{t=Tx+1},...,(x, y, z)^(j)_{t=Tx+Ty}], which is ky = 3*Ty dimensional. We consider two scenarios, the first for forecasting a ephemeris a single orbit (approximately 100 minutes) into the future and the second for forecasting ephemeris one day into the future (5 minute time intervals).

[sec4.1_p3] [Table 2: Feature and Label Data Dimensions.] The feature and label data dimensions for each scenario are as follows: Single Orbit uses Tx=10, kx=180, Ty=20, ky=60, and 448K training rows. Single Day uses Tx=30, kx=540, Ty=288, ky=864, and 161K training rows.

[sec4.1_p4] The single orbit prediction experiment has more rows available for training than the single day prediction experiment because there are more non-overlapping single orbit input windows available (due to the dimensions above) than single day windows in this 3-day, 19K RSO, simulated dataset. Because ky is relatively high dimensional in the single day case, we also explored using sparse block diagonal matrices (no inter-time correlations) to reduce the number of covariance elements that need be predicted by the model from (k^2_y + ky)/2 (because the matrix is symmetric) to 6*Ty (as there is one 3x3 lower triangular Cholesky matrix per timestep, which has 6 elements). For the single day model, this reduces the number of covariance related outputs from (864^2 + 864)/2 = 373,680 to 6 x 288 = 1,728.

[sec4.1_p5] We trained models on an A6000 GPU with 48 GB of GPU memory and 4 CPU cores having 10 GB of RAM per CPU, which run at 3.8 GHz. The models used in the experiments were trained upwards of 1,000 epochs, which took between 3.5 hour 7.5 hours. The single orbit model sizes varied from 5.5 MB to 82 MB, while the single day models used were larger, about 375 MB. The best candidate models we found through hyperparameter search tended to have 1 or 2 temporal convolutional layers with a medium number of filters (convolutional layers, if present, are prepended to the network), 4-9 dense layers with a medium number of neurons, and a medium L scale factor.

[sec4.1_p6] We performed speed tests at two different scales: tau_34K, which is the amount of time to propagate 34K RSOs (hypothetically all objects greater than 10cm in LEO), and tau_1M, which is the amount of time to propagate 1 million objects in LEO (hypothetically all objects between 1-10cm). The times recorded are averaged over 20 trials, and include the time it takes to push data in and out of the GPU. Bold values indicate perceived good performance.

### sec4.2 -- Inlier Experiments

[sec4.2_p1] These experiments review the performance of the individual UA-AI models and their ensemble against the held out test dataset.

#### sec4.2.1 -- Single Orbit Forecasts

[sec4.2.1_p1] We compare the performance of two single orbit UA-AI models, a fully populated (60,60) predictive covariance matrix and a sparse block diagonal implementation that ignores inter-time correlations. Each ensemble consists of G = 5 ensemble members and the multivariate Gaussian mixture model is set to M = 5 modes for comparison purposes. We calculate the following quantities and record them in the table: We compute the (positional) Root Mean Squared Errors (RMSEs) between the predicted means mu_t(x) at time t and its corresponding true value yt = (x, y, z)_t per timestep which we then average over time. Because each ensemble is comprised of G = 5 models, we recorded their lowest and highest individual model RMSEs in square brackets. The RMSE for the multivariate Gaussian mixture model is computed using the M = 5 mixture weights before averaging over time.

[sec4.2.1_p2] [Table 3: Inlier Data: Single Orbit Model.] Results for the single orbit model on inlier data (RMSE in km, tau in seconds): Full Cov. Individuals RMSE [9.2 km, 14.5 km], tau_34K 0.0215 s, tau_1M 0.62 s. Full Cov. Ensemble RMSE 7.6 km, tau_34K 0.254 s, tau_1M 7.38 s. Block Cov. Individuals RMSE [8.1 km, 15.4 km], tau_34K 0.0129 s, tau_1M 0.173 s. Block Cov. Ensemble RMSE 5.8 km, tau_34K 0.446 s, tau_1M 12.1 s. Full Cov. Mixture Model Individual RMSE 22 km, tau_34K 0.093 s, tau_1M 2.77 s.

[sec4.2.1_p3] The RMSE for these models remain relatively flat over the period of a single orbit, as shown in Figure 3.

[Figure 1: Single orbit RMSE on inlier data. (a) Full covariance (b) Block Diagonal]

#### sec4.2.2 -- Single Day Forecasts

[sec4.2.2_p1] We compare single and ensemble performance similarly for the single day forecast experiment. Due to memory limitations and the effectiveness of the block diagonal covariance models in the single orbit experiment, we only trained sparse block diagonal single day models. We did not implement a sparse multivariate Gaussian mixture model, so it is omitted.

[sec4.2.2_p2] [Table 4: Inlier Data: Single Day Model.] Results for the single day model on inlier data (RMSE in km, tau in seconds): Block Cov. Individuals RMSE [82.3 km, 91.4 km], tau_34K 0.0849 s, tau_1M 2.46 s. Block Cov. Ensemble RMSE 46.6 km, tau_34K 5.53 s, tau_1M 162.4 s.

[Figure 2: Single day model RMSE over inlier data.]

### sec4.3 -- Outlier Experiments

[sec4.3_p1] These experiments review the performance of the UA-AI models against the eccentricity outlier dataset. We record the relative multiplier of how much larger the outlier RMSE and the time averaged UA-AI model predicted positional displacement standard deviation, sigma_D = (1/T) sum_{t=1}^{T} sigma_{D,t} = (1/T) sum_{t=1}^{T} sqrt(sigma^2_{x,t} + sigma^2_{y,t} + sigma^2_{z,t}), are compared to their inlier counterparts.

[sec4.3_p2] [Table 5: Outlier Data: Uncertainty Awareness.] Results showing RMSE Multiplier and sigma_D Multiplier for outlier vs inlier data: Single Orbit Full Cov. Individuals RMSE Multiplier [7.81, 8.38], sigma_D Multiplier [0.96, 1.02]. Single Orbit Full Cov. Ensemble RMSE Multiplier 10.3, sigma_D Multiplier 4.25. Single Orbit Block Cov. Individuals RMSE Multiplier [5.58, 7.25], sigma_D Multiplier [0.97, 0.99]. Single Orbit Block Cov. Ensemble RMSE Multiplier 8.71, sigma_D Multiplier 4.11. Single Orbit Full Cov. Mixture Model Individual RMSE Multiplier 11.6, sigma_D Multiplier 2.01. Single Day Block Cov. Individuals RMSE Multiplier [3.02, 3.47], sigma_D Multiplier [1.00, 1.02]. Single Day Block Cov. Ensemble RMSE Multiplier 4.5, sigma_D Multiplier 1.98.

[sec4.3_p3] Relative to the increase in RMSE, the ensemble models were more indicative of being in an outlier regime than were the individual models, including the mixture model.

[Figure 3: Single orbit RMSE on outlier data. (a) Full covariance (b) Block Diagonal. We believe RMSE rises and falls because the model learned to exploit the cyclic nature of orbits.]

[sec4.3_p4] While it is unreasonable to expect good RMSE over the outlier data, the UA-AI ensemble models do predict large covariances in high RMSE situations. Note how the individual model covariances not changing much in Table 5 correspond to the "inlier" covariance term in (8), which indicates that the ensemble covariances grew due to the outlier term in (8). The RMSEs are plotted over time in Figures 3 & 4.

[sec4.3_p5] Finally, we also compared the growth in RMSE to the ensemble model predicted sigma_D's over eccentricity in Figures 5, 6, & 7. We see the anticipated growth in RMSE as the 0.089 inlier/outlier eccentricity boundary is approached and surpassed. Further, the key desirable feature that the predicted sigma_D's generally trend upward as the RMSE and eccentricity grows is indicative of the ensemble models' ability to understand and predict their own uncertainty. The single day model did not have as stark an increase in the predicted sigma_D as compared to the single orbit models, but this can likely be explained by the fact that the single day outlier RMSE did not increase as much either.

[Figure 4: Single day model RMSE over outlier data.]

[Figure 5: The RMSE and predicted sigma_D's follow a similar upward trend indicating uncertainty-awareness. They share similar peaks on the inlier testing data, which means both that all statistical outliers in this data cannot be prescribed to large eccentricity alone and that the ensemble model recognizes its own inability to make accurate predictions on those cases. (a) RMSE: Full Covariance Single Orbit Model (b) sigma_D: Full Covariance Single Orbit Model]

[Figure 6: The block diagonal single orbit model shares the same uncertainty-awareness features as the full covariance single orbit model from Figure 5. (a) RMSE: Block Diagonal Single Orbit Model (b) sigma_D: Block Diagonal Single Orbit Model]

[Figure 7: The block diagonal single day model is similarly uncertainty-aware, but the increase in the outlier domain is less pronounced, likely due to the RMSE there not increasing as much as the single orbit models. There are many similarities in the peaks, some of which are overly pronounced in the single orbit model, but the predictions still reliably indicate the large outlier cases. (a) RMSE: Block Diagonal Single Day Model (b) sigma_D: Block Diagonal Single Day Model]

---

## sec5 -- Discussion

[sec5_p1] The UA-AI LEO ephemeris prediction models we found sit in the middle of the accuracy-speed trade space between highly accurate, but slow, special perturbation models and inaccurate, but fast, simple 2-body Keplerian motion models. Due to J2 and other perturbations in LEO, 2-body Keplerian motion models can easily pick up between 2-5 degrees of angular error over the course of a day (somewhere around 250km-625km). Our single day ensemble model maintained RMSEs around 45 km and our single orbit ensemble model maintained RMSEs around 6 km. In terms of speed, these models were able to forecast 1 million ephemerides in the LEO belt on the order of seconds or minutes rather than days or weeks.

[sec5_p2] While we were able to find some relatively performant UA-AI models, our hyperparameter search (approximately 250 shallowly trained models) only just started to explore the large set of possible UA-AI models that could be trained or designed. As an example, our choice of the number of timesteps in the input dimension to be 10 and 30 for the single orbit and single day models, respectively, was relatively arbitrary and not explored nor optimized. The large space of possible UA-AI models can potentially densely populate new/sparse regions in the accuracy-speed modeling trade space.

[sec5_p3] Further, although not shown explicitly in our experiments above, the amount of data available for training has a considerable impact on performance. Prior to the 19,210 RSO 3-day dataset, we had a similar but smaller dataset consisting of about 750 RSOs. Even with hyperparameter search, we had difficulty breaking an RSME of about 60km in the single orbit experiment with this smaller dataset. However, taking that model, and without changing its hyperparameters, the model reached a RMSE of about 15km when training on the larger dataset. While there are almost certainly diminishing returns in performance as the amount of data increases, it is encouraging that with more data the models could continue to improve. Further, it should be noted that we had to stop the single day training short, which was still continuing to improve at the time of submission.

[sec5_p4] The ability of these neural models to make rapid predictions, while also maintaining accuracy, implies this approach can handle the increase in complexity required to propagate ephemeris uncertainty along with mean ephemeris by pushing thousands of representative Monte Carlo samples (particle filter propagation) through the UA-AI model. Similarly, or perhaps in addition, this method could be used for "quick and dirty" space traffic control/conjunction screening to rapidly rule out large swaths of infeasible conjunctions, in an uncertainty quantified manner. Alternatively, if ephemeris training data comes with heteroskedastic uncertainties, these uncertainties could likely be learned outright and predicted by the UA-AI model. It would be interesting to see how well this approach performs on other orbital regimes or realistic, non-simulated, orbits with maneuvers.

[sec5_p5] An essential feature of this uncertainty-aware AI approach is that its predicted uncertainty measures can be used to overcome some critical limitations that prevent AI's wide adoption into SDA applications. Because our UA-AI ensemble models were able to correctly identify, predict, and indicate when their performance is expected to diminish due to the presence of outliers, this information can be used to build more efficient decision systems. Rather than running computationally expensive propagators for all RSOs in LEO, one could instead opt to only run these propagators if the UA-AI exceeds a prediction uncertainty tolerance, or in a conjunction screening scenario, if the system similarly exceeds a miss distance and uncertainty tolerance. Such an approach would drive down computational cost and free up additional resources.

[Appendix: Acknowledgements omitted -- funding/collaborator names only]
