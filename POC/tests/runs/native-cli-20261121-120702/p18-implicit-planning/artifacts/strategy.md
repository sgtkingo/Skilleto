# Strategie property-based testování TTL cache

## Cíl a rozsah

Testovat `Cache` z `cache.py` jako stavový systém: generovat celé posloupnosti
zápisů a čtení, po každém kroku porovnávat pozorovatelné chování s referenčním
modelem a při selhání zachovat co nejmenší reprodukovatelnou posloupnost.
Prioritou jsou přepisy stejného klíče kolem expirace, které zmiňuje `README.md`.

Repozitář obsahuje jen `README.md` a `cache.py`, bez testovacího frameworku či
deklarovaných závislostí. Návrh lze realizovat pomocí `unittest`, `random`,
`itertools` a `json` ze standardní knihovny. Není potřeba nic instalovat,
stahovat ani používat skutečné hodiny, `sleep` či mockování času.

## 1. Kontrakt odvozený ze současného kódu

| Situace | Očekávané chování |
| --- | --- |
| `set(k, v, t, ttl)` | Nahradí předchozí zápis pro `k`; konec platnosti je `t + ttl`. |
| `get(k, t)`, pokud `k` nikdy nebyl zapsán | Vyvolá `KeyError`. |
| Poslední zápis má konec platnosti `e`, `t < e` | Vrátí poslední zapsanou hodnotu. |
| Poslední zápis má konec platnosti `e`, `t >= e` | Vrátí `None`. |
| Nový zápis po expiraci | Znovu nastaví hodnotu i dobu platnosti. |
| Čtení | Neprodlužuje TTL a neodstraňuje záznam. |

Expirace je na pravém okraji výlučná: právě v `e` už hodnota neplatí.
Expirovaný záznam se chováním liší od nikdy nezapsaného klíče. Testy nesmí
předpokládat, že oba případy vracejí `None`.

Základní doménou jsou malé řetězcové klíče, neměnné hodnoty (malá celá čísla,
řetězce a `None`) a celočíselné časy i TTL. Rozdílné hodnoty při přepisu musí
být časté, jinak může chybný návrat staré hodnoty zůstat skrytý.
Uložené `None` má stejný návrat jako expirace, proto hlavní scénáře používají
i hodnoty různé od `None`.

Kód nevaliduje záporné TTL ani návrat času zpět. Samostatné charakterizační
testy zachytí dnešní chování; případné budoucí zamítnutí těchto vstupů musí
být vědomou změnou kontraktu. Testy zatím nepožadují validaci typů, mazání,
omezení kapacity ani souběžnost: takové rozhraní projekt nemá.

## 2. Referenční model a vyhodnocování

Model uchovává historii událostí `Set(key, value, written_at, ttl)`, nikoli
kopii slovníku `Cache.values`. Při čtení vyhledá poslední událost pro klíč podle
pořadí operací, nikoli podle času nebo nejpozdější expirace:

```text
expected_get(history, key, now):
    last = poslední Set pro key v historii
    pokud neexistuje: Missing
    jinak pokud now - last.written_at < last.ttl: Value(last.value)
    jinak: Value(None)
```

Výpočet přes stáří záznamu poskytuje odlišný zápis stejné specifikace než
implementační `now < expires`. Přesto musí mít model vlastní ručně ověřené
příklady pro chybějící klíč, přepis a přesnou expiraci; samotná odlišná struktura
nezaručuje správnost modelu.

Runner převádí výsledek SUT na `Value(v)` nebo `Missing` při `KeyError`.
Jiná výjimka je selhání, nikoli ekvivalent chybějícího klíče. Po každém `Get`
porovná výsledek s modelem. `Set` musí skončit bez výjimky a teprve potom se
zapíše do modelové historie. Neočekávaná výjimka ze `Set` je také selhání.
Každý replay používá novou instanci cache a prázdný model.

Časový kurzor generátoru není součástí cache. Pomocná operace `Advance(dt)`
mění pouze tento kurzor. Před spuštěním runner rozvine scénář na konkrétní
`Set(..., now, ttl)` a `Get(..., now)`, aby šel přesně uložit a přehrát.

