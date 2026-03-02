# Synthesis Memo

**Query:** What are the main failure modes of ML in orbital collision avoidance?
**Generated:** 2026-03-02T05:41:06.682468+00:00
**Model:** claude-sonnet-4-5-20250929
**Word count:** 1140

---

# Machine Learning Failure Modes in Orbital Collision Avoidance: A Research Synthesis

**Executive Summary:** Machine learning applications in spacecraft collision avoidance face fundamental challenges rooted in severe dataset imbalance, operational time constraints, and the critical gap between model performance and deployment readiness. While ML models demonstrate potential improvements over naive forecasting baselines, the field lacks systematic understanding of failure modes that could compromise safety-critical decision-making in orbital operations.

## Introduction

The application of machine learning to spacecraft collision avoidance represents a high-stakes testing ground where algorithmic failures could result in satellite loss or contribute to orbital debris proliferation. Following the 2019 ESA Spacecraft Collision Avoidance Challenge, which released over four years of operational conjunction data messages (CDMs), the research community gained unprecedented access to real-world collision risk data (uriot2022, sec0_p1). However, this opportunity has simultaneously exposed critical failure modes that must be addressed before ML systems can be reliably deployed in operational collision avoidance pipelines.

## Dataset Imbalance and Sampling Bias

The most fundamental failure mode stems from unavoidable dataset imbalance. The ESA competition results demonstrated that "several challenges, mostly derived from the unavoidable unbalanced nature of the dataset, had to be accounted for" and that these challenges "limited" the use of automated, off-the-shelf ML pipelines (uriot2022, sec7_p1). This imbalance reflects operational reality: the vast majority of conjunction events do not result in collisions, creating a dataset dominated by negative examples. When ML models train on such imbalanced data without careful intervention, they can learn to simply predict "no collision" for all cases—achieving high accuracy while completely failing at the safety-critical task of identifying genuine threats.

The imbalance problem compounds with operational constraints. A substantial portion of events—approximately 37.2% of the full dataset—failed to meet basic eligibility requirements for ML approaches (catulo2023, sec3.1_p2). Events must contain at least two CDMs, with the first released before a two-day cut-off and the last within one day of time of closest approach (TCA). This filtering requirement means ML models must learn from an already-constrained sample that may not represent the full distribution of conjunction scenarios operators encounter.

## The Naive Forecasting Benchmark Problem

Perhaps the most surprising and sobering failure mode is the strong performance of naive forecasting methods. Competition results revealed that "naive forecasting models have surprisingly good performances and thus are established as an unavoidable benchmark for any future work" (uriot2022, sec7_p1). This finding suggests that much of the apparent temporal structure in collision risk evolution can be captured by simple extrapolation or persistence models that assume future risk resembles recent risk.

The strength of naive baselines creates a credibility problem for ML deployment. If sophisticated neural networks or ensemble methods achieve only marginal improvements over simple heuristics, the additional complexity, computational cost, and opacity of ML systems becomes difficult to justify. More concerningly, this pattern hints that the CDM time series may contain less predictive signal than initially hoped—most of the "forecasting" may simply reflect measurement refinement as objects approach rather than discovery of new physical information about the conjunction.

## Generalization Failures Beyond Training Data

The competition design process explicitly acknowledged concerns about model generalization, dedicating analysis to "the generalization of ML models in this problem beyond their training data" (uriot2022, sec1.1_p3). This concern reflects a critical failure mode: models that perform well on historical data may fail when confronted with novel conjunction geometries, new classes of debris objects, or changes in the CDM generation process itself.

The collision avoidance domain presents unusual generalization challenges. The physical dynamics of orbital mechanics are well-understood and deterministic, yet the uncertainty quantification in CDMs depends on tracking data quality, which varies based on object size, altitude, observation geometry, and tracking network capabilities. An ML model that learns to exploit artifacts of historical tracking accuracy rather than physical collision mechanics will fail silently when these artifacts change. Furthermore, the conjunction database represents only events that exceeded initial screening thresholds—creating a selection bias where models never observe the full distribution of potential encounters (uriot2022, sec2_p3).

## Operational Integration and Decision Support Failures

Even when ML models achieve technical performance improvements, they face failure modes related to operational integration. Collision avoidance decisions ultimately rest with satellite operators who must balance multiple considerations: mission objectives, fuel constraints, schedule disruptions, and the costs of false alarms versus missed detections (newman2022, sec1_p3). An ML system that provides risk estimates without uncertainty quantification, explainability, or alignment with operational decision-making processes represents a failure regardless of predictive accuracy.

The Kessler library acknowledges this challenge by emphasizing "Bayesian inference and therefore helping operators/users to determine key variables that lead to conjunction events and make reliable predictions (with associated uncertainties)" (acciarini2021, sec5_p1). The explicit emphasis on uncertainty quantification suggests that point predictions alone constitute an insufficient—and potentially dangerous—failure mode. Operators need calibrated probabilities that honestly reflect model limitations rather than overconfident predictions that could lead to either excessive maneuvering (wasting fuel and disrupting missions) or complacency about genuine threats.

## The Automation Readiness Gap

A meta-level failure mode concerns the gap between demonstrating ML feasibility and achieving deployment readiness for "scalable automated systems" (acciarini2021, sec1_p7). The competition successfully showed that "ML models can improve upon such a benchmark, hinting at the possibility of using ML to improve the decision-making process" (uriot2022, sec7_p1). However, "hinting at possibility" falls far short of the reliability standards required for safety-critical automation.

This readiness gap manifests in several dimensions. Current research focuses on predicting final collision risk from CDM sequences ending two days before TCA (catulo2023, sec1_p5), but operational systems must also handle incomplete sequences, corrupted data, delayed messages, and rapidly evolving situations that deviate from historical patterns. The failure modes that emerge in these edge cases—precisely when automated decision support would be most valuable—remain largely uncharacterized.

## Implications and Research Priorities

The evidence reveals that ML in orbital collision avoidance faces a confluence of challenges that extend beyond typical ML deployment concerns. The field needs systematic study of failure modes under distributional shift, adversarial scenarios (such as intentional maneuvers by non-cooperative actors), and cascading failures where incorrect risk assessments lead to suboptimal decisions that increase future collision risk.

**Critical gaps** requiring additional evidence include: (1) failure rates and modes when models encounter conjunction geometries absent from training data, (2) the interaction between ML risk forecasts and human decision-making under time pressure, (3) performance degradation as orbital debris populations evolve beyond historical distributions, and (4) the potential for ML models to introduce new systematic biases that naive methods avoid.

The research community must resist premature deployment enthusiasm. While ML tools show promise for enhancing collision avoidance, the "unavoidable unbalanced nature" of the problem (uriot2022, sec7_p1) and the surprising competitiveness of simple baselines suggest fundamental limitations. Future work should prioritize characterizing failure modes as rigorously as measuring performance improvements—particularly given that the consequences of failure include irreversible contributions to the orbital debris problem that threatens all space operations.

## References

- uriot2022 — Spacecraft Collision Avoidance Challenge: Design and results (2022)
- acciarini2021 — Kessler: ML library for spacecraft collision avoidance (2021)
- catulo2023 — ML methods in collision risk estimation (2023)
- newman2022 — Introduction to Conjunction Assessment at NASA (2022)