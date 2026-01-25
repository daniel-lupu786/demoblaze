# Security Findings – Task II  
## Lightweight Security Assessment (Tracking API)

This document provides a lightweight security assessment of the Tracking API used in Task II.
The goal is not to perform intrusive security testing, but to identify common risks relevant
to the API usage context and propose pragmatic mitigations.

---

## Scope

**API under test**
GET https://tracking.bosta.co/shipments/track/:trackingNumber


**Assessment focus**
- input handling and validation
- abuse prevention
- observability and monitoring
- client-side security considerations

No authentication or authorization mechanisms were tested, as the endpoint is intended
to be publicly accessible for shipment tracking.

---

## 1. Input Validation

### Observations
- The API accepts the `trackingNumber` as a path parameter.
- Invalid or malformed inputs (e.g. special characters, overly long values) generally result
  in `4xx` responses.
- No server-side errors (`5xx`) were observed during invalid input testing.

### Risks
- Insufficient input validation could lead to:
  - injection vulnerabilities (depending on backend implementation)
  - unnecessary backend processing
  - inconsistent error handling

### Recommendations
- Enforce strict allowlists for `trackingNumber`:
  - numeric characters only
  - defined minimum and maximum length
- Reject malformed inputs early in the request lifecycle.
- Return consistent and predictable error responses for invalid inputs.

---

## 2. Rate Limiting & Abuse Prevention

### Observations
- The endpoint appears to be publicly accessible without authentication.
- No explicit rate limiting behavior was observed during testing.

### Risks
- Public endpoints are susceptible to:
  - scraping
  - brute-force enumeration
  - denial-of-service attempts

### Recommendations
- Implement IP-based rate limiting with sensible thresholds.
- Apply burst limits to prevent sudden traffic spikes from overwhelming the system.
- Consider basic bot-detection or WAF rules for abnormal traffic patterns.

---

## 3. Monitoring & Logging

### Observations
- Error responses are returned correctly for invalid inputs.
- Server-side logging behavior is not visible from the client perspective.

### Risks
- Without sufficient monitoring, abnormal usage patterns may go unnoticed.
- Security incidents may be harder to investigate without proper logs.

### Recommendations
- Log:
  - request rate anomalies
  - high error rates
  - unusual input patterns
- Correlate logs using request IDs or similar identifiers.
- Expose high-level metrics (error rate, latency, throughput) to monitoring dashboards.

---

## 4. Client-Side / Consumer-Side XSS Considerations

### Observations
- The API returns JSON responses.
- The API itself does not render content in a browser context.

### Risks
- While the API is not directly vulnerable to XSS, client applications consuming the API may be.
- If API response fields are rendered into HTML without proper encoding, reflected or stored XSS
  could occur on the client side.

### Recommendations
- Treat all API response data as untrusted input in consuming applications.
- Apply output encoding when rendering data in the UI.
- Avoid directly injecting API response values into the DOM without sanitization.

---

## Summary

The Tracking API demonstrates reasonable baseline robustness for a public tracking endpoint.
Primary security considerations relate to input validation, abuse prevention, and observability.

The recommended mitigations are pragmatic, low-overhead measures that significantly improve
security posture without impacting usability for legitimate users.