# FDT reference use case — Time-to-groin in acute ischaemic stroke care (Netherlands)

| | |
|---|---|
| **Status** | Working draft v0.2 — reference case for the FAIR Data Train itinerary patterns (P4 discovery chain; also P9 recurring, cross-domain). Decisions of 11 Sep 2026: the two-hour figure is dropped in favour of the official component norms; real stakeholders are not involved directly for now (fictional stations); the GP / huisartsenpost hop is included as an optional final hop |
| **Date** | 11 September 2026 |
| **Purpose** | Ground the case stated by Luiz Olavo in official Dutch guidelines, quality standards, registries and law, so that the architectural analysis rests on what the Dutch care chain actually records, who holds it and under which legal basis it may be used |
| **Provenance** | Facts below were located on 11 Sep 2026 in the cited documents; quotations are the Dutch originals. Where a document could not be opened or a claim could not be verified, this is stated (Section 8). Legal texts were partly read from mirror sites and should be checked against the Staatsblad / wetten.overheid.nl before formal citation |

## 1. The case in one paragraph

Endovascular thrombectomy (EVT, in Dutch practice long called *intra-arteriële trombectomie*, IAT) removes the clot in a large-vessel ischaemic stroke via a catheter inserted through the femoral artery in the groin. Benefit falls steeply with time: the Zorginstituut's 2016 assessment cites "een uur vertraging in tijd vanaf symptomen tot reperfusie geassocieerd met 6,7% lagere absolute kans op functioneel onafhankelijke uitkomst" [ZIN 2016]. The interval **symptom onset → groin puncture** ("onset-to-groin") therefore summarises the performance of the whole acute chain: the person or bystander noticing symptoms, the dispatch centre (meldkamer ambulancezorg, MKA), the ambulance service (regionale ambulancevoorziening, RAV), a first (primary) stroke centre that gives intravenous thrombolysis and CT-angiography, transfer to one of the EVT centres, and the intervention itself. No single organisation holds all the time stamps, and the route a given patient took is only known from the records of the organisations involved. Computing the metric for a population is thus a **multi-hop, discovery-driven, cross-sector** analysis — exactly the P4 pattern of the itinerary catalogue.

## 2. What the official documents say about time

### 2.1 Clinical guideline (NVN/FMS, *Richtlijn Herseninfarct en hersenbloeding*, modules 2024; guideline last updated 24 Mar 2026)

- **EVT 0–6 h**: patients with a proven distal ICA / M1 / M2 occlusion "dienen endovasculair te worden behandeld … ongeacht de ernst van de neurologische uitval"; "Als de patiënt binnen zes uur kan worden behandeld is geen verdere diagnostiek nodig" [Richtlijn, module EVT vroege tijdsvenster].
- **EVT 6–24 h**: treat "tussen 6-24 uur na het ontstaan van de verschijnselen middels EVT" subject to imaging-based selection (collateral flow on CTA, perfusion mismatch on CTP), with the window counted from onset or *laatst goed gezien* (last known well) [Richtlijn, module EVT late tijdsvenster].
- **Chain organisation**: the dispatch centre sends an A1 ambulance for a positive FAST test within 24 h of onset; the ambulance presents the patient at a hospital with stroke unit and thrombolysis facility; the guideline's default is **drip-and-ship** ("Als in het dichtbijzijnde ziekenhuis een intracraniële arteriële occlusie wordt aangetoond, wordt de patiënt met spoed (A1-urgentie) naar een interventiecentrum met EVT faciliteiten vervoerd"), and it finds "onvoldoende bewijs om patiënten direct naar een interventiecentrum … te vervoeren ('mothership')" [Richtlijn, module Acute opvang].
- The only numeric in-hospital target in the guideline text is for thrombolysis: "deze behandeling binnen 30 minuten na binnenkomst in het ziekenhuis te starten". **The guideline sets no door-to-groin, door-in-door-out or onset-to-groin target**; those live in the professional quality criteria and the indicator set below.

