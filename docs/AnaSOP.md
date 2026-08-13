# AnaSOP
Analysis Standard Operating Procedure

## 1. Research Objective

### Central Research Question

- Research question: Following the 28 July 2026 earthquake, how much of an official-total-scaled shelter stress load can Kumamoto Prefecture's designated general-shelter system explain under walking, motorized, and mixed-mode accessibility bounds, and whether accessibility, deployable capacity, or facility availability is the binding planning constraint?
- Why it matters: The official aggregate of 10,467 shelter users establishes that evacuation occurred but does not identify residential origins, travel modes, or assigned facilities. A model that reaches fewer than 10,467 people under a 15-minute walking rule therefore identifies the limit of that planning rule, not the number of people actually refused shelter.
- Data support currently visible: Prefecture-wide evidence includes 62,945 populated 125 m meshes, 36,657 disclosure-group demand units, 1,315 geolocated designated shelters across 45 municipalities, four official aggregate event-use snapshots, and a road network with road-class baseline travel times. All 1,156 general shelters and virtually all residential population are attached to the network. Official numeric capacities for 118 general shelters calibrate 25-, 50-, 100-, and 200-person scenarios. Under the high-loss-weighted stress geography, 15-minute walking reaches 60.1 percent of the load, whereas the central low-speed motorized benchmark reaches 99.7 percent.
- Key readable variables or data scope: Reported Evacuees; three observed-total-scaled stress geographies; Standardized Capacity per General Shelter; Network Walking Time; Network Motorized Time; Vehicle-Enabled Demand Share; Mixed-Mode Accessibility Coverage; Capacity-Constrained Served Demand; Model Explanation Gap; Municipality; facility availability.
- What would verify it: Accessibility coverage and capacity-constrained assignment change materially across mode-availability assumptions but only modestly across plausible capacity thresholds, with explicit municipality and facility-loss evidence locating the remaining planning gaps.
- What would falsify or weaken it: An accessibility-binding interpretation would weaken if higher standardized capacity closes most of the walking-based gap, if motorized or mixed-mode access changes little, or if findings depend on one unsupported demand spatialization or one facility-loss realization.
- Required next feasibility check: Complete the motorized and mixed-mode capacity screen, regenerate the accessibility and robustness outputs, and retain the 50-person walking allocation as a conservative stress case rather than the central adequacy estimate.

### Supporting Research Questions

The plan contains one central question and four supporting questions.

#### Supporting Point 1

- Role relative to central point: demand estimation
- Research question: How does the geographic distribution of an official-total-scaled stress load change under population-, central-housing-loss-, and high-housing-loss-weighted spatializations, and which distribution places the greatest pressure on designated-shelter access?
- Why it matters: The official reports identify 10,467 shelter users but not their residential origins. The aggregate is therefore a scaling reference for counterfactual demand surfaces, not a second estimate of actual event demand.
- Data support currently visible: The highest available first-72-hour snapshot provides the 10,467-person aggregate benchmark. Complete 125 m population meshes, central and high housing-loss demand weights, municipality boundaries, and epicentral distance support three internally consistent spatializations with the same prefecture-wide total.
- Key readable variables or data scope: Reported Evacuees; Observed-Use Stress Demand Population Weighted; Observed-Use Stress Demand Central-Loss Weighted; Observed-Use Stress Demand High-Loss Weighted; Residential Population; Municipality; Epicentral Distance.
- What would verify it: Each spatialization preserves the 10,467-person total, is never relabeled as observed local demand, and produces interpretable differences in accessibility and capacity-constrained service.
- What would falsify or weaken it: The demand-side comparison would be weak if any spatialization changes the aggregate benchmark, uses incomplete geographic weights, or is interpreted as the actual residential origin of evacuees.
- Required feasibility check: Completed. The three spatializations preserve the aggregate total and have full-prefecture municipality and network coverage; their local patterns remain modeled alternatives rather than observed origins.

#### Supporting Point 2

- Role relative to central point: reverse capacity and opening requirements
- Research question: Does standardized capacity materially constrain explainable service once accessibility and the opening budget are imposed, and how many municipality-contained openings are required under central and stress capacity cases?
- Why it matters: Complete facility area and numeric capacity cannot be recovered reliably for all 1,315 records. A reverse requirement is more defensible than presenting unsupported facility-level capacity estimates as facts.
- Data support currently visible: The official inventory identifies 1,156 general and 159 welfare-specific shelters. The largest available observed-use snapshot reports 10,467 users and an undifferentiated total of 415 open shelters. Among 118 deduplicated general shelters with Official Numeric Capacity in Uki, Uto, and Yatsushiro, the median is 241 persons; 88.1 percent support at least 50 persons and 80.5 percent support at least 100 persons.
- Key readable variables or data scope: Standardized Capacity per General Shelter; Minimum Open Shelters Required; Required Capacity if All General Shelters Open; Critical Reverse Capacity; Official Capacity Threshold Calibration; Municipality; Shelter Service Class.
- What would verify it: The 100-person central scenario is plausible relative to documented capacities, the 50-person case provides a conservative stress test, and raising capacity from 50 to 100 or 200 persons changes walking-based assigned service much less than changing the access mode or time bound.
- What would falsify or weaken it: The threshold approach would be weak if the inadequacy conclusion disappeared under the optimistic opening budget and plausible higher capacities, or if the selected threshold were unsupported by the documented calibration sample.
- Required feasibility check: Compare the completed 50-person result with 25-, 100-, and 200-person thresholds while retaining welfare-specific supply separately and reporting calibration selection limits explicitly.

#### Supporting Point 3

- Role relative to central point: spatial accessibility and municipal heterogeneity
- Research question: How do walking, motorized, and mixed-mode access assumptions change the share and geography of stress demand that can reach at least one general shelter?
- Why it matters: Capacity in Kumamoto City or another municipality may be too distant or operationally irrelevant to residents near the hypocenter, on islands, or in sparsely connected rural areas.
- Data support currently visible: Population meshes, all general shelter locations, road-class baseline travel times, direct network attachments, and administrative areas support connector-inclusive walking and motorized shortest paths. At 15 minutes, walking reaches 60.1 percent of high-loss-weighted stress demand; the central motorized benchmark reaches 99.7 percent. Mixed-mode accessibility increases monotonically from 60.1 to 99.7 percent as the vehicle-enabled demand share rises from zero to one.
- Key readable variables or data scope: Network Walking Time; Network Motorized Time; Motorized Speed Factor; Vehicle-Enabled Demand Share; Mixed-Mode Accessibility Coverage; Municipality; Shelter Location.
- What would verify it: Mode assumptions change accessibility materially, results remain monotonic under speed and vehicle-share sensitivity, and remaining gaps can be located without relabeling scenario assignments as observed travel.
- What would falsify or weaken it: Results would be weak if shelters or demand nodes cannot be attached reliably, cross-municipality walking is modeled unrealistically, or island and disconnected-network limitations are ignored.
- Required feasibility check: Diagnose municipalities where the walking and motorized accessibility bounds differ most and test whether capacity-constrained mixed-mode allocation leaves residual explanation gaps.

#### Supporting Point 4

