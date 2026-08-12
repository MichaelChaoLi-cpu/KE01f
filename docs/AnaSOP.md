# AnaSOP
Analysis Standard Operating Procedure

## 1. Research Objective

### Central Research Question

- Research question: Following the 28 July 2026 earthquake, is the existing designated shelter system across Kumamoto Prefecture sufficient to accommodate earthquake-related evacuation demand during the first 0-72 hours, both in total effective capacity and in local spatial accessibility?
- Why it matters: The official hypocenter was in Uki City rather than Kumamoto City, and damaging shaking and evacuation needs may extend across municipal boundaries. A city-only capacity surplus cannot establish whether residents nearer the source area or in rural and coastal municipalities have adequate reachable shelter capacity.
- Data support currently visible: Prefecture-wide evidence includes 62,945 populated 125 m meshes, 36,657 disclosure-group demand units, 1,315 geolocated designated shelters across 45 municipalities, four official aggregate event-use snapshots, and a pedestrian-screened road network. All 1,156 general shelters have accepted direct walking-network attachments; population-mesh attachments cover 99.989 percent of residents. Official numeric capacity for 118 general shelters calibrates the accepted 50-person primary threshold, with 25, 100, and 200 persons used in sensitivity analysis. In the completed primary 50-person, 415-opening, 15-minute allocation, 5,894.54 of 10,467 high-loss-weighted stress-demand persons are served and 4,572.46 remain unmet.
- Key readable variables or data scope: prefecture-wide shelter demand by mesh \(D_{is}\); municipality; epicentral distance; shelter location; nominal and effective shelter capacity \(C_{js}^{eff}\); network walking time \(t_{ij}\); served and unserved demand; facility utilization; municipality-level capacity surplus or deficit.
- What would verify it: The study shows that the 10,467-person observed-use stress total can be assigned to reachable general shelters across three defensible residential spatializations under explicit walking, capacity, opening, and facility-unavailability assumptions, with low and spatially limited unmet demand.
- What would falsify or weaken it: A sufficiency conclusion would fail or weaken if substantial demand remains beyond 15- or 30-minute access, the 50-person allocation produces stable source-proximate deficits, or results depend strongly on unknown facility opening and availability.
- Required next feasibility check: The completed primary allocation rejects unconditional sufficiency at 50 persons and 415 openings because only 56.32 percent of the high-loss-weighted stress demand is served. Capacity thresholds, alternative demand spatializations, walking assumptions, general-shelter unavailability, and the 30 highest-pressure single-shelter removals have now been tested. The road-evidence audit does not support deterministic pedestrian-edge deletion; retain lower-pressure local-criticality checks as a limitation in the content dictionary and manuscript.

### Supporting Research Questions

The plan contains one central question and four supporting questions.

#### Supporting Point 1

- Role relative to central point: demand estimation
- Research question: How does the geographic distribution of the highest available observed-use stress total change under population-, central-housing-loss-, and high-housing-loss-weighted spatializations, and which distribution places the greatest pressure on reachable shelter capacity?
- Why it matters: The official reports identify 10,467 shelter users but not their residential origins. Prefecture-wide adequacy therefore depends on transparent alternative spatializations rather than an invented observed local-demand map.
- Data support currently visible: The highest available first-72-hour snapshot provides the 10,467-person aggregate benchmark. Complete 125 m population meshes, central and high housing-loss demand weights, municipality boundaries, and epicentral distance support three internally consistent spatializations with the same prefecture-wide total.
- Key readable variables or data scope: Reported Evacuees; Observed-Use Stress Demand Population Weighted; Observed-Use Stress Demand Central-Loss Weighted; Observed-Use Stress Demand High-Loss Weighted; Residential Population; Municipality; Epicentral Distance.
- What would verify it: Each spatialization preserves the 10,467-person total, is never relabeled as observed local demand, and produces interpretable differences in accessibility and capacity-constrained service.
- What would falsify or weaken it: The demand-side comparison would be weak if any spatialization changes the aggregate benchmark, uses incomplete geographic weights, or is interpreted as the actual residential origin of evacuees.
- Required feasibility check: Completed. The three spatializations preserve the aggregate total and have full-prefecture municipality and network coverage; their local patterns remain modeled alternatives rather than observed origins.

