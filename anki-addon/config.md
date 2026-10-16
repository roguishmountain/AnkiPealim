The add-verb dialog saves its choices here each time you click OK.

- `deck_id`: id of the deck used last time.
  The dialog starts on it when opened from the deck list;
  on a deck's page it starts on that deck instead.
  `null` means start on Anki's current deck.
- `tenses`: which tenses to make cards for.
  Any of `"INF"` (infinitive), `"AP"` (present), `"PERF"` (past), `"IMPF"` (future), `"IMP"` (imperative).
  Passive forms of present, past and future are included when the verb has them.
