# Revize rezervačního protokolu

## Rozsah a závěr

Revize vychází z `README.md`, `specs/Reservations.tla` a
`specs/verification-notes.md`. Projekt obsahuje malý formální model, nikoli
implementaci služby. Nelze proto posoudit databázové transakce, API ani souběh
reálných klientů. Specifikace již nyní porušuje vlastní vlastnost `Safety`:
jediný kus lze rezervovat opakovaně a potvrzením rezervací dostat zásobu pod nulu.

Nic nebylo instalováno a původní specifikace nebyla změněna. Níže uvedený návrh
opravy je podklad k ověření, nikoli již zapracovaná změna.

## Hlavní rizika

| Priorita | Nález a důkaz | Dopad a doporučení |
| --- | --- | --- |
| Kritická | `Reserve` kontroluje pouze `stock > 0` a ponechává `stock` beze změny (`specs/Reservations.tla:5`). | Libovolně mnoho rezervací na jeden kus. Vymezit význam zásoby a vázat rezervace na zbývající kapacitu. |
| Kritická | `Commit` kontroluje jen `holds > 0` (`specs/Reservations.tla:6`). | Po přerezervování odečte i z nulové zásoby a poruší `Safety`. Samotné přidání `stock > 0` by zápornou zásobu zastavilo, ale ponechalo nesplnitelné rezervace. Je nutné opravit přijetí rezervace. |
| Vysoká | `Safety == stock >= 0` nezachycuje závazky vůči rezervacím (`specs/Reservations.tla:8`). | Stav `(stock, holds) = (1, 2)` je podle této vlastnosti bezpečný, ale již nemůže splnit všechny rezervace. Přidat typový a kapacitní invariant. |
| Vysoká | Není definována temporální `Spec`, fairness ani požadavek živosti; chybí konfigurace TLC. | Akce samy neurčují, jaký pokrok musí nastat. Definovat stuttering, férovost zpracování a konkrétní temporální vlastnost. |
| Vysoká | Opakováním `Reserve` vzniká `(1, n)` pro libovolné přirozené `n`. | Původní model má nekonečný dosažitelný prostor. Úplný konečný průchod nelze očekávat; libovolný limit `holds` není důkazem původního modelu. |
| Střední | Po `Reserve; Commit` je stav `(0, 0)` bez povolené akce. | TLC může ohlásit deadlock, přestože může jít o očekávané vyprodání. Explicitně definovat terminální chování a odlišit je od uvázlých rezervací. |
| Střední | Model má jen dva čítače. | Neověří vlastníka rezervace, dvojité potvrzení stejné rezervace, idempotenci, expiraci ani pády. Před implementací určit, které z těchto situací protokol musí pokrýt. |

### Konkrétní protipříklad

Stav je dvojice `(stock, holds)`:

| Krok | Akce | Stav | Význam |
| --- | --- | --- | --- |
| 0 | `Init` | `(1, 0)` | Jeden kus bez rezervací. |
| 1 | `Reserve` | `(1, 1)` | První rezervace. |
| 2 | `Reserve` | `(1, 2)` | Druhá rezervace na tentýž kus. |
| 3 | `Commit` | `(0, 1)` | Zbývá závazek bez zásoby. |
| 4 | `Commit` | `(-1, 0)` | `Safety` je nepravdivá. |

Všechny přechody splňují současné stráže. Jde o nejkratší porušení `Safety`;
přerezervování je viditelné už po druhé akci. Fairness tento konečný bezpečnostní
problém neopraví.

## Doporučená interpretace a oprava

Zachovat `stock` jako počet dosud neprodaných kusů včetně rezervovaných a `holds`
jako počet aktivních rezervací. Volná kapacita je pak `stock - holds`.
`Reserve` musí vyžadovat `stock > holds`; `Commit` nadále sníží oba čítače.
Základní invarianty jsou:

```tla
TypeOK == /\ stock \in Nat
          /\ holds \in Nat
Capacity == holds <= stock
```

Jiná možná interpretace je volná zásoba, kterou sníží již `Reserve`; pak by ji
`Commit` nesměl odečíst znovu. Tyto dvě interpretace nesmějí být smíchány.

