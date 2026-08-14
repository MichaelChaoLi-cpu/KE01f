# AnaSOP
Analysis Standard Operating Procedure

## 1. Research Objective

### Central Research Question

- Research question: Following the 28 July 2026 earthquake, how much of an official-total-scaled shelter stress load can Kumamoto Prefecture's designated general-shelter system explain under walking, motorized, and mixed-mode accessibility bounds, and whether accessibility, deployable capacity, or facility availability is the binding planning constraint?
- Why it matters: The official aggregate of 10,467 shelter users establishes that evacuation occurred but does not identify residential origins, travel modes, or assigned facilities. A model that reaches fewer than 10,467 people under a 15-minute walking rule therefore identifies the limit of that planning rule, not the number of people actually refused shelter.
- Data support currently visible: Prefecture-wide evidence includes 62,945 populated 125 m meshes, 36,657 disclosure-group demand units, 1,315 geolocated designated shelters across 45 municipalities, four official aggregate event-use snapshots, and a road network with road-class baseline travel times. All 1,156 general shelters and virtually all residential population are attached to the network. Official numeric capacities for 118 general shelters calibrate 25-, 50-, 100-, and 200-person scenarios. Under the high-loss-weighted stress geography, 15-minute walking reaches 60.1 percent of the load, whereas the corrected central low-speed motorized benchmark reaches 99.0 percent.
- Key readable variables or data scope: Reported Evacuees; three observed-total-scaled stress geographies; Standardized Capacity per General Shelter; Network Walking Time; Network Motorized Time; Vehicle-Enabled Demand Share; Mixed-Mode Accessibility Coverage; Capacity-Constrained Served Demand; Model Explanation Gap; Municipality; facility availability.
- What would verify it: Accessibility coverage and capacity-constrained assignment change materially across mode-availability assumptions but only modestly across plausible capacity thresholds, with explicit municipality and facility-loss evidence locating the remaining planning gaps.
- What would falsify or weaken it: An accessibility-binding interpretation would weaken if higher standardized capacity closes most of the walking-based gap, if motorized or mixed-mode access changes little, or if findings depend on one unsupported demand spatialization or one facility-loss realization.
- Required next feasibility check: Completed. Corrected accessibility bounds, the central shared-capacity comparison, the all-shelter opening-scale contrast, and mixed-pressure targeted facility-loss tests are all available with explicit solver qualifications.

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
- Data support currently visible: Population meshes, all general shelter locations, road-class baseline travel times, direct network attachments, and administrative areas support connector-inclusive walking and motorized shortest paths. At 15 minutes, walking reaches 60.1 percent of high-loss-weighted stress demand; the corrected central motorized benchmark reaches 99.0 percent. Mixed-mode accessibility increases monotonically from 60.1 to 99.0 percent as the vehicle-enabled demand share rises from zero to one.
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