### 2.2 Quality criteria for EVT centres and stroke centres (NVvR/NVN, adopted 4 Feb / 16 Dec 2021)

- "Een EVT-centrum verricht per jaar ten minste 50 EVT-procedures."; "Een EVT-interventionalist verricht per jaar ten minste 20 EVT-procedures".
- "Mediane door-to-groin-tijd < 30 minuten voor patiënten die verwezen zijn vanuit een primair (IVT) CVA-centrum."
- "Mediane door-to-groin-tijd < 75 minuten voor patiënten die zich direct in een EVT-centrum presenteren."
- 24/7 availability of EVT and of CT-perfusion or MRI.
- Registration duty: "ten minste registratie van door-to-groin tijd, **onset to groin tijd**, TICI score, mRS na 3 maanden, complicaties" — onset-to-groin **must be registered by every EVT centre, but no target value is set for it** [Kwaliteitscriteria EVT-centrum 2021].
- Stroke centres: "Mediane deur-tot-naald-tijd < 45 minuten"; at least 100 acute stroke patients per year; a centre without EVT "moet regionale afspraken hebben met een EVT behandelcentrum en met de regionale ambulancedienst (RAV) over snelle verwijzing" [Kwaliteitsnormen Acute Beroertezorg 2021/2022].
- Earlier national standard (Kwaliteitsstandaard Acuut Herseninfarct, ZIN register 2017): ≥ 50 IAT per centre per year; median door(IAT centre)-to-groin < 60 min — still found in several regional ROAZ protocols [ZIN Tussenrapportage 2017; Regioprotocol Acute Zorgregio Oost 2019; BRAIN-RACE Regio West 2021].

### 2.3 Ambulance care (Ambulancezorg Nederland, Kwaliteitskader Ambulancezorg 2.0, June 2024; ZIN register 2 Oct 2024)

- Response: "Binnen 15 minuten is 95% van de A1-inzetten ter plaatse."
- Stroke throughput signal (signaal 4, *CVA-doorlooptijd*): the percentage of A1 patients with suspected stroke possibly eligible for IVT/EVT "waarbij de patiënt binnen 45 minuten na melding MKA is aangeleverd bij een acuut beroerte/EVT-centrum"; **streefwaarde 80 %, minimale waarde 70 %**. Sector result 2024: 67 % [Sectorkompas Ambulancezorg 2024].
- The national protocol (LPA-HC, formerly LPA 9, 2023) uses FAST; the RACE scale for large-vessel occlusion is used only in regional pilots [AZN vakblad 2022].
- Ambulance records carry the times *meldtijd, uitruktijd, rijtijd, behandeltijd, vervoertijd, overdrachttijd* per ride [Sectorkompas 2024].

### 2.4 National quality indicators and the DASA registry

- The Zorginstituut *Transparantiekalender* indicator set **Beroertezorg (voorheen CVA)**, verslagjaar 2026, contains among others: "4 Mediane begin-tot-deur tijd", "5b Mediane deur-tot-naald tijd", "6b Mediane deur-tot-lies tijd … uitgesplitst voor verwezen en niet-verwezen patiënten", "7 Mediane deur-in-deur-uit tijd in het verwijzend centrum" [Zorginzicht, Beroertezorg 2026].
- Definitions (Indicatorengids DASA 2025): "Begin: tijdstip van ontstaan klachten en/of symptomen van het herseninfarct; deur: tijdstip van presentatie op de spoedeisende hulp"; "lies: tijdstip van aanprikken van de lies voor start endovasculaire trombectomie"; a *verwezen patiënt* is one referred by another centre; for referred patients the 2024 gids defines deur(1) at the referring centre and deur(2) at the intervention centre.
- The **Dutch Acute Stroke Audit (DASA)**, run by DICA (data processor MRDM) since 2016 on the initiative of the NVN, is mandatory because its indicators are on the Transparantiekalender; 68 hospitals, 33 736 patients registered in 2023. Benchmarks: median door-to-groin fell from 87 min (2014) to 48 min (2023) and 47 min (2026 press); median door-to-door-to-groin for referred patients 117 min (2023); median begin-tot-deur 150 min (IQR 68–557) in 2023 [DICA; Hart & Vaatcijfers; Kennisnetwerk CVA 2026].

