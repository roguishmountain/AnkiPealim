# Pealim Verb Cards

An Anki add-on that makes flashcards for Hebrew verbs from [pealim.com](https://www.pealim.com).
Click **Pealim** in Anki's top toolbar, type an infinitive in Hebrew (e.g. `לקרוא`),
choose a deck and the tenses you want,
and it adds cards with the forms in Hebrew (with nikkud) on one side
and their English meanings on the other.

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
