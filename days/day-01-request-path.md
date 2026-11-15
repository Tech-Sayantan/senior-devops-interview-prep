# Day 1 · Follow an HTTPS request

Imagine someone on your team says, “The API is down.” Before restarting anything, ask what they saw. A message saying `Could not resolve host` points you toward name resolution. A `404` tells you an HTTP server already answered. You’ll look in different places for those two problems.

## From the URL to the response

Take `https://api.example.com/orders`. `https` tells the client to use secured HTTP. `api.example.com` is the hostname. `/orders` is the path the client will request. The default port for HTTPS is `443`.

For a new HTTPS connection using HTTP/1.1 or HTTP/2 over TCP, the sequence is:

```text
DNS resolves the name → TCP connects to an IP and port → TLS secures the connection → HTTP carries the request and response
```

### 1. DNS · What address can I connect to?

You typed `api.example.com`. To make a connection, your Mac needs an IP address. It asks a DNS resolver, which can use a cached answer or look up a fresh one. An `A` record gives an IPv4 address and an `AAAA` record gives an IPv6 address. You might get more than one address back for the same name.

Say you just changed a DNS record and your Mac gets the new address, but a customer still gets the old one. Their resolver might have looked it up before you made the change. The record’s **TTL** tells caches how long they can reuse an answer. In the lab, the number before `IN A` in the `dig` output is the remaining TTL in seconds. [AWS Route 53 guide to DNS resolution](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/welcome-dns-service.html)

DNS looks up `api.example.com` whether you request `/orders` or `/health`. Those paths appear later in the HTTP request. If name resolution fails and the client has no usable address cached, it has nowhere to start the TCP connection.

### 2. TCP · Can I open a connection to that address and port?

One machine can run a website on port `443`, SSH on `22`, and a test app on `8765`. The IP gets you to the machine or network endpoint. The port identifies which service you’re trying to reach. A process that’s ready to accept connections on that address and port is **listening**.

You’ll hear the TCP setup called a three-way handshake. The client sends `SYN` to ask for a connection. The server sends `SYN-ACK` to acknowledge the request and reply. The client sends `ACK` to confirm it received the reply. With a connection established, TCP keeps the bytes in order and retransmits lost data.