- Design principle: This is an applied partial-identification and scenario-comparison assessment. It estimates how much of an official-total-scaled stress surface can be assigned to the designated general-shelter system under explicit access, capacity, opening, and facility-availability rules. It does not reconstruct actual evacuation, estimate actual travel-mode shares, or infer an unobserved factual capacity for every shelter.
- Demand identification: The largest available official aggregate observation, 10,467 Reported Evacuees, scales three counterfactual residential stress surfaces using Residential Population, Housing-Loss Shelter Demand Central, and Housing-Loss Shelter Demand High. The aggregate is an observed reference; every mesh- and municipality-level allocation is modeled. The unscaled housing-loss estimates remain contextual displacement inputs.
- Capacity identification: Standardized Capacity per General Shelter is 100 persons in the central scenario, 50 persons is a conservative stress case, and 25 and 200 persons are lower and upper sensitivities. Official Numeric Capacity from 118 deduplicated general shelters provides plausibility calibration only. Welfare-specific shelters remain outside unrestricted general-population supply.
- Reverse-requirement contrast: Minimum Open Shelters Required, Required Capacity if All General Shelters Open, and Critical Reverse Capacity are calculated before network routing. These arithmetic screens distinguish implausible capacity requirements from gaps created by geographic access or a limited opening budget.
- Access identification: The 15-minute, 4-km/h walking case is the restrictive accessibility bound. Motorized travel uses road-class baseline travel time on every traversed road edge, and each edge time is divided by Motorized Speed Factor. The central factor is 0.50; 0.25 and 1.00 are sensitivity values. Off-network demand and shelter connectors remain walking segments at 4 km/h. Vehicle-Enabled Demand Share ranges from zero to one and proportionally divides each demand unit into walking-only and vehicle-enabled components without estimating observed behavior.
- Shared-capacity identification: Walking-only and vehicle-enabled components compete for the same Scenario-Available General Shelter Capacity and the same opening budget. Vehicle-enabled demand may use the faster reachable walking or motorized route, but capacity cannot be counted once for each mode. At most 415 general shelters may open in the central constrained comparison. This optimistic budget is anchored to the official undifferentiated Open Shelters total, not an observed list of open general shelters.
- Allocation algorithm: The location-allocation estimand is maximum Capacity-Constrained Served Demand. A coverage-selection relaxation supplies an upper bound, and exact maximum flow through the selected facilities supplies a feasible lower bound. Equality proves the maximum-service result; otherwise the lower bound and relative solver gap are reported. The analysis does not claim to minimize the number of openings, minimize assigned travel time, or identify a unique optimal facility set.
- Comparable constraint diagnosis: The high-housing-loss-weighted stress geography, 15-minute threshold, 4-km/h walking speed, 0.50 Motorized Speed Factor, and 415-opening budget form the common comparison base. Mode availability is varied across five Vehicle-Enabled Demand Shares at the 100-person central capacity. Capacity is compared at a fixed 50-percent vehicle-enabled share using the 50- and 100-person cases. Opening scale compares at most 415 openings with all 1,156 general shelters selectable under the same central mixed-mode assumptions. Facility-unavailability penalties use that same base. A factor is described as more binding only when its matched percentage-point contrast is larger; the contrasts are descriptive scenario comparisons rather than causal effects.
- Robustness identification: Demand geography, capacity threshold, walking speed, time threshold, capacity-free Motorized Speed Factor, Vehicle-Enabled Demand Share, opening scale, and 0, 10, 20, and 30 percent facility unavailability are varied. Random unavailability is summarized across reproducible draws. Targeted loss ranks facilities by the declared central mixture of 50-percent walking-only reachable pressure and 50-percent vehicle-enabled reachable pressure. The walking-only single-shelter screen remains secondary evidence. Cross-municipality assignment is allowed only through an eligible path within the selected time threshold.
- Road-evidence boundary: Event records do not establish complete motorized or pedestrian edge failure, event congestion, or direction-specific road operability. Motorized scenarios therefore scale travel time on all eligible and available road edges rather than imposing undocumented closures. Toll and expressway edges may be used in motorized paths, while demand and shelter attachments remain on ordinary roads. The motorized graph is an accessibility bound where directionality is unavailable, not an observed post-earthquake transport system.
- Output connection: Prefecture Shelter Demand and General Shelter Geography establishes the stress inputs; the capacity tables establish pre-network requirements; Walking and Motorized Accessibility Bounds reports corrected access envelopes; Capacity-Constrained Service Gaps under the 50-Person Stress Case preserves the restrictive walking stress case; Accessibility, Capacity, and Facility-Unavailability Robustness and Network Accessibility and Robustness report matched access, shared-capacity, opening, and failure contrasts.
- Interpretation limit: Capacity-Constrained Served Demand is assigned modeled stress demand. Model Explanation Gap is demand not explained by the selected designated-shelter rules, not observed people refused shelter. Actual residents may have traveled farther, used vehicles or non-designated places, crossed unmodeled road conditions, or encountered facility conditions absent from the available evidence.

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

Let demand unit \(i\) and shelter \(j\) attach to an augmented pedestrian graph that splits their accepted access edges at the attachment positions. Let \(\mathcal{P}_{ij}^{W}\) be the set of eligible pedestrian paths between those positions and let \(d_e\) be the length in meters of pedestrian edge or fractional edge segment \(e\). The within-network walking distance is

\[
\delta_{ij}=\min_{\pi\in\mathcal{P}_{ij}^{W}}\sum_{e\in\pi}d_e.
\]

Here, \(\delta_{ij}\) is the shortest pedestrian-network distance, \(\pi\) is one eligible path, and \(e\) indexes every complete or fractional road segment on that path. Door-to-door Network Walking Time is

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