#### Supporting Point 2

- Role relative to central point: reverse capacity and opening requirements
- Research question: What standardized capacity per open general shelter and how many modeled openings are required to accommodate prefecture-wide and municipality-contained demand without relying on unavailable facility areas?
- Why it matters: Complete facility area and numeric capacity cannot be recovered reliably for all 1,315 records. A reverse requirement is more defensible than presenting unsupported facility-level capacity estimates as facts.
- Data support currently visible: The official inventory identifies 1,156 general and 159 welfare-specific shelters. The largest available observed-use snapshot reports 10,467 evacuees and an undifferentiated total of 415 open shelters. Among 118 deduplicated general shelters with Official Numeric Capacity in Uki, Uto, and Yatsushiro, 88.1 percent have capacity of at least 50 persons and the median is 241 persons.
- Key readable variables or data scope: Standardized Capacity per General Shelter; Minimum Open Shelters Required; Required Capacity if All General Shelters Open; Critical Reverse Capacity; Official Capacity Threshold Calibration; Municipality; Shelter Service Class.
- What would verify it: A standardized threshold accommodates the stress scenarios at or below an optimistic general-shelter opening budget anchored to the official undifferentiated total of 415 and remains plausible relative to documented official capacities; 25, 50, 100, and 200 persons reveal sensitivity rather than alternative factual estimates. The completed primary network model shows that 50 persons does not accommodate the high-loss-weighted stress scenario within 15 minutes even under this optimistic opening budget.
- What would falsify or weaken it: The threshold approach would be weak if the inadequacy conclusion disappeared under the optimistic opening budget and plausible higher capacities, or if the selected threshold were unsupported by the documented calibration sample.
- Required feasibility check: Compare the completed 50-person result with 25-, 100-, and 200-person thresholds while retaining welfare-specific supply separately and reporting calibration selection limits explicitly.

#### Supporting Point 3

- Role relative to central point: spatial accessibility and municipal heterogeneity
- Research question: Which 125 m population meshes and municipalities remain beyond practical shelter access or face demand exceeding nearby capacity even if aggregate prefecture-wide capacity is sufficient?
- Why it matters: Capacity in Kumamoto City or another municipality may be too distant or operationally irrelevant to residents near the hypocenter, on islands, or in sparsely connected rural areas.
- Data support currently visible: Population meshes, all general shelter locations, pedestrian-screened road nodes and edges, direct network attachments, recomputed walking components, administrative areas, and age-specific population support capacity-constrained accessibility analysis. Nearest-shelter results show 67.2 percent population coverage and 60.1 percent high-loss-weighted stress-demand coverage within 15 minutes at 4 km/h, rising to 92.4 and 91.6 percent within 30 minutes. Capacity and the 415-opening limit reduce primary high-loss-weighted stress-demand service to 56.32 percent.
- Key readable variables or data scope: network walking time; 10- and 15-minute reachability; municipality; reachable capacity; served and unserved demand; older affected population; shelter utilization.
- What would verify it: Demand can be assigned without double-counting shelter capacity, municipality-level gaps remain interpretable under alternative walking, capacity, and facility-availability assumptions, and mesh-level maps are treated as one modeled optimum unless allocation stability is separately demonstrated.
- What would falsify or weaken it: Results would be weak if shelters or demand nodes cannot be attached reliably, cross-municipality walking is modeled unrealistically, or island and disconnected-network limitations are ignored.
- Required feasibility check: Diagnose the municipalities and components responsible for the completed primary deficits and test whether 30-minute access or higher standardized capacity materially closes them.

#### Supporting Point 4

