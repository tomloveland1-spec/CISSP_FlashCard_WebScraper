# CISSP Flashcard → Chapter Classification Rulebook (v2 — section-aware)

You classify CISSP flashcards into ONE chapter of the **Official (ISC)² CISSP Study
Guide, 9th edition (Sybex)**. The domain is derived from the chapter later, so you only
need to pick the chapter.

This v2 spec adds the **actual section headings inside each chapter** (from the book's
table of contents). Use the section list to resolve cards that could plausibly fall in
two chapters: if a card's topic matches a *named section* of a chapter, that chapter wins.

## Output format (one line per card, TAB-separated)
```
<lineno>\t<chapter_number 1-21>\t<confidence HIGH|MEDIUM|LOW>\t<short reason>
```
- `lineno` = the integer that prefixes the card in your input file. Echo it exactly.
- `chapter_number` = your single best chapter (1–21), ALWAYS provide one, even when unsure.
- `confidence`:
  - **HIGH** = the card's topic unambiguously belongs to exactly one chapter (often because
    it matches a named section below).
  - **MEDIUM** = topic fits this chapter best but is plausibly covered in another chapter too.
  - **LOW** = genuinely unsure / topic spans multiple chapters / generic.
- `reason` = brief (<= 12 words) justification. No tabs inside the reason.
- Output ONLY these lines, nothing else. One line for EVERY card in your input.

## Chapters, with their book sections (authoritative scope)

1. **Security Governance Through Principles and Policies** — sections: Security 101;
   Understand and Apply Security Concepts (CIA triad, DAD, AAA, confidentiality/integrity/
   availability aspects, abstraction, data hiding); Security Boundaries; Evaluate and Apply
   Security Governance Principles (governance, COBIT, due care/due diligence); Manage the
   Security Function; Security Policy, Standards, Procedures, and Guidelines; Threat Modeling
   (STRIDE, PASTA, VAST, DREAD, trike, proactive/reactive); Supply Chain Risk Management.
2. **Personnel Security and Risk Management Concepts** — sections: Personnel Security Policies
   and Procedures (hiring/onboarding/termination, NDA, job rotation, separation of duties,
   screening, vendors/SLA); Understand and Apply Risk Management Concepts (asset valuation,
   threat, vulnerability, exposure, SLE/ARO/ALE, qualitative vs quantitative, risk responses
   mitigate/transfer/accept/avoid, RMF, control categories & types preventive/detective/
   corrective/deterrent/compensating, admin/technical/physical, APT/threat actors);
   Social Engineering; Establish/Maintain a Security Awareness, Education, and Training Program.
3. **Business Continuity Planning** — sections: Planning for Business Continuity; Project Scope
   and Planning; Business Impact Analysis (BIA, MTD, RTO, RPO, MTBF); Continuity Planning;
   Plan Approval and Implementation. (BCP scoping vs DRP.)
4. **Laws, Regulations, and Compliance** — sections: Categories of Laws; Laws (computer crime
   laws, intellectual property — patent/trademark/copyright/trade secret, licensing,
   import/export); State Privacy Laws (GDPR, HIPAA, GLBA, COPPA, CCPA); Compliance (PCI DSS);
   Contracting and Procurement.
5. **Protecting Security of Assets** — sections: Identifying and Classifying Information and
   Assets (data classification/categorization, PII/PHI, SBU, classification levels); Establishing
   Information and Asset Handling Requirements (marking, labeling, handling, retention, data
   states at-rest/in-transit/in-use, EOL/EOS, data destruction — clearing/purging/degaussing/
   destruction); Data Protection Methods (DLP, anonymization, pseudonymization); Understanding
   Data Roles (owner, custodian, controller, processor, steward); Using Security Baselines
   (scoping & tailoring).
6. **Cryptography and Symmetric Key Algorithms** — sections: Cryptographic Foundations
   (substitution/transposition, key space); Modern Cryptography; Symmetric Cryptography
   (DES, 3DES, AES, Blowfish, Twofish, RC, block/stream, cipher modes ECB/CBC/CTR…);
   Cryptographic Life Cycle. (Symmetric key mgmt only.)
7. **PKI and Cryptographic Applications** — sections: Asymmetric Cryptography (RSA, ECC, DH,
   ElGamal); Hash Functions (MD5, SHA, HMAC); Digital Signatures; Public Key Infrastructure
   (certificates, CA, key escrow); Asymmetric Key Management; Hybrid Cryptography; Applied
   Cryptography (TLS, S/MIME, PGP, IPsec crypto, blockchain); Cryptographic Attacks.
