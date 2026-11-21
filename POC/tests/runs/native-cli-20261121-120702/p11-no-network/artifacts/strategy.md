# Strategie: diagnostika liveness a fairness protipříkladů v TLA+

## Rozhodnutí Skilleto a místní důkazy

Stav k 21. 11. 2026. Cílem je doplnit opakovatelný specialistický postup pro
triage TLA+ protipříkladů včetně refinementu. Tato úloha dodává jeho proveditelný
návrh; neinstaluje skill ani model checker.

- **Decision: `NO_INSTALL`.** Pro sepsání strategie stačí místní čtení a zápis.
  Specialistická schopnost ani její ověření tím nejsou dokončené.
- **Search performed: ne; `DISCOVERY_UNAVAILABLE`.** Uživatel zakázal síť,
  `npx` a jiné instalátory. Nebyly spuštěny ani jejich příkazy pro seznam,
  nápovědu či kontrolu verze. Nebyla použita webová ani konektorová náhrada.
- **Capability gap:** rozbor periodických stop, přesné vyhodnocení WF/SF,
  rozlišení chyby modelu od chybějícího předpokladu a kontrola refinement mappingu.
- **Evidence:** `README.md` výslovně požaduje TLA+ refinement, fairness a liveness
  triage a uvádí, že projekt neobsahuje TLC ani ekvivalent. Inventura místních
  souborů nalezla README a `.agents/skills/skilleto/` s referencemi, žádné
  `.tla`, `.cfg`, stopy ani JAR. Dostupný katalog skillů neobsahuje specialistu
  na TLA+. `Get-Command java,tlc` nevrátil příkaz v aktuálním PATH; to nevylučuje
  nástroje uložené jinde. Uživatelské disky ani další cache nebyly prohledávány.
- **Candidate: žádný ověřený. Fit: N/A. Risk: N/A.** Absence discovery není
  důkaz, že vhodný veřejný skill neexistuje. Žádný název, repozitář ani revize
  externího kandidáta se nepovažují za ověřené.
- **Scope:** Codex, projekt
  `D:\Projects\Skilleto\.test-lab\skilleto-cli-lab-506f62bfcc4c\p11-no-network`.
  Pro tuto úlohu vzniká pouze `strategy.md`.
- **Authorization:** místní čtení a zápis strategie povoleny; síť a instalátory
  zakázány; instalace nebyla vyžádána ani schválena.
- **Provisioning: not attempted. Activation: N/A.** Skilleto bylo přečteno
  a použito jako rozhodovací workflow; žádný nový skill není aktivován.

Rozhodnutí vychází z místních instrukcí
`.agents/skills/skilleto/SKILL.md` a referencí `workflow.md`, `discovery.md`,
`semantic-matching.md`, `security-policy.md` a `provisioning.md`.

## Možnosti doplnění

| Varianta | Proveditelnost nyní | Přínos a omezení |
| --- | --- | --- |
| Ruční postup podle tohoto dokumentu | Ano, bez dalších nástrojů | Umožní rozbor dodané úplné stopy; nenahradí její vygenerování a ověření checkerem. |
| Vlastní projektový skill tvořený instrukcemi | Lze připravit offline jako následný úkol | Zachytí doménové kontroly a šablonu závěru bez runtime závislostí. Musí projít odbornou kontrolou a ověřením na příkladech. |
| Převzetí úplného balíčku z místního archivu | Podmíněně, pokud bude dodán | Teď žádný takový kandidát není doložen. Nutná kontrola původu, všech souborů a závislostí před případným převzetím. |
| Hledání na skills.sh a následná instalace | V této úloze nedostupné | Odložit do jiné úlohy s výslovně změněnými omezeními; neobcházet zákaz jiným registrem nebo nástrojem. |

Nejmenší užitečné doplnění je vlastní instrukční workflow s ručně ověřenými
ukázkami. Samostatnou závislostí pro automatické ověření je TLC a kompatibilní
Java; skill sám tuto schopnost neposkytne. Nyní se nic nestahuje ani neinstaluje.

## Postup použitelný offline

### 1. Převzít reprodukovatelné vstupy

Pro každý případ založit samostatný adresář, například `diagnostics/<case>/`,
a uložit kopie specifikace `.tla`, importovaných modulů, konfigurace `.cfg`,
kontrolované formule a úplného výstupu checkeru. Připojit verzi a příkaz
checkeru, pokud jsou známé, a otisky vstupních souborů pomocí
`Get-FileHash -Algorithm SHA256 -LiteralPath <soubor>`.

Zaznamenat `Init`, `Next`, n-tici `vars`, konstanty, fairness předpoklady,
constraints, symetrii, případné zobrazení stavů a refinement mapping.
Rozlišit invariant, temporální vlastnost a předpoklad vložený do specifikace.
Nezaměnit kontrolovanou vlastnost s předpokladem, který by ji vynutil.
Původní vstupy zachovat; hypotézy ověřovat na oddělených kopiích.

