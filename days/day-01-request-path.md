Yes, Tan. You want the **whole Day 1 lesson in one go**, including the answers and how to work through the scenarios. The answer should help you see *why* something happened, so you can explain it your own way in an interview. I split up the lesson when you were asking me to change how I teach it.

# Day 1 · What actually happens when you open a URL?

Say you type `https://orders.example.com/health` on your Mac. You know exactly what you mean by that. Your Mac has to work it out one step at a time.

`orders.example.com` tells it which service you want. `/health` tells it what to ask that service for. `https` tells it to use encryption and, because you didn’t specify a port, to try port `443`.

For the kind of HTTPS connection we’ll run today, the order is **DNS → TCP → TLS → HTTP**. Let’s follow it, and at each step imagine what you’d see if it broke.

## DNS · Where do I send this?

Your Mac has the name `orders.example.com`. To connect, it needs an IP address. It asks for one through **DNS**, and a resolver either gives it a cached answer or looks it up.

Say the answer is `192.0.2.44`. Now your Mac has an address to try. That’s the job DNS did. The URL could end in `/health`, `/login`, or `/orders`, and the lookup would still be for `orders.example.com`. The path comes into play later.

When you run `dig` in the lab, you’ll see an **A record**, which gives an IPv4 address. **AAAA** is the equivalent for IPv6. You may get several addresses back. You’ll also see a number called the **TTL**, which tells you how long the answer can stay in a cache. This helps explain a real problem you might get on call. You’ve just changed a DNS record, your laptop sees the new address, and a customer is still using the old one because their resolver cached it earlier.

If curl says **`Could not resolve host`**, picture it getting stuck here. It couldn’t get an address for that name, so it hasn’t tried to connect to the website yet.

## TCP · Can I connect to the service at that address?

Let’s say DNS worked. Your Mac now tries `192.0.2.44` on port `443`.

Why the port? One machine can run a website on `443`, an SSH service on `22`, and a test app on `8765`. The IP gets you to the machine or network endpoint. The port identifies which service you’re trying to reach. A process that’s waiting for connections on an address and port is **listening**.

TCP starts with three short messages. You’ll hear them called **SYN, SYN-ACK, ACK**. Read them as “I’d like to connect,” “I received that and I’m ready,” and “I received your reply.” Now the two sides have a connection they can use to exchange data.

Two failures can look similar to a user who just says “the site is down”:

- **`Connection refused` immediately.** The connection attempt was rejected. Check whether you’re using the right IP and port and whether anything is listening there. A firewall can actively reject it too.
- **It waits, then times out.** If the trace never got past `Trying`, the connection didn’t finish before the deadline. Now you have to check things like routing, filtering, and reachability from that client. If you already saw `Connected`, look further down the trace. Curl can also time out while waiting for TLS or an HTTP response.

## TLS · Can I trust who’s on the other end, and can we talk privately?

Now curl prints **`Connected`**. Good. Something accepted the TCP connection. Before your Mac sends the HTTPS request, it wants to check that the service on the other end is who it claims to be. It also needs to set up encryption.

This is where the server presents a **certificate**. Your Mac checks things like these. Does the certificate cover `orders.example.com`? Is it within its validity dates? Can I trace it back to a certificate authority I trust?

Imagine you can open the connection every time, but the browser keeps reporting an expired certificate. At that point you have a much smaller problem to investigate. Which component presented that certificate? In AWS that might be the load balancer in front of your app. If that’s where TLS ends, updating a certificate inside the app container wouldn’t fix the certificate the customer sees.

## HTTP · Now can I have `/health`?

Once TLS is ready, the client finally sends something like `GET /health`. **GET** is what the client wants to do. **`/health`** is what it’s asking for. The reply contains a status code and can contain a body, such as `ok` or some JSON.

Think about a browser that loads `/health` but gives you `404` for `/heath`. You can see the typo here. In a real app it could also be a missing route or a proxy sending traffic to the wrong place. Either way, **something understood enough HTTP to send you an answer**. That’s a very different clue from a connection refusal. Your next job is to find out which component answered and why.

## Interview questions · Let’s work through the answers

**1. `dig` returns the right IP. Why might the site still be down?**

You’ve answered “where should I try?” The machine could still have nothing listening on `443`, the certificate could be expired, or the app could respond with an error. Run `curl -v` and follow the output until something goes wrong. If the problem is only happening inside a pod or on a VPN, test there too. A DNS answer from your Mac may differ from the one the failing workload gets.

**2. I can ping the server. Why can’t I open the website?**

Ping asks for a different kind of reply. The server can answer ping while its web service is stopped or its web port is blocked. Try the URL the user is trying. That tests the actual hostname, service port, and web request.

**3. HTTPS works with the hostname. Why does it complain when I put the IP directly in the URL?**