- Role relative to central point: robustness and conditional gap response
- Research question: Which shelters and municipalities remain operationally important after separating accessibility bounds from capacity and facility-unavailability effects?
- Why it matters: A nominally sufficient system can be fragile when one large facility or a concentrated group of high-pressure facilities becomes unavailable.
- Data support currently visible: Standardized capacity thresholds, pedestrian-screened network structure, and a complete general-shelter inventory support facility-unavailability and critical-shelter sensitivity. Thirty reproducible random draws at each of 10, 20, and 30 percent unavailability and pressure-targeted removal scenarios have been completed. The road-evidence audit identifies motor-vehicle restrictions but no pedestrian-passability variable, so road-edge failure is not a main estimand. Emergency evacuation sites, public facilities, schools, and parks remain conditional supplementary-site inputs only.
- Key readable variables or data scope: facility availability; single-shelter failure service loss; Capacity-Constrained Served Demand; Model Explanation Gap; Municipality.
- What would verify it: The same shelters and municipalities appear as priorities across plausible demand, capacity, walking, and facility-loss scenarios, and supplementary sites measurably reduce persistent deficits. Current pressure-targeted and single-removal results concentrate critical facilities in Uki, Uto, and Yatsushiro.
- What would falsify or weaken it: Supplementary-site analysis should be deferred if baseline prefecture-wide capacity cannot be established or no stable local deficit is found.
- Required feasibility check: If needed, expand single-removal screening beyond the 30 highest-pressure shelters; then evaluate candidate-site geometry and usable-area evidence only in deficits that remain persistent.

### Scope of Analysis

- Topics: Accessibility bounds and operational robustness of the existing designated shelter system after the recent earthquake, measured through official-total-scaled demand geography, walking and motorized networks, standardized capacity, municipality heterogeneity, and facility loss.
- Study area: The full administrative area of Kumamoto Prefecture. Municipality and ward boundaries are reporting strata; distance from the official hypocenter is an additional exposure stratification rather than a study-area exclusion.
- Units of analysis: 125 m residential population meshes and disclosure groups as demand units; 1,315 designated shelters as capacity units; municipalities, Kumamoto City wards, epicentral-distance bands, and the prefecture as reporting units.
- Period: The first 0-72 hours after the 28 July 2026 earthquake, represented by scenarios rather than a continuous time series.
- Exclusions: Temporary housing and recovery-period accommodation; prefectures outside Kumamoto; causal impact estimation; continuous temporal reconstruction; independent re-estimation of upstream housing damage; general multi-function open-space optimization unless shelter gaps require a conditional extension.

### Study Design Declaration

- Research type: applied
- Study design: Applied empirical prefecture-wide shelter assessment combining partial-identification accessibility bounds, scenario-based capacity accounting, constrained allocation, and failure sensitivity.
- Interpretation limit: Results quantify what specified designated-shelter and network rules can explain. They do not estimate actual travel-mode shares, reconstruct individual evacuation, measure people refused shelter, prove causal effects, or establish event-specific road speeds and facility operability.

## 2. Theoretical Background  /  Conceptual Framework  /  Problem Formulation

Research type: applied
Section focus: Empirical context, practical problem, and cautious interpretation limits.

### Research Gap

- Existing shelter inventories and aggregate use reports do not show which accessibility assumptions are required to reconcile observed system use with designated-shelter geography. The applied gap is a prefecture-wide assessment that separates walking and motorized access bounds from capacity and facility-availability constraints without treating unobserved origins or travel modes as facts.

### Conceptual Framework

- The earthquake creates spatially uneven shelter pressure through housing loss, precautionary evacuation, and local shaking impacts. The highest available official shelter-use total scales three transparent counterfactual residential geographies. The analysis then asks how much of each surface is explainable under walking-only, motorized, and mixed-mode accessibility, before adding capacity, opening, and facility-loss constraints.
- Analytical chain: official aggregate use -> alternative stress geographies -> walking and motorized accessibility bounds -> mixed-mode sensitivity -> reverse capacity and opening requirements -> capacity-constrained stress allocation -> facility failure sensitivity -> residual planning gaps.
- Aggregate, municipal, and local adequacy are distinct. A positive prefecture-wide balance does not establish sufficiency when capacity is concentrated in Kumamoto City, separated by water or network components, or too distant from source-proximate demand.
- Scope boundary: The core analysis covers 1,156 general shelters during the first 0-72 hours; 159 welfare-specific shelters remain separate. Official facility capacity evidence calibrates thresholds but is not extrapolated as observed capacity for unsupported shelters. Open spaces enter only if persistent local gaps remain after the existing system is evaluated.

### Problem Formulation

- Let \(i\in I\) index prefecture-wide demand meshes, \(j\in J\) designated shelters, \(g\in G\) municipalities, and \(s\in S\) stress geographies. Mode-specific reachability is \(a_{ijk}\), where \(k\) denotes walking or motorized access, and effective capacity is \(C_{js}^{eff}\).
- Prefecture-wide aggregate adequacy is

\[
R_s^{pref}=\frac{\sum_j C_{js}^{eff}}{\sum_i D_{is}}.
\]

- Let \(y_{ijs}\) be demand assigned from mesh \(i\) to shelter \(j\). Feasible assignment requires

\[
\sum_j y_{ijs}\leq D_{is},\qquad \sum_i y_{ijs}\leq C_{js}^{eff},
\]

  and \(y_{ijs}=0\) when the shelter is unreachable under the selected access scenario.
- The model explanation gap is

\[
Q_s=\sum_i\left(D_{is}-\sum_j y_{ijs}\right).
\]

- Here, \(Q_s\) is demand not assigned within the modeled designated-shelter rules. It does not count observed unmet evacuees; it may reflect travel beyond the selected threshold, motorized movement, non-designated destinations, or other mechanisms outside the model.
- Municipality summaries diagnose where scenario residuals remain concentrated. Cross-municipality assignment is permitted only through an eligible path within the selected time threshold.
- Interpretation limit: The four official snapshots are observed aggregate shelter use, with the highest available value of 10,467 people at 07:30 on 30 July 2026. They contain no municipality origins, facility destinations, or travel modes. The reported 415 open shelters are also undifferentiated by service class. Capacity for shelters lacking numeric or area evidence remains provisional.

## 3. Data Overview

### Data Scope

- Data sources reviewed: 40
- Variables summarized: 705
- Distribution plots generated: 80
- Files skipped during briefing: 0
- Unit of observation and time coverage: Core analytical units are 62,945 populated 125 m meshes, 36,657 disclosure-group demand units, 1,315 designated shelters, 45 municipalities, and four prefecture-wide official observations within the first 0-72 hours after the 28 July 2026 earthquake. Census and network inputs are static reference layers rather than repeated event observations.