V současném projektu tyto vstupy chybí. Lze připravit šablonu rozboru,
ale nelze diagnostikovat konkrétní běh ani tvrdit výsledek model checkingu.

### 2. Určit typ svědectví

- Porušení safety lze doložit konečným prefixem. U invariantu vyznačit první
  chybný stav; u akční podmínky první chybný přechod.
- U liveness hledat nekonečné chování popsané prefixem a opakující se smyčkou
  (lasso), případně explicitním nekonečným stutteringem. Zapsat index začátku
  smyčky a přechod z posledního stavu zpět na její začátek.
- Konečný výpis bez informace o pokračování není sám o sobě důkaz porušení
  liveness. Deadlock hlášený TLC je samostatný výsledek; při temporálním rozboru
  lze zvlášť posoudit stutteringové pokračování dovolené `[Next]_vars`.

Pro každou hranu identifikovat možné akce z `Next` podle jejich formulí.
Více akcí může platit současně; nevynucovat jediný název. Nestačí odhad
z popisku stopy nebo z jediné změněné proměnné.

### 3. Vyhodnotit kontrolovanou liveness formuli

Zapsat přesnou formuli a její negaci; nezužovat každý problém na eventualitu.
Pro konečné lasso jsou praktické tyto kontroly:

- `<>P` selže, pokud `P` neplatí nikde v prefixu ani ve smyčce.
- `[]<>P` selže, pokud ve smyčce není žádný stav s `P`.
- `P ~> Q` (tj. `[](P => <>Q)`) selže, pokud existuje výskyt `P`, od něhož
  už nikdy nenastane `Q`. Svědek může být v prefixu i ve smyčce; kontrolovat
  budoucnost přes uzavírací hranu a další opakování cyklu.

U složené temporální formule rozebrat jednotlivé operátory, případně použít
ověřený checker. Neprohlašovat obecnou temporální formuli za vyhodnocenou
jen podle těchto tří vzorů.

### 4. Sestavit fairness tabulku

Pro každou fairness podmínku přepsat přesný výraz `WF_vars(A)` nebo
`SF_vars(A)`. Fairness se vztahuje k nestutteringové akci
`<<A>>_vars == A /\ (vars' # vars)`; záleží tedy i na zvolené n-tici `vars`.

| Položka | Co zaznamenat |
| --- | --- |
| Stav cyklu | Index a hodnoty potřebné pro guard a omezení akce |
| Enabledness | Zda platí `ENABLED <<A>>_vars`, včetně zdůvodnění |
| Výskyt akce | Zda konkrétní hrana splňuje `<<A>>_vars`, i hrana uzavírající cyklus |
| WF/SF závěr | Předpoklad splněn, porušen, nebo nezjištěn; uvést svědky |

`ENABLED` znamená existenci přípustného následného ohodnocení, nikoli to,
že akce byla zvolena nebo je příštím krokem ve stopě. Samotný guard nemusí
stačit: pravá strana akce může být nesplnitelná. Z neúplné projekce stavů
enabledness nelze vždy určit.

Na přesně periodickém cyklu:

- `WF_vars(A)` selže, pokud je nestutteringová akce enabled v každém stavu
  cyklu a na žádné hraně cyklu nenastane.
- `SF_vars(A)` selže, pokud je enabled alespoň v jednom stavu cyklu a na
  žádné hraně cyklu nenastane. Opakováním cyklu je enabled nekonečně často.
- Výskyt na hraně cyklu se opakuje nekonečně; jednorázový výskyt v prefixu
  neodstraňuje pozdější starvation. Občasné vypnutí akce může stačit k tomu,
  aby WF nic nevynucovala, zatímco SF ji stále vynucuje.

Tyto zkratky platí pro doložený konečný periodický cyklus. U libovolného
nekonečného chování použít definice: WF reaguje na trvalou enabledness od
nějakého okamžiku, SF na enabledness nekonečně často.

Zkontrolovat všechny fairness předpoklady skutečně použité ve specifikaci.
Pokud údajný protipříklad některý porušuje, není platným svědkem této
specifikace: prověřit konfiguraci, přepis stopy a zvolenou n-tici proměnných.
Chybějící údaje označit jako neznámé, nikoli jako splněný předpoklad.

### 5. Rozlišit příčinu a zkontrolovat refinement

Rozhodovat podle konkrétních svědků:

1. **Akce není enabled:** prozkoumat guard, invariant, deadlock a podmínky
   prostředí. Fairness nezajistí provedení nemožné akce.
2. **Akce je ignorována:** posoudit starvation a realistický předpoklad
   plánování. SF přidat pouze s argumentem, že ji implementace či prostředí
   skutečně poskytuje; nejde o automatickou opravu neúspěšné liveness.
3. **Akce probíhá, pokrok chybí:** hledat livelock, chybně definované dosažení
   cíle nebo chybějící argument poklesu dobře založené míry.
4. **Refinement:** zobrazit každý konkrétní stav přes mapping do abstraktního
   stavu. Ověřit abstraktní `Init`, simulaci každého kroku pomocí
   `[NextAbs]_varsAbs` a zvlášť požadované temporální vlastnosti.

