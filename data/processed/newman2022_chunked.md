# newman2022 -- Conjunction Assessment: NASA Best Practices and Lessons Learned

**Authors:** Lauri K. Newman, Alinda K. Mashiku, Daniel E. Oltrogge
**Venue:** AMOS Conference 2022 (2022)
**DOI:** https://ntrs.nasa.gov/citations/20220013191

---

## sec0 -- Abstract

[sec0_p1] This presentation, delivered at the 2022 AMOS Conference, documents NASA's best practices and lessons learned for conjunction assessment (CA). It covers the introduction to conjunction assessment at NASA, key best practices for spacecraft design and operations, and challenges and future work including autonomous maneuvering, active-versus-active CA issues, and cis-lunar CA.

---

## sec1 -- Introduction to Conjunction Assessment at NASA

[sec1_p1] Conjunction Assessment (CA) is the process of identifying close approaches between two orbiting objects, sometimes called conjunction "screening." The 18th Space Defense Squadron (18 SDS) at Vandenberg SFB maintains the high accuracy catalog of space objects. Orbital Safety Analysts (OSAs) at VSFB screen protected assets against the catalog, perform tasking requests, and generate close approach data.

[sec1_p2] CA Risk Analysis (CARA) is the process of assessing collision risk and assisting satellites in planning maneuvers to mitigate that risk, if warranted. The NASA CARA program performs risk assessment for all NASA operational non-human space flight (HSF) satellites, and some partner missions. JSC performs risk assessment for all NASA HSF program assets and also performs maneuver decisions and execution.

[sec1_p3] Collision Avoidance is the process of executing mitigative action, typically in the form of an orbital maneuver, to reduce collision risk. Each satellite Owner/Operator (O/O) -- mission management, flight dynamics, and flight operations -- is responsible for making maneuver decisions and executing the maneuvers.

[Figure 1: CA Operations 3-Step Process. Three orbital diagrams illustrate the stages: (1) Conjunction Assessment (screening) shows a primary spacecraft with multiple secondary objects on intersecting trajectories; (2) CA Risk Analysis (CARA) shows a primary spacecraft and single secondary object with overlapping uncertainty ellipsoids at the point of closest approach; (3) Collision Avoidance shows the primary spacecraft executing a delta-V maneuver to change its trajectory away from the secondary object.]

---

## sec2 -- NASA CA Best Practices Handbook

[sec2_p1] Debris-producing space events have the potential to make LEO unusable. Experienced Conjunction Assessment (CA) practitioners have established approaches to minimize this risk. Many space actors do not use these established approaches: there is no one international standard set of CA guidelines or best practices, many Owner/Operators (O/Os) are unaware of best practices, and some O/Os presume CA will be burdensome. NASA collected its CA best practices and published them to assist other operators in maturing their practices and keeping space safe and accessible.

[sec2_p2] The NASA Spacecraft Conjunction Assessment and Collision Avoidance Best Practices Handbook helps space system operators understand existing capabilities and processes, including related US Space Command (USSPACECOM) and the US Space Force 18th Space Defense Squadron (SDS) best practices. The handbook provides technical background on NASA CA processes, including why requirements were levied and how to implement them, and offers best practices for use by any spacecraft Owner/Operator to help protect the space environment. A companion software repository contains many of the tools used by NASA, available at https://github.com/nasa/CARA_Analysis_Tools.

---

## sec3 -- Key Best Practices

### sec3.1 -- Spacecraft Design Considerations

[sec3.1_p1] It is important and efficient to make plans for conjunction assessment during spacecraft planning and design. CA process needs can be accommodated more easily prior to spacecraft fabrication. All processes and tools should be developed and validated well in advance of launch. Key items to consider during design include orbit selection, trackability, deployment plan, and ephemeris generation process and tools.

[sec3.1_p2] Lesson learned example: A NASA spacecraft assumed that two-line elements (TLEs) would be available for use in providing acquisition data to tracking radars. After launch, it was discovered that the orbit was too low an inclination for DOD CA sensors to reliably track and maintain it, so TLEs were not available. This situation could have been prevented through pre-launch analysis.

### sec3.2 -- Orbit Selection

[sec3.2_p1] Orbit altitude affects event rate: small changes in orbit altitude may make large differences in the number of close approaches. Co-location is also a consideration: determining in advance that there are other neighbors in the intended location of the spacecraft allows planning of communication and space sharing operations concepts.