Let \(\mathcal{P}_{ij}^{M}\) be the set of eligible motorized paths between the augmented demand and shelter access positions, let \(\tau_e\) be road-class baseline travel time in minutes for complete or fractional motorized edge segment \(e\), and let \(q\in\{0.25,0.50,1.00\}\) be Motorized Speed Factor. Corrected within-network motorized time is

\[
\tau_{ijq}^{road}=\min_{\pi\in\mathcal{P}_{ij}^{M}}\sum_{e\in\pi}\frac{\tau_e}{q}.
\]

Here, \(\tau_{ijq}^{road}\) is shortest motorized road time under factor \(q\). The division by \(q\) applies to every intervening road edge and to the road portions of both access edges; it is not limited to the two local access edges. Network Motorized Time is

\[
m_{ijq}=\frac{60\ell_i^{snap}}{1000v_w}+\tau_{ijq}^{road}+\frac{60\ell_j^{snap}}{1000v_w}.
\]

Here, \(m_{ijq}\) is connector-inclusive motorized time and \(v_w=4\) km/h is connector walking speed. The central benchmark uses \(q=0.50\). Motorized reachability is \(b_{ijqh}=1[m_{ijq}\leq h]\). Vehicle-enabled demand may use either mode, so its reachability is \(r_{ijqvh}=\max(a_{ijvh},b_{ijqh})\). For Vehicle-Enabled Demand Share \(p\in\{0,0.25,0.50,0.75,1.00\}\), Mixed-Mode Accessibility Coverage is

\[
G_{spqvh}^{mix}=\frac{\sum_iD_{is}\left((1-p)1[\sum_ja_{ijvh}>0]+p1[\sum_jr_{ijqvh}>0]\right)}{\sum_iD_{is}}.
\]

Here, \(G_{spqvh}^{mix}\) is the share of scenario demand with access before shelter capacity and opening constraints. It is an accessibility bound, not an estimate of observed mode share. Pairwise motorized reachability is enumerated with time-truncated shortest paths so that the later allocation model can consider every reachable shelter rather than only the nearest shelter.

Network validation must precede substantive interpretation. For each demand-shelter pair, \(m_{ij,0.25}\geq m_{ij,0.50}\geq m_{ij,1.00}\), and the corresponding reachable sets must be nested. The minimum pairwise time over shelters must reproduce the corrected nearest-shelter result. Speed-factor sensitivity is invalid if only the access-edge portions change while intervening path edges retain unscaled baseline time.

### Shared-Capacity Multimodal Facility Selection and Assignment

For a fixed scenario \(\theta=(s,c,p,q,v,h,B,u)\), let \(B\) be the maximum number of modeled openings, let \(u\) index a facility-availability realization, and let \(o_{ju}\in\{0,1\}\) indicate whether general shelter \(j\) is available in that realization. Let \(z_{j\theta}\in\{0,1\}\) indicate whether shelter \(j\) opens. Let \(y_{ij\theta}^{W}\geq0\) and \(y_{ij\theta}^{V}\geq0\) be walking-only and vehicle-enabled stress demand assigned from unit \(i\) to shelter \(j\). The maximum-service problem is

\[
Z_{\theta}^{max}=\max_{y,z}\sum_i\sum_j\left(y_{ij\theta}^{W}+y_{ij\theta}^{V}\right)
\]

Here, \(\theta\) collects all scenario parameters and \(Z_{\theta}^{max}\) is maximum assigned demand. The optimization is subject to

\[
0\leq y_{ij\theta}^{W}\leq(1-p)D_{is}a_{ijvh},
\]

\[
\sum_j y_{ij\theta}^{W}\leq(1-p)D_{is},
\]

\[
0\leq y_{ij\theta}^{V}\leq pD_{is}r_{ijqvh},
\]

\[
\sum_j y_{ij\theta}^{V}\leq pD_{is},
\]

\[
\sum_i\left(y_{ij\theta}^{W}+y_{ij\theta}^{V}\right)\leq cz_{j\theta},
\]

\[
z_{j\theta}\leq o_{ju},\qquad \sum_jz_{j\theta}\leq B.
\]

