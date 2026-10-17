# Week 2: Capture Emails and Test LLM Calls

## This Week's Goals

1. **Capture emails on your laptop:** Connect your inbox through Nylas so every new email is delivered to your local app and saved.
2. **Test LLM calls:** Run small examples that call different kinds of language models.

## Before You Start

Complete the Week 1 homework first:

- `.env` contains `NYLAS_CLIENT_ID`, `NYLAS_API_KEY`, `NYLAS_API_URI`, and `EMAIL`
- The Nylas Dashboard lists `http://localhost:5010/oauth/exchange` as a callback URI

Install the dependencies:

```bash
uv sync
```

## Part 1: Capture Emails on Your Laptop

When this part is done, each new email flows to your laptop like this:

```text
New email → Nylas → Cloudflare tunnel → main.py /events → saved to requests/events/
                                                        → shown at localhost:8000
```

Already finished Part 1 and coming back to test again? See [Start a New Session](docs/start-new-session.md).

### Step 1: Connect Your Email Account

Start the authentication helper:

```bash
cd app/config
uv run config_auth.py
```

1. Visit `http://localhost:5010/nylas/auth` to begin authentication.
2. Log in with your email account and allow access.
3. Copy the returned grant ID into `.env`:

   ```env
   NYLAS_GRANT_ID=your_grant_id
   ```

4. Restart the helper so it loads the new value.
5. Visit `http://localhost:5010/nylas/recent-emails` to view your latest emails.
6. Visit `http://localhost:5010/nylas/send-email` to send a test email to your own account.

If `NYLAS_GRANT_ID` is already set, `/nylas/auth` returns that ID and skips the login. To connect a different account, clear the value first.

The flow looks like this:

```text
Browser → Nylas login → http://localhost:5010/oauth/exchange → grant ID
```

Nylas only redirects to callback URIs registered in the dashboard, which is why the Week 1 homework added it.

### Step 2: Configure a Tunnel

Nylas must reach your local server over the internet to deliver webhooks. We use a [Cloudflare quick tunnel](https://github.com/cloudflare/cloudflared), which needs no account.

Install it once:

```bash
brew install cloudflared
```

On Windows, use `winget install --id Cloudflare.cloudflared` instead.

In a separate terminal, run:

```bash
cloudflared tunnel --url http://localhost:8000
```

Copy the `https://...trycloudflare.com` URL it prints into `.env`:

```env
SERVER_URL=https://your-tunnel-name.trycloudflare.com
```

Keep this terminal open. A new URL can take up to a minute to start working. Each time you restart `cloudflared` you get a new URL, so update `SERVER_URL` and register a new webhook. See the [troubleshooting guide](docs/webhook-troubleshoot-guide.md#2-expired-or-changed-tunnel-url) for how to check whether the tunnel is down.

### Step 3: Start the Server

In another terminal:

```bash
cd app
uv run main.py
```

Visit `http://localhost:8000`. You should see the Nylas Webhooks page.

### Step 4: Create the Webhook

```bash
cd app/config
uv run config_webhook.py
```

This registers `SERVER_URL/events` with Nylas for new-email events and prints a webhook secret. Add it to `.env`:

```env
WEBHOOK_SECRET=your_webhook_secret
```

**Restart `main.py` so it loads the secret.** `main.py` reads `.env` only when it starts, and it uses the secret to verify that each email came from Nylas. Without a restart, every email returns `401`. Then open **Notifications** in the Nylas Dashboard to confirm the webhook is listed.

When you register a new webhook for a new tunnel URL, delete the old one in the dashboard.

### Step 5: Test the Webhook

1. Send an email to the address in `EMAIL`.
2. Watch the `main.py` terminal for the incoming request and a `200` status.
3. Refresh `http://localhost:8000` to see the new message.

Each event is also saved as JSON in `requests/events/`. These files contain email content and are excluded from Git.

`main.py` and the tunnel must both be running to receive emails. If the webhook stops working or returns errors, see the [Webhook Troubleshooting Guide](docs/webhook-troubleshoot-guide.md).

To see what each file in Part 1 does, see [Email Capture Files](docs/email-capture-files.md).

## Part 2: Test LLM Calls

The `week2/` folder has standalone quickstarts for each type of model call. See [week2/README.md](week2/README.md) for the dependencies, API keys, and run commands.

| File | What it shows |
|------|---------------|
| `week2/openai-quickstart.py` | Hosted generative model with an API key |
| `week2/structured_output.py` | Typed output with Pydantic and OpenAI |
| `week2/jev-quickstart.py` | Decision model with Choice, Score, and Noul |
| `week2/ollama-quickstart.py` | Open source model running locally, no key |
| `week2/pydantic-introduction.ipynb` | Pydantic basics |