[Figure 2: Number of cataloged objects versus orbital altitude from 440 to 600 km, showing sharp spikes in object density at specific altitudes (notably near 500 km and 550 km), demonstrating that small changes in altitude can dramatically change the conjunction event rate. Source: NASA CARA Program (2019) unpublished internal data.]

[sec3.2_p2] Transiting to final orbital position can create CA complexities. Transiting spacecraft should yield way to on-station spacecraft. Frequent, sometimes constant, maneuvering must be modeled in ephemerides provided to 18 SDS to communicate position to neighboring spacecraft. Transiting through constellations or large groups of active payloads requires frequent contact with other O/Os to adjudicate close approaches.

### sec3.3 -- Trackability

[sec3.3_p1] Technology advances make possible spacecraft that are too small to be tracked by the Space Surveillance Network (SSN). The SSN is the DOD USSF resource assigned to track all on-orbit objects. Objects must be greater than 10 cm to be tracked reliably in LEO, and greater than 50 cm to be tracked reliably in GEO. Passive tracking is not currently available beyond GEO (e.g., cis-lunar). CA can be performed only against well tracked objects in the catalog.

[sec3.3_p2] Un-trackable objects on orbit pose a threat to flight safety. Objects in low inclination orbits have fewer SSN sensors with geometric visibility. Objects in eccentric orbits present challenges because perigee can be away from radars and the satellite can be too dim at apogee for optical sensors.

[sec3.3_p3] Potential workarounds for trackability challenges include: providing O/O ephemerides (though this does not work after end of operations), on-board tracking radio beacons to provide position and ID, corner cubes with an arrangement with a laser tracking facility, coded light signals from a light source on the exterior of the spacecraft, radio frequency interrogation of an exterior Van Atta array, and passive increase of albedo.

[sec3.3_p4] The best practice is to ensure objects are large enough to be tracked passively on-orbit, enabling tracking even after the spacecraft is no longer operational, until demise. At injection, objects should be placed far enough away from other deployed satellites and on-orbit objects to allow unique, unambiguous tracking.

### sec3.4 -- Deployment Plan

[sec3.4_p1] Complex deployments create cataloguing difficulties. Rapid child deployments proliferate deployed satellites, when parents may already be difficult to distinguish, track, and catalog depending on the number of objects deployed. Tethered deployments follow non-Keplerian trajectories, making them difficult to maintain in the orbit catalog.

[sec3.4_p2] The recommended approach is to attempt to simplify and prepare for the situation: delay child deployments until 18 SDS is able to catalogue the parent, and for tethered deployments, work out a tracking and maintenance strategy with 18 SDS in advance of launch. Rideshare missions must rely on the launch provider to protect their spacecraft by using safe deployment practices.

### sec3.5 -- Ephemeris Generation Process and Tools

[sec3.5_p1] Since close approaches are computed using predictions of future spacecraft position, those predictions must be accurate enough to enable maneuver planning. If a spacecraft is not passively trackable or if it is maneuverable, predicted trajectory information must be provided to 18 SDS to enable close approach computation. This must be done at least once per day, predicted at least 7 days into the future, using quality modelling (especially atmospheric drag) to reduce errors, and including realistic covariances.

[sec3.5_p2] Two Line Elements (TLEs, e.g. obtained from SpaceTrack.org) are not sufficient for CA. TLEs have 1-2 km theory error, which is too large for maneuver planning, and no covariance is available to compute probability of collision and make risk decisions. Operators should maintain Space-Track.org information, including contact information (24x7, since other O/Os may be in a different time zone) and active and maneuverable status flags.

---

## sec4 -- Challenges and Future Work

### sec4.1 -- Satellite Autonomous Maneuvering

[sec4.1_p1] It is becoming more common for satellites to employ autonomous maneuvering, especially large constellations. A current example is SpaceX's Starlink, with approximately 2000 active satellites operated this way. Maneuvers are automatically commanded and executed, and often ground systems do not even know of maneuvers until after execution.

[sec4.1_p2] CA can also be executed autonomously. Conjunction Data Messages (CDMs) for upcoming conjunctions are uploaded to the spacecraft. On-board CA software can determine risk based on the spacecraft's latest position information, plan maneuvers to avoid close approaches, and execute them. If CDMs are generated with a sufficiently large screening volume, then autonomous CA is likely to be effective against debris.