| Data source | Rows | Columns |
| --- | ---: | ---: |
| Data source 1 | 4 | 14 |
| Data source 2 | 5 | 5 |
| Data source 3 | 62945 | 31 |
| Data source 4 | 62945 | 40 |
| Data source 5 | 62945 | 50 |
| Data source 6 | 190 | 18 |
| Data source 7 | 62945 | 8 |
| Data source 8 | 36657 | 16 |
| Data source 9 | 1315 | 20 |
| Data source 10 | 1315 | 22 |
| Data source 11 | 182 | 23 |
| Data source 12 | 11146 | 25 |
| Data source 13 | 11146 | 24 |
| Data source 14 | 8714 | 17 |
| Data source 15 | 182 | 27 |
| Data source 16 | 8 | 5 |
| Data source 17 | 5 | 11 |
| Data source 18 | 1315 | 11 |
| Data source 19 | 36657 | 43 |
| Data source 20 | 5 | 17 |
| Data source 21 | 62945 | 10 |
| Data source 22 | 49 | 8 |
| Data source 23 | 264 | 13 |
| Data source 24 | 62945 | 16 |
| Data source 25 | 1315 | 5 |
| Data source 26 | 1713 | 6 |
| Data source 27 | 62945 | 35 |
| Data source 28 | 709 | 6 |
| Data source 29 | 1660 | 4 |
| Data source 30 | 917 | 6 |
| Data source 31 | 6105 | 17 |
| Data source 32 | 36 | 16 |
| Data source 33 | 390234 | 21 |
| Data source 34 | 314391 | 5 |
| Data source 35 | 6105 | 14 |
| Data source 36 | 566505 | 18 |
| Data source 37 | 56424 | 12 |
| Data source 38 | 98884 | 12 |
| Data source 39 | 680 | 34 |
| Data source 40 | 343844 | 20 |

### Time-Series Candidates

Potential time-series structure was detected in 11 data source(s).
Specific source files and original column names remain in the data-briefing artifacts, not in AnaSOP.

### Data Limitations

- No skipped files were recorded by the briefing script.
- Treat this section as exploratory; final variable decisions belong to Section 4.
- AnaSOP intentionally avoids raw dataset names, source file paths, and original column names.

### Temporal Evidence Handling

- Potential time structure is present in 11 data sources, but the project does not estimate temporal trends because event snapshots are sparse, irregular, and incomplete.
- Four official prefecture-wide shelter-use observations fall within the first 0-72 hours. They are used as time-stamped benchmarks and not as a reconstructed evacuation trajectory.
- The largest available observation is 10,467 shelter users with 415 open shelters. It is the highest among available snapshots, not a proven event peak.

### Shelter, Capacity, and Network Evidence Limits

- The prefecture-wide inventory contains 1,315 geolocated records: 1,156 general shelters and 159 welfare-specific shelters. Welfare-specific supply is not counted as unrestricted general-population capacity.
- Official numeric capacity is available for 118 deduplicated general shelters in three source-proximate cities. It calibrates standardized thresholds but is not representative proof of capacity for every prefecture-wide shelter.
- Additional area evidence is basis-specific. Gymnasium or indoor-arena area can support a conservative lower-bound calculation, while whole-facility gross area cannot be treated as accommodation area without a usable-area factor.
- Aggregate shelter-use reports contain no municipality-level origin table. Population-, central-loss-, and high-loss-weighted spatializations of the 10,467-person total are transparent stress scenarios rather than observed local evacuation counts.
- All general shelters have accepted pedestrian-network attachments, and population-mesh attachments cover 99.989 percent of residents. The baseline nevertheless remains a road-centreline proxy without sidewalks, private footpaths, or event-specific pedestrian-passability observations.
- The road-evidence audit reviewed 680 administrative traffic-restriction observations across 15 snapshots. The latest snapshot within 72 hours contains 32 named Kumamoto Prefecture records, of which 31 indicate active full traffic closure, but no field identifies pedestrian prohibition or pedestrian impassability.
- Restriction-to-edge links are many-to-many spatial candidates. At the latest 72-hour snapshot, alternative rules identify between 30 and 1,307 walking edges, or 0.024-0.417 percent of baseline walking-network length. This sensitivity prevents the candidate links from being treated as confirmed failed walking edges.
## 4. Variable Construction  /  Key Variables

The table uses readable, article-facing variable names. Each row states the variable role, formal definition or coding rule, and construction basis used in the analysis.