- Role relative to central point: robustness and conditional gap response
- Research question: Which shelters and municipalities are critical under facility unavailability, and where would supplementary sites be needed if persistent local deficits remain?
- Why it matters: A nominally sufficient system can be fragile when one large facility or a concentrated group of high-pressure facilities becomes unavailable.
- Data support currently visible: Standardized capacity thresholds, pedestrian-screened network structure, and a complete general-shelter inventory support facility-unavailability and critical-shelter sensitivity. Thirty reproducible random draws at each of 10, 20, and 30 percent unavailability and pressure-targeted removal scenarios have been completed. The road-evidence audit identifies motor-vehicle restrictions but no pedestrian-passability variable, so road-edge failure is not a main estimand. Emergency evacuation sites, public facilities, schools, and parks remain conditional supplementary-site inputs only.
- Key readable variables or data scope: facility availability; single-shelter failure service loss; local unmet demand; supplementary-site eligibility and conservative added capacity.
- What would verify it: The same shelters and municipalities appear as priorities across plausible demand, capacity, walking, and facility-loss scenarios, and supplementary sites measurably reduce persistent deficits. Current pressure-targeted and single-removal results concentrate critical facilities in Uki, Uto, and Yatsushiro.
- What would falsify or weaken it: Supplementary-site analysis should be deferred if baseline prefecture-wide capacity cannot be established or no stable local deficit is found.
- Required feasibility check: If needed, expand single-removal screening beyond the 30 highest-pressure shelters; then evaluate candidate-site geometry and usable-area evidence only in deficits that remain persistent.

### Scope of Analysis

- Topics: Adequacy and robustness of the existing designated shelter system after the recent earthquake, measured through prefecture-wide demand, effective capacity, municipality heterogeneity, network accessibility, and local deficits.
- Study area: The full administrative area of Kumamoto Prefecture. Municipality and ward boundaries are reporting strata; distance from the official hypocenter is an additional exposure stratification rather than a study-area exclusion.
- Units of analysis: 125 m residential population meshes and disclosure groups as demand units; 1,315 designated shelters as capacity units; municipalities, Kumamoto City wards, epicentral-distance bands, and the prefecture as reporting units.
- Period: The first 0-72 hours after the 28 July 2026 earthquake, represented by scenarios rather than a continuous time series.
- Exclusions: Temporary housing and recovery-period accommodation; prefectures outside Kumamoto; causal impact estimation; continuous temporal reconstruction; independent re-estimation of upstream housing damage; general multi-function open-space optimization unless shelter gaps require a conditional extension.

### Study Design Declaration

- Research type: applied
- Study design: Applied empirical prefecture-wide shelter-adequacy assessment combining scenario-based demand-capacity accounting with capacity-constrained spatial accessibility and failure sensitivity.
- Interpretation limit: Results estimate sufficiency conditional on available capacity evidence, facility operability, modeled demand, walking assumptions, and the pedestrian-screened baseline network. They do not measure every evacuee, prove causal effects, identify event-specific pedestrian road failure, or imply that capacity in one municipality is substitutable for inaccessible capacity elsewhere.

## 2. Theoretical Background  /  Conceptual Framework  /  Problem Formulation

Research type: applied
Section focus: Empirical context, practical problem, and cautious interpretation limits.

### Research Gap

- Existing prefecture-wide shelter lists establish locations, while earthquake-demand estimates establish spatially uneven potential need. Neither alone shows whether the system has enough effective capacity in the municipalities affected most strongly or whether residents can reach that capacity. The applied gap is a prefecture-wide, evidence-bounded assessment that joins demand, capacity, accessibility, municipality heterogeneity, and system fragility.

### Conceptual Framework

- The earthquake creates spatially uneven shelter demand through housing loss, precautionary evacuation, and local shaking impacts. The primary event-specific benchmark is the highest available observed-use total, spatialized under three transparent residential-origin assumptions. Because complete facility capacity is unavailable, the analysis identifies the minimum standardized capacity and modeled opening set required for service; only capacity that is assumed available and network-reachable contributes to conditional effective supply.
- Analytical chain: official hypocenter and highest available observed-use stress total -> alternative population- and housing-loss-weighted spatializations -> reverse capacity and opening requirements -> pedestrian-screened accessibility and capacity assignment -> municipality and source-distance deficits -> facility failure sensitivity -> conditional supplementary-site response. Motor-vehicle restriction records remain contextual evidence rather than pedestrian-edge failures.
- Aggregate, municipal, and local adequacy are distinct. A positive prefecture-wide balance does not establish sufficiency when capacity is concentrated in Kumamoto City, separated by water or network components, or too distant from source-proximate demand.
- Scope boundary: The core analysis covers 1,156 general shelters during the first 0-72 hours; 159 welfare-specific shelters remain separate. Official facility capacity evidence calibrates thresholds but is not extrapolated as observed capacity for unsupported shelters. Open spaces enter only if persistent local gaps remain after the existing system is evaluated.

