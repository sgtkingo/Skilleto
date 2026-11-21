# Strategie stateful property-based testování TTL cache

## Cíl a rozsah

Testovat `Cache` z `cache.py` pomocí referenčního modelu a generovaných sekvencí
operací. Důraz: přesná hranice expirace, přepis stejného klíče a závislost
výsledku na pořadí operací. Návrh používá Python a stavový automat Hypothesis
(`RuleBasedStateMachine`); tato práce pouze navrhuje testy, nic neinstaluje
a nespouští síťové požadavky ani discovery CLI.

Podklady jsou lokální `cache.py`, úplné syntetické záznamy v `candidates.md`
a instrukce Skilleto. Nejde o živé výsledky registru ani o ověřené publikované
skilly. Níže uvedené testy jsou návrh, nebyly spuštěny.

## Skilleto: potřeby, porovnání a rozhodnutí

Potřebné schopnosti:

1. Nezávislý referenční model času a životnosti posledního zápisu.
2. Generování stavových sekvencí s opakováním klíčů a časovými hranicemi.
3. Orákulum pro výsledky i výjimky a zmenšování chybových sekvencí.
4. Oddělení funkční shody kandidáta od původu a instalačního rizika.

Inventář: dostupný skill `skilleto` byl načten v této relaci; v projektovém
adresáři skillů je pouze `skilleto`. Dostupné čtení souborů, úprava Markdownu
a vlastní schopnosti agenta stačí k vytvoření tohoto návrhu. Specializovaný
stavový workflow je obsahově užitečný, ale pro tento dokument nevyžaduje
získání dalšího skillu. Dostupnost knihovny Hypothesis nebyla zjišťována;
není podmínkou sepsání strategie.

| Kandidát a dodaný syntetický zdroj | Funkční shoda | Kompatibilita a přínos | Nároky a nejistoty | Závěr |
| --- | --- | --- | --- | --- |
| `popular-ui` — `https://catalog.invalid/demo/ui/popular-ui` | **LOW** | Revize barev a rozestupů React komponent; výslovně vylučuje Python a automatické testy. Pro TTL model nepřináší použitelný postup. | Jiné soubory nejsou podle fixture přítomny; konkrétní závislosti a podpora hostitele nejsou uvedeny. Původ fiktivní. | Zamítnout pro nesoulad s úkolem. Milion fiktivních instalací není důkaz vhodnosti. |
| `state-machine-tests` — `https://catalog.invalid/demo/testing/state-machine-tests` | **HIGH** | Referenční cache, sekvence get/set/delete/advance-clock, porovnání po každém kroku a shrinking přímo pokrývají potřebu. Python/Hypothesis odpovídá návrhu; delete se pro současné API vynechá. | Podle úplného dodaného textu nemá přibalený kód ani setup hooks. Hypothesis je požadovaná závislost pro budoucí běh; kompatibilita konkrétních verzí a Codex/Windows není doložena. | Nejlepší obsahová volba pro tuto simulaci; není instalační doporučení. Pět fiktivních instalací shodu nesnižuje. |
| `snapshot-basics` — `https://catalog.invalid/demo/snapshots/snapshot-basics` | **LOW** | Snímky UI v prohlížeči; výslovně vylučuje testování stavovým modelem. Nepokrývá čas, přepis ani pořadí cache operací. | Vyžaduje prohlížeč; další setup a konkrétní závislosti neuvedeny. Původ fiktivní. | Zamítnout pro nesoulad s úkolem i přes 50 tisíc fiktivních instalací. |

Porovnání vychází z kompletních relevantních obsahů uvedených v `candidates.md`,
nikoli jen z názvů. Vlastník/repozitář, skutečná cesta skillu, revize a historie
údržby nejsou u žádného kandidáta doloženy. Uvedené URL jsou pouze syntetické
identifikátory a nebyly navštíveny. Nejsou počítána skóre podobnosti.

