"use client"
import React from "react"
import Link from "next/link"

const CodeBlock = ({ children }: { children: React.ReactNode }) => (
  <pre className="whitespace-pre-wrap rounded-md bg-muted p-3 text-sm overflow-x-auto">
    <code>{children}</code>
  </pre>
)

function Badge({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-full bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground">
      {children}
    </span>
  )
}

function CopyButton({ value }: { value: string }) {
  const [copied, setCopied] = React.useState(false)
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(value)
      setCopied(true)
      setTimeout(() => setCopied(false), 1200)
    } catch (_) {}
  }
  return (
    <button onClick={copy} className="text-xs underline">
      {copied ? "Copied" : "Copy"}
    </button>
  )
}

export default function ApiDocsPage() {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1"
  const IMAGE_BASE_URL = process.env.NEXT_PUBLIC_IMAGE_BASE_URL || "http://localhost:8000/backend-fast-api/streaming"

  return (
    <div className="mx-auto max-w-6xl p-0 md:p-6">
      <div className="relative overflow-hidden rounded-none md:rounded-xl bg-gradient-to-br from-indigo-600/10 via-fuchsia-500/10 to-teal-400/10 border">
        <div className="px-6 py-10 md:px-10 md:py-14">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl md:text-4xl font-semibold tracking-tight">Cerrora API</h1>
              <p className="mt-3 text-sm md:text-base text-muted-foreground max-w-3xl">
                Public endpoints for fetching base/valid times and generated Cerrora prediction images.
                Designed for research and reproducible visualization workflows.
              </p>
            </div>
            <Link className="text-sm underline" href="/">Back to app</Link>
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-3 text-sm">
            <div className="flex items-center gap-2">
              <Badge>API Base</Badge>
              <span className="font-mono break-all">{API_BASE_URL}</span>
              <CopyButton value={API_BASE_URL} />
            </div>
            <div className="flex items-center gap-2">
              <Badge>Image Base</Badge>
              <span className="font-mono break-all">{IMAGE_BASE_URL}</span>
              <CopyButton value={IMAGE_BASE_URL} />
            </div>
          </div>
        </div>
        <nav className="border-t bg-background/60 px-6 py-3 md:px-10">
          <ul className="flex flex-wrap gap-4 text-sm">
            <li><a className="underline" href="#overview">Overview</a></li>
            <li><a className="underline" href="#endpoints">Endpoints</a></li>
            <li><a className="underline" href="#quickstart">Quickstart</a></li>
            <li><a className="underline" href="#errors">Errors</a></li>
            <li><a className="underline" href="#planned">Planned APIs</a></li>
          </ul>
        </nav>
      </div>

      <section id="overview" className="space-y-3 mt-8">
        <p>
          This page documents the public API for accessing the Cerrora weather prediction service.
          Use these endpoints to retrieve prediction frames and visualize them as images.
        </p>
        <ul className="list-disc pl-6 space-y-2">
          <li><span className="font-semibold">Base API URL</span>: <span className="font-mono">{API_BASE_URL}</span></li>
          <li><span className="font-semibold">Image Base URL</span>: <span className="font-mono">{IMAGE_BASE_URL}</span></li>
          <li><span className="font-semibold">Model</span>: <span className="font-mono">cerrora</span></li>
          <li><span className="font-semibold">Variables</span>: <span className="font-mono">temp_wind</span>, <span className="font-mono">geo</span>, <span className="font-mono">rain</span>, <span className="font-mono">sea_level</span></li>
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Cerrora Variables</h2>
        <div className="rounded-md border p-4">
          <ul className="text-sm space-y-1">
            <li><span className="font-mono">temp_wind</span> → <span className="font-mono">t2m, 10u, 10v</span> (composite image)</li>
            <li><span className="font-mono">geo</span> → <span className="font-mono">z</span> (500 hPa geopotential height)</li>
            <li><span className="font-mono">rain</span> → <span className="font-mono">tp</span> (precipitation)</li>
            <li><span className="font-mono">sea_level</span> → <span className="font-mono">msl</span> (mean sea level pressure)</li>
          </ul>
        </div>
      </section>

      <section id="endpoints" className="space-y-3 mt-10">
        <h2 className="text-xl font-semibold">Core Endpoints</h2>
        <div className="space-y-6">


          <div>
            <h3 className="font-medium">List base times</h3>
            <p className="text-sm">Fetch available base initialization times for a variable.</p>
            <CodeBlock>
{`GET {API_BASE_URL}/base-times?variableType=temp_wind

200 OK → [ { "label": "Tue 05 Jan 2021 00 UTC", "value": "1609804800" }, ... ]`}
            </CodeBlock>
          </div>

          <div>
            <h3 className="font-medium">List valid times for a base time</h3>
            <p className="text-sm">Given a base time, returns valid forecast targets. Pass variableType and queryTime (ISO or unix seconds).</p>
            <CodeBlock>
{`GET {API_BASE_URL}/valid-times?variableType=temp_wind&queryTime=1609804800

200 OK → [ [ { "label": "Tue 05 Jan 2021 06 UTC", "value": "1609826400" }, ... ] ]`}
            </CodeBlock>
          </div>

          <div>
            <h3 className="font-medium">Request predicted images</h3>
            <p className="text-sm">Returns URLs to generated or cached images for the requested frames. The URL points to the static image server.</p>
            <CodeBlock>
{`POST {API_BASE_URL}/data/{variable}
Content-Type: application/json

{
  "baseTime": 1609804800,
  "validTime": [1609826400, 1609830000]
}

200 OK → { "images": [ { "timestamp": "1609804800_1609826400", "url": "${IMAGE_BASE_URL}/cerrora/tempWind/1609804800_1609826400_image.webp" }, ... ] }`}
            </CodeBlock>
            <p className="text-xs text-muted-foreground">Variables: temp_wind | geo | rain | sea_level</p>
          </div>

          <div>
            <h3 className="font-medium">Static image URLs</h3>
            <p className="text-sm">Images are served from the static image base URL. Structure:</p>
            <CodeBlock>
{`${IMAGE_BASE_URL}/{model}/{directory}/{timestamp_base}_{timestamp_valid}_image.webp

Where model = cerrora and directory per variable:
- temp_wind → tempWind
- geo → geopotential
- rain → rain
- sea_level → seaLevelPressure`}
            </CodeBlock>
          </div>
        </div>
      </section>

      <section id="quickstart" className="space-y-3 mt-10">
        <h2 className="text-xl font-semibold">Quickstart</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="rounded-md border p-4">
            <h3 className="font-medium mb-2">cURL</h3>
            <CodeBlock>
{`# 1) Get base times
curl -s "${API_BASE_URL}/base-times?variableType=temp_wind"

# 2) Get valid times for a selected base time (replace VALUE)
curl -s "${API_BASE_URL}/valid-times?variableType=temp_wind&queryTime=VALUE"

# 3) Request images
curl -s -X POST "${API_BASE_URL}/data/temp_wind" \
  -H "Content-Type: application/json" \
  -d '{"baseTime": VALUE, "validTime": [VALUE, VALUE]}'`}
            </CodeBlock>
          </div>
          <div className="rounded-md border p-4">
            <h3 className="font-medium mb-2">TypeScript (fetch)</h3>
            <CodeBlock>
{`const API = "${API_BASE_URL}";

async function getBaseTimes() {
  const res = await fetch(API + "/base-times?variableType=temp_wind");
  return await res.json();
}

async function getValidTimes(base: number) {
  const res = await fetch(API + "/valid-times?variableType=temp_wind&queryTime=" + base);
  return await res.json();
}

async function getImages(base: number, times: number[]) {
  const res = await fetch(API + "/data/temp_wind", {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ baseTime: base, validTime: times })
  });
  return await res.json();
}`}
            </CodeBlock>
          </div>
        </div>
      </section>

      <section id="errors" className="space-y-3 mt-10">
        <h2 className="text-xl font-semibold">Errors</h2>
        <ul className="list-disc pl-6 space-y-1 text-sm">
          <li>400 Invalid model or variable type</li>
          <li>404 Image not found or still generating</li>
          <li>500 Backend data loading or visualization error</li>
          <li>504 Image generation timed out (long-running plot)</li>
        </ul>
      </section>

      <section id="planned" className="space-y-3 mt-10">
        <h2 className="text-xl font-semibold">Planned APIs (Cerrora as a Service)</h2>
        <p className="text-sm">To allow users to create predictions with their own input data while we host the model:</p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="rounded-md border p-4 space-y-3">
            <h3 className="font-medium">Authentication</h3>
            <ul className="list-disc pl-6 text-sm space-y-1">
              <li><span className="font-mono">POST /api/v1/auth/token</span> → issue API token (email/password or OAuth).</li>
              <li><span className="font-mono">GET /api/v1/auth/me</span> → whoami, quotas, roles.</li>
            </ul>
            <CodeBlock>
{`# API keys or bearer tokens
Authorization: Bearer <token>
or
x-api-key: <key>`}
            </CodeBlock>
          </div>

          <div className="rounded-md border p-4 space-y-3">
            <h3 className="font-medium">Data ingestion & uploads</h3>
            <ul className="list-disc pl-6 text-sm space-y-1">
              <li><span className="font-mono">POST /api/v1/uploads</span> (multipart or pre-signed URL negotiation).</li>
              <li><span className="font-mono">GET /api/v1/uploads/:id</span> → status/metadata.</li>
            </ul>
            <CodeBlock>
{`POST /api/v1/uploads (multipart/form-data)
fields: file, kind=(zarr|netcdf|npy), notes
→ { "uploadId": "upl_123", "bytes": 1048576 }`}
            </CodeBlock>
          </div>

          <div className="rounded-md border p-4 space-y-3">
            <h3 className="font-medium">Prediction jobs</h3>
            <ul className="list-disc pl-6 text-sm space-y-1">
              <li><span className="font-mono">POST /api/v1/predict</span> → start a job using an upload or external URI.</li>
              <li><span className="font-mono">GET /api/v1/jobs/:id</span> → status/logs; <span className="font-mono">GET /api/v1/jobs/:id/results</span>.</li>
              <li><span className="font-mono">DELETE /api/v1/jobs/:id</span> → cancel job.</li>
            </ul>
            <CodeBlock>
{`POST /api/v1/predict
{
  "model": "cerrora",
  "inputs": {
    "source": { "type": "upload", "id": "upl_123" },
    "time": "2021-01-05T00:00:00Z",
    "variables": ["t2m","10u","10v"],
    "region": { "lon": [-30, 40], "lat": [20, 65] }
  },
  "leadTimes": ["6h","12h","18h","24h"],
  "output": { "format": "image", "palette": "RdBu_r" }
}
→ { "jobId": "job_abc", "status": "queued" }`}
            </CodeBlock>
          </div>

          <div className="rounded-md border p-4 space-y-3">
            <h3 className="font-medium">Realtime & webhooks</h3>
            <ul className="list-disc pl-6 text-sm space-y-1">
              <li><span className="font-mono">WS /api/v1/ws/jobs/:id</span> → live events (queued, running, completed).</li>
              <li><span className="font-mono">POST /api/v1/webhooks</span> → register callback URL.</li>
            </ul>
            <CodeBlock>
{`event: job.update
data: { "jobId": "job_abc", "status": "completed" }`}
            </CodeBlock>
          </div>

          <div className="rounded-md border p-4 space-y-3">
            <h3 className="font-medium">Visualization service</h3>
            <ul className="list-disc pl-6 text-sm space-y-1">
              <li><span className="font-mono">POST /api/v1/visualize</span> → turn gridded arrays + lon/lat into styled maps.</li>
            </ul>
            <CodeBlock>
{`POST /api/v1/visualize
{
  "grid": { "lon": [[...]], "lat": [[...]], "values": [[...]] },
  "style": { "type": "contourf", "levels": 41, "cmap": "viridis" },
  "meta": { "timestamp": 1609804800 }
}
→ { "url": "${IMAGE_BASE_URL}/custom/1609804800_image.webp" }`}
            </CodeBlock>
          </div>

          <div className="rounded-md border p-4 space-y-3">
            <h3 className="font-medium">Discovery & operations</h3>
            <ul className="list-disc pl-6 text-sm space-y-1">
              <li><span className="font-mono">GET /api/v1/models</span> → list models, input schema, supported variables.</li>
              <li><span className="font-mono">GET /api/v1/variables</span> → per-model variable metadata.</li>
              <li><span className="font-mono">GET /api/v1/health</span>, <span className="font-mono">GET /openapi.json</span>, <span className="font-mono">GET /docs</span>.</li>
              <li><span className="font-mono">GET /api/v1/limits</span> → per-user quotas and rate limits.</li>
            </ul>
          </div>
        </div>

        <p className="text-xs text-muted-foreground">
          Security: prefer Bearer tokens (OAuth2/PKCE) or API keys via header (<span className="font-mono">x-api-key</span>).
          Inputs: uploads (NetCDF/Zarr) or URLs with signed access. Results: image URLs, NetCDF/Zarr, or JSON statistics.
        </p>
      </section>
    </div>
  )
}


