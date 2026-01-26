# Performance Testing (Task III)

Performance- und Lasttests werden mit k6 durchgeführt, um das Verhalten der Tracking-API unter realistischen und 
erhöhten Lastbedingungen zu bewerten.

Der Fokus liegt auf:
- Durchsatz (Requests pro Sekunde)

- Antwortzeit-Perzentilen (p90 / p95)

- technischer Stabilität (Netzwerkfehler und serverseitige Fehler)

Funktionale 4xx-Antworten (z. B. unbekannte oder ungültige Trackingnummern) gelten als erwartetes Verhalten und werden nicht als technische Fehler gewertet.

## Tooling

k6 – skriptbasiertes, CLI-getriebenes Performance-Test-Tool

k6 wurde gewählt, da es:
- reproduzierbare, versionierbare Performance-Tests ermöglicht
- flexible Lastmodelle unterstützt
- funktionale und technische Fehler klar trennt
- einfach in CI-Pipelines integrierbar ist

## Scope

API under test

GET https://tracking.bosta.co/shipments/track/:trackingNumber

Workload-Charakteristik
- gemischter Input (valid-ähnliche und invalid-ähnliche Trackingnummern)
- konfigurierbares Verhältnis über Environment-Variablen
- konstantes Arrival-Rate-Lastmodell

UI-Performance-Tests wurden aufgrund der Browser-Limitationen von k6 nicht automatisiert.

## Load Profiles

Im k6-Skript sind mehrere Lastprofile definiert, die über Environment-Variablen auswählbar sind:

Profile	Description
- smoke:	Baseline verification and script validation
- load:	    Steady-state performance under realistic load
- stress:	Gradual ramp-up to identify limits
- spike:	Sudden traffic increase and recovery
- soak:	    Long-running stability test

Für dieses Assessment wurden die Profile smoke und load ausgeführt.

## Execution
- Smoke test (baseline)
````
k6 run -e PROFILE=smoke -e VALID_RATIO=1 k6/tracking_api_perf.js
````
Mit zusätzlichem Rohdaten-Export für Visualisierungen:
````
k6 run -e PROFILE=smoke -e VALID_RATIO=1 k6/tracking_api_perf.js --out json=artifacts\load_raw.json
````


- Load test (steady-state)
````
k6 run -e PROFILE=load -e VALID_RATIO=0.8 k6/tracking_api_perf.js
````

Mit zusätzlichem Rohdaten-Export für Visualisierungen:
````
k6 run -e PROFILE=load -e VALID_RATIO=0.8 k6/tracking_api_perf.js --out json=artifacts/load_raw.json
````

## Metrics & Thresholds

Zur Vermeidung von False Positives durch erwartete 4xx-Antworten wird eine eigene technische Fehler-Metrik verwendet.

Technische Fehler:
- network / timeout errors
- HTTP 5xx responses

Definierte Schwellenwerte:
- technische Fehlerquote < 1 %
- p95 latency < 300 ms
- p99 latency < 800 ms

Bei Überschreitung schlägt der Testlauf automatisch fehl.

## Performance Test Results

### Smoke Test (Baseline)

#### Ergebnisse
- Durchsatz: ~2,0 Requests/Sekunde
- Technische Fehlerquote: 0
- Latenz:
→ p95: ~178 ms

**Interpretation**

Der Smoke-Test bestätigt die korrekte Funktion des Scripts sowie eine gute Baseline-Performance.
Es traten keine technischen Fehler auf, und die Latenz blieb deutlich unter den definierten SLA-Grenzen.

**Findings – Rate Limiting & Latency**

Der Latenz-Graph zeigt über den gesamten Test hinweg stabile p95-Antwortzeiten mit einem einzelnen,
kurzzeitigen Ausreißer. Dieser korreliert mit HTTP-429-Antworten und ist auf Rate Limiting
zurückzuführen, nicht auf eine systemische Performance-Verschlechterung.

Die Statuscode-Verteilung zeigt überwiegend HTTP-429-Antworten, was für einen öffentlichen
Tracking-Endpoint erwartetes und gewünschtes Verhalten darstellt.

### Load Test (Steady-State)

#### Ergebnisse
* Durchsatz: ~19,96 Requests/Sekunde (Ziel: 20 RPS)
* Technische Fehlerquote: 0
* Latenz:
  - p90: ~66,8 ms
  - p95: ~87,7 ms

**Interpretation**

Unter konstanter Last wurde der Ziel-Durchsatz zuverlässig erreicht.
Die Latenz blieb stabil und deutlich unterhalb der SLA-Grenzen, was auf ausreichende Performance-Reserven hinweist.

Während des Load-Tests blieben die p95-Antwortzeiten im Bereich von 60–90 ms.
Kurzzeitige Peaks korrelieren mit HTTP-429-Antworten und sind auf aktives Rate Limiting
statt auf Backend-Engpässe zurückzuführen.

Die RPS-Kurve zeigt im Mittel einen stabilen Durchsatz mit kurzen Drops und Bursts,
verursacht durch Throttling und das verwendete Constant-Arrival-Rate-Modell.

### Gesamtbewertung
Über alle ausgeführten Profile hinweg zeigte die Tracking-API:
- stabilen Durchsatz
- niedrige und konsistente Latenz
- keine technischen Fehler
- saubere Skalierung von Baseline- zu Steady-State-Last

Alle definierten Performance- und Stabilitätskriterien wurden erfüllt.

### Hinweise & Einschränkungen
- Die Tests wurden gegen eine öffentliche API ausgeführt; Ergebnisse können netzwerkabhängig variieren.
- Serverseitige Metriken (CPU, RAM) standen nicht zur Verfügung.
- Weitere Profile (stress, spike, soak) sind implementiert, wurden jedoch aus Zeit- und Umfangsgründen nicht ausgeführt.

##### UI-Performance-Überlegungen

UI-Performance-Tests für die DemoBlaze-Flows (UC1: Browse, UC2: Add-to-Cart, UC3: Checkout)
wurden im Rahmen dieses Assessments nicht automatisiert.

Begründung:
- Browserbasierte UI-Lasttests sind deutlich komplexer und erfordern umfangreiche Infrastruktur (z. B. Selenium/Playwright-Grids, Session-Isolation).
- Tools wie k6 sind nicht für browserbasierte UI-Performance-Tests ausgelegt.
- DemoBlaze ist ein öffentliches Demo-System mit eingeschränkten Stabilitätsgarantien.

Stattdessen wurde die UI-Performance konzeptionell bewertet:
- Identifizierte UI-SLAs:
  - „Add to Cart“ p95 < 2,0 s
  - „Checkout“ p95 < 3,0 s

- In produktiven Umgebungen würde UI-Performance typischerweise über folgende Ansätze gemessen:
  - Synthetic Monitoring (Single-User-Transaktionen)
  - Frontend-Performance-Metriken (LCP, TTI, TBT)
  - Korrelation mit API-Performance und Server-Metriken


### Artifacts

Performance test artifacts are stored under:

```text
artifacts/k6
├─ k6_summary_smoke.json
├─ k6_summary_load.json
├─ smoke_raw.json
├─ load_raw.json
└─ *.png (optional graphs)

````

