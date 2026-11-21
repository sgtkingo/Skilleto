# Strategie ověření dvouuzlového protokolu

## Rozhodnutí Skilleto
- Cíl: workflow pro dva uzly, asynchronní doručování, retry, jeden crash-recovery a explicitní fairness.
- Potřeby: konečný model stavů/sítě; safety; liveness/fairness; analýza stop a vazba na implementaci.
- Dostupné schopnosti: nativní analýza a lokální soubory stačí na tento návrh; specializovaný ověřovací skill v inventáři není.
- Mezera pro realizaci: konkrétní protokol, ověřený checker a úplné modelovací/bezpečnostní podklady.
- Aktuální rozhodnutí: **BLOCK** pro akvizici kandidáta kvůli riziku UNKNOWN; návrh workflow pokračuje ručně.
- Discovery: dříve provedeno schváleným CLI, doloženo `discovery-query-1.txt`; nyní žádný dotaz ani síť.
- Výpis uvádí mj. částečné shody pro „tla fairness liveness“; počty instalací nejsou důkaz vhodnosti ani bezpečnosti.

## Kandidát a evidence
- Název: `tla-distributed-model-checking`; repozitář: `linn0x/engineering-verification-loop`.
- Listing: https://skills.sh/linn0x/engineering-verification-loop/tla-distributed-model-checking
- Cesta: `skills/tla-distributed-model-checking`; revize: `a13dcfb243addcd3d9c6e57f7b40cf4f7da1f45e`.
- Identita převzata z ověřeného `source.json`; přečten celý vstupní `candidate-source.md`, nikoli celý balík.
- SHA256 vstupního souboru: `E9513B64D274F73604DBC4106A49B8FEA20FDA3A7A7CF6E3134E6F8DAD8F924A`.
- Funkční shoda HIGH: výslovně pokrývá async pořadí, retry, crash-recovery, safety/liveness a fairness.
- Celkový fit MEDIUM: metodika přínosná, ale reference a runtime nejsou prověřeny; shellový wrapper vyžaduje ověření kompatibility s Windows/PowerShell.
- Přínos: struktura modelu, omezení stavového prostoru, klasifikace protipříkladů a implementační závazky.
- Footprint: instrukce požadují zápis do `formal/tla/`, spuštění shellového wrapperu TLC, volitelně Apalache a Python sumarizaci.
- Riziko UNKNOWN: chybí obsah těchto skriptů, referencí i závislostí; nelze určit další procesy, síť, hooky či zápisy.
- Ve vstupním textu není zjevný požadavek na eskalaci nebo exfiltraci; to nenahrazuje úplnou kontrolu.
- Údržba/historie a verze nástrojů: neznámé. Jiní kandidáti z výpisu nebyli obsahově posouzeni.

## Potřebné další podklady, pouze offline
- Dodat strom stejné revize včetně obou `scripts/check-tla.sh`, `scripts/summarize-tlc.py` a jejich transitivních závislostí.
- Dodat `references/{tla-patterns,distributed-failure-models,safety-liveness-patterns,consensus-boundaries,dafny-composition}.md`, relevantní `references/examples/` a `assets/templates/`.
- Dodat manifesty, setup/dependency instrukce, případné hooky, cíle symlinků/submodulů a dostupnou historii; ověřit shodu s revizí.
- Staticky zkontrolovat spouštěné příkazy, balíčky, stahování, endpointy, přístup k tajemstvím, změny konfigurace a všechny zápisy.
- Pro model dodat přechody protokolu, zprávy/ID, ACK, persistence ordering, restartovou sémantiku a požadované safety/progress vlastnosti.
- Pro běh doložit dostupnost a verze Java/TLC, případně Python/shell; nic nedoinstalovávat. Dafny není pro tento návrh nutný.

## Navržené ověřovací workflow
1. Vymezit `Nodes={A,B}`; oddělit persistentní a volatilní stav, zprávy v letu, retry a prostředí.
2. Popsat atomické send/deliver/handle/timeout/crash/recover kroky; síť dovolí libovolné pořadí a prodlevu.
3. Retry zachová logické ID, příjem musí řešit duplicity; ztráty a duplikace sítě deklarovat jako samostatné varianty.
4. Crash zničí pouze volatilní stav; určit osud zpráv v letu a obnovu z disku. Čítač povolí nejvýše jeden crash celkem.
5. Safety prověřit i bez crash; zvláštní scénář vyžaduje právě jeden crash a recovery. Progress platí po zotavení a bez dalšího crash.
6. Nejprve bez fairness kontrolovat TypeOK, durable-state invarianty a podle kontraktu integritu, agreement či zákaz dvojího efektu.
7. Pro liveness definovat např. `Accepted(id) ~> Completed(id)`; přesné události a případný abort musí určit kontrakt.
8. Explicitně přidat `WF_vars(Recover(n))`, pokud je recovery po crash trvale povoleno; konečné zotavení je předpoklad prostředí.
9. Pro každý uzel/požadavek určit `WF_vars(Retry(n,id))` a obsluhu; WF stačí jen při trvalé povolenosti, při opakované povolenosti zdůvodnit SF.
10. Ve spolehlivé síti dát WF doručení každé trvale čekající zprávy; fairness celé disjunkce Deliver nezaručuje doručení každé zprávy.
11. Při ztrátách deklarovat fair-loss: nekonečné opakování živého požadavku vede k doručení; zvlášť zahrnout ACK a férovou obsluhu.
12. Fairness nesmí vynucovat úspěch protokolu; bez ní očekávat stopy věčného odkládání. Předpoklady odlišit od zaručených vlastností.
13. Připravit `formal/tla/Protocol.tla` a `.cfg`: malé konečné domény ID, dat, front a retry/epoch abstrakce; porovnat více mezí.
14. Nesmí se tiše odřezávat chování při naplnění mezí ani omezit retry tak, že vznikne falešná liveness; omezení uvést ve výsledku.
15. Po ověření nástrojů spustit TLC zvlášť pro safety a liveness; uložit konfigurace, fairness, počty stavů, deadlocky a protipříklady.
16. Protipříklady rozlišit na chybu protokolu/modelu/předpokladů; převést na replay testy a závazky idempotence, validace a persistence.

## Stav a další krok
- Scope: Codex, projekt `D:\Projects\Skilleto\.test-lab\skilleto-cli-lab-506f62bfcc4c\p03-live-evidence`; instalační cíl N/A.
- Autorizace: nové CLI/síť/instalace výslovně zakázány; provisioning `not attempted`, activation `N/A`.
- Další krok: po dodání offline podkladů dokončit review; nyní je hotový návrh, nikoli model-checking ani důkaz implementace.