8. **Principles of Security Models, Design, and Capabilities** — sections: Secure Design
   Principles; Techniques for Ensuring CIA (confinement, bounds, isolation); Understand the
   Fundamental Concepts of Security Models (Bell-LaPadula, Biba, Clark-Wilson, Brewer-Nash,
   Take-Grant, Graham-Denning, state machine, lattice); Select Controls Based on Systems
   Security Requirements (Common Criteria, EAL, TCSEC, ITSEC, certification & accreditation);
   Understand Security Capabilities of Information Systems (TCB, reference monitor, security
   modes, rings, tokens).
9. **Security Vulnerabilities, Threats, and Countermeasures** — sections: Shared Responsibility;
   Data Localization and Data Sovereignty; Assess and Mitigate Vulnerabilities of Security
   Architectures (hardware/CPU/memory/firmware); Client-Based Systems; Server-Based Systems;
   Industrial Control Systems (ICS/SCADA); Distributed Systems; High-Performance Computing (HPC);
   Real-Time Operating Systems; Internet of Things; Edge and Fog Computing; Embedded Devices and
   Cyber-Physical Systems; Microservices; Infrastructure as Code; Immutable Architecture;
   Virtualized Systems (hypervisor); Containerization; Mobile Devices (BYOD/COPE/CYOD/MDM);
   Essential Security Protection Mechanisms; Common Security Architecture Flaws and Issues.
   (Cloud models IaaS/PaaS/SaaS as architecture live here.)
10. **Physical Security Requirements** — sections: Apply Security Principles to Site and Facility
    Design; Implement Site and Facility Security Controls (wiring closets, media storage facility,
    locks, fencing/lighting/CCTV/guards, mantraps, fire classes/detection/suppression, power UPS/
    brownout, HVAC, emanations/TEMPEST, fail-open vs fail-secure doors); Implement and Manage
    Physical Security.
11. **Secure Network Architecture and Components** — sections: OSI Model; TCP/IP Model; Analyzing
    Network Traffic; Common Application Layer Protocols; Transport Layer Protocols; Domain Name
    System (DNS, DNSSEC); Internet Protocol (IP) Networking (addressing, ports); ARP Concerns;
    Secure Communication Protocols; Implications of Multilayer Protocols (converged protocols);
    Segmentation (microsegmentation); Edge Networks; Wireless Networks (Wi-Fi standards, WPA,
    Bluetooth); Satellite Communications; Cellular Networks; Content Distribution Networks (CDNs);
    Secure Network Components (switch/router/firewall types as components, cabling, topologies).
12. **Secure Communications and Network Attacks** — sections: Protocol Security Mechanisms;
    Secure Voice Communications (VoIP); Remote Access Security Management; Multimedia Collaboration;
    Monitoring and Management; Load Balancing; Manage Email Security (S/MIME usage, spam, phishing
    controls at email layer); Virtual Private Network (VPN, IPsec/L2TP tunneling); Switching and
    Virtual LANs (VLAN, SDN); Network Address Translation (NAT/PAT); Third-Party Connectivity;
    Switching Technologies; WAN Technologies; Fiber-Optic Links; Prevent or Mitigate Network
    Attacks (DoS/DDoS, spoofing, hijacking, man-in-the-middle, eavesdropping).
13. **Managing Identity and Authentication** — sections: Controlling Access to Assets; The AAA
    Model (identification vs authentication, auth factors type 1/2/3, passwords, biometrics
    FAR/FRR/CER, MFA, accountability, AAA protocols RADIUS/TACACS+); Implementing Identity
    Management (SSO, federation, SAML/OIDC, IDaaS, Kerberos, credential management, session mgmt);
    Managing the Identity and Access Provisioning Life Cycle (provisioning/deprovisioning).
14. **Controlling and Monitoring Access** — sections: Comparing Access Control Models (DAC, MAC,
    RBAC, ABAC, rule-based); Implementing Authentication Systems (authorization mechanisms,
    implicit deny, need-to-know vs least privilege as access concepts); Zero-Trust Access Policy
    Enforcement; Understanding Access Control Attacks (brute force, dictionary, rainbow table,
    pass-the-hash, access aggregation).
15. **Security Assessment and Testing** — sections: Building a Security Assessment and Testing
    Program; Performing Vulnerability Assessments (vuln scans, Nessus, SCAP); Testing Your
    Software (code review & testing, static/dynamic, fuzzing, misuse case, interface testing);
    Training and Exercises; Implementing Security Management Processes and Collecting Security
    Process Data (log review, KPIs, account/backup management review). Penetration testing
    (white/black/gray box) lives here.
16. **Managing Security Operations** — sections: Apply Foundational Security Operations Concepts
    (need-to-know/least privilege operationally, SoD & job rotation operationally, privileged
    account mgmt); Address Personnel Safety and Security; Provision Information and Assets Securely
    (asset/media management, resource protection); Managed Services in the Cloud; Perform
    Configuration Management (CM) (baselining, versioning); Manage Change (change management);
    Manage Patches and Reduce Vulnerabilities (patch management).