### 2.5 Is there an official "under two hours" onset-to-groin target?

**Not in any official document found.** Searched: the guideline, the ZIN standpunt (2016) and kwaliteitsstandaard (2017), the NVN/NVvR criteria (2021), the DASA indicator guides (2023–2026), the Kwaliteitskader Ambulancezorg 1.0/2.0, the Kwaliteitskader Spoedzorgketen, Hersenstichting and Hartstichting pages, and VWS letters to parliament. What the documents contain are eligibility windows (6 h / 24 h), in-hospital process norms (door-to-needle, door-to-groin), a prehospital norm (45 min call-to-centre) and the duty to register onset-to-groin. The "two hours" figure may be a reasonable *chain* expectation (≈ 45 min prehospital + ≈ 45 min at the primary centre + ≤ 30 min at the EVT centre) or may stem from regional ambitions or international benchmarks, but it should not be attributed to Dutch regulation in FDT material. **Decision (Luiz, 11 Sep 2026): the two-hour figure is dropped.** The use case computes the onset-to-groin distribution and its components across the chain and benchmarks them against the official component norms above.

## 3. Who holds which time stamps

| Time point (DASA/AZN term) | Recorded by | Where it lives today | Notes |
|---|---|---|---|
| Symptom onset / last seen well (*begin*) | Patient, bystander, GP, ambulance crew, ED | Ambulance ride record (free text / field), hospital EHR, DASA (*begin*) | Often estimated; the DASA gidsen read do not define handling of unknown onset (not verified) |
| Call to dispatch (*melding MKA*) | Meldkamer / RAV | RAV ride-registration system (four different systems across 25 RAVs) | Basis of the 45-min ambulance norm |
| On scene, departure, hand-over (*ter plaatse, vertrek, overdracht*) | RAV | RAV ride record; aggregated only in Sectorkompas | No national patient-level ambulance database (Nivel/AZN 2019) |
| Door primary centre (*deur(1)*), CT/CTA time, needle (*naald*), door-out | Primary stroke centre | Hospital EHR; DASA (deur, naald, deur-in-deur-uit) | Indicator 7 (DIDO) on the 2026 set; mandatory status not confirmed |
| Door EVT centre (*deur(2)*) | EVT centre | Hospital EHR; DASA | ~17 EVT centres (last official count 2018) |
| Groin puncture (*lies*), recanalisation (TICI) | EVT centre | Hospital EHR / intervention log; DASA (lies); TICI per EVT criteria | TICI not in the Transparantiekalender set |
| Which ambulance service / which referring hospital | EVT centre (referral letter, transport record) | Hospital EHR; ambulance record | The **routing information** that makes the discovery chain possible |

Two consequences for the FDT case. First, **DASA already assembles the hospital-side intervals for the whole country**, so a single-station query against a DASA-like registry answers begin-to-door and door-to-groin; the FDT itinerary adds value for the **prehospital** part (ambulance time stamps and place of pick-up) and for **per-region, per-route drill-down** that a national registry does not expose. Second, the ambulance side is genuinely federated: 25 RAVs, several registration systems, no national patient-level store — a natural fit for stations at RAVs (or at the regional ROAZ level), visited only when a patient's record points to them.

## 4. The FDT itinerary for this case (P4 discovery chain, cross-domain)

