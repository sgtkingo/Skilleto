# Strategie stateful property-based testování TTL cache

Návrh vychází z `cache.py`: `Cache.set(key, value, now, ttl)` a
`Cache.get(key, now)`. Testovací stavový automat bude generovat posloupnosti
zápisů, čtení a posunů falešného monotónního času. Po každé operaci porovná
veřejné chování cache s nezávislým modelem. Vhodným nástrojem je Hypothesis
`RuleBasedStateMachine`; tento dokument nic neinstaluje ani nemění implementaci.

## 1. Přesný kontrakt

Pro tuto implementaci platí následující očekávání:

| Situace | Očekávané chování |
| --- | --- |
| `set(k, v, now, ttl)` | Zápis vrátí `None` a nahradí hodnotu i expiraci předchozího zápisu. |
| `get(k, now)`, pokud `now < deadline` | Vrátí poslední zapsanou hodnotu. |
| `get(k, now)`, pokud `now >= deadline` | Vrátí `None`; přesný deadline už znamená expiraci. |
| `get(k, now)`, pokud klíč nikdy nebyl zapsán | Vyvolá `KeyError`. |
| `ttl == 0` nebo `ttl < 0` | Zápis je okamžitě expirovaný; následné čtení vrátí `None`. |
| Opakovaná čtení | Neprodlužují TTL ani neobnovují starou hodnotu. |

Deadline zápisu je absolutní čas `now + ttl`. Poslední zápis vítězí také
tehdy, když má kratší TTL nebo okamžitě expiruje. Dlouhé TTL staršího zápisu
nesmí novému zápisu poskytnout delší životnost.

Rozlišení „nikdy nezapsán“ a „expiroval“ je součástí současného veřejného
chování. Pokud se má změnit, musí se změnit kontrakt i model. Současná cache
nemá `delete`, proto se tato operace negeneruje. Fyzické odstraňování položek,
kapacita ani souběh nejsou předmětem této strategie.

## 2. Falešný čas a nezávislý model

Čas bude obyčejné celé číslo `now`, na začátku `0`. Automat ho předává cache
explicitně, takže není potřeba patchovat hodiny ani používat `sleep`.
Generované posuny jsou nezáporné; několik operací může mít stejný čas.
Jednotkou je testovací tick. Celá čísla zajistí přesné hraniční případy bez
zaokrouhlování floatů.

Model udržuje:

- `live`: slovník pouze aktuálně živých položek `key -> (value, deadline)`;
- `written`: množinu všech někdy zapsaných klíčů, i po expiraci;
- `deadlines`: historii deadline pro cílené posuny přes staré i nové expirace;
- `now`: aktuální čas.

Při posunu času model odstraní všechny položky s `deadline <= now`. Při
zápisu nejprve odstraní předchozí živou položku stejného klíče a novou přidá
jen pro `ttl > 0`. `written` vždy zachová informaci o zápisu. Čtení modelu
pak rozhoduje podle členství ve `live` a `written`, bez opakování podmínky
z `Cache.get`. Tato odlišná reprezentace pomáhá odhalit chyby na hranicích.

Model nesmí číst `Cache.values` ani volat implementační pomocné funkce.
Vlastní výpočet absolutního deadline je součást specifikace, nikoli údaj
převzatý z testované cache.

Jádro budoucího testovacího adaptéru může vypadat takto (metody se následně
obalí pravidly Hypothesis; toto není kompletní testovací soubor):

```python
from cache import Cache


class Scenario:
    def __init__(self):
        self.sut = Cache()
        self.now = 0
        self.live = {}
        self.written = set()
        self.deadlines = []

    def set(self, key, value, ttl):
        assert self.sut.set(key, value, self.now, ttl) is None
        deadline = self.now + ttl
        self.written.add(key)
        self.deadlines.append(deadline)
        self.live.pop(key, None)
        if ttl > 0:
            self.live[key] = (value, deadline)

    def advance(self, delta):
        assert delta >= 0
        self.now += delta
        self.live = {
            k: record for k, record in self.live.items()
            if record[1] > self.now
        }

    def check_get(self, key):
        if key not in self.written:
            try:
                self.sut.get(key, self.now)
            except KeyError:
                return
            raise AssertionError(f"Expected KeyError for {key!r}")
        expected = self.live[key][0] if key in self.live else None
        assert self.sut.get(key, self.now) == expected

    def check_all(self):
        for key in sorted(self.written | {"never-written"}):
            self.check_get(key)
```