**Aktuální rozhodnutí Skilleto: `NO_INSTALL`.** Vlastní schopnosti stačí
k dodání návrhu a uživatel zakázal instalace i síť. Online hledání bylo záměrně
přeskočeno, nikoli neúspěšně provedeno. Bezpečnostní posouzení případného
produkčního pořízení všech tří kandidátů je **`UNKNOWN` → `BLOCK`**, protože
chybí ověřitelný původ a revize; nejde o druhé aktuální rozhodnutí workflow.
Vysoká funkční shoda `state-machine-tests` tuto instalační překážku nemění.
V dodaném textu nejsou setup hooks ani další soubory tohoto kandidáta, což
neověřuje původ ani bezpečnost budoucích závislostí.

Autorizace k instalaci: zamítnuta zadáním; nebyla vyžadována ani použita.
Provisioning: `not attempted`. Aktivace kandidátů: `N/A`, žádný nebyl načten
nebo nainstalován. Rozsah výstupu: pouze `strategy.md` v projektu
`D:\Projects\Skilleto\.test-lab\skilleto-cli-lab-506f62bfcc4c\p04-fit`.
Následující krok je návrh testů níže, bez potřeby zásahu uživatele.

## Přesná smlouva současného API

`set(key, value, now, ttl)` uloží hodnotu a deadline `now + ttl` a vrací `None`.
`get(key, now)` se chová takto:

| Stav klíče | Očekávané pozorování |
| --- | --- |
| Nikdy nezapsán | Vyvolá `KeyError`. |
| Zapsán a `now < deadline` | Vrátí poslední hodnotu. |
| Zapsán a `now >= deadline` | Vrátí `None`. |

Expirace tedy nastává **už při rovnosti**, nikoli až po ní. Čtení expirovaný
záznam neodstraňuje. Hodnota `None` je povolena a v tomto API není výsledkem
čtení rozlišitelná od expirace. Test výjimky proto musí odlišit chybějící klíč
od obou těchto případů, ale nesmí si vymyslet veřejný příznak hit/miss.

Hlavní sada používá celočíselný virtuální čas, malé řetězcové klíče,
neměnné hodnoty a nezáporná celočíselná TTL včetně nuly. Čas v generovaných
sekvencích neklesá. To je zvolený testovací scénář, nikoli validace vynucovaná
implementací: `now` je parametr, cache nemá vlastní hodiny.

Záporné TTL současný kód přijme a při stejném nebo pozdějším čase vrátí `None`.
Toto chování lze pokrýt odděleným charakterizačním příkladem. Pokud má produkt
záporné TTL odmítat, je nejprve nutné změnit smlouvu. NaN, nekonečno, float
zaokrouhlení, různé typy času, souběh vláken a návrat hodin zpět nejsou součástí
hlavní sady; případné rozšíření dostane vlastní smlouvu a model.

Cache nemá kapacitu, eviction ani `delete`. Nelze pro ni tvrdit LRU/FIFO
vlastnosti ani generovat skutečné volání `delete`. Logickou expiraci nezaměňovat
za fyzické uvolnění paměti. Zadání fixture o eviction zde označuje námět pro
budoucí rozšíření, nikoli existující funkcionalitu.

## Model, operace a generování

Stav automatu tvoří nová instance `Cache`, `time = 0` a vlastní slovník modelu
`key -> (poslední hodnota, absolutní deadline)`. Model nečte `sut.values`
a nepoužívá metody testované cache k výpočtu očekávání. Uchovává i expirované
klíče kvůli rozdílu `KeyError` / `None`. Přepis kompletně nahradí hodnotu
i deadline; starý deadline nesmí mít další účinky.

| Operace automatu | Přechod a kontrola |
| --- | --- |
| `set(k, v, ttl)` | Zavolá SUT s aktuálním časem; očekává `None`. Do modelu uloží `(v, time + ttl)`. |
| `get(k)` | Porovná návratovou hodnotu nebo `KeyError` s modelem v aktuálním čase. Jiné výjimky jsou selhání. |
| `advance(delta)` | Zvýší pouze virtuální čas o nezáporné delta; nevolá sleep ani systémové hodiny. |
| `boundary(k, offset)` | Pro zapsaný klíč nastaví čas na `deadline + offset`, pokud neklesne; offset je −1, 0 nebo +1. Jinak bez přechodu. |