### Problem Formulation

- Let \(i\in I\) index prefecture-wide demand meshes, \(j\in J\) designated shelters, \(g\in G\) municipalities, and \(s\in S\) scenarios. Shelter demand is \(D_{is}\), and effective capacity is \(C_{js}^{eff}\).
- Prefecture-wide aggregate adequacy is

\[
R_s^{pref}=\frac{\sum_j C_{js}^{eff}}{\sum_i D_{is}}.
\]

- Let \(y_{ijs}\) be demand assigned from mesh \(i\) to shelter \(j\). Feasible assignment requires

\[
\sum_j y_{ijs}\leq D_{is},\qquad \sum_i y_{ijs}\leq C_{js}^{eff},
\]

  and \(y_{ijs}=0\) when the shelter is unreachable under the pedestrian-screened baseline network and selected walking threshold.
- Scenario-specific unmet demand is

\[
U_s=\sum_i\left(D_{is}-\sum_j y_{ijs}\right).
\]

- Municipality and source-distance summaries diagnose where prefecture-wide surplus fails to translate into local service. Cross-municipality assignment is permitted only when the network path and distance threshold make it feasible; no administrative transfer is assumed merely because capacity exists elsewhere.
- Interpretation limit: Housing-loss weights remain scenario-based. The four official prefecture-wide snapshots are observed aggregate shelter use, with the highest available value of 10,467 people at 07:30 on 30 July 2026; they contain no municipality-level origin table and therefore cannot be spatially allocated and relabeled as observed local demand. The reported count of 415 open shelters is also undifferentiated by general versus welfare-specific service class. The earlier Kumamoto City count of 2,344 remains only a local benchmark. Capacity for shelters lacking numeric or area evidence remains provisional.

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
| Capacity-Constrained Served Demand | Demand Assigned to Reachable General Shelter Capacity | service outcome | \(S_{is}=\sum_j y_{ijs}\). | Final for all three 10,467-person demand spatializations under the primary 50-person, optimistic 415-opening, 15-minute, and 4-km/h assumptions; walking, capacity, and facility-unavailability sensitivities are also complete. | yes |
| Local Unmet Shelter Demand | Demand Unserved after Access and Capacity Constraints | primary gap outcome | \(U_{is}=D_{is}-\sum_j y_{ijs}\). | Final for the high-loss-weighted primary scenario and separates lack of reachable selected capacity from aggregate prefecture-wide supply. | yes - primary scenario |

## 5. Identification Strategy

