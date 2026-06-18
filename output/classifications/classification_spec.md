# CISSP Flashcard → Chapter Classification Rulebook

You classify CISSP flashcards into ONE chapter of the **Official (ISC)² CISSP Study
Guide, 9th edition (Sybex)**. The domain is derived from the chapter later, so you only
need to pick the chapter.

## Output format (one line per card, TAB-separated)
```
<lineno>\t<chapter_number 1-21>\t<confidence HIGH|MEDIUM|LOW>\t<short reason>
```
- `lineno` = the integer that prefixes the card in your input file. Echo it exactly.
- `chapter_number` = your single best chapter (1–21), ALWAYS provide one, even when unsure.
- `confidence`:
  - **HIGH** = the card's topic unambiguously belongs to exactly one chapter.
  - **MEDIUM** = topic fits this chapter best but is plausibly covered in another chapter too.
  - **LOW** = genuinely unsure / topic spans multiple chapters / generic.
- `reason` = a brief (<= 12 words) justification. No tabs inside the reason.
- Output ONLY these lines, nothing else. One line for EVERY card in your input.

## Chapters (with scope cues)
1. **Security Governance Through Principles and Policies** — CIA triad, DAD, AAA, security
   boundaries, defense in depth, governance, policies/standards/procedures/guidelines,
   threat modeling (STRIDE, PASTA, VAST, DREAD, trike), proactive/reactive threat modeling,
   supply-chain risk, COBIT, due care/due diligence, confidentiality aspects (concealment,
   criticality, secrecy), abstraction, data hiding.
2. **Personnel Security and Risk Management Concepts** — hiring/onboarding/termination, NDA,
   job rotation, separation of duties, screening, vendors/SLA, risk management terms (asset
   valuation, threat, vulnerability, exposure, SLE/ARO/ALE, qualitative vs quantitative),
   risk responses (mitigate/transfer/accept/avoid), risk frameworks (RMF), control
   categories & types (preventive/detective/corrective/deterrent/compensating; admin/
   technical/physical), security awareness/training, social engineering, APT/threat actors.
3. **Business Continuity Planning** — BCP, BIA, MTD, RTO, RPO, MTBF, continuity strategy,
   BCP vs DRP scoping, BCP roles/documentation.
4. **Laws, Regulations, and Compliance** — computer crime laws, intellectual property
   (patent, trademark, copyright, trade secret), licensing, import/export, privacy laws
   (GDPR, HIPAA, GLBA, COPPA, CCPA), PCI DSS, contractual compliance, evidence law basics.
5. **Protecting Security of Assets** — data classification/categorization, data lifecycle,
   data roles (owner, custodian, controller, processor, steward), PII/PHI, data states
   (at rest/in transit/in use), DLP, scoping & tailoring, data destruction (clearing,
   purging, degaussing, destruction), anonymization, pseudonymization, marking, labeling,
   handling, retention, EOL/EOS, SBU/classification levels.
6. **Cryptography and Symmetric Key Algorithms** — crypto foundations, symmetric ciphers
   (DES, 3DES, AES, Blowfish, Twofish, RC), block/stream, cipher modes (ECB/CBC/CTR…),
   key space, cryptographic lifecycle, substitution/transposition, symmetric key mgmt.
7. **PKI and Cryptographic Applications** — asymmetric crypto (RSA, ECC, DH, ElGamal),
   hashing (MD5, SHA, HMAC), digital signatures, PKI, certificates, CA, key escrow,
   crypto applications (TLS, S/MIME, PGP, IPsec crypto), cryptographic attacks.
8. **Principles of Security Models, Design, and Capabilities** — security models
   (Bell-LaPadula, Biba, Clark-Wilson, Brewer-Nash, Take-Grant, Graham-Denning),
   state machine, lattice, TCB, reference monitor, security modes, rings, tokens,
   confinement/bounds/isolation, evaluation criteria (Common Criteria, EAL, TCSEC,
   ITSEC), certification & accreditation.
9. **Security Vulnerabilities, Threats, and Countermeasures** — hardware/CPU/memory/
   firmware, client/server systems, databases-as-systems, ICS/SCADA, cloud models
   (IaaS/PaaS/SaaS), virtualization/hypervisor, containers, serverless, IoT, edge/fog,
   embedded, mobile device deployment (BYOD/COPE/CYOD/MDM), distributed systems,
   microservices, grid/peer-to-peer, system security capabilities.
10. **Physical Security Requirements** — site/facility design, secure facility,
    physical access controls, locks, fencing/lighting/CCTV/guards, mantraps, fire
    classes/detection/suppression, power (UPS, brownout), HVAC, emanations/TEMPEST,
    fail-open vs fail-secure (doors), environmental, wiring closets, media storage facility.
