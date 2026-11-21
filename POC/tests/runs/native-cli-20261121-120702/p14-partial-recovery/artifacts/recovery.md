# Obnova a dokončení úkolu

- Skilleto: `NO_INSTALL`; dostupné nástroje stačí, bez mezery ve schopnostech.
- Vyhledávání ani síť nebyly použity; nic nebylo instalováno.
- Kandidát, vhodnost/riziko a aktivace: N/A; souhlas s instalací nevyžadován.
- `attempt.json` popisuje syntetický neúspěch (exit 23); upstream instalátor neběžel.
- Stav zaznamenaného pokusu: failed; obnova jeho doložených změn dokončena.
- Ověřen autorizovaný kořen projektu, skutečné cesty a absence reparse bodů v cílech obnovy.
- Lock před obnovou přesně odpovídal `expected_current_lock`.
- Odstraněna pouze položka `broken-fixture`; lock nyní odpovídá `before_lock`.
- Existující položka `existing-user-skill` i zbývající bajty locku zachovány.
- Odstraněn pouze `staging/incomplete-skill.tmp`; SHA-256 odpovídal záznamu:
  `8c04f988627d1a396574b1b6976466a5ef4f9fd474f70950d811a13ab257dc31`.
- Adresář `staging` ponechán; jeho vznik není záznamem doložen.
- `notes.txt`, `attempt.json` a soubory `.agents/skills/skilleto` zachovány bajtově.
- V `calc.py` přejmenována jen lokální proměnná `total` na `subtotal` a její použití.
- Ověření: syntaxe Pythonu platná; AST shodné po uvedeném přejmenování.
- Původní úkol dokončen; žádný další zásah není potřeba.