- Design principle: This is an applied partial-identification and scenario-based adequacy assessment, not a causal design and not an attempt to estimate an unobserved factual capacity for every shelter. The analysis asks what standardized capacity and opening scale would be required to serve explicit demand scenarios, then tests whether that capacity is geographically reachable.
- Demand identification: The largest available official aggregate observation, 10,467 Reported Evacuees, defines the primary event-specific stress total. It is spatialized separately using Residential Population, Housing-Loss Shelter Demand Central, and Housing-Loss Shelter Demand High. These are transparent alternative residential distributions and are never labeled as observed municipality or residential-origin counts. The unscaled low, central, and high housing-loss estimates remain contextual demand-construction evidence rather than separate primary adequacy estimands.
- Capacity identification: Standardized Capacity per General Shelter is 50 persons in the primary analysis and 25, 100, and 200 persons in sensitivity analysis. Official Numeric Capacity from 118 deduplicated general shelters is used only for plausibility calibration. Welfare-specific shelters are excluded from unrestricted general-population supply. Comprehensive facility area is not required and unsupported facility capacity is not presented as observed fact.
- Reverse-requirement contrast: Aggregate and municipality-contained calculations identify Minimum Open Shelters Required, Required Capacity if All General Shelters Open, and Critical Reverse Capacity before routing. This distinguishes an implausible capacity requirement from a shortage caused by geographic reachability.
- Access identification: Network Walking Time uses the routable road network and includes demand and shelter off-network connector distances. The primary access specification is 15 minutes at 4 km/h; 10 minutes is a strict urban-access sensitivity, 30 minutes is a rural-access extension, and 3 km/h represents mobility-constrained walking.
- Facility-selection and allocation principle: At most 415 general shelters may open in the primary scenario. This is an optimistic general-shelter budget anchored to the official undifferentiated total of open shelters, not an observed count of open general shelters. The lexicographic model first maximizes Capacity-Constrained Served Demand, then minimizes the number of open shelters, and finally minimizes total Network Walking Time. The first two primary stages are proven optimal. Because the global third-stage mixed-integer solve returned no incumbent within its time limit, walking distance is minimized exactly conditional on the stage-two optimal opening set. This produces one modeled optimal-service opening set rather than claiming to reconstruct the unknown actual open-facility list.
- Robustness identification: Capacity thresholds, demand spatialization, walking speed, time threshold, and 0, 10, 20, and 30 percent facility unavailability are varied. Random unavailability is summarized across reproducible draws; targeted loss removes high-pressure facilities first. Cross-municipality assignment is permitted only through an eligible network path within the selected time threshold.
- Road-evidence boundary: Event records identify administrative motor-vehicle restrictions and causes, but no final Section 4 variable identifies pedestrian prohibition or pedestrian impassability. Restriction-to-edge links are many-to-many spatial candidates rather than confirmed failed walking edges. Deterministic road-edge deletion is therefore excluded from the main model. Any retained appendix comparison must be labelled motor-vehicle-restriction-footprint sensitivity, show multiple match rules, and cannot be interpreted as observed pedestrian inaccessibility.
- Output connection: Prefecture Shelter Demand and General Shelter Geography establishes the input geography; Municipality Reverse Capacity and Opening Pressure and the two threshold tables establish non-network capacity requirements; Network Walking Access and Geographic Gaps separates geographic access from capacity; Capacity-Constrained Service Gaps at 50 Persons evaluates the primary adequacy claim; Threshold and Facility-Unavailability Robustness and Network Adequacy and Robustness test fragility.
- Interpretation limit: Conditional sufficiency means that modeled demand can be assigned under the stated capacity, opening, walking, and network assumptions. It does not prove that facilities were safe, staffed, supplied, unlocked, acceptable to evacuees, or among the facilities actually opened during the event. A local modeled deficit is a planning signal, not an observed count of turned-away residents. Exact served and unserved mesh cells represent one optimal allocation unless stability across alternative optima is separately demonstrated; municipality and aggregate summaries are the primary location-specific evidence.

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

### Network Walking Time

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

### Facility Selection and Capacity-Constrained Assignment

Let \(z_j\in\{0,1\}\) indicate whether general shelter \(j\) opens and let \(y_{ijscvh}\geq0\) be demand assigned from unit \(i\) to shelter \(j\). The primary scenario sets \(c=50\), \(v=4\), \(h=15\), and permits at most \(B=415\) general shelters under the optimistic observed-total-anchored opening budget. The first lexicographic stage solves

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

subject to the preceding constraints and fixed first- and second-stage optima. Capacity-Constrained Served Demand and Local Unmet Shelter Demand are

\[
S_{iscvh}=\sum_j y_{ijscvh},
\]

\[
U_{iscvh}=D_{is}-S_{iscvh}.
\]

Here, \(S_{iscvh}\) is served demand and \(U_{iscvh}\) is unserved demand in unit \(i\).

### Primary Baseline Estimate

For the high-housing-loss-weighted 10,467-person observed-use stress scenario, 15-minute walking access at 4 km/h reaches 6,286.84 persons before capacity and opening constraints. The 50-person, at-most-415-opening model serves 5,894.54 persons (56.32 percent) and leaves 4,572.46 persons unmet (43.68 percent). Maximum service and the requirement to use all 415 openings are proven optimal. Demand-weighted walking distance is 630.18 m after exact continuous distance minimization conditional on the selected stage-two optimal opening set. The global distance-minimization facility-set tie-break was time-limited and is not claimed as proven globally optimal.

Capacity-threshold sensitivity separates capacity, opening-scale, and geographic limits. With at most 415 openings, proven-optimal service is 5,894.54 persons at 50 persons per shelter, 6,004.58 at 100 persons, and 6,006.57 at 200 persons. The 25-person run returns 5,518.74 persons with a 5,530.35 upper bound and 0.21 percent MIP gap. When all 1,156 general shelters are available, exact service is 5,835.86, 6,181.05, 6,286.84, and 6,286.84 persons at 25, 50, 100, and 200 persons per shelter. Thus capacity of at least 100 persons removes capacity shortfall among geographically reachable demand only when all general shelters are available; it cannot overcome the 15-minute geographic ceiling, and the 415-opening limit remains binding even at 200 persons.

