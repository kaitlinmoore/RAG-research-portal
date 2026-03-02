# Synthesis Memo

**Query:** time series prediction errors conjunction data messages temporal accuracy
**Generated:** 2026-03-02T05:35:18.070569+00:00
**Model:** claude-sonnet-4-5-20250929
**Word count:** 1082

---

# Research Synthesis Memo: Temporal Accuracy Challenges in Conjunction Data Message Prediction

## Executive Summary

Time-series prediction of conjunction events faces fundamental accuracy constraints arising from atmospheric uncertainty, data scarcity, and the temporal decay of orbit prediction reliability. Evidence indicates prediction errors scale systematically with miss distance variance and time-to-closest-approach, with machine learning approaches achieving approximately 0.2km accuracy for low-variance events but degrading substantially for high-variance scenarios within 1-2 days of conjunction.

## Temporal Constraints on Conjunction Prediction Accuracy

The accuracy of conjunction predictions deteriorates predictably as forecasting horizons extend. Conjunction Data Messages (CDMs) are generated no earlier than 7 days prior to time of closest approach (TCA) for low Earth orbit specifically due to inherent limitations in orbit prediction accuracy over longer periods, predominantly caused by atmospheric drag effects creating position and velocity uncertainties (mashiku2025, sec2_p2). This temporal boundary represents a hard constraint on prediction systems rather than an operational choice. Furthermore, late notice events—conjunctions identified within 8 hours of TCA—occur due to unpredicted atmospheric drag changes from solar storms or space weather phenomena (mashiku2025, sec2_p2), demonstrating that even short-term predictions remain vulnerable to external perturbations.

The temporal distribution of CDMs itself creates analytical challenges. Operators typically receive approximately three CDMs per day during active conjunction monitoring (catulo2023, sec2.2.2_p2), with significant heterogeneity in both the number of available messages and the actual time-to-TCA at which they become available across different events (uriot2022, sec4_p3). This irregularity complicates efforts to build standardized prediction models, as the available data points vary substantially between conjunction events.

## Quantified Prediction Error Patterns

Recent machine learning approaches have quantified specific error-variance relationships in conjunction prediction. Long Short-Term Memory (LSTM) networks applied to CDM time-series data demonstrated a strong linear relationship between intrinsic miss distance variance and prediction error, with error approximately doubling for each meter of miss distance standard deviation increase (mashiku2025, sec4.2.4_p5). Under optimal conditions—specifically low-variance events—these models achieved miss distance predictions within 0.2km accuracy for observations averaging 1.8 days before TCA (mashiku2025, sec4.2.4_p5). However, performance degraded substantially for events exhibiting high intrinsic miss distance variability across the observation timeline, highlighting fundamental stochasticity in conjunction predictions (mashiku2025, sec4.2.4_p5).

These accuracy limitations persist despite the adoption of recurrent architectures explicitly designed to handle temporal dependencies. Standard neural networks, whether shallow or deep, do not retain memory of previous time-series inputs but focus only on immediate past data during training (mashiku2025, sec3.4_p1). While LSTM networks address this limitation by retaining memory about inputs and utilizing associated memory values for time-dependent prediction (mashiku2025, sec3.4_p1), the evidence suggests that architectural sophistication cannot fully compensate for the underlying physical uncertainty in orbital dynamics.

## Data Scarcity and Its Impact on Temporal Learning

The scarcity of high-risk conjunction events creates significant obstacles for training accurate prediction models. Analysis of 782 total conjunction events yielded only 27 high-risk events (mashiku2025, sec4.2.4_p5), representing approximately 3.5% of the dataset. This extreme class imbalance reflects the reality that most conjunction events eventually result in negligible risk as uncertainties reduce when objects approach each other (uriot2022, sec4_p3). The removal of events requiring avoidance maneuvers from operational databases further reduces the availability of high-risk training examples (uriot2022, sec4_p3).