The shared capacity constraint prevents the same shelter capacity from being counted separately for walking-only and vehicle-enabled demand. Computation uses a coverage-selection relaxation as an upper bound and exact maximum flow through the selected facilities as a feasible lower bound. Equality of the bounds proves the maximum-service optimum; otherwise both the lower bound and relative solver gap are retained. Opening counts and facility selections are computational solutions for maximum service, not minimum-opening or minimum-travel-time estimands. Capacity-Constrained Served Demand, Model Explanation Gap, and assigned share are

\[
S_{i\theta}=\sum_j\left(y_{ij\theta}^{W}+y_{ij\theta}^{V}\right),
\]

\[
Q_{i\theta}=D_{is}-S_{i\theta},
\]

\[
A_{\theta}=100\frac{\sum_iS_{i\theta}}{\sum_iD_{is}}.
\]

Here, \(S_{i\theta}\) is assigned stress demand, \(Q_{i\theta}\) is Model Explanation Gap in unit \(i\), and \(A_{\theta}\) is the percentage of scenario demand assigned under the complete rule set.

### Matched Constraint Contrasts

Let \(A_s(p,c,B,q,u)\) denote \(A_{\theta}\) when \(v=4\) km/h and \(h=15\) minutes are fixed. Let \(u=0\) denote no facility removal. The mode-availability contrast is

\[
\Delta_s^{mode}=A_s(0.50,100,415,0.50,0)-A_s(0,100,415,0.50,0).
\]

Here, \(\Delta_s^{mode}\) is the percentage-point difference between the central 50-percent vehicle-enabled scenario and walking-only shared-capacity assignments. The fully vehicle-enabled case remains an upper sensitivity bound. The capacity contrast at the same central mixed-mode share is

\[
\Delta_s^{capacity}=A_s(0.50,100,415,0.50,0)-A_s(0.50,50,415,0.50,0).
\]

Here, \(\Delta_s^{capacity}\) is the percentage-point gain from increasing shared capacity from the 50-person stress case to the 100-person central case. The opening-scale contrast is

\[
\Delta_s^{opening}=A_s(0.50,100,1156,0.50,0)-A_s(0.50,100,415,0.50,0).
\]

Here, \(\Delta_s^{opening}\) is the percentage-point gain when all 1,156 general shelters may be selected instead of at most 415. For a nonzero facility-removal realization \(u\), facility-availability loss is

\[
L_{su}^{facility}=A_s(0.50,100,415,0.50,0)-A_s(0.50,100,415,0.50,u).
\]

Here, \(L_{su}^{facility}\) is the percentage-point service loss relative to the matched no-removal scenario. Comparing \(\Delta_s^{mode}\), \(\Delta_s^{capacity}\), \(\Delta_s^{opening}\), and \(L_{su}^{facility}\) identifies the largest operational constraint within the stated scenarios. It does not identify a causal effect or an observed mechanism.

### Current Valid Evidence and Focused Re-estimation

The completed walking analysis remains valid as a restrictive stress benchmark. Under the high-housing-loss-weighted 10,467-person stress surface, 15-minute walking at 4 km/h reaches 60.1 percent before capacity and opening constraints. The 50-person, at-most-415-opening walking allocation assigns 56.3 percent and leaves a 43.7 percent Model Explanation Gap.

Corrected motorized time now scales every intervening road edge. The 15-minute motorized accessibility bound is 99.0 percent at the central 0.50 speed factor. Under shared 100-person capacity and at most 415 openings, assigned service rises from 57.4 percent for walking-only demand to 77.5 percent when 50 percent of demand is vehicle-enabled. At the same 50-percent vehicle-enabled share, the 50-person lower bound is 77.4 percent with an upper bound equal to the proven 100-person result; the supported capacity gain is therefore between zero and approximately 0.1 percentage point. Focused re-estimation adds the all-1,156-opening central case and replaces vehicle-only targeted pressure with the declared 50-percent walking and 50-percent vehicle-enabled pressure.

### Scenario and Failure Sensitivity

Relationship to Section 8 outputs: The demand equations support Prefecture Shelter Demand and General Shelter Geography; reverse-capacity equations support Municipality Reverse Capacity and Opening Pressure and the two capacity tables; corrected accessibility equations support Walking and Motorized Accessibility Bounds; shared-capacity allocation and matched contrasts support Accessibility, Capacity, and Facility-Unavailability Robustness and Network Accessibility and Robustness; the walking-only 50-person allocation supports Capacity-Constrained Service Gaps under the 50-Person Stress Case.