Demand-geography sensitivity holds the observed-use stress total at 10,467 and the primary 15-minute, 4-km/h, 50-person, 415-opening assumptions constant. Proven-optimal served shares are 62.60 percent for population weighting, 62.03 percent for central-housing-loss weighting, and 56.32 percent for high-housing-loss weighting. The high-loss geography is therefore the most demanding of the three because more demand lies in weak-access areas.

Walking sensitivity holds high-loss-weighted stress demand, capacity, and opening scale constant. Proven-optimal served shares are 18.84 percent at 10 minutes and 3 km/h, 38.58 percent at 15 minutes and 3 km/h, and 32.01 percent at 10 minutes and 4 km/h. At 30 minutes, time-limited feasible service reaches 77.72 percent at 3 km/h with a 0.89 percent MIP gap and 87.06 percent at 4 km/h with a 1.66 percent MIP gap. These are lower bounds, with corresponding solver upper bounds of 78.41 and 88.50 percent, and are not labeled proven optima.

General-shelter unavailability is evaluated on the primary 1-km network using 30 reproducible random draws per removal share plus a deterministic high-reachable-pressure stress test. Random removal of 10, 20, and 30 percent yields mean served shares of 54.02, 51.22, and 47.67 percent, with observed draw ranges of 53.08-54.98, 49.55-52.82, and 45.14-50.48 percent. Pressure-targeted removal produces much larger declines: served shares fall to 37.20, 19.23, and 11.51 percent. Targeted removal is a worst-case concentration diagnostic, not a probability forecast. All unavailability solutions have reported MIP gaps below 0.1 percent.

Single-shelter removal reoptimizes the remaining facility pool for the 30 highest reachable-pressure general shelters. The largest confirmed service-loss lower bounds are 47.92 persons for Toyofuku Elementary School Gymnasium in Uki, 47.91 each for Uki City Ogawa Disaster Prevention Base Center and Ogawa General Cultural Center Rapport, 47.89 for Kagami Elementary School in Yatsushiro, and 46.30 for Matsutaka Elementary School in Yatsushiro. These losses remain after replacement facility selection and are close to one full 50-person standardized capacity. The screen is not exhaustive: lower-total-pressure shelters may still be locally indispensable and require municipality-specific follow-up.

### Scenario and Failure Sensitivity

Relationship to Section 8 outputs: The demand equations support Prefecture Shelter Demand and General Shelter Geography; reverse-capacity equations support Municipality Reverse Capacity and Opening Pressure and the two capacity tables; walking equations support Network Walking Access and Geographic Gaps; the allocation and failure models support Capacity-Constrained Service Gaps at 50 Persons, Threshold and Facility-Unavailability Robustness, and Network Adequacy and Robustness.

- Demand geography: Three 10,467-person observed-use stress spatializations based on Residential Population and central or high housing-loss demand. Unscaled low, central, and high housing-loss estimates remain contextual demand-construction bounds rather than separate primary network scenarios.
- Capacity: 50 persons per open general shelter is primary; 25, 100, and 200 are sensitivity thresholds.
- Access: 15 minutes at 4 km/h is primary; 10 and 30 minutes and 3 km/h are sensitivity assumptions.
- Opening scale: all general shelters available versus an optimistic budget of at most 415 modeled general-shelter openings anchored to the official undifferentiated open-shelter total.
- Unavailability: 0, 10, 20, and 30 percent of general shelters unavailable. Reproducible random draws measure distributional sensitivity; targeted removal evaluates dependence on high-pressure shelters.
- Road evidence: The primary and sensitivity models retain the pedestrian-screened baseline graph. Administrative traffic restrictions, baseline bridge classes, and warning-zone exposure do not identify pedestrian edge failure and are not converted into deterministic closures. A motor-vehicle-restriction footprint may be reported only as a non-primary appendix matching audit without service-effect claims.
- For individual shelter \(j\), failure service loss is

\[
L_{jscvh}=U_{scvh}^{(-j)}-U_{scvh}.
\]