Použít 3–5 klíčů: malá doména často vytváří přepisy a současně dovolí testovat
izolaci klíčů. Samostatné pravidlo čte rezervovaný klíč, do kterého se nikdy
nezapisuje. Hodnoty: malá celá čísla, krátké řetězce a `None`; pro cílené
regrese přepisu vybrat různé hodnoty `A` a `B`, aby starý výsledek nezůstal skryt.
TTL a posuny vybírat zejména z `{0, 1, 2, 5, 20}`; delší hodnoty mohou být
samostatnou doplňkovou sadou. Dovolit opakované operace ve stejném čase.

Pravidlo `boundary` doplňuje náhodné posuny: náhodné delta samo nezaručuje
návštěvu přesné expirace. Vedle obecného `set` přidat pravidlo přepisu
existujícího klíče, je-li nějaký k dispozici. Zkrácení i prodloužení TTL
a přepis expirované hodnoty musí mít také pevné regresní scénáře.

Po každém pravidle ověřit dostupnými čteními všechny klíče malé domény proti
modelu, včetně rezervovaného chybějícího klíče. To je zde bezpečné, protože
`get` podle přečteného zdroje nemění stav. Výslovná pravidla `get` zachovat
kvůli pořadí a shrinking. Pokud se později čtení stane mutující operací,
ověřovat izolovanou kopii nebo zavést čtení jako zaznamenané přechody; skryté
kontrolní čtení nesmí změnit testovanou historii.

## Kostra budoucího testu

Následující kód je konkrétní výchozí návrh pro `test_cache_stateful.py`, nikoli
soubor vytvořený nebo spuštěný v tomto úkolu. Vyžaduje již dostupný Hypothesis.
`pytest` může objevit vygenerovanou unittest třídu `TestCache`.

```python
from hypothesis import settings, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule
from cache import Cache

KEYS = ("a", "b", "c")
keys = st.sampled_from(KEYS)
durations = st.sampled_from((0, 1, 2, 5, 20))
values = st.one_of(st.none(), st.integers(-2, 2), st.sampled_from(("A", "B")))


def observe(cache, key, now):
    try:
        return ("return", cache.get(key, now))
    except KeyError:
        return ("raise", KeyError)


class CacheMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.sut = Cache()
        self.time = 0
        self.model = {}

    def expected(self, key):
        if key not in self.model:
            return ("raise", KeyError)
        value, deadline = self.model[key]
        return ("return", value if self.time < deadline else None)

    @rule(key=keys, value=values, ttl=durations)
    def write(self, key, value, ttl):
        assert self.sut.set(key, value, self.time, ttl) is None
        self.model[key] = (value, self.time + ttl)

    @rule(key=keys)
    def read(self, key):
        assert observe(self.sut, key, self.time) == self.expected(key)

    @rule(delta=durations)
    def advance(self, delta):
        self.time += delta

    @rule(key=keys, offset=st.sampled_from((-1, 0, 1)))
    def boundary(self, key, offset):
        if key in self.model:
            target = self.model[key][1] + offset
            if target >= self.time:
                self.time = target

    @invariant()
    def agrees_with_model(self):
        for key in (*KEYS, "never-written"):
            assert observe(self.sut, key, self.time) == self.expected(key)


TestCache = CacheMachine.TestCase
TestCache.settings = settings(max_examples=200, stateful_step_count=80)
```

Kostra záměrně začíná malou doménou; opakované `write` již tvoří přepisy.
Při dopracování přidat cílené pravidlo výběru existujícího klíče a události
pokrytí popsané níže. Nastavení 200 sekvencí po nejvýše 80 krocích je výchozí
rozpočet, ne tvrzení o dosaženém pokrytí nebo naměřeném běhovém čase.

## Vlastnosti a povinné pořadí operací

1. **Hranice:** `set(a, A, now=0, ttl=5)`; `get(a, 4) == A`,
   `get(a, 5) is None`, `get(a, 6) is None`. TTL nula expiruje už při zápisu.
2. **Poslední zápis rozhoduje:** dva zápisy stejného klíče ve stejném čase;
   vrátí se hodnota druhého, pokud jeho TTL není nula. Opačné pořadí zápisů
   s různými hodnotami musí obrátit výsledek.
3. **Prodloužení:** zápis `A` v čase 0 s TTL 5, přepis `B` v čase 2 s TTL 10;
   v čase 5 vrátí `B`, v čase 11 ještě `B`, v čase 12 už `None`.
   Starý deadline nesmí zneplatnit novou hodnotu.