- Demand geography: Three 10,467-person observed-total-scaled stress spatializations based on Residential Population and central or high housing-loss demand. Unscaled low, central, and high housing-loss estimates remain contextual demand-construction bounds.
- Capacity: 100 persons per open general shelter is central; 50 persons is the conservative stress case; 25 and 200 persons are lower and upper sensitivities.
- Access: 15 minutes at 4 km/h is the restrictive walking bound. Motorized Speed Factors of 0.25, 0.50, and 1.00 define capacity-free accessibility sensitivity. Vehicle-Enabled Demand Shares of 0, 0.25, 0.50, 0.75, and 1.00 are evaluated at \(q=0.50\).
- Shared-capacity multimodal screen: Mode availability is evaluated for \(p\in\{0,0.25,0.50,0.75,1.00\}\) at \(c=100\), \(q=0.50\), \(v=4\) km/h, \(h=15\) minutes, and \(B=415\). The matched capacity contrast uses \(p=0.50\) and \(c\in\{50,100\}\). The 25- and 200-person thresholds remain walking capacity sensitivities rather than multimodal optimization cases.
- Opening scale: all general shelters available versus an optimistic budget of at most 415 modeled general-shelter openings anchored to the official undifferentiated open-shelter total.
- Unavailability: 0, 10, 20, and 30 percent of general shelters unavailable. Reproducible random draws measure distributional sensitivity; targeted removal evaluates dependence on facilities ranked by \(0.5\) times walking-reachable pressure plus \(0.5\) times vehicle-enabled reachable pressure. The matched multimodal comparison uses \(p=0.50\), \(c=100\), \(q=0.50\), \(v=4\) km/h, \(h=15\) minutes, and \(B=415\). The existing walking-only, 50-person failure test remains a conservative secondary benchmark.
- Road evidence: Walking uses the pedestrian-screened graph; motorized sensitivity uses all eligible and available road edges with road-class travel time and explicit speed factors. Administrative traffic restrictions, baseline bridge classes, and warning-zone exposure are not converted into deterministic event closures.
- For individual shelter \(j\), failure service loss is

\[
L_{j\theta}^{person}=\sum_iQ_{i\theta}^{(-j)}-\sum_iQ_{i\theta}.
\]

Here, \(L_{j\theta}^{person}\) is additional Model Explanation Gap in persons after shelter \(j\) is removed and the remaining system is reoptimized, and \(Q_{i\theta}^{(-j)}\) is the post-removal gap in demand unit \(i\).

## 7. Analytical Workflow