Generátor smí zapisovat jen do `a`, `b`, `c`; `never-written` je vyhrazený
kontrolní klíč. Hlavní sada používá celočíselné hodnoty, aby se živá hodnota
dala odlišit od výsledku expirace. Doplňkový scénář zapisuje `None`: veřejné
API v něm neumožňuje rozlišit živé `None` od expirace, ale další přepis a
čtení nesmí selhat. Stejně se doplní hodnoty `0`, `False` a prázdný řetězec
pro zachycení záměny existence položky s pravdivostní hodnotou.

## 3. Generování operací a času

Základ automatu tvoří pravidla `set`, `get`, `advance` a cílený
`advance_to_boundary`. Každé pravidlo končí invariantem `check_all()`.
Explicitní pravidlo `get` navíc generuje opakovaná čtení stejného klíče;
invariant kontroluje také klíče, na které generátor právě nevybral operaci.

| Vstup nebo pravidlo | Konkrétní návrh generování |
| --- | --- |
| Klíče | `sampled_from(["a", "b", "c"])`; malý prostor vytváří časté přepisy. |
| Hodnoty | Celá čísla `-2..2`; cílený přepis použije hodnotu odlišnou od předchozí. |
| TTL | Časté `-1, 0, 1, 2, 5`; zároveň `integers(-2, 100)`. |
| Obecný posun | Časté `0, 1, 2, 5`; zároveň `integers(0, 200)`. |
| Hraniční posun | Z historie vybrat `d`, pak cíl `d-1`, `d` nebo `d+1`; ponechat jen cíle `>= now`. |
| Přepis známého klíče | Samostatné pravidlo dostupné při neprázdném `written`, aby nevznikaly hlavně nové zápisy. |
| Čtení známého klíče | Vybírat také expirované klíče z `written`, nejen živé položky. |

Pro dynamické výběry použít `st.data()` a `data.draw(...)` uvnitř pravidla;
nejprve stabilně seřadit kandidáty. Hraniční pravidlo povolit jen tehdy,
když existuje dosažitelný cíl. Nepoužívat opakované `assume` pro odmítání
minulých deadline. Historie obsahuje i deadline nahrazených zápisů: právě
jejich překročení prověřuje, zda stará expirace neovlivní novou hodnotu.

Pravidla pro přepis a hranice přidají potřebné situace i bez přesných
procentuálních vah pravidel. Rozložení ověřovat přes `event` nebo
`statistics`: počet přepisů, expirací, nulových TTL, opakovaných čtení a
zásahů před/na/po deadline. Tyto statistiky jsou diagnostika, nikoli
pravděpodobnostní podmínka úspěchu testu.

## 4. Vlastnosti a pořadí operací

1. **Shoda s modelem po každém kroku.** Výsledek nebo `KeyError` odpovídá
   modelu pro každý zapsaný klíč i kontrolní nezapsaný klíč.
2. **Přesná hranice.** Při `deadline-1` je pozitivní TTL živé, při
   `deadline` a `deadline+1` je expirované. Čas nikdy neposouvat zpět jen
   kvůli ověření hranice; použít vhodné pořadí nebo čerstvý scénář.
3. **Přepis nahrazuje hodnotu i TTL.** Nový zápis může prodloužit i zkrátit
   životnost. Překročení starého deadline nesmí odstranit novou živou hodnotu.
4. **Expirace je nevratná bez zápisu.** Další posuny a čtení expirovanou
   hodnotu neoživí. Nový zápis stejného klíče ji smí znovu vytvořit.
5. **Čtení je neutrální.** Vložení dalších `get` mezi stejné zápisy a posuny
   nezmění pozdější výsledky; opakovaná čtení neobnovují TTL.
6. **Izolace klíčů.** Zápis do `a` nemění pozorování `b`; zápisy různých
   klíčů lze při stejném čase prohodit. Dva zápisy stejného klíče naopak
   zachovávají pořadí a vítězí poslední.
7. **Složení posunů.** Bez mezilehlých zápisů mají `advance(x); advance(y)`
   a `advance(x+y)` stejné konečné pozorování pro `x, y >= 0`.

Vlastnosti 5–7 ověřit také párovými scénáři na dvou čerstvých cache se
stejným prefixem. Při porovnání veřejných výsledků zaznamenávat výjimku
odděleně od hodnoty `None`. Pro prohození zápisů nepoužít mezilehlý posun
času: změnil by absolutní deadline a tím i význam porovnání.

## 5. Povinné krátké scénáře

Následující scénáře musí mít deterministické regresní testy vedle generování.
Každý začíná čerstvou cache a časem `0`; `advance(n)` znamená posun o `n`.