### sec4.2 -- Active-vs-Active CA Issue

[sec4.2_p1] Autonomous systems program maneuvers and perform CA based on CDMs uploaded as frequently as contacts allow. Co-located autonomously-controlled constellations need other solutions: two satellites in conjunction from different constellations may be planning mitigation actions, but neither knows what the other is planning to do. Satellites could therefore maneuver into each other.

[sec4.2_p2] For autonomous CA with other active satellites, latencies in information exchange cause CA problems. Non-autonomous active satellites need to refrain from maneuvers 12-24 hours before close approaches with autonomous satellites. This allows sufficient time for submitted ephemeris that includes their maneuver to be screened for CA and these screening results uploaded to the autonomous system.

### sec4.3 -- Active-vs-Active CA Issue: Resolution Efforts

[sec4.3_p1] NASA is part of an industry consortium to develop a pathfinder solution. NASA's experimental autonomous constellation (Starling) will be collocated with the Starlink constellation, forcing the issue. The consortium among NASA Ames, NASA CARA, SpaceX, Emergent Technologies, and UT Austin is developing and demonstrating a prototype autonomous CA approach using a "Mother May I" solution. Infrastructure is being built out and ground testing is underway.

[sec4.3_p2] The Department of Commerce (DOC) participates in observer status, having been designated to assume space traffic management responsibility. A successful demonstration of the approach is expected to be embraced by DOC. A day-long session on this issue and investigated approaches was planned for presentation at a conference venue in winter 2022.

### sec4.4 -- Cis-lunar CA

[sec4.4_p1] The catalog of non-cooperatively or passively tracked objects used in CA is only available near Earth. Activity at the Moon, Mars, and Libration points is increasing the risk of collision without screening. NASA MADCAP provides ephemeris-on-ephemeris screening for missions and relies on sharing of data, being open to non-NASA entities.

[sec4.4_p2] The DOD is developing cis-lunar catalog and screening capability, though requirements are not yet defined and implementation is still in the early stages of development. NASA continues to work with DoD on beyond-GEO SSA capabilities.

---

## sec5 -- Summary

[sec5_p1] Increasing congestion of space accentuates the need to follow CA best practices, particularly in LEO. Best practices are incorporated most cheaply and efficiently when designed in from the beginning. NASA CARA is committed to developing and refining appropriate best practices: integrating feedback from space operators, expanding coverage to address emerging areas of interest, and continuing to focus on a safe space environment for all operators.

---

## sec6 -- Backup: Active-vs-Active CA Potential Solutions

### sec6.1 -- "Mother May I" Approach

[sec6.1_p1] A ground hub is established to receive ephemerides from autonomously-controlled constellations. If a satellite wishes to maneuver, it assembles a proposed maneuver ephemeris and submits it to the ground node. If the ephemeris does not produce any CA issues, the ephemeris is "cleared" for use, and a message is sent to the constellation indicating this.

[sec6.1_p2] The submitting satellite now has a "right" to this ephemeris, and other satellites are prevented from voluntarily impinging on it. The submitting satellite also has an obligation to follow this ephemeris unless they subsequently submit an alternative, which is itself cleared. The system can also allow the submission of multiple, ranked maneuver ephemerides at the same time; the highest-ranked ephemeris that does not produce CA issues is cleared for use.

[sec6.1_p3] This approach requires contact times frequent enough to enable communication of the plan between spacecraft and ground at appropriate times.

### sec6.2 -- Rule-Based Approach

[sec6.2_p1] A set of rules could be developed that would make clear, in every conjunction, which satellite should perform which actions. Iridium proposed a set of such rules in a recent paper. If this approach is possible, it could eliminate the need for the "Mother May I" communication approach.

[sec6.2_p2] However, some scenarios may not be sufficiently addressed. For example, suppose two autonomous spacecraft each need to perform a maneuver. Each schedules one, unaware the other has done so, creating a conjunction. Unless the maneuvers are planned well in advance (more than 24 hours, to allow the present system to screen submitted ephemerides and send back CA results), there is no way for both satellites to know they are creating a risky conjunction, and no easy way to resolve who is permitted to maneuver.