Pro první interpretaci lze připravit následující samostatný ověřovací model.
`InitialStock` je parametr, `Done` dovoluje klidový přechod pouze při vyprodání
bez závazků. Soubor v tomto kroku není vytvářen.

```tla
---- MODULE ReservationsChecked ----
EXTENDS Naturals
CONSTANT InitialStock
ASSUME InitialStock \in Nat
VARIABLES stock, holds
vars == <<stock, holds>>
Init == /\ stock = InitialStock
        /\ holds = 0
Reserve == /\ stock > holds
           /\ holds' = holds + 1
           /\ UNCHANGED stock
Commit == /\ holds > 0
          /\ stock' = stock - 1
          /\ holds' = holds - 1
Done == /\ stock = 0
        /\ holds = 0
        /\ UNCHANGED vars
Next == Reserve \/ Commit \/ Done
Spec == Init /\ [][Next]_vars /\ WF_vars(Commit)
TypeOK == /\ stock \in Nat /\ holds \in Nat
Capacity == holds <= stock
Safety == stock >= 0
Drain == (holds > 0) ~> (holds = 0)
====
```

Induktivní argument: `Init` splňuje typy i kapacitu. `Reserve` díky přísné
nerovnosti zvýší `holds` nejvýše na `stock`. `Commit` snižuje oba čítače stejně;
z `holds > 0` a kapacity plyne `stock > 0`, takže oba zůstanou nezáporné.
`Done` stav nemění. To je argument pro navrženou opravu, nikoli pro současný model.

## Postup ověření

1. **Potvrdit kontrakt.** Odsouhlasit význam `stock`, možnost nulové počáteční
   zásoby, terminální stav a to, zda jsou požadavky odmítané při plné kapacitě.
   Určit, zda jsou zrušení, expirace, opakování požadavků a pády součástí cíle.
   Jejich nepřítomnost nyní znamená omezení modelu, nikoli ověřenou správnost.

2. **Reprodukovat chybu původního modelu.** V budoucím připraveném prostředí TLC
   použít pro `Reservations.tla` tuto minimální konfiguraci:

   ```text
   INIT Init
   NEXT Next
   INVARIANT Safety
   CHECK_DEADLOCK FALSE
   ```

   Vypnutí kontroly deadlocků zde slouží pouze k izolované reprodukci záporné
   zásoby. Očekávaným výsledkem je uvedená čtyřkroková stopa při průchodu do šířky.
   Uchovat ji jako regresní scénář. Pro analýzu terminálních stavů spustit
   samostatně také kontrolu deadlocků. Žádný nástroj se nyní neinstaluje.

3. **Ověřit opravu bez fairness.** Nejprve kontrolovat `TypeOK`, `Capacity` a
   `Safety` nad `INIT Init` a `NEXT Next` v navrženém modelu. Bezpečnost nesmí
   záviset na předpokladech plánování. Pro `InitialStock = 0, 1, 2, 3, 4, 5`
   úplně projít prostor a kontrolu deadlocků ponechat zapnutou díky `Done`.
   Bez dalších proměnných má oprava pro zásobu `N` právě
   `(N + 1)(N + 2)/2` dosažitelných stavů; to pomůže odhalit nechtěné omezení
   průchodu. Konečné instance doplňují uvedený induktivní argument pro obecné `N`.

4. **Ověřit živost zvlášť.** Pro navržený model použít například:

   ```text
   CONSTANT InitialStock = 2
   SPECIFICATION Spec
   INVARIANT TypeOK
   INVARIANT Capacity
   INVARIANT Safety
   PROPERTY Drain
   CHECK_DEADLOCK TRUE
   ```

   `WF_vars(Commit)` znamená, že trvale povolené potvrzování nemůže být navždy
   ignorováno. V opraveném modelu zůstává při nenulových rezervacích povolené;
   slabá fairness tedy stačí. Při konečné zásobě bez doplňování se rezervace
   postupně vyčerpají. Bez této fairness může povolený stuttering ponechat
   `(1, 1)` navždy, a `Drain` selže. Ověřit obě varianty jako pozitivní
   a negativní kontrolu. Silná fairness není pro tuto vlastnost nutná.
   `Drain` nezaručuje příchod požadavků ani vyprodání zásoby; bez rezervací platí
   prázdně. Neprokazuje ani obsloužení konkrétního klienta, protože chybějí identity.