| variable_name | full_name | role | formal_definition | construction_or_coding | is_final_variable |
|---|---|---|---|---|---|
| Residential Demand Unit ID | Residential Demand Unit Identifier | spatial identifier | One unique identifier per disclosure group. | Preserved from the upstream grouped 125 m population mesh product. | yes |
| Constituent 125 m Mesh Count | Number of Constituent 125 m Population Meshes | spatial-unit descriptor | Number of original 125 m meshes represented by one residential demand unit. | Preserved to prevent disclosure groups from being misinterpreted as single meshes. | yes |
| Municipality Code | Canonical Municipality Code | reporting identifier | One canonical code for each of the 45 municipalities. | Kumamoto City wards are collapsed to municipality code 43100 for municipal summaries while their polygon codes are retained separately. | yes |
| Administrative Polygon Code | Municipality or Ward Polygon Code | spatial join identifier | Code of the administrative polygon intersecting the demand unit representative point. | Retains Kumamoto City ward codes and municipality codes elsewhere. | yes |
| Municipality | Municipality Name | reporting stratum | One of the 45 municipalities in Kumamoto Prefecture. | Assigned by representative-point intersection with official administrative polygons. | yes |
| Ward | Kumamoto City Ward | secondary reporting stratum | One of five wards for observations inside Kumamoto City; missing elsewhere. | Retained for within-city reporting without narrowing the prefecture-wide study area. | yes |
| Residential Population | Residential Population | denominator | Population residing in a residential demand unit. | Preserved from the 2020 population-mesh preprocessing. | yes |
| Population Age 65+ | Residential Population Age 65 or Older | vulnerable-population denominator | Residents age 65 or older in demand unit \(i\). | Preserved from the population-mesh preprocessing. | yes |
| Epicentral Distance | Distance from the Official Hypocenter | exposure descriptor | Great-circle or projected distance in kilometers from demand unit \(i\) to the official hypocenter. | Preserved from the upstream earthquake-demand product. | yes |
| Housing-Loss Shelter Demand Low | Lower Housing-Loss Shelter-Demand Estimate | demand | \(D_i^{low}\) | Lower-bound upstream affected-population estimate for every prefecture-wide demand unit. | yes |
| Housing-Loss Shelter Demand Central | Central Housing-Loss Shelter-Demand Estimate | demand | \(D_i^{central}\) | Central upstream affected-population estimate for every prefecture-wide demand unit. | yes |
| Housing-Loss Shelter Demand High | Upper Housing-Loss Shelter-Demand Estimate | demand | \(D_i^{high}\) | Upper-bound upstream affected-population estimate for every prefecture-wide demand unit. | yes |
| Housing-Loss Shelter Demand Age 65+ Central | Central Older-Resident Shelter-Demand Estimate | vulnerable demand | \(D_{i,65+}^{central}\) | Upstream central affected-population estimate for residents age 65 or older. | yes |
| Observation Timestamp | Event Shelter-Use Observation Timestamp | validation timestamp | Official as-of time in Japan Standard Time. | Distinguished from the later disaster-headquarters meeting time where the report states an earlier data cutoff. | yes |
| Hours Since Earthquake | Elapsed Hours at Shelter-Use Observation | validation timing | Hours from 16:27 JST on 28 July 2026 to the official as-of time. | Used only to locate discrete observations within the 0-72-hour window. | yes |
| Open Shelters | Official Prefecture-Wide Open Shelter Count | observed system use | Number of open shelters at the observation timestamp. | Extracted and visually verified from four prefectural disaster-headquarters reports. | yes |
| Reported Evacuees | Official Prefecture-Wide Shelter Users | observed-use benchmark | Aggregate evacuees reported across Kumamoto Prefecture. | Values are 4,744, 9,872, 8,886, and 10,467; no municipal allocation is inferred. | yes |
| Highest Observed within Available 0-72h Snapshots | Available-Snapshot Maximum Flag | benchmark flag | Equals 1 for the largest reported evacuee count among the four available snapshots. | Identifies 10,467 at 07:30 on 30 July without claiming it is the true event peak. | yes |
| Observed-Use Stress Demand Population Weighted | Population-Weighted Spatialization of Highest Available Observed Use | stress demand | \(D_i^{pop}=10467P_i/\sum_rP_r\). | Preserves prefecture total 10,467 and follows Residential Population; it is modeled local demand, not observed origins. | yes |
| Observed-Use Stress Demand Central Housing-Loss Weighted | Central-Loss-Weighted Spatialization of Highest Available Observed Use | stress demand | \(D_i^{central-anchor}=10467H_i^{central}/\sum_rH_r^{central}\). | Preserves prefecture total 10,467 and follows central housing-loss geography; it is modeled local demand. | yes |
| Observed-Use Stress Demand High Housing-Loss Weighted | High-Loss-Weighted Spatialization of Highest Available Observed Use | stress demand | \(D_i^{high-anchor}=10467H_i^{high}/\sum_rH_r^{high}\). | Preserves prefecture total 10,467 and follows high housing-loss geography; it is modeled local demand. | yes |
| Shelter ID | Designated Shelter Identifier | capacity-unit identifier | One master identifier for shelter record \(j\). | Preserved across all 1,315 geolocated records. | yes |
| Shelter Location | Designated Shelter Geographic Location | spatial service point | Official latitude and longitude for shelter \(j\). | Preserved from the prefecture-wide shelter inventory. | yes |
| Shelter Municipality | Shelter Municipality | reporting stratum | Municipality containing shelter \(j\). | Assigned from the master municipality code and checked spatially. | yes |
| Facility Type | Shelter Facility Type | capacity classifier | School, public hall, welfare facility, sports facility, or another audited class. | Derived from official identity and facility-name evidence. | yes |
| Shelter Service Class | General or Welfare-Specific Shelter | supply eligibility | `general` or `welfare_specific`. | Derived from the accepted-persons description; welfare-specific capacity is excluded from unrestricted general supply. | yes |
| Official Numeric Capacity | Primary Official Shelter Capacity | documented capacity | Published person capacity for source facility \(j\). | Matched to master records with the source definition preserved; duplicate matches must not be summed twice. | yes |
| Official Capacity Definition | Meaning of Primary Official Capacity | metadata | Source-specific definition such as 3 square meters per person, maximum capacity, or another published basis. | Stored verbatim or as a faithful English description. | yes |
| Secondary Official Capacity | Alternative Published Shelter Capacity | sensitivity input | A second official capacity where the source publishes more than one standard. | Examples include infection-control capacity or a 2-square-meter emergency-place capacity. | yes |
| Documented Area | Official Documented Facility Area | capacity input | Published area in square meters associated with shelter \(j\). | Kept only with its area basis; numeric capacity takes priority when both exist. | yes |
| Area Basis | Meaning of Documented Area | metadata | Gymnasium, indoor arena, gross facility, effective area, or another stated basis. | Prevents gross floor area from being treated automatically as usable accommodation area. | yes |
| Earthquake Opening or Suitability Flag | Source-Specific Earthquake Operability Indicator | operability input | Boolean or missing source flag. | Retains Uki suitability and Yatsushiro opening designations separately from baseline capacity. | yes |
| Earthquake Flag Definition | Meaning of Earthquake Operability Indicator | metadata | Source-specific threshold or suitability meaning. | Must accompany the flag in every use. | yes |
| Capacity Evidence Tier | Shelter Capacity Evidence Grade | uncertainty classifier | A numeric capacity; B gymnasium area; C gross area; D school identity only; E public-facility identity only; F no source link. | Assigned hierarchically so each master shelter has exactly one primary tier. | yes |
| Source Record ID | Official Capacity-Source Record Identifier | provenance identifier | Unique identifier for an extracted official source row. | Links each match back to its municipality table and source URL. | yes |
| Source Match Multiplicity | Number of Master Records Matched to One Source Row | deduplication diagnostic | Count of master shelter records sharing one source record. | Values above one require review before capacity aggregation. | yes |
| Must Deduplicate Capacity before Summation | Duplicate Capacity Match Flag | aggregation safeguard | Equals 1 when source match multiplicity exceeds one. | Prevents one official facility capacity from being counted multiple times. | yes |
| Documented-Only General Capacity | General-Shelter Capacity without Imputation | lower-bound capacity | Sum of deduplicated official numeric capacity and separately identified confirmed area-derived capacity for general shelters only. | Unsupported shelters receive zero; used as a documented lower bound rather than a complete prefecture estimate. | yes |
| Standardized Capacity per General Shelter | Capacity-Threshold Scenario | capacity parameter | \(c \in \{25,50,100,200\}\) persons per open general shelter. | A stress-test parameter, not an assertion of observed facility capacity. Official numeric capacities from 118 general shelters calibrate plausibility. | yes |
| Minimum Open Shelters Required | Reverse Shelter-Opening Requirement | operational requirement | \(N_{gs}(c)=\lceil D_{gs}/c \rceil\) for municipality \(g\), scenario \(s\), and threshold \(c\). | Calculated under municipality containment for the first screen; later network assignment may permit reachable cross-boundary service. | yes |
| Required Capacity if All General Shelters Open | Municipality Capacity Pressure | capacity requirement | \(c_{gs}^{all}=D_{gs}/J_g\), where \(J_g\) is the number of general shelters in municipality \(g\). | Measures the average capacity each local shelter would need if all were open. | yes |
| Critical Reverse Capacity | Minimum Capacity at the Observed-Total-Anchored Opening Budget | primary threshold outcome | \(c_s^*=\min\{c:\sum_g\lceil D_{gs}/c\rceil\leq415,\ \lceil D_{gs}/c\rceil\leq J_g\ \forall g\}\). | Uses 415 as an optimistic general-shelter opening budget anchored to the undifferentiated number open at the largest available observed-use snapshot and retains municipality containment; it is modeled, not observed general-shelter availability or capacity. | yes |
| Official Capacity Threshold Calibration | Share of Documented Shelters Meeting a Threshold | validity diagnostic | \(P_c=J_{doc}^{-1}\sum_{j\in J_{doc}}1[C_j^{official}\geq c]\). | Reported for 25, 50, 100, and 200 persons using 118 deduplicated general shelters in Uki, Uto, and Yatsushiro; selection limits are explicit. | yes |
| Scenario-Available General Shelter Capacity | Conditional General Shelter Supply | capacity | \(C_{js}^{threshold}=c\times o_{js}\). | Combines a standardized capacity threshold with an explicit opening or operability indicator; welfare-specific shelters remain outside unrestricted supply. | yes |
| Demand Walking-Network Attachment | Population-Mesh Centroid Attachment to Pedestrian-Screened Roads | accessibility input | Nearest eligible walking edge, normalized edge fraction, connector distance, and recomputed walking-network component for demand mesh \(i\). | National expressways and toll edges are excluded; direct snap is accepted within 250 m in EPSG:6670. | yes |
| Shelter Walking-Network Attachment | General-Shelter Attachment to Pedestrian-Screened Roads | accessibility input | Nearest eligible walking edge, normalized edge fraction, connector distance, and recomputed walking-network component for shelter \(j\). | All 1,156 general shelters receive an accepted direct road snap within 250 m. | yes |
| Network Walking Time | Door-to-Door Time to the Nearest General Shelter | accessibility measure | \(t_{iv}=60d_i^{nearest}/(1000v)\), where \(v\in\{3,4\}\) km/h. | Includes demand connector, shortest pedestrian-screened road distance, and shelter connector; calculated to 2 km for the 30-minute maximum screen. | yes |
| Reachable within Time Threshold | Nearest General Shelter Reachability Indicator | accessibility indicator | \(a_{ivh}=1[t_{iv}\leq h]\), where \(h\in\{10,15,30\}\) minutes. | Constructed for 3 and 4 km/h without imposing shelter capacity or the 415-opening limit. | yes |
| Network Accessibility Coverage | Scenario Demand within Reach of a General Shelter | accessibility outcome | \(G_{svh}=\sum_iD_{is}a_{ivh}/\sum_iD_{is}\). | Reported separately for population, housing-loss demand, and three observed-use stress spatializations. | yes |
| Motorized Speed Factor | Fraction of Baseline Road Speed Available after the Earthquake | accessibility parameter | \(q\in\{0.25,0.50,1.00\}\). | Multiplies the existing road-class baseline speed; 0.50 is the central low-speed benchmark, while 0.25 and 1.00 bound more severe disruption and the undisrupted reference. It is a scenario parameter rather than an observed event speed. | yes |
| Network Motorized Time | Connector-Inclusive Time to the Nearest General Shelter by Motor Vehicle | accessibility measure | \(m_{ijq}=\ell_i^{snap}/v_w+\tau_{ij}/q+\ell_j^{snap}/v_w\). | Uses walking speed \(v_w=4\) km/h on off-network connectors and the road-class baseline travel time \(\tau_{ij}\) on all eligible and available road edges. Shelter and demand attachments remain on non-expressway, toll-free access edges to avoid artificial direct entry to controlled roads. | yes |
| Vehicle-Enabled Demand Share | Share of Scenario Demand Able to Use a Motor Vehicle | accessibility parameter | \(p\in\{0,0.25,0.50,0.75,1.00\}\). | Splits each demand unit proportionally into walking-only and vehicle-enabled components. Values are sensitivity bounds and are not estimates of observed evacuation mode choice or vehicle sleeping. | yes |
| Mixed-Mode Accessibility Coverage | Scenario Demand within Reach under a Walking and Motorized Mode Split | accessibility outcome | \(G_{s}^{mix}(p)=(1-p)G_s^{walk}+pG_s^{motor}\). | Reports an accessibility envelope before capacity and opening constraints. It does not reconstruct individual travel behavior or imply that roads were uncongested and undamaged. | yes |
| Capacity-Constrained Served Demand | Stress Demand Assigned to Reachable General Shelter Capacity | service outcome | \(S_{is}=\sum_j y_{ijs}\). | Quantifies the part of a modeled stress surface assignable under an explicit mode, capacity, opening, and availability scenario; it is not observed shelter admission. | yes |
| Model Explanation Gap | Stress Demand Not Assigned within the Modeled Designated-Shelter Rules | diagnostic outcome | \(Q_{is}=D_{is}-\sum_j y_{ijs}\). | Measures the limit of the modeled rule set. It may reflect travel beyond the threshold, motorized movement, non-designated destinations, or other omitted mechanisms and is not an observed count of people refused shelter. | yes |

