# Choreboard: A Privacy-First Chore Chart, Built for One Kid

## Why I built this instead of using an app

LittleNugget needed a chore chart. The app-store options all wanted the same thing: an account, a cloud sync, usually ads or an in-app purchase wall, and a data-collection policy written for a company's lawyers, not for a parent trying to figure out if their kid remembered to feed the fish. None of that is proportionate to what the problem actually is — a list of chores, a way to tick them off, and a small reward at the end.

So I built Choreboard: a self-hosted chore chart, served from my home server, running on an iPad mounted on the wall. No account. No cloud. No third party ever sees that LittleNugget exists, let alone what her chores are or when she does them.

This write-up is less about the code (it's a small Flask app, nothing exotic) and more about the design decisions behind it, and the handful of real engineering lessons that came out of a project I actually had to keep working for a real user, not just get running once for a screenshot.

## The design constraint that shaped everything: minimise what's collected, and where it lives

Before writing any code, I set one rule: collect the least data possible, and keep whatever's collected as close to the child's own device as it could reasonably be. That rule produced two concrete decisions:

**The server only ever holds the chore *configuration*** — the list of chores, their names, emoji, and the reward text. That's it. It's stored in a single JSON file (`config.json`) on the server, editable through a parent-only admin panel. There's no user table, no accounts, no login for the child at all — the iPad simply displays whatever's in that file.

**Completion state — which chores are done today — never leaves the device.** It's stored in the iPad's browser `localStorage`, not on the server. The server has no record of when a chore was ticked off, how long it took, or any behavioural pattern at all. If someone compromised the server entirely, the worst they'd learn is a list of chore names and a reward description — nothing about the child's actual behaviour, habits, or timing.

This is privacy-by-design in miniature: not a policy document, just an architecture that makes certain data simply not exist anywhere it could leak from.

## How it actually works

- **Backend:** Python 3.11 + Flask, containerised with Docker, running on my home server.
- **Frontend:** Vanilla HTML/CSS/JS — no framework, because the whole UI is a grid of tappable cards and a couple of screens; a framework would be solving a problem I don't have.
- **Config flow:** the admin panel reads and writes `config.json` via a small `GET`/`POST /api/config` API. The child-facing display polls that same endpoint on load — no websockets, no push, just a simple fetch with a cache-busting timestamp.
- **Done-state flow:** ticks are written straight to `localStorage`. The daily list resets at midnight; the weekly list resets on a day I made configurable (more on why below).

It's a boring architecture on purpose. Boring is auditable. I can hold the entire data flow in my head, which matters more to me for something LittleNugget actually uses daily than it would for a portfolio toy project I'll never touch again.

## What actually went wrong (and what it taught me)

A tutorial project teaches you the happy path. A project LittleNugget actually uses every day for months teaches you the edge cases, because she finds every single one of them.

**Docker doesn't rebuild what you think it rebuilds.** My first instinct after editing the HTML templates was `docker restart`. Nothing changed — because the templates are baked into the image at *build* time, not read live from disk. I needed a proper rebuild step every time, which is obvious in hindsight and completely invisible the first time you hit it. Lesson: understand what's actually baked into your image versus what's mounted as a live volume, before you start debugging why your change "isn't working."

**A single misplaced import produced a 500 error that only showed up in one code path.** I'd referenced a module inside a route handler without importing it at the top of the file — Python let the rest of the app run fine, and it only blew up the moment that specific route was hit. Small thing, but it's a good reminder that "the app started successfully" and "the app works" are different claims.

**iOS treats a home-screen PWA and a Safari tab as genuinely different caching environments.** I wanted this to feel like a real app icon on the home screen, but `Cache-Control` headers that worked perfectly in a normal Safari tab were silently ignored once the same page was added to the home screen as a PWA — stale content kept showing up with no way to force a refresh from the OS UI. I ended up keeping it as a pinned Safari tab with a manual refresh button rather than fighting an undocumented platform quirk. Sometimes the right fix is admitting the platform won't do what you want and designing around it instead.

**localStorage looked like a fine idea for config too — until there was a second device.** My original design put *everything*, including the chore config, in the iPad's `localStorage`. That's fine until you want to edit a chore from your phone and see it show up on the iPad. I moved the config (but deliberately not the completion state) to the server for exactly that reason — a good illustration of "which data needs to sync across devices" and "which data should never leave a device" being two genuinely different questions, not the same question asked twice.

**iOS 12, on the older iPad this actually runs on, doesn't support the CSS `inset` shorthand.** Full-screen overlays needed four explicit properties (`top`, `left`, `width`, `height`) instead of the one-line shorthand I'd have used on a modern browser. A small thing, but a real reminder that "works on my machine" means nothing when your actual user's device is a hand-me-down.

## If this were a provider environment

This is a home project for one kid, not a system built for a registered NDIS provider or allied-health practice — but the same instincts scale, and it's worth being explicit about what would actually change if the "user" here were an NDIS participant rather than LittleNugget, under the Privacy Act and the NDIS Information Management Practice Standard:

- **Data minimisation would need to be a documented decision, not just an instinct.** The choice to keep completion-state device-local and never sync it to a server is exactly the kind of design decision a Practice Standard-compliant Information Management Plan requires providers to actually record and justify — not just quietly do.
- **"No accounts" doesn't mean "no access control" at provider scale.** For one family, a shared admin panel with no login is a reasonable trade-off. For a provider with multiple staff and participants, that same panel would need role-based access and an audit trail of who changed what configuration and when.
- **Device-local storage raises its own retention question at scale.** On a single family iPad, an unbounded `localStorage` history isn't a real risk. Across a fleet of shared devices in a provider setting, "what's stored on the device, for how long, and what happens if the device is lost or reassigned" becomes a real data-retention and device-management question that needs an actual policy, not an assumption.
- **The admin/parent boundary is a stand-in for a much stricter support-worker/participant boundary.** In a provider context, the equivalent of my "parent admin panel" would need proper authentication, and almost certainly a break-glass/audit story for support staff accessing or changing a participant's records — not the trust-based, single-household model this project relies on.
- **A breach here means a family finds out their kid's chore list leaked. A breach in a provider environment means a genuine NDIS participant's information is exposed** — a categorically different risk tier that the Practice Standard's incident-notification obligations exist specifically to address.

I'm not presenting this as a compliance authority — I'm a first-semester Diploma of IT student applying the *logic* of these standards at home scale, because it's the same underlying discipline (minimise what you collect, know where it lives, know who can touch it) whether the stakes are a chore chart or a participant's records.