5. **Prověřit hranice a sílu kontrol.** Pro zásobu 0 nesmí být povoleno
   rezervování ani potvrzení. Pro zásobu 1 musí po rezervaci zůstat povoleno
   pouze potvrzení a po něm klidový stav. Pro větší zásobu ověřit střídání akcí
   i vytvoření všech rezervací před potvrzováním. Návrat stráže na `stock > 0`
   musí znovu vyvolat porušení `Capacity` a následně `Safety`; odstranění fairness
   musí odhalit selhání živosti. Omezení stavového prostoru nesmí odstranit tyto
   protipříklady. Hloubkově omezený průchod označit výslovně jako neúplný.

6. **Třídit výsledky a uchovat reprodukci.** U každého běhu zaznamenat revizi
   modelu, konfiguraci, verzi TLC/Javy, parametry, počty stavů, ukončení a stopu.
   U bezpečnostního selhání najít první porušený invariant; u živosti rozlišit
   prefix a opakující se cyklus, povolené akce a fairness. U deadlocku rozlišit
   očekávané vyprodání od nevyřízených rezervací. Přerušený běh ani běh s ořezem
   nevydávat za důkaz. Nejprve opravit model nebo vysvětlit předpoklad, teprve pak
   měnit vlastnost; neskrývat chybu zeslabením kontrol.

7. **Navázat na implementaci, až bude existovat.** Určit atomické body rezervace
   a potvrzení a mapování databázového stavu na proměnné modelu. Podmínku kapacity
   a zápis rezervace provést atomicky; jinak dva klienti mohou oba přečíst volný
   kus. Podle kontraktu doplnit identity, idempotenci a selhání a prověřit je
   modelem i integračními scénáři. Výsledek nad čítači sám o sobě neověřuje službu.

## Co bylo skutečně ověřeno

- Staticky byly přečteny všechny tři návrhové soubory projektu.
- Dostupným Pythonem byl proveden průchod do šířky původních přechodů do hloubky
  nejvýše 6; nejkratší nalezené porušení `Safety` má výše uvedené 4 akce.
- Stejným pomocným překladem akcí byl úplně prohledán návrh s opravenou stráží
  pro počáteční zásoby 0 až 5. Počty stavů byly 1, 3, 6, 10, 15 a 21;
  všude platilo `0 <= holds <= stock <= InitialStock`. Jediným stavem bez
  přechodu před doplněním `Done` byl `(0, 0)`.
- Tento pomocný průchod nekontroluje syntaxi TLA+, temporální sémantiku ani
  fairness. TLC, parser TLA+ a kontrola živosti nebyly spuštěny. Kontrola příkazů
  `java`, `tlc`, `tla2tools` je nenalezla na PATH a projekt neobsahuje JAR ani
  konfiguraci TLC; tím není vyloučena instalace nástrojů jinde v počítači.
- Doplňkově bylo v [oficiální implementaci odečítání v TLC](https://github.com/tlaplus/tlaplus/blob/master/tlatools/org.lamport.tlatools/src/tlc2/module/Naturals.java)
  ověřeno, že samotné `EXTENDS Naturals` nezabrání zápornému výsledku `0 - 1`.
  Import modulu nenahrazuje invariant nezáporné zásoby.

Za dokončené ověření návrhu lze považovat až reprodukovaný negativní test,
schválený kontrakt, průchod invariantů opraveného modelu, vysvětlené terminální
chování a pozitivní i negativní kontrolu živosti se zaznamenanými předpoklady.

## Použité schopnosti a omezení

Rozhodnutí místního workflow `skilleto`: **NO_INSTALL**. Pro tento malý model
postačují dostupné čtení souborů, přímý rozbor přechodů a pomocný Python.
Potřeby byly analýza bezpečnosti, předpoklady živosti a návrh reprodukovatelného
ověření; pro vypracování tohoto posudku nebyla zjištěna mezera vyžadující nový
skill. Online hledání skillů neproběhlo, žádný kandidát nebyl vybírán (shoda a riziko
kandidáta: N/A), instalace ani aktivace nebyly prováděny. Uživatel instalace
výslovně zakázal. Provedení budoucích běhů TLC zůstává otevřeným krokem;
posudek nevyžaduje změnu oprávnění ani instalaci k dokončení.