## 3. Vlastnosti, které musí držet

1. **Shoda s modelem pro každou sekvenci.** Včetně čtení chybějících klíčů,
   opakovaných čtení, expirace a libovolného počtu přepisů.
2. **Poslední zápis vítězí.** Nová hodnota a nové TTL zcela nahrazují starý
   záznam. Nevybírá se maximální expirace. Po expiraci nového zápisu se stará
   hodnota znovu neobjeví, ani kdyby původně platila déle.
3. **Hraniční časy.** Pro poslední zápis s expirací `e` vrací čtení v `e-1`
   jeho hodnotu a v `e`, `e+1` vrací `None`. V monotónním režimu používat
   zápis s `ttl >= 1`; pro `ttl <= 0` testovat především okamžik zápisu a dál.
4. **Izolace klíčů a instancí.** Zápisy do `b` nemění výsledky pro `a`.
   Stejný zápis v jedné instanci nesmí ovlivnit druhou instanci.
5. **Čtení nemění stav.** Vložení dalších čtení do sekvence nemění výsledky
   původních čtení. Opakované čtení ve stejném čase dává stejný výsledek;
   čtení těsně před expirací neposouvá její hranici.
6. **Stálost expirace při rostoucím čase.** Po expiraci vracejí další čtení
   stejného klíče `None`, dokud nepřijde další `Set`. Vlastnost vyžaduje
   neklesající časy a absenci přepisu.
7. **Posun časové osy.** Přičtení stejného celého `c` ke všem časům `now`
   při nezměněném TTL zachová výsledky i výjimky. Prověřit kladné i záporné
   posuny; žádné závislosti na skutečném aktuálním čase.
8. **Přejmenování klíčů.** Prosté vzájemně jednoznačné přejmenování klíčů
   zachová výsledky. Zachovat přitom vztahy stejných a různých klíčů.

Pro čisté čtení a izolaci porovnávat dvojice běhů na nových instancích.
Hlavní oracle má kontrolovat veřejné výsledky, nikoli přesnou strukturu
`values`; to umožní pozdější změnu reprezentace při zachování kontraktu.

## 4. Generování sekvencí a času

### Malé domény a řízené kolize

Výchozí délka sekvence je 1–100 operací, klíče z množiny `a`, `b`, `c`.
Většinu zápisů směřovat na již použitý klíč. Orientačně generovat 45 % `Set`,
45 % `Get`, 10 % `Advance`; tato rozdělení jsou nastavení generátoru,
nikoli požadavky na produkt. Vedle toho pravidelně vynutit čtení dosud
nezapsaného klíče a alespoň dva odlišné klíče v jedné sekvenci.

TTL vybírat hlavně z `0, 1, 2, 5`, doplnit širším rozsahem a velmi velkými
celými čísly. Záporné TTL vybírat v samostatné sadě. Časové kroky zvýhodňují
`0, 1, 2`, takže vznikají i zápisy a čtení ve stejném okamžiku.

### Dva oddělené časové režimy

- **Hlavní režim:** všechny časy operací neklesají. Generátor často míří na
  `e-1`, `e`, `e+1` posledního zápisu i na hranice přepsaných zápisů, pokud
  daný čas není před aktuálním kurzorem. Jinak vybere jinou dostupnou hranici.
- **Charakterizační režim:** časy mohou klesat. Protože `get` neodstraňuje
  záznam, dříve expirovaná hodnota se při dotazu do minulosti může znovu
  vrátit. Neaplikovat zde vlastnost stálosti expirace. Poslední zápis se stále
  určuje pořadím volání, i když má menší `now` než předchozí zápis.

Pro časovou hranici vždy evidovat, ke kterému zápisu patří. Staré hranice
jsou důležité: odhalí například situaci, kdy po přepisu stará expirace
nesprávně zneplatní nový záznam.

### Povinné cílené motivy

Samotný náhodný výběr nezaručuje dosažení kritických interakcí. Každá sada
proto obsahuje i generované motivy s náhodnými parametry:

