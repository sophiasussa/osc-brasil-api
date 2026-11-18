# osc-brasil-api

## Analytics and organization completeness

`GET /analytics` returns organization totals and grouped counts. It accepts
`state`, `status`, `activityArea`, `legalNature`, `foundedFrom`, and `foundedTo`;
these filters use the same predicates as `GET /organizations`.
`legalNature` is the integer code from `LegalNature.code`. The `legalNatures`
options in `GET /filters` include both `code` and display `name`; send the code,
not the display name, when filtering either endpoint.

The organization `search` parameter compares names, CNPJ, and municipality
names. For accented input, it also searches a diacritic-free variant of the
query so it can match stored spellings with or without accents. This
normalization is applied only to the query; response values are returned as
stored.
This does not reconstruct accents already absent from stored records. There
are no ETL scripts or source datasets in this repository to establish or fix
the upstream cause.

The details response from `GET /organizations/{id}` and the Analytics response
include a `completeness` object. The currently calculable categories are:

- `general_data`: 14 model fields: legal name, CNPJ, trade name, legal-nature
  code, matrix/branch, registration status, MOSC removal flag, foundation
  date, closing date and year, address, municipality code, latitude, and
  longitude. A string is complete when non-blank after trimming; other values
  are complete when non-null. `False` and zero count as present.
- `activity_areas`: one item each for having at least one linked activity area
  and at least one linked subarea. Either association can contribute
  independently.

The repository contains no ETL mappings or source CSVs, and the organization
model has no description, governance/work, project/program, or funding fields.
Those four categories are therefore returned with `percentage: null`, not
treated as zero. They are excluded from `average`; the average is the arithmetic
mean of the calculable category percentages. Analytics first computes each
organization's category percentages, then averages those per organization.
With no matching organizations, the average and calculable category
percentages are `null`.

Example requests:

```http
GET /analytics?state=SP&foundedFrom=2000&foundedTo=2020
GET /organizations/123
```

Each response contains `completeness.average` and a list of category objects
with `key`, `label`, and nullable `percentage`. Analytics also returns
`summary`, `byState`, `byActivityArea`, `byFoundationYear`, and `byLegalNature`.

## Rate limiting

The API uses a process-local sliding-window rate limiter to reduce excessive
requests. By default, each client IP may make 100 requests per 60 seconds.
Each accepted request is timestamped; only timestamps inside the rolling
window count, and the oldest active request determines when capacity returns.
Configure it through the environment:

```env
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_ENABLED=true
```

When the limit is exceeded, the API returns HTTP 429 with
`{"detail":"Rate limit exceeded. Please try again later."}` and a
`Retry-After` header containing the number of seconds until the oldest request
in the active window expires. `/health` is excluded so liveness checks remain
available during traffic spikes.

The client IP is taken from the ASGI connection (`scope["client"][0]`); the
middleware does not trust `X-Forwarded-For` or other forwarding headers. When
the ASGI client address is missing, those requests share an explicit fallback
bucket and are still rate-limited (so they can affect one another). No
trusted-proxy configuration is currently present. Behind a reverse proxy, the
ASGI connection IP may identify the proxy rather than the original client;
configure trusted proxy handling explicitly before using proxy-provided
client addresses.
Set `RATE_LIMIT_ENABLED=false` to disable limiting.

**The rate limiter uses process-local memory. Its counters are not shared
between application processes, workers, containers, or pods. All counters are
lost when the application restarts.** This is suitable for the current
single-instance deployment; multi-instance deployments need shared storage
such as Redis.

Run the test suite with `pip install -r requirements-dev.txt` followed by
`pytest`.