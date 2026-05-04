# Security Policy

## Supported Versions

| Version           | Supported | Notes                                                         |
| :---------------- | :-------- | :------------------------------------------------------------ |
| **Latest Stable** | **Yes**   | Security updates are restricted to the latest tagged release. |
| **< Latest**      | **No**    | Older versions are immediately End-of-Life (EOL).             |

## Reporting a Vulnerability

We advocate for **Responsible Disclosure**. If you discover a vulnerability, please report it privately.

### Reporting Process

- **GitHub Security Advisories (Preferred)**: Navigate to the **[Security tab](https://github.com/wtransport/webtransport-interop/security)** and click **"Report a vulnerability"** to open an encrypted draft.

- **Email (Alternative)**: Send a message to `security@wtransport.org` with the subject `[SECURITY] WebTransport Interop Vulnerability Report`.

### Report Contents

- **Description**: Technical details of the vulnerability.
- **Impact**: Potential consequences and attack vectors.
- **Reproduction**: Minimal code example or step-by-step guide.
- **Environment**: Versions of Python, WebTransport Interop, and OS.

### Response SLA

- **Acknowledgment**: Within 48 hours.
- **Assessment**: Initial severity assessment within 5 business days.
- **Resolution**: Mitigation or remediation of critical vulnerabilities within 30 days.

## Supply Chain Security

WebTransport Interop enforces a **minimal-dependency philosophy**. We actively monitor runtime dependencies for CVEs, ensuring upstream patches trigger an immediate release.

## Disclosure Policy

Upon validating a vulnerability, we will:

1.  Collaborate with the reporter to verify the fix.
2.  Reserve a CVE identifier if applicable.
3.  Publish a security advisory on GitHub.
4.  Merge the patched code into the `main` branch.
5.  Credit the reporter in the advisory and `CHANGELOG.md` (unless anonymity is requested).

---

**Note**: This project does not currently operate a financial Bug Bounty program.