You changed the identity you asked curl to verify. The certificate may cover `orders.example.com`, while the URL now asks curl to verify `192.0.2.44`. If you’re testing a specific IP for that service, `curl --resolve` lets you choose the address while keeping the original hostname in the URL. This is handy when you’re testing whether a DNS change will send traffic to the right new endpoint. [Everything curl on selecting an address](https://everything.curl.dev/usingcurl/connections/name.html)

**4. If I got a `404`, can I rule out DNS?**

You know the request reached *an* HTTP responder. Think about what happens if a stale DNS answer sends you to an older load balancer that serves other pages but has no `/health` route. You can get a perfectly valid `404` from the wrong place. Check the hostname, where it resolved, and whose logs show the request.

## Production scenarios · Follow each connection separately

### What really happened to AWS DynamoDB?

On **October 19–20, 2025**, a timing bug in AWS’s DNS automation removed the addresses for the public DynamoDB endpoint in `us-east-1`. Systems trying to open a new connection through that endpoint couldn’t resolve its name. AWS restored the DNS data manually, and clients recovered as cached DNS responses expired. [AWS’s incident report](https://aws.amazon.com/message/101925/)

Now put yourself on call for a checkout service during an incident like that. Customers are seeing **`503`**, but checkout’s logs say **it can’t resolve the DynamoDB hostname**. How can you have an HTTP response and a DNS failure at the same time?

Because you’re looking at **two different requests**.

- The **customer’s browser → checkout** request got far enough for checkout to send an HTTP response.
- The **checkout → DynamoDB** request got stuck trying to find DynamoDB’s address.

So where do you test? **From the affected checkout workload.** Look up the exact DynamoDB name there and compare it with a name you know works from the same workload. Check whether other workloads in that region see the same thing, and compare the timing with AWS Health. After recovery, check that checkout can make a real DynamoDB call and that customers can finish placing orders. Seeing an IP in a DNS answer is only the first part of confirming recovery.

### The browser shows `502`, but the certificate is fine

Here’s an everyday deployment problem. Your browser connects securely to an AWS Application Load Balancer. After a configuration change, the load balancer starts sending `502`. The app behind it is still running.

There are two connections here too. The browser’s HTTPS connection ends at the load balancer. The load balancer then makes **its own** connection to the app. Suppose the target group was switched to HTTPS, but the app still speaks plain HTTP on port `8080`. The browser can pass its TLS check while the load balancer’s TLS handshake to the app fails.

How do you prove that’s the issue? Check what protocol and port the target group uses. From inside the network, confirm what the app actually responds to on `8080`. If the target group change introduced the mismatch, restore the known-good protocol setting and check the original customer URL and the `502` rate. In the lab below, you’ll see this same protocol mismatch happen on your Mac. [AWS on load balancer errors](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-troubleshooting.html)

## Mac lab · See it happen in about 15 minutes

### A. Watch a working request

```bash
dig example.com A +noall +answer
curl -sSv --http1.1 --max-time 10 -o /dev/null https://example.com/
```

In the `dig` output, look for an IP at the end of an `A` record. The number before `IN A` is the remaining TTL in seconds.

In the curl output, read just these lines on your first pass. The exact wording can vary.

```text
* Host example.com:443 was resolved.
* Connected to example.com (...) port 443
* SSL certificate verify ok.
> GET / HTTP/1.1
< HTTP/1.1 200 OK
```

Read that as “I found an address, I connected, I verified the certificate, I asked for the page, and I got a reply.” The `>` line is what curl sends. The `<` line is what it receives. [How to read curl’s verbose output](https://everything.curl.dev/usingcurl/verbose/index.html)

### B. See what changes when the problem moves

In **Terminal tab 1**, make a tiny file called `health` and start a web server that’s reachable only from your Mac.

```bash
lab_dir=$(mktemp -d)
printf 'ok\n' > "$lab_dir/health"
python3 -m http.server 8765 --bind 127.0.0.1 --directory "$lab_dir"
```

Leave that tab running. If `8765` is already in use, change it to `8766` in all the lab commands. [Python’s local HTTP server](https://docs.python.org/3.14/library/http.server.html)

Open **Terminal tab 2** and try these one at a time.

```bash
lsof -nP -iTCP:8765 -sTCP:LISTEN
curl -si --max-time 3 http://127.0.0.1:8765/health
curl -si --max-time 3 http://127.0.0.1:8765/missing
curl -sSv --max-time 3 https://127.0.0.1:8765/health
```

Look at what you changed and what came back:

- **`/health` gives `200` and `ok`.** Python is listening and found the file you asked for.
- **`/missing` gives `404`.** You used the same address and port. Python is still there. The only thing you changed was the path.
- **`https://` gives `Connected`, followed by a TLS error.** The same TCP connection still works. This time you tried to start a TLS conversation with a server that speaks plain HTTP.

Now press **Ctrl+C in tab 1** to stop Python. Go back to tab 2 and try the original request again.

```bash
curl -sSi --max-time 3 http://127.0.0.1:8765/health
```

You should get a connection failure, usually curl error `(7)`. You asked for the same file that worked before. This time Python is gone, so there’s nobody on that port to answer. In tab 1, clean up with `rm "$lab_dir/health"` and then `rmdir "$lab_dir"`.

**When you run it, send me what you saw.** Explain the `404`, the TLS error, and the refusal in whatever words make sense to you. I’ll help you check the reasoning, then push the completed Day 1 notes to your private repo.