## 5. Identification Strategy

- Design principle: This is an applied partial-identification and scenario-based accessibility assessment. It does not reconstruct actual evacuation or estimate an unobserved factual capacity for every shelter. The analysis compares what the designated-shelter system can explain under explicit walking, motorized, mixed-mode, capacity, opening, and facility-availability rules.
- Demand identification: The largest available official aggregate observation, 10,467 Reported Evacuees, scales three counterfactual residential stress surfaces using Residential Population, Housing-Loss Shelter Demand Central, and Housing-Loss Shelter Demand High. The official count is an observed aggregate reference, while all mesh and municipality values are modeled alternatives. The unscaled housing-loss estimates remain contextual displacement inputs.
- Capacity identification: Standardized Capacity per General Shelter is 100 persons in the central capacity scenario, 50 persons is a conservative stress case, and 25 and 200 persons bound lower and upper sensitivity. Official Numeric Capacity from 118 deduplicated general shelters supplies plausibility calibration only. Welfare-specific shelters remain outside unrestricted general-population supply.
- Reverse-requirement contrast: Aggregate and municipality-contained calculations identify Minimum Open Shelters Required, Required Capacity if All General Shelters Open, and Critical Reverse Capacity before routing. This distinguishes an implausible capacity requirement from a shortage caused by geographic reachability.
- Access identification: The 15-minute, 4-km/h walking case is the restrictive lower accessibility bound. Motorized road time uses existing road-class baseline travel time multiplied by Motorized Speed Factor, with 0.50 as the central low-speed benchmark and 0.25 and 1.00 as sensitivity. Off-network connectors are traversed at 4 km/h. Vehicle-Enabled Demand Share ranges from zero to one and creates mixed-mode accessibility bounds without estimating actual travel-mode choice.
- Facility-selection and allocation principle: At most 415 general shelters may open in the constrained stress allocation. This optimistic budget is anchored to the official undifferentiated total of open shelters, not an observed list of open general shelters. The lexicographic model maximizes assigned stress demand, minimizes openings, and then minimizes travel impedance. The returned opening set is one modeled solution rather than a reconstruction of actual operations.
- Robustness identification: Capacity thresholds, demand spatialization, walking speed, time threshold, and 0, 10, 20, and 30 percent facility unavailability are varied. Random unavailability is summarized across reproducible draws; targeted loss removes high-pressure facilities first. Cross-municipality assignment is permitted only through an eligible network path within the selected time threshold.
- Road-evidence boundary: Event restriction records do not identify complete motorized or pedestrian edge failure. Motorized results therefore vary speed rather than deleting matched edges, and no motorized scenario is interpreted as observed event travel time. Toll and expressway edges are permitted for motorized paths, while demand and shelter access attachments remain on ordinary roads.
- Output connection: Prefecture Shelter Demand and General Shelter Geography establishes the input geography; the capacity tables establish pre-network requirements; Walking and Motorized Accessibility Bounds identifies the access envelope; the 50-person gap map preserves a conservative stress case; Accessibility, Capacity, and Facility-Unavailability Robustness and Network Accessibility and Robustness distinguish access, capacity, and failure effects.
- Interpretation limit: Capacity-Constrained Served Demand is the share assigned under a modeled rule set. Model Explanation Gap is the residual not explained by that rule set, not observed unaccommodated population. Facilities may have been unsafe, closed, staffed differently, or replaced by non-designated destinations, and actual residents may have used vehicles or traveled beyond the threshold.