An immediate refusal usually means the connection attempt received a rejection. Check whether a process is listening on the correct address and port. A connection timeout means the attempt failed to finish before its deadline. Routing problems and dropped traffic are possible causes. Use the trace to check whether the timeout happened at connect time or later while waiting for a response. [Everything curl on connection timeouts](https://everything.curl.dev/usingcurl/connections/timeout.html)

### 3. TLS · Am I talking securely to the hostname I asked for?

The TCP connection is open. For HTTPS, the client and server now do a TLS handshake. The client typically tells the server which hostname it wants so a shared server can pick the right certificate. The client checks that the certificate covers the hostname, is within its validity period, and chains to a trusted authority. The handshake establishes keys that protect the traffic.

Suppose curl prints `Connected` and then says the certificate expired yesterday. TCP already connected to port `443`. You’d start by finding out which component presented the certificate. If an AWS load balancer handled TLS for the customer, check the certificate served by the load balancer’s listener. A server speaking plain HTTP on that same port could also accept TCP and then fail when the client tries to start TLS.

### 4. HTTP · What did I ask for, and what answered?

The client can now send a request such as `GET /orders`. `GET` means it wants to retrieve something. It gets a response with a status, headers, and often a body. A `200` reports success for that request. A `404` says the responder couldn't find the requested resource. A `502` from a gateway points you toward its attempt to talk to a backend. The responder could be the app, a reverse proxy, or a load balancer.

Use `curl -v` to see the last step that completed. If the trace reaches `Connected` and then fails on a certificate, you can spend your time on TLS. If you see `< HTTP/1.1 404`, identify which component responded and why it handled that path that way. [Everything curl on verbose output](https://everything.curl.dev/usingcurl/verbose/index.html)

## Interview questions and how to reason through them

**`dig` returns the expected IP, but the site is down. What do you check next?**

That tells you what the resolver you queried returned. Check the exact URL with `curl -v` from the affected client environment. For a Kubernetes issue, that means testing from the affected workload or an equivalent network location where you have access. Look for the destination address curl actually used, the TCP connection, TLS verification, and the HTTP response. The first missing step narrows the next check. Your Mac may use a different resolver, route, or proxy from the workload.

**Ping works. Why can HTTPS still fail?**

Ping tests whether an ICMP echo gets a reply from an address. HTTPS needs an open TCP port, a successful TLS handshake, and an HTTP response. You can get a ping reply while port `443` refuses connections or the HTTPS certificate has expired. Test the exact URL to exercise what the customer uses.

**I replaced the HTTPS hostname with the server IP. Why did the certificate fail?**

The client now checks whether the certificate covers that IP address. A certificate issued for the hostname typically lacks the IP address as a certificate identity, and a server that hosts multiple sites might present a different certificate. To test a known candidate IP while preserving the original hostname, use `curl --resolve HOST:PORT:IP` and keep the hostname in the HTTPS URL. This overrides name resolution for that curl invocation and keeps normal TLS verification. [curl `--resolve` reference](https://curl.se/docs/manpage.html#--resolve)

**Can a DNS change cause a `404`?**

Yes, indirectly. A stale or incorrect record can take a client to an old load balancer or a different server that returns `404` for the same hostname and path. Compare the destination IP from the failing request against the expected addresses and check the responding component's route configuration and access logs. A `404` is an HTTP response, so the client reached an HTTP responder on that attempt.

## A real production incident · DynamoDB in Northern Virginia

During the October 2025 `us-east-1` incident, a race condition in AWS’s DNS automation left `dynamodb.us-east-1.amazonaws.com` with an empty DNS record. A race condition is a bug where the order or timing of overlapping operations changes the outcome. Affected callers couldn't resolve the endpoint to a usable address, so new attempts could fail before opening a connection. Services relying on DynamoDB were also affected. AWS restored the DNS information, and cached answers had to expire before affected clients could consistently resolve it again. [AWS post-event summary](https://aws.amazon.com/message/101925/)

**Interview scenario.** Customers get a `503` from your checkout API. The checkout logs say it can’t resolve the DynamoDB hostname. How can you get an HTTP response and a DNS error at the same time?

There are two requests. The customer reached checkout and got an HTTP response. Checkout’s own request to DynamoDB stopped at DNS. Start where the failure happened. Look up the exact DynamoDB name from an affected checkout workload. Try another known-good name there and compare the DynamoDB result with a healthy workload. Those checks can help you see whether resolution is broken more broadly or only for that endpoint. Compare the timing and Region with AWS Health. After DNS recovers, verify that checkout can make a real DynamoDB call and customers can finish placing orders again.

## A separate interview scenario · AWS load balancer returns 502

Imagine a team changes an Application Load Balancer target group from HTTP to HTTPS. The app still listens on port `8080` and speaks plain HTTP. Users logging into the service now see `502 Bad Gateway`.

There are two connections to think about. The client can reach the ALB over HTTPS and get an HTTP `502`. On the second connection, the ALB tries TLS to a backend that expects HTTP. The TCP handshake to the backend can succeed before the TLS handshake fails.

Check the target group's protocol and port against the last working configuration. From the affected network, confirm what the app serves on `8080`. Compare ALB-generated 5xx errors with target-generated 5xx errors if you need to confirm the source. If the protocol change caused the failure, restore the known-good target configuration through the deployment process. Verify the original customer URL and check that the ALB's 502 rate falls. [AWS ALB troubleshooting guide](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-troubleshooting.html)

## Mac lab · See each step

Allow 10–15 minutes. Use Terminal and `python3`. First you’ll look up and request a public example site. Then you’ll serve one temporary file on your Mac’s loopback address, `127.0.0.1`.

### A. Read a successful public HTTPS trace

```bash
dig example.com A +noall +answer
curl -sSv --http1.1 --max-time 10 -o /dev/null https://example.com/
```

Read `dig` as a question about IPv4 addresses. In curl's output, look for `Trying`, `Connected … port 443`, the TLS version or certificate verification line, `> GET / HTTP/1.1`, and `< HTTP/1.1 200 OK`. Your actual IP and TLS details can vary. The `>` and `<` lines show data curl sent and received. `-v` shows the trace, `-sS` hides the progress meter and still shows errors, and `-o /dev/null` discards the page body. [curl command reference](https://curl.se/docs/manpage.html)

### B. Create and break a local request

In **Terminal 1**, create one temporary file and leave the Python server running.

```bash
lab_dir=$(mktemp -d)
printf 'ok\n' > "$lab_dir/health"
python3 -m http.server 8765 --bind 127.0.0.1 --directory "$lab_dir"
```

In **Terminal 2**, run these one at a time.

```bash
lsof -nP -iTCP:8765 -sTCP:LISTEN
curl -sSi --max-time 3 http://127.0.0.1:8765/health
curl -sSi --max-time 3 http://127.0.0.1:8765/missing
curl -sSv --max-time 3 https://127.0.0.1:8765/health
```

1. `lsof` should show Python listening on `127.0.0.1:8765`.
2. `/health` should return `200 OK` with the body `ok`.
3. `/missing` should return `404 File not found`. The server still received the HTTP request and answered.
4. Changing `http` to `https` on the same address and port should show a TCP connection followed by a TLS error. The exact error text varies with your curl build. The Python server may also log a bad request because it received TLS handshake bytes on a plain HTTP listener.

Press **Ctrl+C** in Terminal 1 to stop the server. Repeat the original plain HTTP request in Terminal 2.

```bash
curl -sSi --max-time 3 http://127.0.0.1:8765/health
```

Expect a connect error, typically `curl: (7) Failed to connect …`. The same address and port that returned HTTP responses now have no listening process. Using the numeric loopback address removes hostname resolution from this experiment. Using plain `http` on the first two requests removes TLS. [Python HTTP server CLI](https://docs.python.org/3/library/http.server.html) · [curl exit codes](https://everything.curl.dev/cmdline/exitcode.html)

Clean up in **Terminal 1** after the server stops.

```bash
rm "$lab_dir/health"
rmdir "$lab_dir"
```

### Troubleshooting

- If Python reports `Address already in use`, switch `8765` to `8766` in the server, `lsof`, and curl commands. If the temporary file already exists, reuse the same `lab_dir`.
- If the first localhost request fails immediately, check that Terminal 1 still says it is serving and run `lsof` to confirm the listener. Match the address and port in both terminals.
- If the trace shows curl using a proxy for the localhost request, add `--noproxy 127.0.0.1` to the local curl commands. This makes those requests go directly to the lab listener.

**Practice checkpoint.** For the public HTTPS request and each local request, name the last step that succeeded. Then explain why the live plain HTTP server, the same server receiving HTTPS, and the stopped server give three different results.

**Lab status.** Trunks verified the public trace and the local 200, 404, TLS failure, and connection failure on the Mac. Tan’s independent run is pending.

[Back to the 60-day study plan](../60-day-study-plan.md)
