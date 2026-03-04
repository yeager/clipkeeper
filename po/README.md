# Translations

ClipKeeper uses [Transifex](https://app.transifex.com/danielnylander/clipkeeper/) for translation management.

## How to Translate

1. Create a free account on [Transifex](https://www.transifex.com/)
2. Join the [ClipKeeper project](https://app.transifex.com/danielnylander/clipkeeper/)
3. Select your language and start translating

## For Developers

### Regenerate the .pot file

```bash
xgettext --language=Python --keyword=_ --keyword=N_ \
    --output=po/clipkeeper.pot \
    --package-name=ClipKeeper \
    --package-version=0.1.0 \
    --copyright-holder="Daniel Nylander" \
    clipkeeper/*.py
```

### Push source strings to Transifex

```bash
tx push -s
```

### Pull translations from Transifex

```bash
tx pull --minimum-perc 20
```

## Available Languages

- Danish (da)
- Dutch (nl)
- Finnish (fi)
- French (fr)
- German (de)
- Italian (it)
- Norwegian Bokmål (nb_NO)
- Polish (pl)
- Portuguese (Brazil) (pt_BR)
- Spanish (es)
- Swedish (sv)

## Notes

- Do NOT edit .po files manually — use Transifex
- Source strings are in English
- Minimum 20% completion before syncing translations