17. **Preventing and Responding to Incidents** — sections: Conducting Incident Management
    (incident response lifecycle: detection/response/mitigation/reporting/recovery/remediation/
    lessons learned); Implementing Detection and Preventive Measures (IDS/IPS, SIEM, firewalls
    operationally, honeypots/honeynets, allowlist/blocklist, anti-malware, DoS response, threat
    intelligence/hunting); Logging and Monitoring; Automating Incident Response (SOAR).
18. **Disaster Recovery Planning** — sections: The Nature of Disaster; Understand System
    Resilience, High Availability, and Fault Tolerance (RAID); Recovery Strategy (recovery sites
    hot/warm/cold/mobile, backups full/incremental/differential); Recovery Plan Development;
    Training, Awareness, and Documentation; Testing and Maintenance (read-through/walk-through/
    simulation/parallel/full-interruption tests).
19. **Investigations and Ethics** — sections: Investigations (types criminal/civil/regulatory/
    admin, evidence — admissible/types/chain of custody, digital forensics, eDiscovery,
    interviewing); Major Categories of Computer Crime; Ethics ((ISC)² Code of Ethics, RFC 1087).
20. **Software Development Security** — sections: Introducing Systems Development Controls (SDLC,
    waterfall/agile/spiral, DevOps/DevSecOps, maturity models CMM/SAMM, change/config mgmt in dev,
    OOP concepts, APIs, code repositories, secure coding lifecycle); Establishing Databases and
    Data Warehousing (ACID, normalization, aggregation/inference, polyinstantiation); Storage
    Threats; Understanding Knowledge-Based Systems (expert systems, ML/AI, neural networks).
21. **Malicious Code and Application Attacks** — sections: Malware (virus, worm, trojan, RAT,
    ransomware, rootkit, logic bomb, spyware, components); Malware Prevention; Application Attacks
    (buffer overflow, TOCTOU, privilege escalation, rootkits); Injection Vulnerabilities (SQL
    injection, command injection, LDAP/XML injection); Exploiting Authorization Vulnerabilities
    (IDOR, directory traversal); Exploiting Web Application Vulnerabilities (XSS, CSRF/XSRF,
    session hijacking at app layer); Application Security Controls; Secure Coding Practices.

## Tricky / commonly-confused cases (section detail resolves these)
- **CIA triad definitions/aspects** → **1** (Understand and Apply Security Concepts). But
  confinement/bounds/isolation as a *design technique* → **8** (Techniques for Ensuring CIA).
- **Data sovereignty / data localization** → **9** (it is a named Ch9 section), NOT Ch5.
- **Email security** → **12** (Manage Email Security). Anti-malware/spam *as incident prevention*
  → 17; the cryptographic mechanism S/MIME/PGP internals → 7.
- **Load balancing** → **12** (named Ch12 section).
- **Managed services in the cloud / cloud operational management** → **16**. Cloud *architecture*
  models (IaaS/PaaS/SaaS, responsibility) → **9**.
- **Knowledge-based systems / expert systems / AI / neural networks** → **20** (named Ch20 section).
- **Storage threats (in a software/DB context)** → **20**.
- "fail-open / fail-secure" door/system → **10**.
- APT / threat actors / motivations → **2** unless clearly about a malware specimen → 21.
- Social engineering general definition/principles → **2**; phishing handled at email layer → 12;
  phishing as an attack to respond to → 17.
- Need-to-know & least privilege & SoD: as a *model/access* concept → 14; as an *operations*
  practice → 16. Use the card's framing.
- Firewalls: as a *network component/type* → 11; as an *incident-prevention* tool → 17.
- Data destruction / anonymization / pseudonymization → **5**.
- Virtualization / containers / IoT / ICS / BYOD-COPE-CYOD / embedded → **9**.
- VPN / NAT / VLAN / network attacks → **12**. OSI/TCP-IP/DNS/protocols/components → **11**.
- Biometrics / SSO / Kerberos / authentication factors / AAA → **13**; access control *models*
  (DAC/MAC/RBAC) and access control *attacks* → **14**.
- Cryptography: symmetric ciphers → **6**; asymmetric/hashing/PKI/signatures/crypto-attacks → **7**.
- Security *models* (Bell-LaPadula etc.) → **8**.
- Penetration testing / vulnerability scanning / code testing → **15** (assessment), vs malware/
  exploit *mechanics* → **21**, vs incident *response* → **17**.
- When a topic maps to two chapters and the section list doesn't break the tie, pick the best and
  use MEDIUM (or LOW if genuinely a toss-up).