| Motiv | Konkrétní svědek a očekávání |
| --- | --- |
| Přesná expirace | `Set(a,A,0,2); Get(a,1)→A; Get(a,2)→None; Get(a,3)→None` |
| Přepis prodlouží platnost | `Set(a,A,0,2); Set(a,B,1,5); Get(a,2)→B; Get(a,6)→None` |
| Přepis zkrátí platnost | `Set(a,A,0,10); Set(a,B,1,1); Get(a,2)→None; Get(a,3)→None` |
| Přepis právě v expiraci | `Set(a,A,0,2); Set(a,B,2,3); Get(a,2)→B; Get(a,5)→None` |
| Obnovení po expiraci | `Set(a,A,0,1); Get(a,1)→None; Set(a,B,2,2); Get(a,2)→B` |
| Nulové TTL přepíše živý záznam | `Set(a,A,0,10); Set(a,B,1,0); Get(a,1)→None` |
| Záporné TTL | `Set(a,A,5,-1); Get(a,5)→None` |
| Nezávislé klíče | `Set(a,A,0,2); Set(b,B,0,5); Get(a,2)→None; Get(b,2)→B` |
| Čtení neobnovuje TTL | `Set(a,A,0,2); Get(a,1)→A; Get(a,2)→None` |
| Návrat času | `Set(a,A,0,2); Get(a,2)→None; Get(a,1)→A` |
| Poslední zápis má starší čas | `Set(a,A,5,10); Set(a,B,4,10); Get(a,5)→B` |

Písmena `A`, `B` zde označují různé hodnoty. Přidat také samostatné motivy
pro chybějící klíč a uložené `None`. Část motivů obalit náhodným prefixem,
prokládat operacemi na druhém klíči a rozšířit suffixem. Každé čtení nadále
vyhodnocuje model, protože přidané operace mohou legitimně změnit očekávání.

## 5. Zmenšování selhání

Zmenšovač lze implementovat bez externí knihovny. Jeho vstupem je konkrétní
sekvence, režim a identifikátor porušené vlastnosti. Kandidáta přijmout pouze
tehdy, když splňuje doménu a předpoklady vlastnosti a reprodukuje stejnou
kategorii selhání. Přechod z chybného výsledku na nesouvisející výjimku není
úspěšné zmenšení. U každého kandidáta začínat s novou cache i modelem.

Postup opakovat do pevného bodu v deterministickém pořadí:

1. **Odříznout suffix za prvním selháním.** Pozdější operace nejsou potřeba.
2. **Odstraňovat bloky operací metodou delta debugging.** Začít velkými bloky,
   pak zkoušet menší až po jednotlivé operace. Nejprve odstraňovat rušivé
   klíče a čtení. Časy zbývajících operací ponechat absolutní, aby odebrání
   časového kroku mimoděk nezměnilo všechny další časy.
3. **Zmenšit počet klíčů a hodnoty.** Kanonizovat na `a`, `b` a malé hodnoty.
   U vlastnosti izolace zachovat dva různé klíče, u přepisu odlišné hodnoty,
   pokud jsou nutné k pozorování chyby. Sloučení klíčů zkoušet jako samostatný
   kandidát se znovuvyhodnocením modelu.
4. **Normalizovat čas.** Zkusit společný posun prvního času na nulu, potom
   zmenšovat mezery a TTL k `0`, `1`, případně `-1` v záporné doméně.
   V monotónním režimu zachovat neklesající pořadí. Zkoušet i velká čísla
   zmenšit k nejbližší relevantní hranici.
5. **Zachovat časový vztah, který chybu vyvolává.** Pro dotaz reprezentovaný
   jako `written_at + ttl + offset` zmenšovat zápis a TTL společně s dotazem;
   offset preferovat `-1`, `0`, `1`. Pouhý shrink všech čísel k nule může
   zničit svědka přesné expirace. Po smazání cílového zápisu přepočítat
   vztahy podle nové historie, nebo danou strukturální transformaci přeskočit.

Pro obyčejnou shodu s modelem je čtení bez předchozího zápisu platná operace
s očekáváním `Missing`. Není důvod automaticky zakazovat odstranění zápisu.
Naopak specializovaná vlastnost „přepis zkrátil TTL“ potřebuje dva zápisy
stejného klíče a odpovídající vztah jejich expirací. Tyto předpoklady se
kontrolují znovu po každé úpravě, nikoli podle původních indexů operací.