1. **Plan**: the train owner (e.g. a regional stroke network or a Kennisnetwerk CVA working group) parametrises a *time-to-groin* train with a period, a region (ROAZ) and the component norms to benchmark against; the plan names only the **entry stations** (EVT centres in the region). The itinerary map shows those stations and marks further hops as "to be discovered".
2. **Hop 1 — EVT centre station**: per EVT patient in the period: groin time, door(2) time, referral status, referring hospital, ambulance service that delivered the patient, and a linkage key (Section 5). Result inspection at the station: the train may carry onward only the linkage keys and the identifiers of the next stations, not clinical data (P4 "state travelling onward" as a policy object).
3. **Hop 2a — referring primary stroke centre station** (if referred): door(1), CTA and needle times, door-out time.
4. **Hop 2b — RAV station** (one per ambulance service involved): melding, ter plaatse, vertrek, overdracht times and pick-up location for the same patient. Because each RAV is a different organisation, this hop is discovered per patient (the tree structure of P4).
5. **Hop 3 — onset determination (optional final hop, decided 11 Sep 2026)**: if onset is unknown in the hospital and ambulance records, the train visits a GP / huisartsenpost station (primary care — a third sector) for the last-known-well time; the chain ends when onset is found or the budget is exhausted. This is what makes the chain open-ended and the strongest demonstration of P4.
6. **Merge and deliver**: the orchestrator (Train Handler, or an orchestrator station of the regional network) assembles per-patient intervals, computes distributions per component (call-to-centre vs 45-min norm, door-to-needle vs 45-min norm, door-to-groin vs 30/75-min norms, door-in-door-out, onset-to-groin) and per route (mothership vs drip-and-ship), and delivers **aggregates only**, with disclosure control as an ODRL duty at every station's result inspection.
7. **Recurring** (P9): the same plan re-runs per quarter for regional quality improvement; the replay view shows how the route mix and the intervals change over time.

Coordination: query/API trains at hospital stations (FHIR or SQL over the EHR/registry extract) require **orchestration**; a container train with the routing algorithm embedded could realise the same chain by **choreography** if RAV and hospital stations allow forwarding — the case supports evaluating both (ADR-013).

Cross-domain character: hospitals (medisch-specialistische zorg, NVN/NVvR standards, DASA/DICA vocabulary, FHIR) and ambulance care (AZN standards, LPA, ride-registration vocabularies, Sectorkompas) are different sectors with different governance, systems and terminologies; the join keys are the patient (via pseudonym) and place/time. This is the "cross-domain interoperability" argument in a real, regulated setting.

## 5. Legal basis and linkage (as documented)

- **Medical confidentiality**: BW 7:457 (WGBO) forbids disclosure without consent; 7:458 allows disclosure for "statistiek of wetenschappelijk onderzoek op het gebied van de volksgezondheid" without consent under conditions (asking consent not reasonably possible, or data "in zodanige vorm … dat herleiding tot individuele natuurlijke personen redelijkerwijs wordt voorkomen"; general interest; not possible without the data; no objection by the patient; annotation in the record). UAVG art. 24 gives the corresponding exception to the Art. 9 GDPR ban for research/statistics.
- **BSN**: under the Wabvpz every *zorgaanbieder* in the Wkkgz sense — hospitals and RAVs alike — records the BSN (art. 8) to ensure data relate to the right client (art. 4); the Wabvpz itself gives no basis for secondary-use linkage.
- **Quality registries**: the *Wet kwaliteitsregistraties zorg* (Stb. 2025, 391; in force 1 Jan 2026; opt-out regime from 1 Jan 2027) creates a legal basis for registries entered in the Zorginstituut register (art. 11k ff. Wkkgz as amended), with **pseudonymisation at the source** and delivery of the BSN "ten behoeve van een in het register … opgenomen kwaliteitsregistratie" (art. 30b). Its scope is *medisch-specialistische zorg* designated by ministerial regulation — **whether ambulance care falls inside is not verified and appears unlikely**, which is precisely the gap an FDT chain would have to bridge with its own agreements.
- **Pseudonymisation in practice**: DICA/MRDM registries (including DASA) use **ZorgTTP** as an independent pseudonymisation service producing irreversible pseudonyms from BSN or name/date of birth/sex, with deterministic and probabilistic linking; the Nivel/AZN 2019 feasibility study found linking RAV ride data to GP data via ZorgTTP "juridisch te onderbouwen en technisch haalbaar". No national instrument specifically authorising hospital–ambulance linkage for stroke was found.
- **EHDS (Regulation (EU) 2025/327)**: in force 26 March 2025; the Netherlands intends a single body, the *Gezondheidsdata-autoriteit*, combining the access-body and digital-health-authority tasks; secondary-use obligations for the first data categories apply from 26 March 2029 (Chapter IV), with patient opt-out. Under Art. 73 access under a data permit is only through a **secure processing environment** (named persons, unique identities, logs kept ≥ 1 year, download only of non-personal data after review) — the FDT station's checkpoints map directly onto these duties (see `fdt-data-space-alignment.md`).

