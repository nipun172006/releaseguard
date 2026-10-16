# Frontend Architecture

ReleaseGuard's frontend is a React and TypeScript single-page application. It is intentionally small, but its responsibilities are separated so the UI remains understandable as the project gains Docker, CI/CD, Kubernetes, and observability.

## File responsibilities

```text
frontend/src/
├── App.tsx                         Dashboard state and workflow coordination
├── api.ts                         All HTTP communication and API error parsing
├── types.ts                       Shared release, statistics, filter, and payload types
├── components/
│   ├── ReleaseDrawer.tsx          Detail, readiness, lifecycle, and delete actions
│   └── ReleaseForm.tsx            Create and edit form with live score preview
└── styles.css                     Responsive visual system and component states
```

`App.tsx` coordinates the screen, but it does not contain raw request code. `api.ts` gives the rest of the interface typed functions such as `getReleases`, `createRelease`, and `updateRelease`. This boundary prevents every component from implementing its own fetch and error-handling rules.

## Data flow

```text
User action
    |
    v
React event handler
    |
    v
Typed function in api.ts
    |
    v
FastAPI validates input and applies business rules
    |
    v
PostgreSQL commit
    |
    v
Typed ReleaseRecord response
    |
    v
React updates the detail view and refreshes statistics/table data
```

The frontend knows which lifecycle buttons are useful to display and disables `Mark ready` when mandatory evidence is missing. FastAPI still validates every transition. Keeping the backend authoritative means a script, another UI, or a manipulated browser cannot bypass the release rules.

## Dashboard workflow

1. On load, React requests `/health`, `/api/releases/stats`, and `/api/releases`.
2. The sidebar shows whether the local API is connected.
3. The six statistic cards use the aggregated backend response rather than recalculating portfolio data in the browser.
4. Search and filter values are sent to the list endpoint, so filtering continues to work when the database grows beyond what is currently visible.
5. Selecting a table row opens a release drawer with its computed score, risk, blockers, checklist, metadata, and allowed lifecycle actions.
6. Readiness switches send small updates immediately. The backend recalculates score and risk and returns the new release representation.
7. Create and edit forms send the complete editable release payload. A live score preview helps the operator understand the five evidence weights before saving.

## State handling

The interface explicitly handles four operational states:

- **Loading:** skeleton rows preserve the table layout while requests are pending.
- **Empty:** the user sees either a first-release action or guidance to clear active filters.
- **Error:** failed requests show an explanation and a retry action.
- **Success:** mutations show a short confirmation message and refresh dashboard data.

Requests use `AbortController`, so obsolete requests are cancelled when filters change or the component unmounts. This prevents a slower, older response from overwriting newer screen state.

## Responsive behavior

- Desktop widths use a persistent dark navigation sidebar, six statistic cards, and a full release table.
- Tablet widths move navigation into a compact top bar and reduce nonessential table columns.
- Mobile widths use two-column or single-column statistic cards, card-like release rows, and full-screen form/detail surfaces.
- Reduced-motion preferences disable nonessential transitions and animations.

## Why calculated fields remain read-only

`readiness_score`, `risk_level`, `blockers`, and `is_ready` are rendered from the API response. The form never submits them because they are derived business facts, not user input. This keeps one source of truth and prevents the browser and database from disagreeing about deployment safety.