## 6. Main Estimation Framework

### Demand Scenarios

Let \(i\) index Residential Demand Unit ID, \(j\) index general Shelter ID, \(g\) index Municipality, and \(s\) index a demand scenario. Housing-loss demand is preserved directly as \(H_i^{low}\), \(H_i^{central}\), and \(H_i^{high}\), corresponding to Housing-Loss Shelter Demand Low, Central, and High.

Symbol definitions and consistency: \(i\), \(j\), \(g\), and \(s\) denote the demand unit, general shelter, municipality, and demand scenario throughout Section 6. Later equations reuse the same symbols consistently, and each new symbol is defined where it is introduced.

Let \(O=10467\) be the highest Reported Evacuees value among the available first-72-hour snapshots and let \(P_i\) be Residential Population. The population-weighted observed-use stress scenario is

\[
D_i^{pop}=O\frac{P_i}{\sum_r P_r}.
\]

Here, \(D_i^{pop}\) is modeled demand in unit \(i\) and \(r\) indexes all prefecture-wide demand units. The two housing-loss-weighted observed-use stress scenarios are

\[
D_i^{central-anchor}=O\frac{H_i^{central}}{\sum_r H_r^{central}},
\]

\[
D_i^{high-anchor}=O\frac{H_i^{high}}{\sum_r H_r^{high}}.
\]

Here, \(D_i^{central-anchor}\) and \(D_i^{high-anchor}\) preserve the central and high housing-loss spatial patterns while matching the aggregate observed-use stress total. Neither variable is interpreted as observed local evacuation.

### Reverse Capacity and Opening Requirements

Let \(D_{gs}=\sum_{i\in g}D_{is}\) be scenario demand in municipality \(g\), let \(J_g\) be its number of general shelters, and let \(c\in\{25,50,100,200\}\) be Standardized Capacity per General Shelter. Minimum Open Shelters Required is

\[
N_{gs}(c)=\left\lceil\frac{D_{gs}}{c}\right\rceil.
\]

Required Capacity if All General Shelters Open is

\[
c_{gs}^{all}=\frac{D_{gs}}{J_g}.
\]

At an optimistic general-shelter opening budget of 415, anchored to the official undifferentiated open-shelter total, Critical Reverse Capacity is

\[
c_s^*=\min\left\{c:\sum_g N_{gs}(c)\leq415,\ N_{gs}(c)\leq J_g\ \text{for all }g\right\}.
\]

Here, \(c_s^*\) is the smallest integer per-shelter capacity that satisfies the optimistic opening-budget limit while retaining residents within their municipality in this conservative pre-network screen. The official reports do not establish that all 415 open facilities were general shelters.

### Walking, Motorized, and Mixed-Mode Accessibility

Let demand unit \(i\) attach to road edge \(e_i\) of length \(L_{e_i}\) at fractional position \(f_i\), and let shelter \(j\) attach to network node \(n_j\). The within-network distance is

\[
\delta_{ij}=\min\left\{f_iL_{e_i}+d(n_{e_i}^{from},n_j),(1-f_i)L_{e_i}+d(n_{e_i}^{to},n_j)\right\}.
\]

Here, \(\delta_{ij}\) is the shortest network distance from demand access point \(i\) to shelter node \(n_j\), \(n_{e_i}^{from}\) and \(n_{e_i}^{to}\) are the access-edge endpoints, and \(d(\cdot,\cdot)\) is shortest-path distance on eligible and available road edges. Door-to-door Network Walking Time is

\[
t_{ijv}=\frac{60\left(\ell_i^{snap}+\delta_{ij}+\ell_j^{snap}\right)}{1000v}.
\]

Here, \(t_{ijv}\) is walking time in minutes at speed \(v\in\{3,4\}\) km/h, \(\ell_i^{snap}\) is demand connector distance, and \(\ell_j^{snap}\) is shelter connector distance. Reachability at \(h\in\{10,15,30\}\) minutes is

\[
a_{ijvh}=1[t_{ijv}\leq h].
\]

Here, \(a_{ijvh}\) equals one when shelter \(j\) is reachable from demand unit \(i\). Network accessibility coverage before capacity constraints is

\[
G_{svh}=\frac{\sum_i D_{is}1[\sum_j a_{ijvh}>0]}{\sum_i D_{is}}.
\]

Here, \(G_{svh}\) is the share of scenario demand within reach of at least one general shelter before capacity and opening limits.

Let \(\tau_{ij}\) be the shortest road-class baseline travel time between the demand and shelter access edges and let \(q\in\{0.25,0.50,1.00\}\) be Motorized Speed Factor. Network Motorized Time is

\[
m_{ijq}=\frac{60\ell_i^{snap}}{1000v_w}+\frac{\tau_{ij}}{q}+\frac{60\ell_j^{snap}}{1000v_w}.
\]

Here, \(m_{ijq}\) is connector-inclusive motorized time, \(v_w=4\) km/h is connector walking speed, and the central benchmark uses \(q=0.50\). Let \(b_{ijqh}=1[m_{ijq}\leq h]\) be motorized reachability. Vehicle-enabled demand may use either mode, so its reachability is \(r_{ijqh}=\max(a_{ij,4,h},b_{ijqh})\). For Vehicle-Enabled Demand Share \(p\in\{0,0.25,0.50,0.75,1.00\}\), Mixed-Mode Accessibility Coverage is

\[
G_s^{mix}(p)=\frac{\sum_iD_{is}\left((1-p)1[\sum_ja_{ij,4,15}>0]+p1[\sum_jr_{ij,0.50,15}>0]\right)}{\sum_iD_{is}}.
\]

Here, \(G_s^{mix}(p)\) is an accessibility bound, not an estimate of observed mode share.

### Facility Selection and Capacity-Constrained Assignment

Let \(z_j\in\{0,1\}\) indicate whether general shelter \(j\) opens and let \(y_{ijscvh}\geq0\) be stress demand assigned from unit \(i\) to shelter \(j\). The conservative walking stress case sets \(c=50\), \(v=4\), \(h=15\), and permits at most \(B=415\) general shelters. Capacity interpretation centers on \(c=100\), while accessibility interpretation compares walking and mixed-mode bounds. The first lexicographic stage solves

\[
Z_{scvh}^{max}=\max_{y,z}\sum_i\sum_j y_{ijscvh}
\]

subject to

\[
0\leq y_{ijscvh}\leq D_{is}a_{ijvh},
\]

\[
\sum_j y_{ijscvh}\leq D_{is},
\]

\[
\sum_i y_{ijscvh}\leq cz_j,
\]

\[
\sum_j z_j\leq B.
\]

Here, \(Z_{scvh}^{max}\) is maximum served demand and \(B\) is the opening limit. Conditional on maximum service, the second stage minimizes \(\sum_j z_j\), the number of modeled open shelters. Conditional on both maximum service and the minimum opening count, the third stage solves