Architectural consequence: the linkage step is a first-class hop or service (a TTP/pseudonymisation element), the agreement at each station must reference the applicable basis (7:458 research disclosure, Wkz registry basis, or — from 2029 — an EHDS data permit), and every station must be able to prove that only aggregates left it.

## 6. What the case demonstrates for FDT

P4 discovery chain with per-record branching; state travelling onward as a policy object distinct from delivered results; a linkage/TTP hop; agreements under different legal bases in one run; cross-sector vocabularies (DASA vs AZN) and identity federations; recurring runs with replay; and, from 2029, alignment with EHDS secure-processing-environment duties. It is also honest about scope: part of the answer already exists in DASA, so the FDT contribution is the prehospital extension and the regional, route-level insight — a good test of whether data visiting adds value where a central registry exists.

## 7. Sample data for mock-ups (fictional)

Stations are **fictional** (decision of 11 Sep 2026: real stakeholders are not involved directly for now; real-world cases will be used when they come online): e.g. "Noorderlicht MC (EVT centre)", "Zuiderlicht Ziekenhuis (primary stroke centre)", "Regio Oost Ambulancezorg station", "Huisartsenpost Oost station", "Linkage station (TTP)". Official documents are cited for norms and data structures only, not as case actors. Times: use the official medians as realistic sample values (door-to-groin ≈ 47 min; door-to-door-to-groin ≈ 117 min; begin-to-door ≈ 150 min; call-to-centre ≤ 45 min in ~67 % of rides).

## 8. Verified, not found, to be checked with Luiz

**Verified (document + URL in Section 9)**: guideline EVT windows and chain organisation; EVT-centre and stroke-centre norms (50/20; DTG < 30/< 75; DTN < 45; 100/yr); ambulance A1 15 min and CVA 45-min signal with 80 % target and 2024 result 67 %; Transparantiekalender indicators 4, 5b, 6b, 7 and DASA definitions; DASA benchmarks; ZIN 2016 standpunt and 2017 standard; WGBO 7:457/458, UAVG 24, Wabvpz 4/8, Wkz dates and articles; ZorgTTP role; EHDS dates and Dutch implementation letters.

**Not found**: any official "< 2 h onset-to-groin" target; numeric DTG/DIDO targets in the guideline itself; the 2026 indicator-gids PDF (server error) and hence the mandatory status of indicator 7; the DASA data dictionary (ambulance fields, TICI); the rule for unknown onset; a current official list/count of EVT centres (last official: 17, ZIN 2018); whether the Wkz ministerial regulation covers ambulance care; the full LPA-HC stroke protocol text.

**Decided with Luiz (11 Sep 2026)**: the two-hour figure is dropped; no real stakeholders are involved directly for now (a ROAZ region, DASA/DICA or Kennisnetwerk CVA may be approached when a real-world case comes online); the GP / huisartsenpost hop is included as an optional final hop.

## 9. Sources