Here, \(U_{scvh}^{(-j)}\) is prefecture-wide unmet demand after shelter \(j\) is unavailable and \(U_{scvh}\) is baseline unmet demand under the same scenario.

## 7. Analytical Workflow

| step | variables used | formula/model used | generated figure/table title | theory or claim evaluated | support status |
|---|---|---|---|---|---|
| Separate general and welfare-specific supply and calibrate thresholds | Shelter Service Class, Official Numeric Capacity, Capacity Evidence Tier, Official Capacity Threshold Calibration | Threshold-calibration share in Section 4 | Capacity Evidence and Threshold Calibration | Whether 50 persons is a defensible stress threshold without claiming universal observed capacity | partially supported by 118 documented general shelters in three municipalities; selection limitation remains |
| Construct prefecture-wide demand scenarios | Residential Population, Housing-Loss Shelter Demand Central, Housing-Loss Shelter Demand High, Reported Evacuees, Municipality, Epicentral Distance | Demand spatialization equations in Section 6 | Prefecture Shelter Demand and General Shelter Geography | Whether the observed aggregate stress total can be tested across plausible geographies without inventing observed origins | supported as three alternative spatializations; not observed local demand |
| Estimate reverse capacity and openings | Standardized Capacity per General Shelter, Minimum Open Shelters Required, Required Capacity if All General Shelters Open, Critical Reverse Capacity | Reverse capacity and opening equations in Section 6 | Municipality Reverse Capacity and Opening Pressure; Aggregate Observed-Use and Reverse Capacity Thresholds; Municipality Shelter Opening and Capacity Pressure | Whether aggregate and municipality-contained supply can accommodate demand before network constraints | supported after correction of the concise table's prefecture-level municipality-contained totals |
| Audit and calculate geographic reachability | Network Walking Time, Residential Population, Municipality, Shelter Location, Shelter Service Class | Shortest-path, walking-time, and accessibility equations in Section 6 | Network Walking Access and Geographic Gaps | Whether demand can reach at least one general shelter under urban, primary, rural, and mobility-constrained assumptions | supported for current network: 67.2 percent of population and 60.1 percent of high-loss-weighted stress demand are within the primary threshold |
| Select facilities and allocate demand at the primary threshold | Standardized Capacity per General Shelter, Scenario-Available General Shelter Capacity, Capacity-Constrained Served Demand, Local Unmet Shelter Demand, Network Walking Time, Municipality | Three-stage maximum-service, minimum-opening, minimum-walking allocation in Section 6 | Capacity-Constrained Service Gaps at 50 Persons; Network Adequacy and Robustness | Whether an optimistic budget of at most 415 modeled general-shelter openings at 50 persons can serve spatial demand and which municipalities retain the greatest gaps | completed for three demand spatializations; high-loss-weighted primary scenario serves 56.32 percent and leaves 43.68 percent unmet; mesh map represents one modeled optimum |
| Test threshold, access, and facility-loss robustness | Standardized Capacity per General Shelter, Scenario-Available General Shelter Capacity, Capacity-Constrained Served Demand, Local Unmet Shelter Demand, Shelter Location | Scenario grid and failure-loss equation in Section 6 | Threshold and Facility-Unavailability Robustness; Network Adequacy and Robustness | Whether the adequacy conclusion survives lower capacity, slower walking, tighter thresholds, and facility unavailability | capacity, opening-scale, demand-geography, walking, general-shelter-unavailability, and 30 high-pressure single-removal sensitivities completed; exhaustive lower-pressure local-criticality checks remain |
| Audit road-disruption evidence boundary | No pedestrian-impassability variable adopted in Section 4 | Evidence-suitability and spatial-match sensitivity audit; no deterministic edge deletion | No main Section 8 output; optional appendix context only | Whether administrative traffic restrictions can identify failed pedestrian paths | not supported for pedestrian-edge failure; motor-vehicle restrictions cannot be relabelled as observed walking inaccessibility |
| Decide whether supplementary sites are needed | Local Unmet Shelter Demand, Network Walking Time, Municipality | Conditional rule: consider supplementary sites only for deficits persistent under the primary and plausible sensitivity scenarios | No supplementary-site output unless a persistent geographic or capacity gap is established | Whether extra open spaces are necessary rather than assumed in advance | baseline gaps established; defer site expansion until threshold and unavailability robustness is complete |

