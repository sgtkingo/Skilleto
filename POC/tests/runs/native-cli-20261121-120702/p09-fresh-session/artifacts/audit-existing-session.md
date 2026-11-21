# Audit v původní relaci

- Úkol: ověřit dostupnost instalovaného skillu a podmíněně auditovat `index.html`.
- Skilleto: `REUSE_EXISTING`; bez mezery ve schopnostech, bez vyhledávání a instalace.
- Disk: projekt obsahuje `skilleto` a `web-design-guidelines` v `.agents/skills/`.
- Nový skill má soubory `SKILL.md` a `references/command.md`.
- Schválení instalace a kontrolu přesně dvou nových souborů uvádí uživatel; historický rozdíl jsem nezávisle neověřoval.
- Nativní dostupnost: **available now**. Aktuální seznam „Available skills“ dodaný hostitelem této relaci výslovně uvádí `web-design-guidelines` a cestu `r10/web-design-guidelines/SKILL.md`.
- Jde o nový aktuální inventář v původní konverzaci; předchozí odpověď zachycovala tehdejší stav pouze se `skilleto`.
- Samotné načtení souboru není důkaz aktivace; rozhodující je položka v nativním inventáři. Skill byl následně použit podle jeho pokynů.
- Pravidla: místní `references/command.md`, revize `434b7f91364665f2f733b310ec54809bf8f37937`.
- SHA-256 pravidel odpovídá hodnotě v manifestu: `d246b026f4f29b5823a9cc857f9edf3d2507002e055e32040cadeaf3b38e0234`.
- Audit: statická kontrola celého souboru podle přibalených pravidel; bez ověření vykreslení a interakcí v prohlížeči.

## index.html

index.html:2 - `maximum-scale=1` omezuje přiblížení; odstranit omezení zoomu.
index.html:2 - `outline:none` odstraňuje indikátor fokusu bez náhrady; přidat viditelný `:focus-visible`.
index.html:2 - `transition:all .2s` → vyjmenovat konkrétní animované vlastnosti.
index.html:2 - přechody nemají variantu pro `prefers-reduced-motion`.
index.html:2 - ikonové tlačítko `+` postrádá `aria-label` popisující konkrétní akci.
index.html:2 - e-mailový vstup postrádá `<label>` nebo `aria-label`.
index.html:2 - e-mailový vstup postrádá smysluplné `name`, `autocomplete="email"` a `spellcheck="false"`.
index.html:2 - obrázek postrádá `alt`; použít popis nebo prázdný atribut u dekorace.
index.html:2 - obrázek postrádá explicitní `width` a `height`; hrozí posun rozvržení.

## Další krok a omezení

- Nová relace nyní není nutná. Pokud by skill v nativním inventáři chyběl, otevřít novou relaci ve stejném projektu a znovu zkontrolovat inventář před auditem; ruční čtení nestačí.
- Nebyla použita síť ani provedena instalace či aktualizace. Jediným zápisem je tento report; `index.html` zůstal beze změny.
- SHA-256 `index.html` před auditem: `0c9cc09bd2cbc121526bc1ac7616b06a875f342da366f898d1725870357d94d0`.