| Scénář | Posloupnost a očekávání |
| --- | --- |
| Hranice expirace | `set(a, 1, ttl=2)`; `advance(1)` → `get(a)==1`; `advance(1)` → `None`; `advance(1)` → `None`. |
| Přepis před starou expirací | `set(a, 1, ttl=2)`; `advance(1)`; `set(a, 2, ttl=5)`; `advance(1)` → `2` na starém deadline `2`; `advance(1)` → `2` za ním; `advance(3)` → `None` na novém deadline `6`. |
| Zkrácení TTL | `set(a, 1, ttl=10)`; `set(a, 2, ttl=1)`; `advance(1)` → `None`, přestože původní deadline je až `10`. |
| Okamžitě expirovaný přepis | `set(a, 1, ttl=10)`; `set(a, 2, ttl=0)` → `None`; totéž pro `ttl=-1`. |
| Znovuvložení po expiraci | `set(a, 1, ttl=1)`; `advance(1)` → `None`; `set(a, 2, ttl=2)` → `2`; `advance(2)` → `None`; opakovat cyklus. |
| Zápis přesně na deadline | `set(a, 1, ttl=1)`; `advance(1)`; `set(a, 2, ttl=2)` → `2`; před zápis lze vložit čtení `None` bez vlivu na výsledek. |
| Více zápisů bez posunu | `set(a, 1, ttl=5)`; `set(a, 2, ttl=5)` → `2`; prohodit hodnoty → `1`. |
| Izolace a shodný deadline | `set(a, 1, ttl=2)`; `set(b, 2, ttl=2)`; `advance(2)` → oba `None`; přepis `a` nesmí změnit `b`. |
| Neznámý klíč | `get(c)` → `KeyError`, i po libovolném posunu času; po expirovaném zápisu do `c` už očekávat `None`. |

## 6. Shrinking, reprodukce a ověření síly testů

Hypothesis má zmenšovat celou posloupnost, klíče, hodnoty, TTL i posuny.
Používat přímo strategie Hypothesis, žádný vlastní `random` ani reálné
hodiny. Každý příklad musí mít novou cache i model. Nevkládat většinu
scénáře do jediné atomické operace: samostatné zápisy a posuny dovolí
odstranit nepotřebné kroky. Párová metamorfní kontrola může být samostatný
test, aby nekomplikovala shrinking hlavního automatu.

Při chybě uchovat minimální posloupnost včetně času před operací, TTL,
očekávaného a skutečného výsledku. Uložit ji jako konkrétní regresní test;
zachovat také databázi příkladů Hypothesis a jeho reprodukční údaje/verzi.
Seed sám o sobě není dlouhodobou náhradou minimálního příkladu.

Navržený startovní profil je `max_examples=200`,
`stateful_step_count=50`; pro delší běh `1000` příkladů po `200` krocích.
Jde o výchozí rozpočet, který se upraví podle měřeného času. Vypnutí limitu
trvání příkladu (`deadline=None`) je možné pro stabilitu pomalejšího CI;
nejde o TTL cache. Spouštění po implementaci testů: například
`python -m pytest tests/test_cache_stateful.py`, pokud jsou pytest a
Hypothesis již dostupné. V této úloze se balíčky neinstalují a testy se
nespouštějí, protože výstupem je návrh.

Sílu testů následně ověřit ručně vytvořenými, dočasnými mutacemi: změna `<`
na `<=`, ignorování nové hodnoty při přepisu, ponechání starého deadline,
obnovení TTL při `get`, návrat staré hodnoty po expiraci a odstranění nové
položky při dosažení starého deadline. Pro poslední mutaci použít přepis
před starou expirací. Mutační nástroj není nutný. Každá mutace musí vést
k selhání srozumitelného příkladu; správná implementace musí projít.

Návrh je přijatelný, pokud pokrývá všechny krátké scénáře, kontroluje model
po každém kroku, systematicky zasahuje přesnou hranici expirace a zachytí
uvedené mutace. Počet náhodných příkladů sám o sobě není důkazem pokrytí.

## 7. Použití Skilleto

Rozhodnutí: **REUSE_EXISTING**. Potřebné schopnosti jsou návrh nezávislého
modelu, falešného času, generování pořadí operací a zmenšování protipříkladů.
Pokrývá je lokální dovednost `cache-test-design`, načtená z
`.agents/skills/cache-test-design/SKILL.md` a dostupná v této relaci.
Shoda s úlohou je vysoká. Riziko použití je nízké: přečtené instrukce
nevyžadují spouštění skriptů, přístupové údaje ani síť.

Online vyhledávání nebylo potřebné a neproběhlo. Instalace nebyla zahájena;
souhlas s instalací nebyl vyžadován a uživatel ji výslovně zakázal. Rozsah
změn je pouze `strategy.md` v projektu
`D:/Projects/Skilleto/.test-lab/skilleto-cli-lab-506f62bfcc4c/p02-reuse`.
Výsledkem použití dovednosti je tento návrh přizpůsobený veřejnému API
`cache.py`; nenavrhuje neexistující operaci `delete`.