## 8. Figure and Table Plan

### Figures

| title | what it expresses | figure type | subpanels | key variables | status |
|---|---|---|---:|---|---|
| Prefecture Shelter Demand and General Shelter Geography | Locates prefecture-wide housing-loss demand, the three 10,467-person observed-use stress spatializations, all general shelters, welfare-specific shelters, municipalities, and the official hypocenter without treating modeled local demand as observed use. | map | 4 | Housing-Loss Shelter Demand High, Reported Evacuees, Residential Population, Municipality, Epicentral Distance, Shelter Location, Shelter Service Class | done |
| Municipality Reverse Capacity and Opening Pressure | Shows the average capacity required if every local general shelter opens and the minimum number that must open under the 50-person primary threshold, highlighting source-proximate pressure. | map and bar | 3 | Municipality, Minimum Open Shelters Required, Required Capacity if All General Shelters Open, Critical Reverse Capacity, Standardized Capacity per General Shelter | done |
| Network Walking Access and Geographic Gaps | Identifies demand units that can reach at least one general shelter within 10, 15, or 30 minutes at 4 km/h and within the mobility-constrained 3 km/h sensitivity. | map | 4 | Network Walking Time, Residential Population, Municipality, Shelter Location, Shelter Service Class | done |
| Capacity-Constrained Service Gaps at 50 Persons | Maps served and unserved demand after jointly enforcing network reachability and 50-person capacity for population-, central-loss-, and high-loss-weighted observed-use stress scenarios. | map | 3 | Standardized Capacity per General Shelter, Capacity-Constrained Served Demand, Local Unmet Shelter Demand, Municipality, Shelter Location | done |
| Threshold and Facility-Unavailability Robustness | Compares unmet demand under 25, 50, 100, and 200 persons per shelter and 0, 10, 20, and 30 percent general-shelter unavailability, and identifies shelters whose loss is most consequential. | line, bar, and map | 4 | Standardized Capacity per General Shelter, Scenario-Available General Shelter Capacity, Capacity-Constrained Served Demand, Local Unmet Shelter Demand, Shelter Location | done |

### Tables

| title | what it expresses | rows | columns | row meaning | column meaning | status |
|---|---|---:|---:|---|---|---|
| Capacity Evidence and Threshold Calibration | Documents shelter service class, numeric-capacity evidence, source coverage, and the share of documented general shelters meeting each standardized capacity threshold. | 12 | 10 | One evidence tier, municipality calibration group, or capacity threshold | Shelter counts, service class, official capacity distribution, threshold coverage, source limitation, and interpretation | done |
| Aggregate Observed-Use and Reverse Capacity Thresholds | Compares the four official event-use snapshots with 25-, 50-, 100-, and 200-person capacity thresholds and reports the reverse critical capacity at the 415-open-shelter scale. | 20 | 11 | One snapshot-threshold or spatialization-critical-capacity combination | Observation, evacuees, open shelters, threshold capacity, surplus or shortfall, minimum openings, and interpretation | done |
| Municipality Shelter Opening and Capacity Pressure | Provides a concise paper-facing summary of prefecture-wide municipality-contained opening requirements and the ten municipalities with the greatest pre-network capacity pressure; complete 45-municipality results remain supporting analytical data. | 14 | 12 | One prefecture scenario summary or one high-pressure municipality | Population, demand, shelters, required capacity, municipality-contained minimum openings, feasibility, source proximity, and pressure rank | done |
| Network Adequacy and Robustness | Provides a concise paper-facing summary of primary and sensitivity results, selected high-unmet-demand municipalities, and the most consequential screened shelter removals. | 24 | 14 | One network scenario, selected municipality summary, or selected critical shelter | Scenario assumptions, coverage, served demand, unmet demand, municipality gap evidence, failure loss, and solution interpretation | done |

Interpretation warning: The primary scenario, three observed-use stress spatializations, capacity thresholds, walking thresholds, general-shelter unavailability scenarios, and single-site failures among the 30 highest-pressure shelters are complete. Road evidence represents motor-vehicle restrictions and does not support deleting pedestrian edges in the main model. Lower-pressure facilities may still be locally critical, and the results do not represent every real road and facility state.