| step | variables used | formula/model used | generated figure/table title | theory or claim evaluated | support status |
|---|---|---|---|---|---|
| Separate general and welfare-specific supply and calibrate thresholds | Shelter Service Class, Official Numeric Capacity, Capacity Evidence Tier, Official Capacity Threshold Calibration | Threshold-calibration share in Section 4 | Capacity Evidence and Threshold Calibration | Whether 100 persons is a defensible central capacity case and 50 persons a conservative stress case | partially supported by 118 documented general shelters in three municipalities; selection limitation remains |
| Construct official-total-scaled stress surfaces | Residential Population, Housing-Loss Shelter Demand Central, Housing-Loss Shelter Demand High, Reported Evacuees, Municipality, Epicentral Distance | Demand spatialization equations in Section 6 | Prefecture Shelter Demand and General Shelter Geography | Whether an observed aggregate can scale alternative geographies without becoming observed local demand | supported as three counterfactual spatializations; no origin reconstruction |
| Estimate reverse capacity and openings | Standardized Capacity per General Shelter, Minimum Open Shelters Required, Required Capacity if All General Shelters Open, Critical Reverse Capacity | Reverse capacity and opening equations in Section 6 | Municipality Reverse Capacity and Opening Pressure; Aggregate Stress Load and Reverse Capacity Thresholds; Municipality Shelter Opening and Capacity Pressure | Whether pre-network requirements differ between prefecture arithmetic and municipality-contained ceilings | supported; both definitions will be labelled directly in the revised outputs |
| Rebuild corrected motorized pairwise travel times | Demand Walking-Network Attachment, Shelter Walking-Network Attachment, Network Motorized Time, Motorized Speed Factor, Shelter Location | Every-edge motorized path-time equation and nesting checks in Section 6 | Walking and Motorized Accessibility Bounds; Network Accessibility and Robustness | Whether motorized sensitivity is internally valid before substantive comparison | supported; every-edge scaling passes nesting checks and the central motorized bound is 99.0 percent |
| Calculate walking, motorized, and mixed-mode accessibility bounds | Network Walking Time, Network Motorized Time, Motorized Speed Factor, Vehicle-Enabled Demand Share, Mixed-Mode Accessibility Coverage, Municipality, Shelter Location | Pairwise reachability and mixed-mode coverage equations in Section 6 | Walking and Motorized Accessibility Bounds | Whether relaxing the walking-only rule materially expands access before capacity constraints | supported; coverage increases monotonically from 60.1 to 99.0 percent across the vehicle-enabled share |
| Preserve the conservative walking allocation | Standardized Capacity per General Shelter, Scenario-Available General Shelter Capacity, Capacity-Constrained Served Demand, Model Explanation Gap, Network Walking Time, Municipality | Walking-only special case of the maximum-service model with \(p=0\) | Capacity-Constrained Service Gaps under the 50-Person Stress Case; Network Accessibility and Robustness | How much of each stress geography is explainable under restrictive walking, opening, and 50-person rules | supported for three stress geographies; 56.3 percent assigned under high-loss weighting and interpreted as a lower-bound stress result |
| Estimate shared-capacity multimodal allocation | Network Walking Time, Network Motorized Time, Motorized Speed Factor, Vehicle-Enabled Demand Share, Standardized Capacity per General Shelter, Scenario-Available General Shelter Capacity, Capacity-Constrained Served Demand, Model Explanation Gap | Maximum-service shared-capacity model with reported lower and upper bounds in Section 6 | Accessibility, Capacity, and Facility-Unavailability Robustness; Network Accessibility and Robustness | Whether mode availability still changes explainable service after capacity and the 415-opening budget are imposed | supported for the 100-person mode grid and matched 50-percent vehicle-enabled capacity contrast; nonzero gaps are retained explicitly |
| Compare matched operational constraints | Vehicle-Enabled Demand Share, Standardized Capacity per General Shelter, Scenario-Available General Shelter Capacity, Capacity-Constrained Served Demand, Model Explanation Gap | Mode, capacity, opening-scale, and facility-loss contrasts in Section 6 | Accessibility, Capacity, and Facility-Unavailability Robustness; Network Accessibility and Robustness | Whether accessibility, deployable capacity, opening scale, or facility availability is most binding under a common scenario base | supported within the declared scenarios; mode availability adds 20.1 percentage points, all-shelter selection adds 2.0 points, and the supported capacity gain is at most about 0.1 point |
| Test facility unavailability and critical shelters | Scenario-Available General Shelter Capacity, Capacity-Constrained Served Demand, Model Explanation Gap, Shelter Location, Municipality | Random, mixed-pressure targeted, and secondary walking single-removal reoptimization with the failure-loss equation in Section 6 | Accessibility, Capacity, and Facility-Unavailability Robustness; Network Accessibility and Robustness | Whether service depends disproportionately on a concentrated facility set | supported as sensitivity evidence; mixed-pressure targeted removal reduces assigned service to 65.9, 38.2, and 22.7 percent at 10, 20, and 30 percent removal |
| Maintain the road-evidence boundary | Motorized Speed Factor, Network Motorized Time | Speed-factor sensitivity on every traversed edge without deterministic event edge deletion | Walking and Motorized Accessibility Bounds; Network Accessibility and Robustness | Whether static road evidence supports bounded motorized planning scenarios without claiming observed travel time | partially supported by available road attributes; congestion, damage, directionality, and observed mode choice remain unobserved |

## 8. Figure and Table Plan

### Figures