Interní konkrétní kroky mohou být abstraktní stuttering. Nekonečně mnoho
takových kroků může zablokovat abstraktní pokrok, i když je simulace kroků
v pořádku. Fairness konkrétní akce automaticky neimplikuje fairness
abstraktní akce; doložit vztah enabledness, výskytů a případného argumentu
o ukončení interní práce. Původní cyklus nezahazovat kompresí projekce.

Prověřit i artefakty modelování: příliš silné předpoklady, omezení prostoru
stavů, symetrii nebo nastavení nevhodné pro liveness v použité verzi nástroje.
Získat konzervativní referenční běh bez těchto redukcí, jakmile bude nástroj
dostupný. Po zesílení předpokladů ověřit nevakuóznost: existuje přípustné
chování a důležitý spouštěč vlastnosti je dosažitelný.

### 6. Uzavřít případ a ověřit opravu

Výstup uložit například do `diagnostics/<case>/analysis.md` se strukturou:
identita a otisky vstupů; přesná vlastnost; prefix a cyklus; tabulka fairness;
první doložená příčina; minimální změna a její zdůvodnění; výsledek ověření;
zbývající neznámé. Oddělit pozorování, hypotézu a potvrzený závěr.

Je-li TLC už lokálně dostupné z důvěryhodného zdroje, použít izolovaný adresář
a zaznamenaný příkaz podle jeho lokální dokumentace. Typický tvar přímého
spuštění je `java -cp <lokalni-tla2tools.jar> tlc2.TLC -config <Model.cfg> <Spec>`;
konkrétní cesty, moduly, volby i kompatibilitu verze ověřit před spuštěním.
Tento příkaz se nyní nespouští: Java ani JAR nejsou doloženy. Nespouštět
wrapper, který nástroje sám stahuje, a nedoplňovat chybějící závislosti.

Nejprve reprodukovat původní problém. Potom ověřit stejnou vlastnost nad
upraveným modelem, relevantní safety invarianty a dosažitelnost spouštěče.
Uchovat původní i nový výstup. Úspěch omezeného modelu není důkaz pro všechny
velikosti systému. Bez checkeru označit výsledek „ruční rozbor, neověřeno TLC“.

## Plán trvalého doplnění a přejímací kritéria

1. Z tohoto postupu připravit v následném úkolu instrukční skill, pracovně
   `tla-liveness-triage`, se `SKILL.md`, šablonou rozboru a lokálními příklady.
   Jde o návrh vlastního názvu, nikoli nalezený externí skill. Navržený cíl je
   `<projekt>/.agents/skills/tla-liveness-triage/`; nyní se nevytváří.
2. Připravit malé specifikace s konfigurací a předem ručně odvozeným výsledkem:
   porušení invariantu; ignorovaná trvale enabled akce bez WF a s WF;
   střídavě enabled akce ignorovaná při WF, ale vyloučená SF; nekonečná interní
   smyčka pod refinement mappingem; vakuózní úspěch s nedosažitelným spouštěčem.
   U případů WF/SF zajistit, aby ostatní zvolené akce dovolovaly uvedený cyklus.
3. U každého příkladu požadovat správnou klasifikaci, uzavírací hranu,
   enabledness a výskyty na cyklu, zdůvodnění příčiny a zdůvodnění případné
   změny fairness. Přidat neúplnou stopu, u níž správný výsledek zní „nelze
   rozhodnout“. Kde je to možné, očekávání zkontroluje druhý odborný čtenář.
4. Po dostupnosti schváleného lokálního TLC spustit příklady a porovnat
   výsledky s ručními očekáváními. Do té doby označovat skill jako návrh bez
   automatické validace. Výsledek checkeru ani odbornou revizi nepředstírat.
5. Pokud bude místo vlastního workflow dodán externí balíček, před převzetím
   doložit původ a přesnou revizi, přečíst celé instrukce, reference, skripty
   a závislosti. Posoudit shodu s těmito příklady, kompatibilitu s Codexem a
   Windows a všechny vedlejší účinky. Neúplně prověřený kandidát má riziko
   `UNKNOWN` a jeho převzetí se zablokuje. Nevykonávat jeho setup při revizi.
6. Případné nasazení řešit jako samostatný konkrétní krok s potřebnou
   autorizací přesného obsahu a projektových cest podle pravidel Skilleto.
   Ověřit kolize, zachovat existující soubory, porovnat nasazený obsah s revizí
   a zvlášť ověřit dostupnost v katalogu aktuální relace. Přítomnost souboru
   na disku není důkaz aktivace; podle hostitele může být nutná nová relace.

Tuto úlohu lze převzít, pokud strategie obsahuje doložené omezení discovery,
žádného smyšleného kandidáta, proveditelnou offline diagnostiku a ověřitelná
kritéria budoucího doplnění. Automatické model checking ověření a instalace
zůstávají výslovně neprovedené.