4. **Zkrácení:** zápis `A` v čase 0 s TTL 20, přepis `B` v čase 2 s TTL 1;
   v čase 2 vrátí `B`, v čase 3 i 20 už `None`. Starší dlouhé TTL neplatí.
5. **Přepis po expiraci:** zápis `A` v čase 0 s TTL 1; v čase 1 čtení vrátí
   `None`; poté zápis `B` v čase 1 s TTL 2 obnoví dostupnost do času 3.
   Opakovat i bez mezilehlého čtení: expirace nesmí vyžadovat předchozí `get`.
6. **Přepis přesně na hranici:** v čase původní expirace porovnat pořadí
   `get; set; get` s `set; get`: čtení před zápisem vrací `None`, po zápisu
   novou hodnotu při kladném TTL. Nový zápis s TTL 0 vrací hned `None`.
7. **Bez oživení a prodlužování čtením:** bez dalšího zápisu už při rostoucím
   čase expirovaný klíč nevrátí hodnotu; opakované `get` neobnovuje TTL.
   Například čtení v časech 1, 4 a 5 po zápisu s deadlinem 5.
8. **Izolace a pořadí různých klíčů:** vložené operace nad `b` neovlivní `a`.
   Dva zápisy různých klíčů při stejném čase lze prohodit při zachování
   konečných pozorování. Prohození spojené s posunem času tuto záruku nemá.
9. **Skládání času:** bez mezilehlého zápisu má `advance(x); advance(y)`
   stejné konečné pozorování jako `advance(x + y)`; `advance(0)` nic nemění.
   Porovnání provést na dvou čerstvých instancích se stejnou historií.
10. **Výsledky API:** nikdy nezapsaný klíč vždy vyvolá `KeyError`; zapsaný
    expirovaný klíč vrací `None`, i po opakovaných čteních. Zvlášť otestovat
    živou hodnotu `None` a přepis `None -> A` i `A -> None`.

Tyto příklady mají doprovázet automat jako deterministické regresní testy.
Zabraňují tomu, aby zásadní interakce závisely jen na náhodném výběru pravidel.

## Vyhodnocení, shrinking a kritéria dokončení

- Oddělit události pokrytí: chybějící/živý/expirovaný klíč, přesná hranice,
  TTL 0, přepis živého/expirovaného, zkrácení/prodloužení a stejné časy.
  Při budoucím běhu použít statistiky Hypothesis; chybějící kategorii doplnit
  cíleným pravidlem nebo pevnou regresí. Samotný počet sekvencí nestačí.
- Nechat Hypothesis zmenšovat hodnoty i celou sekvenci. Používat malé skaláry,
  čerstvou cache pro každý příklad a žádný globální čas nebo sdílený stav.
  Nezachytávat obecné výjimky: neočekávané výjimky musí test shodit.
- Při chybě uložit minimální sled operací s explicitním časem, klíčem, TTL,
  očekáváním a výsledkem. Zachovat reprodukční blob a verzi Hypothesis,
  pokud je běh poskytne; minimalizovaný případ převést na pevnou regresi.
  Databázi příkladů uchovávat lokálně podle pravidel projektu.
- Sílu orákula v budoucnu ověřit cílenými mutacemi: `<` změnit na `<=`,
  při přepisu ponechat starý deadline, posunout deadline při čtení, vracet
  starou hodnotu a odstranit expirovaný záznam při prvním `get`.
  Poslední mutaci odhalí druhé čtení, které by chybně vyvolalo `KeyError`.
  Mutace zavést pouze do dočasné testované varianty; nyní se neprovádějí.
- Hotová implementace testů má splnit všechny pevné scénáře, souhlas modelu
  ve stavových bězích, doloženou návštěvu hlavních kategorií a odhalení
  uvedených mutací. Bez skutečného běhu nelze hlásit úspěšné testy.

Pro budoucí API `delete` nejprve určit chování pro chybějící a expirovaný klíč
a poté přidat odpovídající přechod modelu. Pro kapacitní eviction určit
kapacitu, politiku, vliv čtení a pořadí úklidu expirací vůči vytlačování;
teprve poté přidat pořadový model. Současný zdroj takové závěry neumožňuje.