| title | what it expresses | figure type | subpanels | key variables | status |
|---|---|---|---:|---|---|
| Prefecture Shelter Demand and General Shelter Geography | Locates prefecture-wide housing-loss demand, the three 10,467-person observed-use stress spatializations, all general shelters, welfare-specific shelters, municipalities, and the official hypocenter without treating modeled local demand as observed use. | map | 4 | Housing-Loss Shelter Demand High, Reported Evacuees, Residential Population, Municipality, Epicentral Distance, Shelter Location, Shelter Service Class | done |
| Municipality Reverse Capacity and Opening Pressure | Shows municipality-contained opening requirements under the 100-person central capacity case while retaining 50 persons as a conservative stress case and avoiding cross-scenario ranking. | map and bar | 3 | Municipality, Minimum Open Shelters Required, Required Capacity if All General Shelters Open, Critical Reverse Capacity, Standardized Capacity per General Shelter | done |
| Walking and Motorized Accessibility Bounds | Compares 15-minute walking reachability with connector-inclusive motorized reachability, shows mixed-mode coverage across vehicle-enabled demand shares, and identifies municipalities where mode availability changes the accessibility bound most. | map, line, and bar | 4 | Network Walking Time, Network Motorized Time, Motorized Speed Factor, Vehicle-Enabled Demand Share, Mixed-Mode Accessibility Coverage, Municipality, Shelter Location | done |
| Capacity-Constrained Service Gaps under the 50-Person Stress Case | Maps assigned stress demand and the Model Explanation Gap after jointly enforcing walking reachability, 50-person capacity, and the opening budget; it is explicitly a conservative stress case rather than the central capacity estimate. | map | 3 | Standardized Capacity per General Shelter, Capacity-Constrained Served Demand, Model Explanation Gap, Municipality, Shelter Location | done |
| Accessibility, Capacity, and Facility-Unavailability Robustness | Separates matched mode, capacity, and opening-scale gains, then reports random, mixed-pressure-targeted, and secondary single-facility unavailability. | line, bar, and map | 4 | Mixed-Mode Accessibility Coverage, Standardized Capacity per General Shelter, Scenario-Available General Shelter Capacity, Capacity-Constrained Served Demand, Model Explanation Gap, Shelter Location | done |

### Tables

| title | what it expresses | rows | columns | row meaning | column meaning | status |
|---|---|---:|---:|---|---|---|
| Capacity Evidence and Threshold Calibration | Documents shelter service class, numeric-capacity evidence, source coverage, and threshold calibration without repeating row-level interpretations; the note explains that 100 persons is central and 50 persons is conservative. | 12 | 8 | One evidence tier, municipality calibration group, or capacity threshold | Shelter counts, official capacity distribution, threshold coverage, and source limitation | done |
| Aggregate Stress Load and Reverse Capacity Thresholds | Compares the four official event-use snapshots with capacity scenarios, labels 10,467 as an observed-total-scaled stress load rather than actual unmet demand, and distinguishes prefecture arithmetic from municipality-contained ceilings. | 20 | 9 | One snapshot-threshold or spatialization-critical-capacity combination | Observation, stress load, opening reference, threshold capacity, surplus or shortfall, and minimum openings | done |
| Municipality Shelter Opening and Capacity Pressure | Provides four prefecture summaries plus ten municipalities selected within one declared high-loss-weighted scenario, including infeasible counts and both the 50-person stress and 100-person central opening requirements. | 14 | 10 | One prefecture scenario summary or one high-pressure municipality within the high-loss-weighted scenario | Demand, general shelters, municipality-contained openings, feasibility, required average capacity, and source distance | done |
| Network Accessibility and Robustness | Provides a concise paper-facing summary of walking, motorized, mixed-mode, matched capacity, opening-scale, and facility-loss results, including the 20-percent random-removal case and selected municipality gaps. | 27 | 12 | One accessibility, allocation, opening-scale, municipality, or facility-loss scenario | Mode assumptions, capacity and opening assumptions, accessible or assigned demand, explanation gap, municipality evidence, failure loss, and solver qualification | done |

Interpretation warning: The 10,467-person total is an observed aggregate used to scale counterfactual residential demand surfaces; model residuals are explanation gaps under stated designated-shelter and network constraints, not observed people refused shelter. Walking and motorized results are accessibility bounds, and vehicle-enabled shares are sensitivity parameters rather than reconstructed behavior. Lower-pressure facilities may still be locally critical, and no scenario represents every real road and facility state.
