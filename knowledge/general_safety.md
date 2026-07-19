# General Pet Care Safety Notes

## Priority defaults
When in doubt, medication and feeding tasks should always be marked "high"
priority. Grooming and enrichment tasks default to "low" or "medium" unless
the owner's text signals urgency (e.g. "matted fur", "vet said to do this
today", "hasn't eaten").

## Duration sanity bounds
No single daily pet care task should reasonably take longer than 60 minutes.
If a request implies something longer (e.g. "take to the groomer"), treat it
as an outing and cap the estimated duration at 60 minutes with a note that
travel time is not included.

## Recurrence signals
Words like "every day", "daily", "each morning" imply is_recurring=true,
frequency="daily". Words like "once a week", "weekly" imply
is_recurring=true, frequency="weekly". A one-time request (e.g. "give him a
bath this week") should default to is_recurring=false unless the owner
explicitly asks for a repeating schedule.

## Unsafe or out-of-scope requests
This assistant only schedules routine pet care tasks. It should never
generate a task that involves administering an unprescribed medication,
withholding food/water, or any instruction that contradicts basic animal
welfare. If a request is ambiguous or unsafe, prefer a conservative
interpretation and flag it in the reasoning text rather than guessing.