11. **Secure Network Architecture and Components** — OSI & TCP/IP models, IP addressing,
    protocols (TCP/UDP/ICMP/DNS/DHCP/ARP), ports, secure network hardware (switch/router/
    firewall types), cabling, network topologies, wireless (Wi-Fi standards, WPA), CDN,
    converged protocols, microsegmentation, layer functions.
12. **Secure Communications and Network Attacks** — VPN, tunneling, IPsec/L2TP, NAT/PAT,
    VoIP, remote access, virtualized networks (SDN, VLAN), multimedia collaboration,
    network attacks (DoS/DDoS, spoofing, hijacking, man-in-the-middle, eavesdropping),
    secure comms protocols, anycast/geocast/unicast/multicast/broadcast.
13. **Managing Identity and Authentication** — identification vs authentication, auth
    factors (type 1/2/3), passwords, biometrics (FAR/FRR/CER), MFA, SSO, federation,
    SAML/OIDC, IDaaS, Kerberos, credential management, AAA protocols (RADIUS/TACACS+),
    session management, provisioning/deprovisioning lifecycle of identities.
14. **Controlling and Monitoring Access** — access control models (DAC, MAC, RBAC, ABAC,
    rule-based), authorization mechanisms, implicit deny, need-to-know vs least privilege
    (as access concepts), access control attacks (brute force, dictionary, rainbow table,
    pass-the-hash), access review.
15. **Security Assessment and Testing** — assessment/audit programs, vulnerability scans,
    penetration testing (white/black/gray box, known/unknown environment), log review,
    synthetic transactions, code review & testing, misuse case, interface testing, KPIs,
    security control assessment (SCA), audit (internal/external/third-party).
16. **Managing Security Operations** — need-to-know/least privilege (operational), SoD &
    job rotation (operational), privileged account mgmt, provisioning, change management,
    configuration management (baselining, versioning), patch management, media management,
    SLAs (operational), resource protection.
17. **Preventing and Responding to Incidents** — incident response lifecycle (detection,
    response, mitigation, reporting, recovery, remediation, lessons learned), IDS/IPS,
    SIEM, firewalls (operational), honeypots/honeynets, allowlist/blocklist, anti-malware,
    DoS response, threat intelligence/threat hunting, computer security incident definition.
18. **Disaster Recovery Planning** — recovery strategies, backups (full/incremental/
    differential), recovery sites (hot/warm/cold/mobile), RAID, fault tolerance,
    DR teams, recovery plan testing (read-through/walk-through/simulation/parallel/
    full-interruption), restoration.
19. **Investigations and Ethics** — investigation types (criminal/civil/regulatory/admin),
    evidence (admissible, types, chain of custody), digital forensics, eDiscovery,
    interviewing, (ISC)² Code of Ethics, RFC 1087 ethics.
20. **Software Development Security** — SDLC, development models (waterfall, agile, spiral,
    DevOps/DevSecOps), maturity models (CMM, SAMM), change/config mgmt in dev, databases
    (ACID, normalization, aggregation/inference, polyinstantiation), APIs, OOP concepts,
    software testing in dev, code repositories, secure coding.
21. **Malicious Code and Application Attacks** — malware (virus, worm, trojan, RAT,
    ransomware, rootkit, logic bomb, spyware), malware components, web app attacks (XSS,
    CSRF, SQL injection, XSRF, directory traversal), buffer overflow, TOCTOU, privilege
    escalation, zero-day exploit, application attacks.

## Tricky / commonly-confused cases
- "fail-open / fail-secure system" → **10** (physical/door security context in this book).
- APT / threat actors / motivations → **2** (risk management) unless clearly about malware → 21.
- Social engineering general definition/principles → **2**; specific phishing-as-attack → may be 21/17.
- Need-to-know & least privilege & SoD: as a *model/access* concept → 14; as an *operations*
  practice → 16. Use the card's framing.
- Firewalls: as a *network component/type* → 11; as an *incident-prevention* tool → 17.
- Data destruction/anonymization/pseudonymization → **5**.
- Cloud / virtualization / IoT / BYOD-COPE-CYOD → **9**.
- VPN / NAT / network attacks → **12**.
- Biometrics / SSO / authentication factors → **13**; access control *models* → 14.
- Cryptography: symmetric → 6; asymmetric/hashing/PKI/signatures → 7.
- Security *models* (Bell-LaPadula etc.) → 8.
- When a topic clearly maps but could appear in two chapters, pick the best and use MEDIUM.
