# Project And Milestone Mapping

Read this reference before turning source records into Granoflow project and
monthly milestone proposals.

The purpose is to keep the import organized without creating one project per
thread or one milestone per minor topic.

## Project Mapping

Prefer explicit signals in this order:

1. existing Granoflow project id or title;
2. repository name;
3. workspace or folder name;
4. product, client, or initiative name stated in the source;
5. repeated topic cluster only when no stronger signal exists.

Do not create a separate project for every thread. Merge records into the same
project when they share the same repository, workspace, folder, or explicit
project name.

Ask for confirmation in the preview when:

- one source could belong to two active projects;
- the project title would expose private or customer-sensitive text;
- fewer than two records support a new inferred project;
- the inferred project would duplicate an existing Granoflow project.

## Project Proposal Fields

Each proposal should include:

- stable project key;
- title;
- source signals;
- create or reuse decision;
- confidence: high, medium, or low;
- dedupe key;
- notes and confirmation question when needed.

## Monthly Milestone Mapping

Use monthly milestones for imported historical work:

- title format: `YYYY-MM`;
- create only for months with retained task candidates;
- do not create empty milestones;
- reuse an existing project/month milestone when tools can resolve it safely;
- keep old archived milestone descriptions as final snapshots unless a safe
  app-owned archive/context API says otherwise.

If a source spans multiple months, split task candidates by the best available
work date. If only a broad date range exists, use the end date for completed
work and record the uncertainty in the preview.

## Milestone Proposal Fields

Each proposal should include:

- project key;
- month;
- title;
- create or reuse decision;
- task count;
- dedupe key;
- notes and uncertainty.

## Existing Object Resolution

Before proposing creates, use available Granoflow tools to list or resolve
projects and milestones. Reuse is preferred when:

- title matches exactly;
- normalized repository or folder signal matches;
- the existing project description clearly represents the same work area;
- an existing milestone for the same project/month already exists.

Do not force a reuse when the existing title matches but the description or
source evidence points to a different project.

## Context Notes For Later Backfill

During mapping, collect evidence for later context backfill:

- project purpose;
- imported history summary;
- important decisions;
- recurring lessons;
- active risks or blockers;
- current phase;
- next expected work.

Do not write descriptions during mapping. Description updates happen only after
import readback.