1. Richtlijn Herseninfarct en hersenbloeding (NVN/FMS), modules "Acute opvang", "Endovasculaire trombectomie anterieure circulatie, vroege tijdsvenster (0-6 uur)", "… late tijdsvenster (6-24 uur)" (publ. 26-09-2024; guideline updated 24-03-2026) — https://richtlijnendatabase.nl/richtlijn/herseninfarct_en_hersenbloeding/
2. Kwaliteitscriteria EVT-centrum, NVvR (AV 4-2-2021) / NVN (ALV 16-12-2021) — https://www.neurologie.nl/wp-content/uploads/2022/03/Kwaliteitscriteria-EVT-centrum_2021.pdf
3. Kwaliteitsnormen Acute Beroertezorg, NVvR/NVN (2021/2022) — https://www.neurologie.nl/wp-content/uploads/2022/03/Kwaliteitsnormen-Acute-Beroertezorg-NVvR_NVN_2022-002.pdf
4. Zorginstituut Nederland, Standpunt Intra-arteriële behandeling (IAT) van het acute herseninfarct (21-12-2016); Tussenrapportage implementatie kwaliteitsstandaard Acuut Herseninfarct (11-10-2017); nieuwsbericht "Invoering kwaliteitsstandaard acuut herseninfarct succesvol" (03-09-2018) — https://www.zorginstituutnederland.nl/
5. Zorginzicht / Transparantiekalender, indicatorenset Beroertezorg (voorheen CVA), verslagjaar 2026 (gids 20-08-2026) and Indicatorengids Beroerte (CVA) – DASA verslagjaar 2025 (versie 2025.1) and 2024 — https://www.zorginzicht.nl/kwaliteitsinstrumenten/cerebro-vasculair-accident-cva
6. DICA, Beroertezorg – DASA — https://dica.nl/registratie/beroertezorg-dasa/ ; Hartstichting Hart & Vaatcijfers, Jaarcijfers acuut herseninfarct 2018-2023 — https://www.hartenvaatcijfers.nl/ ; Kennisnetwerk CVA, "Grotere kans op herstel na beroerte door snellere behandeling" (03-06-2026)
7. Ambulancezorg Nederland, Kwaliteitskader Ambulancezorg 2.0 (juni 2024; ZIN register 02-10-2024) — https://www.zorginzicht.nl/ ; Sectorkompas Ambulancezorg 2024 (aug 2025); Landelijk Protocol Ambulancezorg Hoogcomplex — https://www.ambulancezorg.nl/
8. Regional protocols: Acute Zorg Euregio, Regionale procedure acute beroertezorg AZE.CVA.01 v5.0 (21-11-2023); Acute Zorgregio Oost, Regioprotocol acute beroertezorg (2019); Regio West, BRAIN-RACE v1.2 (2021)
9. Nivel/AZN, Naar een lerend zorgsysteem voor de ambulancezorg — haalbaarheidsstudie (juni 2019) — https://www.nivel.nl/
10. Burgerlijk Wetboek Boek 7, art. 457–458 (WGBO); UAVG art. 24; Wet aanvullende bepalingen verwerking persoonsgegevens in de zorg (Wabvpz) art. 4, 8, 15a; Wet kwaliteitsregistraties zorg (Stb. 2025, 391; Stb. 2025, 399) — https://wetten.overheid.nl/ ; Eerste Kamer dossier 36.278
11. ZorgTTP, Historie pseudonimisering — https://www.zorgttp.nl/historie_pseudonimisering/ ; DICA, Nieuwe wetgeving Wkkgz — https://dica.nl/thema/nieuwe-wetgeving-wkkgz/
12. Regulation (EU) 2025/327 (EHDS), arts. 2, 51, 57, 60, 61, 66, 68, 73, 75, 77, 105; VWS Kamerbrieven stand van zaken implementatie EHDS (07-04-2025, 20-01-2026, 18/20-05-2026) — https://www.datavoorgezondheid.nl/