Pořadí kandidátů a přijetí musí zlepšovat pevně zvolenou míru složitosti
(například délku, počet klíčů, součet absolutních čísel a velikost hodnot),
aby zmenšovač necyklil. Evidovat již zkoušené kandidáty a nastavit limit
replayů. Při dosažení limitu uložit nejlepšího dosavadního svědka.
Výsledek označit jako zmenšený případ; globální minimum není zaručeno.
Bez vyčerpání limitu ověřit, že nelze smazat žádnou jednotlivou operaci
a stále zachovat stejné selhání a předpoklady.

Očekávané malé svědky jsou například:

```text
# Chybná podmínka now <= expires místo now < expires:
Set(a, 1, now=0, ttl=0)
Get(a, now=0)  # očekáváno None, chybně 1

# Chybné zachování delšího TTL při přepisu:
Set(a, 1, now=0, ttl=2)
Set(a, 2, now=0, ttl=1)
Get(a, now=1)  # očekáváno None, chybně 2
```

## 6. Reprodukovatelnost a pokrytí

Použít vlastní `random.Random(seed)` pro každý scénář. Při selhání uložit
seed, parametry generátoru, verzi Pythonu, revizi kódu, režim, identifikátor
vlastnosti, první rozdíl mezi modelem a SUT, původní i zmenšenou sekvenci.
Pro hodnoty této domény stačí JSON; nepoužívat `eval` pro replay. Konkrétní
sekvence je hlavní reprodukční artefakt, protože samotný seed nemusí po změně
generátoru vyrobit stejný případ. U vlastností porovnávajících dva běhy uložit
i transformaci a její parametry.

Počítat skutečně dosažené kategorie: chybějící/živé/expirované čtení,
`e-1/e/e+1`, přepis živého i expirovaného klíče, prodloužení/zkrácení TTL,
čtení na staré hranici po přepisu, nulové/záporné TTL, více klíčů a návrat
času v odpovídající sadě. Procenta generátoru nejsou důkaz pokrytí.
Povinné motivy musí tyto kategorie dosáhnout deterministicky; jejich
nedosažení je chyba testovacího harnessu. Náhodnou část při nízkém pokrytí
upravit cíleným generováním, nikoli jen přidáváním seedů.

## 7. Pořadí realizace a kritéria přijetí

1. Přidat model, runner a ručně ověřené motivy v `unittest`. Vyčlenit
   charakterizační sadu pro záporné TTL a návrat času.
2. Přidat omezené úplné prohledávání: například sekvence délky 1–4 z abecedy
   `Set(a,1,0,0)`, `Set(a,2,0,1)`, `Get(a,0)`, `Get(a,1)`.
   Taková malá sada systematicky pokryje i opakované přepisy a čtení.
3. Přidat hlavní generátor a transformační vlastnosti. Výchozí rychlý běh:
   všechny motivy, malá úplná sada a 200 pevných seedů do 100 operací.
   Rozšířený běh: 2 000 seedů do 500 operací plus charakterizační sada.
   Rozpočty upravit podle naměřené doby, bez časově závislých očekávání.
4. Přidat zmenšovač a replay uložených případů. Každý nalezený problém
   proměnit v malý pevný regresní test a ponechat i property, která jej našla.
5. Ověřit citlivost sady na dočasných mutovaných implementacích: `<` na `<=`,
   ignorování přepisu, ponechání staré expirace, použití maxima expirací,
   prodloužení TTL čtením, odstranění záznamu při expiraci a sdílení stavu
   instancí. Mutace držet v testovacích náhradách, neměnit produkční soubor.
   Každou musí odhalit určená vlastnost; odstranění při expiraci například
   následné opakované čtení a test návratu času.

Strategie je úspěšně realizována, když povinné kategorie mají svědky, všechny
property procházejí, uvedené mutace jsou zachyceny a umělé selhání lze uložit,
zmenšit a přehrát nezávisle na seedu. Pouhé velké množství náhodných průchodů
ani pokrytí řádků tento důkaz nenahrazuje.