\[
\min_y\sum_i\sum_j t_{ijv}y_{ijscvh}
\]

subject to the preceding constraints and fixed first- and second-stage optima. Capacity-Constrained Served Demand and Model Explanation Gap are

\[
S_{iscvh}=\sum_j y_{ijscvh},
\]

\[
Q_{iscvh}=D_{is}-S_{iscvh}.
\]

Here, \(S_{iscvh}\) is assigned stress demand and \(Q_{iscvh}\) is Model Explanation Gap in unit \(i\).

### Current Evidence Before Multimodal Capacity Allocation

For the high-housing-loss-weighted 10,467-person stress surface, 15-minute walking access at 4 km/h reaches 6,286.84 persons before capacity and opening constraints. The 50-person, at-most-415-opening stress allocation assigns 5,894.54 persons (56.32 percent), leaving a Model Explanation Gap of 4,572.46 persons (43.68 percent). These values quantify the restrictive walking rule; they do not estimate event shelter admission or actual unmet need.

The central 0.50 motorized speed factor reaches 10,439.26 persons (99.74 percent) within 15 minutes. Mixed-mode accessibility rises from 60.06 percent when no demand is vehicle-enabled to 69.98, 79.90, 89.82, and 99.74 percent at vehicle-enabled shares of 25, 50, 75, and 100 percent. The near-complete motorized bound identifies accessibility assumptions as the main source of the earlier residual.

Capacity-threshold sensitivity separates capacity, opening-scale, and geographic limits. With at most 415 openings, proven-optimal service is 5,894.54 persons at 50 persons per shelter, 6,004.58 at 100 persons, and 6,006.57 at 200 persons. The 25-person run returns 5,518.74 persons with a 5,530.35 upper bound and 0.21 percent MIP gap. When all 1,156 general shelters are available, exact service is 5,835.86, 6,181.05, 6,286.84, and 6,286.84 persons at 25, 50, 100, and 200 persons per shelter. Thus capacity of at least 100 persons removes capacity shortfall among geographically reachable demand only when all general shelters are available; it cannot overcome the 15-minute geographic ceiling, and the 415-opening limit remains binding even at 200 persons.

Demand-geography sensitivity holds the observed-total-scaled stress load at 10,467 and the conservative 15-minute, 4-km/h, 50-person, 415-opening assumptions constant. Proven-optimal assigned shares are 62.60 percent for population weighting, 62.03 percent for central-housing-loss weighting, and 56.32 percent for high-housing-loss weighting. The high-loss geography is therefore the most demanding of the three under the restrictive walking rules.

Walking sensitivity holds high-loss-weighted stress demand, capacity, and opening scale constant. Proven-optimal served shares are 18.84 percent at 10 minutes and 3 km/h, 38.58 percent at 15 minutes and 3 km/h, and 32.01 percent at 10 minutes and 4 km/h. At 30 minutes, time-limited feasible service reaches 77.72 percent at 3 km/h with a 0.89 percent MIP gap and 87.06 percent at 4 km/h with a 1.66 percent MIP gap. These are lower bounds, with corresponding solver upper bounds of 78.41 and 88.50 percent, and are not labeled proven optima.

General-shelter unavailability is evaluated on the conservative 1-km walking network using 30 reproducible random draws per removal share plus a deterministic high-reachable-pressure stress test. Random removal of 10, 20, and 30 percent yields mean assigned shares of 54.02, 51.22, and 47.67 percent, with observed draw ranges of 53.08-54.98, 49.55-52.82, and 45.14-50.48 percent. Pressure-targeted removal produces much larger declines: assigned shares fall to 37.20, 19.23, and 11.51 percent. Targeted removal is a worst-case concentration diagnostic, not a probability forecast. All unavailability solutions have reported MIP gaps below 0.1 percent.

Single-shelter removal reoptimizes the remaining facility pool for the 30 highest reachable-pressure general shelters. The largest confirmed service-loss lower bounds are 47.92 persons for Toyofuku Elementary School Gymnasium in Uki, 47.91 each for Uki City Ogawa Disaster Prevention Base Center and Ogawa General Cultural Center Rapport, 47.89 for Kagami Elementary School in Yatsushiro, and 46.30 for Matsutaka Elementary School in Yatsushiro. These losses remain after replacement facility selection and are close to one full 50-person standardized capacity. The screen is not exhaustive: lower-total-pressure shelters may still be locally indispensable and require municipality-specific follow-up.

### Scenario and Failure Sensitivity

Relationship to Section 8 outputs: The demand equations support Prefecture Shelter Demand and General Shelter Geography; reverse-capacity equations support Municipality Reverse Capacity and Opening Pressure and the two capacity tables; accessibility equations support Walking and Motorized Accessibility Bounds; allocation and failure models support the 50-person stress-case map, Accessibility, Capacity, and Facility-Unavailability Robustness, and Network Accessibility and Robustness.

- Demand geography: Three 10,467-person observed-total-scaled stress spatializations based on Residential Population and central or high housing-loss demand. Unscaled low, central, and high housing-loss estimates remain contextual demand-construction bounds.
- Capacity: 100 persons per open general shelter is central; 50 persons is the conservative stress case; 25 and 200 persons are lower and upper sensitivities.
- Access: 15 minutes at 4 km/h is the restrictive walking bound. Motorized speed factors of 0.25, 0.50, and 1.00 and vehicle-enabled demand shares from zero to one define accessibility sensitivity.
- Opening scale: all general shelters available versus an optimistic budget of at most 415 modeled general-shelter openings anchored to the official undifferentiated open-shelter total.
- Unavailability: 0, 10, 20, and 30 percent of general shelters unavailable. Reproducible random draws measure distributional sensitivity; targeted removal evaluates dependence on high-pressure shelters.
- Road evidence: Walking uses the pedestrian-screened graph; motorized sensitivity uses all eligible and available road edges with road-class travel time and explicit speed factors. Administrative traffic restrictions, baseline bridge classes, and warning-zone exposure are not converted into deterministic event closures.
- For individual shelter \(j\), failure service loss is

\[
L_{jscvh}=Q_{scvh}^{(-j)}-Q_{scvh}.
\]

Here, \(Q_{scvh}^{(-j)}\) is prefecture-wide Model Explanation Gap after shelter \(j\) is unavailable and \(Q_{scvh}\) is the corresponding baseline gap.

## 7. Analytical Workflow

