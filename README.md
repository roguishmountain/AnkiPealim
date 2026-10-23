# Pealim Cards

An Anki add-on that makes flashcards for Hebrew words from [pealim.com](https://www.pealim.com).
Click **Pealim** in Anki's top toolbar, type a word in Hebrew (e.g. `ספר`),
choose a deck and, for verbs, the tenses you want,
and it adds cards with the forms in Hebrew (with nikkud) on one side
and their English meanings on the other.
If several words match, you pick one from a list.

| Part of speech | Hebrew side | English side |
|---|---|---|
| Verb | forms of each chosen tense, one note per tense or person | meanings, then the tense |
| Noun | singular and plural, then the gender: `(ז׳)` or `(נ׳)` | meanings, then `(noun)` |
| Adjective | masculine and feminine, singular and plural | meaning, then `(adjective)` |
| Preposition, pronoun, numeral | the base form, then forms with suffixes, one note per person | meanings, then the part of speech |
| Anything else (e.g. adverbs) | the word | its meaning, then the part of speech |

Notes use Anki's built-in **Basic (and reversed card)** note type
and are tagged `pealim`.
Anki must be online to reach Pealim.

Built for Anki 25.09 and later.
Not affiliated with Pealim or Anki.

## Package it

The add-on is the **contents** of `anki-addon/` (not the folder itself),
without `__pycache__/` or `meta.json`, zipped and named `ankipealim.ankiaddon`.

In PowerShell 7, from the repo folder:

```powershell
Get-ChildItem anki-addon\* -Exclude __pycache__, meta.json | Compress-Archive -DestinationPath ankipealim.zip -Force
Move-Item ankipealim.zip ankipealim.ankiaddon -Force
```

## Add it to Anki

1. In Anki, open **Tools → Add-ons**.
2. Click **Install from file…** and choose `ankipealim.ankiaddon`.
   (Double-clicking the file also works.)
3. Restart Anki.

The **Pealim** link then appears in the top toolbar,
next to Decks · Add · Browse · Stats · Sync.

## How it was made

Built with Claude Code.
I set the design and reviewed and tested each change in Anki;
Claude Code wrote most of the code.