This scarcity problem is compounded by the limited time horizon available for each event. The combination of few available CDMs per event and the short timeline for analysis constrains the development of reliable prediction models, posing fundamental challenges for AI and ML approaches to conjunction assessment (mashiku2025, sec2_p2). Even when multiple CDMs exist for a single event, the temporal series often spans only several days, limiting the historical context available for pattern recognition.

## Methodological Approaches to Error Quantification

Rigorous error assessment requires careful alignment between predicted states and truth data sources. Satellite state errors are computed by comparing predicted state estimates to truth sources such as onboard GPS precision position data, precision telemetry tracking data, or precision ephemerides (nasa_ca_handbook2023, sec12.3_p1). Ideally, predicted and truth data should align temporally with exact time point correspondence and covariance data at each point (nasa_ca_handbook2023, sec12.3_p1).

The construction of ground truth itself involves temporal assumptions about prediction accuracy. One approach adopts the assumption that predictions with shorter forecasting periods possess greater accuracy, constructing ground truth time-series by selecting predictions closest to production date for each time step (precise_orbit_ml2024, sec2.2_p1). When multiple prediction files contain information for a given time step, prioritizing the most recently produced file establishes a practical standard, though this approach inherently conflates temporal proximity with accuracy.

## Temporal Evolution of Risk Assessment

The temporal dimension affects not only state prediction but also risk quantification methodologies. Analysis of 63,603 temporally isolated conjunction events revealed that two-dimensional probability of collision (Pc) methods underestimate from-TCA values by factors of 1.5 or greater in 0.258% of cases, with Monte Carlo from-epoch reruns matching from-TCA outputs (nasa_ca_handbook2023, sec16.8.2_p6). This finding suggests that temporal positioning relative to TCA introduces systematic biases in certain computational approaches.

Temporal risk plots for repeating conjunction sequences demonstrate the evolution of risk estimates as TCA approaches, with Monte Carlo confidence regions capturing the uncertainty inherent in these evolving predictions (nasa_ca_handbook2023, sec16.8.1_p5). The convergence or divergence of these confidence bounds as additional CDMs arrive provides operators with crucial information about prediction reliability, though the evidence does not quantify specific accuracy improvement rates as TCA approaches.

## Implications and Open Questions

The evidence reveals a fundamental tension in conjunction prediction: the periods when accurate predictions are most needed—immediately before TCA—are precisely when data scarcity and model training limitations are most acute. The 0.2km accuracy achieved by current ML approaches for low-variance events represents meaningful progress, yet the doubling of error with each meter of miss distance variance indicates that the most dangerous conjunctions may be the least predictable.

Several critical gaps remain unaddressed in the available evidence. First, no studies quantify prediction accuracy improvements as a function of the number of CDMs received—understanding whether the 10th CDM provides substantially better information than the 3rd would inform resource allocation decisions. Second, the evidence does not establish whether prediction errors exhibit systematic temporal patterns (e.g., consistent over-estimation at specific time-to-TCA intervals) that could be corrected. Third, the interaction between prediction errors and different orbit regimes beyond low Earth orbit remains unexplored in this evidence base.

Future research should investigate whether hybrid approaches—combining physics-based propagation with ML-based correction terms—can reduce the variance-dependent error scaling observed in pure ML methods. Additionally, developing techniques to synthetically augment high-risk event datasets through simulation might address the training data scarcity that currently limits model performance for the most operationally significant conjunctions.

## References

- acciarini2021 — Introduction to conjunction prediction and CDM generation (2021)
- catulo2023 — Hidden Markov Models for conjunction prediction (2023)
- mashiku2025 — Supervised Machine Learning Approaches for conjunction assessment (2025)
- nasa_ca_handbook2023 — NASA Conjunction Assessment Handbook (2023)
- precise_orbit_ml2024 — Machine learning approaches to precise orbit determination (2024)
- uriot2022 — Competition design for conjunction risk forecasting (2022)