| step | variables used | formula/model used | generated figure/table title | theory or claim evaluated | support status |
|---|---|---|---|---|---|
| Separate general and welfare-specific supply and calibrate thresholds | Shelter Service Class, Official Numeric Capacity, Capacity Evidence Tier, Official Capacity Threshold Calibration | Threshold-calibration share in Section 4 | Capacity Evidence and Threshold Calibration | Whether 100 persons is a defensible central capacity case and 50 persons a conservative stress case | partially supported by 118 documented general shelters in three municipalities; selection limitation remains |
| Construct official-total-scaled stress surfaces | Residential Population, Housing-Loss Shelter Demand Central, Housing-Loss Shelter Demand High, Reported Evacuees, Municipality, Epicentral Distance | Demand spatialization equations in Section 6 | Prefecture Shelter Demand and General Shelter Geography | Whether an observed aggregate can scale alternative geographies without becoming observed local demand | supported as three counterfactual spatializations; no origin reconstruction |
| Estimate reverse capacity and openings | Standardized Capacity per General Shelter, Minimum Open Shelters Required, Required Capacity if All General Shelters Open, Critical Reverse Capacity | Reverse capacity and opening equations in Section 6 | Municipality Reverse Capacity and Opening Pressure; Aggregate Stress Load and Reverse Capacity Thresholds; Municipality Shelter Opening and Capacity Pressure | Whether pre-network requirements differ between prefecture arithmetic and municipality-contained ceilings | supported; both definitions will be labelled directly in the revised outputs |
| Calculate walking and motorized accessibility bounds | Network Walking Time, Network Motorized Time, Motorized Speed Factor, Vehicle-Enabled Demand Share, Mixed-Mode Accessibility Coverage, Municipality, Shelter Location | Walking, motorized, and mixed-mode equations in Section 6 | Walking and Motorized Accessibility Bounds | Whether the apparent gap is determined by the walking rule | supported: 15-minute accessibility rises from 60.1 percent under walking to 99.7 percent under the central motorized benchmark |
| Preserve the conservative capacity-constrained stress allocation | Standardized Capacity per General Shelter, Scenario-Available General Shelter Capacity, Capacity-Constrained Served Demand, Model Explanation Gap, Network Walking Time, Municipality | Three-stage allocation in Section 6 | Capacity-Constrained Service Gaps under the 50-Person Stress Case; Network Accessibility and Robustness | How much of each stress geography is explainable under the restrictive walking, opening, and 50-person rules | completed for three demand spatializations; 56.3 percent assigned under high-loss weighting, interpreted as a lower bound rather than actual service |
| Test capacity and facility-loss robustness | Standardized Capacity per General Shelter, Scenario-Available General Shelter Capacity, Capacity-Constrained Served Demand, Model Explanation Gap, Shelter Location | Capacity grid and failure-loss equation in Section 6 | Accessibility, Capacity, and Facility-Unavailability Robustness; Network Accessibility and Robustness | Whether capacity or facility concentration remains binding after accessibility is separated | capacity and walking-based facility-loss results complete; multimodal capacity screen pending |
| Maintain the road-evidence boundary | Motorized Speed Factor, Network Motorized Time | Speed-factor sensitivity without deterministic event edge deletion | Walking and Motorized Accessibility Bounds; Network Accessibility and Robustness | Whether available road evidence supports motorized sensitivity without claiming observed travel time | partially supported as static accessibility bounds; event congestion, damage, and mode choice remain unobserved |

## 8. Figure and Table Plan

### Figures

| title | what it expresses | figure type | subpanels | key variables | status |
|---|---|---|---:|---|---|
| Prefecture Shelter Demand and General Shelter Geography | Locates prefecture-wide housing-loss demand, the three 10,467-person observed-use stress spatializations, all general shelters, welfare-specific shelters, municipalities, and the official hypocenter without treating modeled local demand as observed use. | map | 4 | Housing-Loss Shelter Demand High, Reported Evacuees, Residential Population, Municipality, Epicentral Distance, Shelter Location, Shelter Service Class | done |
| Municipality Reverse Capacity and Opening Pressure | Shows municipality-contained opening requirements under the 100-person central capacity case while retaining 50 persons as a conservative stress case and avoiding cross-scenario ranking. | map and bar | 3 | Municipality, Minimum Open Shelters Required, Required Capacity if All General Shelters Open, Critical Reverse Capacity, Standardized Capacity per General Shelter | pending |
| Walking and Motorized Accessibility Bounds | Compares 15-minute walking reachability with connector-inclusive motorized reachability, shows mixed-mode coverage across vehicle-enabled demand shares, and identifies municipalities where mode availability changes the accessibility bound most. | map, line, and bar | 4 | Network Walking Time, Network Motorized Time, Motorized Speed Factor, Vehicle-Enabled Demand Share, Mixed-Mode Accessibility Coverage, Municipality, Shelter Location | pending |
| Capacity-Constrained Service Gaps under the 50-Person Stress Case | Maps assigned stress demand and the Model Explanation Gap after jointly enforcing walking reachability, 50-person capacity, and the opening budget; it is explicitly a conservative stress case rather than the central capacity estimate. | map | 3 | Standardized Capacity per General Shelter, Capacity-Constrained Served Demand, Model Explanation Gap, Municipality, Shelter Location | pending |
| Accessibility, Capacity, and Facility-Unavailability Robustness | Separates the gains from motorized or mixed-mode accessibility from the much smaller gains produced by increasing capacity, then reports random, pressure-targeted, and single-facility unavailability. | line, bar, and map | 4 | Mixed-Mode Accessibility Coverage, Standardized Capacity per General Shelter, Scenario-Available General Shelter Capacity, Capacity-Constrained Served Demand, Model Explanation Gap, Shelter Location | pending |

### Tables

| title | what it expresses | rows | columns | row meaning | column meaning | status |
|---|---|---:|---:|---|---|---|
| Capacity Evidence and Threshold Calibration | Documents shelter service class, numeric-capacity evidence, source coverage, and threshold calibration without repeating row-level interpretations; the note explains that 100 persons is central and 50 persons is conservative. | 12 | 8 | One evidence tier, municipality calibration group, or capacity threshold | Shelter counts, official capacity distribution, threshold coverage, and source limitation | pending |
| Aggregate Stress Load and Reverse Capacity Thresholds | Compares the four official event-use snapshots with capacity scenarios, labels 10,467 as an observed-total-scaled stress load rather than actual unmet demand, and distinguishes prefecture arithmetic from municipality-contained ceilings. | 20 | 9 | One snapshot-threshold or spatialization-critical-capacity combination | Observation, stress load, opening reference, threshold capacity, surplus or shortfall, and minimum openings | pending |
| Municipality Shelter Opening and Capacity Pressure | Provides four prefecture summaries plus ten municipalities selected within one declared high-loss-weighted scenario, including infeasible counts and both the 50-person stress and 100-person central opening requirements. | 14 | 10 | One prefecture scenario summary or one high-pressure municipality within the high-loss-weighted scenario | Demand, general shelters, municipality-contained openings, feasibility, required average capacity, and source distance | pending |
| Network Accessibility and Robustness | Provides a concise paper-facing summary of walking, motorized, mixed-mode, capacity, and facility-loss results, including the 20-percent random-removal case and selected municipality gaps. | 26 | 12 | One accessibility, allocation, municipality, or facility-loss scenario | Mode assumptions, capacity assumptions, accessible or assigned demand, explanation gap, municipality evidence, failure loss, and solver qualification | pending |

Interpretation warning: The 10,467-person total is an observed aggregate used to scale counterfactual residential demand surfaces; model residuals are explanation gaps under stated designated-shelter and network constraints, not observed people refused shelter. Walking and motorized results are accessibility bounds, and vehicle-enabled shares are sensitivity parameters rather than reconstructed behavior. Lower-pressure facilities may still be locally critical, and no scenario represents every real road and facility state.
