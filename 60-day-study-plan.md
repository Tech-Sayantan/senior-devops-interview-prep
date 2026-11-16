# Senior AWS DevOps interview preparation

This is a 60-session plan for interviewing in 2027. Budget 60–75 minutes per session, including review days. Concepts start in plain English and build toward the decisions a senior engineer has to make when a deployment affects customers, a database change limits rollback, or two teams disagree on who owns a production change.

## The scenario we’ll keep coming back to

An order-processing API is moving to AWS. Its legacy ERP and enterprise service bus (ESB) are still on-premises, and the migration has to keep orders flowing. We’ll decide how to provision the cloud infrastructure, patch the systems that stay on VMs, release the API, monitor customer impact, and move the integration without processing orders twice. Sometimes the right answer will be to use a simpler AWS runtime. Each hands-on exercise is a standalone drill with local tools or synthetic evidence.

## Why these topics earn time

- **Cloud infrastructure, delivery, and operations.** Iris Software’s AWS DevOps posting combines Terraform, Jenkins, EKS, ECR, and incident investigation. ACA Group adds network architecture, AWS data services, GitOps, Python and Bash, with GitHub Actions among its preferred skills. Okta’s senior SRE posting also calls for SLOs, database operations, postmortems, and technical leadership. These are representative examples of responsibilities to prepare for. [Iris Software](https://careers.irissoftware.com/job/Noida-Devops-AWS-Senior-Engineer-UP/61356244/) · [ACA Group](https://careers.acaglobal.com/job/Pune-Senior-DevOps-Engineer/1439440800/) · [Okta](https://www.okta.com/company/careers/subscription-cogs/senior-site-reliability-engineer-k8s-terraform-python-8255904/)
- **Enterprise and hybrid systems.** Wipro’s late-2026 India postings ask for reusable Terraform modules, state and drift management, and Ansible roles and automation workflows. HCLTech’s integration operations posting owns IBM MQ, APIs, and the continuity of business transactions. That’s why you’ll practice both changing infrastructure safely and tracing an order across an integration. [Wipro Terraform Lead](https://careers.wipro.com/job/Chennai-DEVOPS-LEAD-L2-IND-600119/215095-en_US/) · [Wipro Ansible Automation](https://careers.wipro.com/job/Ansible-Automation/213009-en_US/) · [HCLTech Integration Operations](https://careers.hcltech.com/job/Tower-Lead-%28Support-%26-Operations%29/177970-en_US/) · [IBM on the ESB pattern](https://www.ibm.com/think/topics/esb)
- **Modernization goes beyond the migration.** Amtech’s Bengaluru opening combines moving an ERP to multi-account AWS with reusable Terraform, self-service tooling, reliability targets, and cloud costs. That overlap is worth practicing in the same scenario. [Amtech Senior Cloud Engineer](https://job-boards.greenhouse.io/amtechsoftware/jobs/4466968009)
- **Platform engineering, software supply chain, and cost.** Practice designing a self-service way for teams to ship with built-in controls, verifying where an artifact came from before deployment, and reasoning about cost per order alongside reliability. Each comes with a decision to defend and an outcome you can measure. [CNCF platforms white paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/) · [SLSA build provenance](https://slsa.dev/spec/v1.2/build-provenance) · [FinOps unit economics](https://www.finops.org/framework/capabilities/unit-economics/)
- **AI-assisted operations.** One short session covers checking an AI-generated incident hypothesis against the original evidence, using approved data, and keeping a human accountable for production actions. AWS documents this review workflow in its DevOps Agent service card. [AWS DevOps Agent service card](https://docs.aws.amazon.com/ai/responsible-ai/aws-aidevops-agent/overview.html)

## How each session works

1. Explain the concept in everyday English, with an example of when you’d need it at work.
2. Practice direct interview questions and answers, followed by a worked production scenario.
3. Try a fresh question in your own words. For hands-on days, run the small exercise and bring back the output.
4. Review why the answer works, where it needs more evidence, and how to explain the trade-off. Study notes are published in English, with reference links.

For scenario practice, score each area from 0 to 2. Did you scope the customer impact? Did your check distinguish between plausible causes? Was the change safe to try? Did you verify recovery? Did you communicate ownership and the next action? Use the same criteria across the course to see what improves.

## Days 1–7 · Linux and troubleshooting

| Day | Topic and interview practice |
| --- | --- |
| 1 | **[Request path](days/day-01-request-path.md).** Follow DNS, TCP, TLS, and HTTP. Explain what a 404 proves and what a refused connection tells you. |
| 2 | **Processes and services.** Read permissions, process status, signals, file descriptors, `systemd`, and journal logs. Explain why a service behaves differently in a shell and under `systemd`. |
| 3 | **Host saturation.** Separate CPU, memory, cgroup limits, disk space, inodes, and I/O symptoms. Diagnose a host that appears healthy in a CPU dashboard. |
| 4 | **Network evidence.** Trace the path across a resolver, proxy, and backend. Explain which source location, hostname, and port you would test. |
| 5 | **Bash and Git.** Handle quoting, pipeline exit codes, errors, and cleanup. Read a failing shell script and explain how to revert a shared change. |
| 6 | **Python automation.** Parse structured logs, handle malformed lines, and report the top failing route. Use a tiny fixture to check the result. |
| 7 | **Blind troubleshooting drill.** Identify a failed layer from only a few symptoms and ask for the next piece of evidence. |

**Small exercise.** Use a localhost Python server to observe HTTP 200, HTTP 404, and TCP connection refusal. Explain each result in your own words. [Everything curl](https://everything.curl.dev/usingcurl/verbose/index.html) · [Google SRE troubleshooting](https://sre.google/sre-book/effective-troubleshooting/)

## Days 8–14 · AWS architecture and networking

| Day | Topic and interview practice |
| --- | --- |
| 8 | **Identity.** Follow AWS IAM and STS credentials through a cross-account request. Read role trust, identity and resource policies, permissions boundaries, and SCPs in a denial scenario. |
| 9 | **Account design.** Use AWS Organizations to sketch dev, production, shared services, security, and log archive accounts. Explain who gets access and what a shared-service outage can affect. |
| 10 | **Private connectivity.** Work through routes, security groups, NACLs, NAT, and VPC endpoints. Diagnose a workload that loses S3 access. |
| 11 | **Hybrid connectivity.** Reason through DNS forwarding, VPN and Direct Connect, Transit Gateway, and PrivateLink. Consider why AWS resolves an ERP hostname differently from the data center. |
| 12 | **Traffic and certificates.** Choose ALB or NLB, map Route 53 and CloudFront to the request path, and troubleshoot an ACM certificate or target health issue. |
| 13 | **Compute and availability.** Compare EC2, ECS/Fargate, EKS, and Lambda for the case. Explain how an Auto Scaling group and AZ placement affect recovery. |
| 14 | **Storage and design review.** Choose among S3, EBS, and EFS based on access patterns, durability, and recovery requirements. Defend the whole AWS design under follow-up questions. |

**Small exercise.** Mark the forward and return traffic paths on a two-AZ VPC sketch, then identify where a security rule or route could break them. [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)

## Days 15–21 · Terraform

| Day | Topic and interview practice |
| --- | --- |
| 15 | **Configuration and dependency graph.** Read HCL, providers, resource references, variables, and outputs. Explain what the plan says will change. |
| 16 | **Reusable modules.** Version providers and modules, use stable instance addresses, and decide where account or environment boundaries belong. Compare Terraform, CloudFormation/CDK, and OpenTofu at a decision level. |
| 17 | **State and concurrency.** Explain what state tracks, how S3 state locking with `use_lockfile` and bucket versioning help, and what needs access to state or plan artifacts. Recognize deprecated DynamoDB-based locking in older setups. |
| 18 | **Drift and imports.** Decide who owns a manual change. Bring an existing resource under management and check the next plan for unintended changes. |
| 19 | **Refactoring.** Use a `moved` block to preserve resource identity through a module or resource rename. Explain how you’d plan a migration across state boundaries. |
| 20 | **Safe plan and apply.** Review a plan that proposes replacing a critical resource. Define approval gates, execution identity, and limits on concurrent changes. |
| 21 | **Partial apply and recovery drill.** An apply stops partway through. Reconcile the recorded state with real infrastructure and explain what evidence makes the next plan safe to approve. |

**Small exercise.** Use a local Terraform fixture to compare the plan for a module rename before and after using `moved`. Explain why you’d reject the first plan. [Terraform S3 backend](https://developer.hashicorp.com/terraform/language/backend/s3) · [Terraform refactoring](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring)

## Days 22–28 · Ansible and enterprise integration

| Day | Topic and interview practice |
| --- | --- |
| 22 | **Hosts and playbooks.** Read inventory groups, connection settings, facts, variable scope, roles, and task output. Explain where Ansible fits after Terraform provisions an EC2 fleet. |
| 23 | **Repeatable changes.** Practice templates, modules, handlers, and idempotence. Explain what check mode can tell you and why you still verify the actual change. |
| 24 | **Rolling patching.** Plan batches, drain traffic, verify the first batch, and define a stop condition. Decide when to use Ansible, Systems Manager, or a new machine image. |
| 25 | **Enterprise service bus and MQ.** Sketch how an ESB routes messages, translates data, and mediates protocols such as SOAP/XML and HTTP/JSON. Explain where IBM MQ and a JMS client fit in the ERP request path. |
| 26 | **Integration choices.** Decide when to use a synchronous API, an SQS queue, SNS fan-out, EventBridge routing, or Kafka/MSK. Compare ordering, retention, and consumer needs. |
| 27 | **Failures and delivery semantics.** Model retries, backoff, dead-letter queues, replay, correlation IDs, idempotent consumers, and transactional outbox. Explain what can be duplicated and where to guard the business side effect. |
| 28 | **ERP migration drill.** Plan adapters, parallel operation, message reconciliation, and cutover and rollback conditions. Explain who should own each contract. |

**Small exercise.** Apply a harmless playbook to an isolated local target twice. Explain why the second run should report zero changes, then review a rolling patch plan for a service with limited spare capacity. [Ansible playbook guide](https://docs.ansible.com/projects/ansible/latest/playbook_guide/index.html)

**Small exercise.** Replay a synthetic order message twice against a tiny SQLite-backed Python consumer. Show one stored business effect and discuss how you’d handle a timed-out downstream call. [AWS messaging decision guide](https://docs.aws.amazon.com/decision-guides/latest/decision-guides/sns-or-sqs-or-eventbridge.html) · [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/patterns/messaging/)

## Days 29–35 · Docker, CI/CD, and release security

| Day | Topic and interview practice |
| --- | --- |
| 29 | **CI/CD and Docker artifacts.** Trace a commit through PR checks, image building, and promotion. Use digests to verify what reached production. Explore multi-stage builds, image layers and caching, and startup and shutdown issues. |
| 30 | **Jenkins and Groovy.** Write and review a Declarative `Jenkinsfile`. Explain agents, stages, credentials scope, post conditions, and when to use a Shared Library. |
| 31 | **GitHub Actions.** Compare runners and reusable workflows. Read an AWS OIDC trust policy and scope deployment permissions to the intended repo and environment. |
| 32 | **Artifact trust.** Distinguish image digests, dependency scans, software bills of materials (SBOMs), signatures, and provenance. Explain what must pass before promoting an image in ECR. |
| 33 | **Safe release strategy.** Compare rolling, canary, and blue-green releases. Define promotion and rollback triggers and explain compatibility during a schema change. |
| 34 | **Smoke checks.** Write a small Bash or Python check with a timeout and meaningful exit codes. Test how it behaves when a dependency fails. |
| 35 | **Pipeline review mock.** Review Jenkins and GitHub Actions snippets for inconsistent artifacts, risky runner permissions, and an ineffective test gate. |

**Small exercise.** Given a commit, an image digest, build evidence, and a release manifest, trace what would actually reach production and argue whether to approve the deployment. [Jenkins Pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/) · [GitHub Actions OIDC for AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws) · [SLSA build provenance](https://slsa.dev/spec/v1.2/build-provenance)

## Days 36–42 · Kubernetes, EKS, and Argo CD

| Day | Topic and interview practice |
| --- | --- |
| 36 | **Controllers and scheduling.** Follow a Deployment through ReplicaSets and Pods. Find why a pod stays `Pending`. |
| 37 | **Probes and capacity.** Explain requests, limits, readiness, liveness, startup probes, HPA, and disruption budgets. Diagnose a rollout that stalls under load. |
| 38 | **Network path.** Trace a request through CoreDNS, ingress routing, a Service and EndpointSlice, and the pod. Review a migration from the retired `ingress-nginx` controller to Gateway API, including controller-specific behavior and route tests. |
| 39 | **Identity.** Distinguish EKS human access, Kubernetes RBAC, and pod access to AWS using EKS Pod Identity or IRSA. Investigate an application `AccessDenied`. |
| 40 | **Cluster operations.** Explain the effect of node changes, CNI/IP capacity, AZ placement, and upgrades. Choose an order of checks when new pods can’t start. |
| 41 | **Packaging and reconciliation.** Read Helm or Kustomize changes. Interpret Argo CD sync and health, drift, self-heal, and prune. |
| 42 | **GitOps release drill.** Promote the same image digest by changing the deployment repository. Decide what to do when Argo CD is synced and customer errors increase. |

**Small exercise.** Compare a Deployment and Service against pod events and EndpointSlice output to identify why `Running` pods receive no traffic. Verify what changed after the proposed fix. [Kubernetes Service debugging](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/) · [Ingress NGINX retirement](https://kubernetes.io/blog/2026/03/30/kubernetes-v1-36-sneak-peek/) · [Gateway API](https://gateway-api.sigs.k8s.io/docs/) · [EKS workload identity](https://docs.aws.amazon.com/eks/latest/userguide/service-accounts.html) · [Argo CD automated sync](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/)

## Days 43–49 · Observability, SRE, and databases

| Day | Topic and interview practice |
| --- | --- |
| 43 | **Signals.** Correlate metrics, logs, and traces across CloudWatch, Prometheus, Grafana, and OpenTelemetry. Find which dependency explains rising tail latency. |
| 44 | **SLOs and paging.** Define a user-facing service-level indicator and objective, reason about error budgets, and decide when high burn warrants a page. |
| 45 | **Incident timeline.** Use deployment events, CloudTrail audit records, and the application timeline to choose the next investigation step. Write a concise customer-impact update. |
| 46 | **SQL and relational operations.** Use PostgreSQL and RDS/Aurora scenarios to practice SQL, indexes, `EXPLAIN`, locks, and connection pooling. Triage a release that exhausts connections. |
| 47 | **Recovery and data safety.** Design for an AZ outage and a regional incident. Define RTO and RPO, compare failover and point-in-time restore, and describe how to test the restore and validate the recovered data. |
| 48 | **NoSQL and caching.** Explain DynamoDB partition and access patterns, throttling, Redis TTL, and cache stampedes. Decide how the app should behave when the cache is unavailable. |
| 49 | **Timed incident mock.** Investigate a partial outage with conflicting signals, present a safe mitigation, and define proof of customer recovery. |

**Small exercise.** Draw the incident timeline from timestamped synthetic logs, metrics, and deployment events. Draft a two-sentence stakeholder update with impact and next action. [Google SRE on SLO alerting](https://sre.google/workbook/alerting-on-slos/)

## Days 50–56 · Security, platform design, FinOps, and senior ownership

| Day | Topic and interview practice |
| --- | --- |
| 50 | **Defensive cloud operations.** Explain KMS and secrets rotation, workload isolation, audit logging, policy as code, and emergency access. Review the response to an accidentally exposed deployment credential. |
| 51 | **Self-service platform.** Give teams a supported path from repo creation through deployment, identity, and observability. Define adoption and time to first successful production deploy. |
| 52 | **FinOps and capacity.** Use cost allocation, egress, rightsizing, and cost per order to evaluate a proposed architecture change alongside p95 latency and availability. |
| 53 | **Migration leadership.** Propose a phased move from VMs, negotiate ownership with other teams, and define measurable cutover and rollback decisions. |
| 54 | **AI-assisted operations.** Use synthetic incident evidence to review an AI-generated hypothesis. Identify unsupported claims, missing evidence, and actions that require human approval. |
| 55 | **DORA and delivery improvement.** Pick a delivery bottleneck, propose a change, and explain how metrics such as change lead time and change fail rate would help evaluate the result. |
| 56 | **Behavioral answers and review.** Build truthful examples of an incident, a difficult design decision, and work that improved delivery. Practice explaining your contribution and the measured result. |

**Small exercise.** Sketch a developer onboarding flow for the order API. Choose what is built into the template, what requires team input, and how the platform team learns where users are blocked. [CNCF platforms white paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/) · [DORA delivery performance metrics](https://dora.dev/guides/dora-metrics/)

## Days 57–60 · Full interview practice

| Day | Mock interview |
| --- | --- |
| 57 | **Architecture.** Present the AWS design and defend runtime, account, identity, integration, cost, and recovery decisions under follow-up questions. |
| 58 | **Incident.** Work from incomplete evidence. Scope customer impact, ask for a decisive check, choose a safe mitigation, and verify recovery. |
| 59 | **Live coding and delivery.** Solve a Python or Bash operational problem, then review a Groovy pipeline, GitHub Actions workflow, or SQL change. Explain how you’d test the result. |
| 60 | **Targeted retest.** Attempt fresh versions of weak questions. Rehearse concise answers and match your strongest examples to the requirements of a target role. |
