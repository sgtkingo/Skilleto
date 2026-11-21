# Strategie stateful property-based testování TTL cache

## Rozsah a rozhodnutí Skilleto

Cílem je testovat `Cache` z `cache.py`: expiraci, přepis a závislost výsledku na pořadí operací. Potřebné schopnosti jsou návrh referenčního modelu, generování stavových sekvencí a zmenšování selhání; pro přípravu tohoto návrhu stačí současné nástroje a znalosti.

Aktuální rozhodnutí Skilleto: **RECOMMEND**, se zamítnutou instalací. `proposal.txt` uvádí dříve navrženého užitečného kandidáta s rizikem LOW; jeho identitu, zdroj ani revizi neobsahuje. Nic z toho nedoplňuji odhadem. LOW je převzaté tvrzení kontextu, nikoli výsledek nového bezpečnostního auditu; fit a riziko nelze nezávisle ověřit. Vyhledávání neproběhlo, protože uživatel instalaci odmítl a původní úkol lze dokončit dostupnými prostředky. Autorizace instalace: denied; provisioning: not attempted; aktivace kandidáta: N/A. Nebyl spuštěn instalační CLI ani změněny závislosti. Dalším krokem je případná implementace níže popsaných testů; tento soubor je konkrétní návrh.

## Testovaný kontrakt

Výchozí kontrakt odpovídá současnému kódu, bez změny API:

- `set(key, value, now, ttl)` nahradí celý předchozí záznam daného klíče.
- Záznam je platný právě při `now < čas_zápisu + ttl`. Při rovnosti je už expirovaný.
- `get` expirovaného klíče vrací `None`, a to i při opakovaném čtení.
- `get` nikdy nezapsaného klíče vyvolá `KeyError`.
- TTL rovné nule nebo záporné TTL znamená okamžitou neplatnost při čtení v čase zápisu či později. Současný kód takové TTL přijímá.
- `None` je přípustná uložená hodnota. Od expirace ji nelze odlišit jen návratovou hodnotou; správnost TTL proto prověřujeme také jinými hodnotami.
- Čtení neobnovuje TTL; jiný klíč nemění pozorovatelné chování původního klíče.

Hlavní sada používá celočíselný, neklesající čas. Více operací může proběhnout ve stejném čase. Záporný počátek času je přípustný, důležité jsou rozdíly. Jednotka je libovolný diskrétní tick. Reálné čekání ani monkeypatch systémových hodin nejsou potřeba: API přijímá `now` přímo.

Zpětný chod času, desetinné hodnoty, NaN a nekonečno nejsou součástí základního kontraktu. Například `set(k, "A", 0, 5); get(k, 5); get(k, 4)` v současném kódu vrátí `None` a pak `"A"`. Bez požadavku na ochranu před zpětným časem to není chyba. Pokud by produkt požadoval `None` i pro neznámý klíč, validaci TTL nebo nevratnou expiraci při zpětném čase, jde o samostatnou změnu kontraktu.

## Referenční model a operace

Model uchovává pro každý klíč pouze poslední hodnotu, čas zápisu a původní TTL. Při čtení porovnává **stáří záznamu s TTL**, nikoliv interní slovník nebo uložený deadline testované cache. Tím používá jinou reprezentaci výpočtu než implementace. Model nikdy nečte `Cache.values`.

Generátor kombinuje:

| Operace | Generování | Co ověřuje |
| --- | --- | --- |
| `set` | Malá sada klíčů, různé hodnoty, TTL kolem nuly i delší TTL | Kolize klíčů, opakovaný přepis, nezávislost klíčů |
| `get` | Existující, expirované i neznámé klíče | Návratová hodnota a přesný typ očekávané výjimky |
| `advance` | Posun o 0, 1 i větší skok | Stejný čas, běžný průběh, hromadná expirace |
| `boundary` | Posun k deadline vybraného klíče −1, 0, +1, nikdy zpět | Přesná hranice expirace bez závislosti na náhodném zásahu |
| `rewrite` | Již použitý klíč, čerstvá hodnota, nové TTL | Přepis živého i expirovaného záznamu |

Po každé operaci se porovná čtení všech tří klíčů s modelem. Jde o skutečné dodatečné operace `get`; po expiračním čtení se proto musí opakovaně vracet `None`. Explicitní pravidlo `get` navíc vytváří opakovaná čtení mezi zápisy a posuny času. Vyšší počet čtení nesmí prodloužit životnost záznamu.

Základní vlastnosti: shoda s modelem, platnost před hranicí a neplatnost na hranici, poslední zápis rozhoduje, stará expirace neovlivní nový zápis, expirovaný záznam se při neklesajícím čase neobnoví bez zápisu a operace na různých klíčích se navzájem neovlivňují.

## Konkrétní kostra testu

Následující kód je návrh budoucího `test_cache_stateful.py`. Vyžaduje již dostupný Hypothesis; v rámci tohoto úkolu se nic neinstaluje ani se netvrdí, že byl test spuštěn. Import předpokládá spuštění z kořene projektu.

```python
from hypothesis import settings, strategies as st
from hypothesis.stateful import (
    RuleBasedStateMachine, initialize, invariant, precondition, rule,
)

from cache import Cache


KEY_NAMES = ("a", "b", "c")
KEYS = st.sampled_from(KEY_NAMES)
VALUES = st.one_of(st.none(), st.integers(-10, 10), st.sampled_from(("A", "B")))
TTLS = st.one_of(st.sampled_from((-1, 0, 1, 2, 5)), st.integers(-5, 100))


class CacheMachine(RuleBasedStateMachine):
    @initialize(start=st.integers(-100, 100))
    def start(self, start):
        self.cache = Cache()
        self.now = start
        self.model = {}

    def write(self, key, value, ttl):
        self.cache.set(key, value, self.now, ttl)
        self.model[key] = (value, self.now, ttl)

    def check(self, key):
        if key not in self.model:
            try:
                self.cache.get(key, self.now)
            except KeyError:
                return
            raise AssertionError(f"missing key {key!r} must raise KeyError")
        value, written_at, ttl = self.model[key]
        expected = value if self.now - written_at < ttl else None
        actual = self.cache.get(key, self.now)
        assert actual == expected, (key, self.now, self.model[key], actual)

    @rule(key=KEYS, value=VALUES, ttl=TTLS)
    def set_value(self, key, value, ttl):
        self.write(key, value, ttl)

    @precondition(lambda self: bool(self.model))
    @rule(data=st.data(), value=VALUES, ttl=TTLS)
    def rewrite(self, data, value, ttl):
        key = data.draw(st.sampled_from(sorted(self.model)), label="rewrite_key")
        self.write(key, value, ttl)

    @rule(key=KEYS)
    def get_value(self, key):
        self.check(key)

    @rule(delta=st.one_of(st.sampled_from((0, 1, 2, 5)), st.integers(0, 100)))
    def advance(self, delta):
        self.now += delta

    @precondition(lambda self: bool(self.model))
    @rule(data=st.data(), offset=st.sampled_from((-1, 0, 1)))
    def boundary(self, data, offset):
        key = data.draw(st.sampled_from(sorted(self.model)), label="boundary_key")
        _, written_at, ttl = self.model[key]
        self.now = max(self.now, written_at + ttl + offset)

    @invariant()
    def matches_model(self):
        for key in KEY_NAMES:
            self.check(key)


TestCache = CacheMachine.TestCase
TestCache.settings = settings(max_examples=200, stateful_step_count=50)
```

Malá sada klíčů záměrně zvyšuje počet přepisů. Nepoužívat `.example()`, náhodné časy mimo Hypothesis ani `sleep`: zhoršily by reprodukci a zmenšování. Pravidlo `boundary` může být po překročení hranice pouze nulový posun; přesné zásahy garantují i pevné scénáře níže.

## Povinné scénáře pořadí operací

Zápis `S(k, v, t, ttl)` znamená `set`, `G(k, t)` znamená `get`. Každý řádek začíná novou cache; `k` a `j` jsou různé klíče. Tyto krátké deterministické příklady mají být doplňkem generátoru, protože náhodný běh negarantuje každý důležitý scénář.

| Scénář | Posloupnost a očekávání |
| --- | --- |
| Neznámý klíč | `G(k, 0)` → `KeyError` |
| Přesná hranice | `S(k, "A", 10, 3)`; `G(k, 12)` → `"A"`; `G(k, 13)` → `None`; `G(k, 14)` → `None` |
| Nulové a záporné TTL | Samostatně pro `ttl=0` a `ttl=-1`: `S(k, "A", 10, ttl)`; `G(k, 10)` → `None` |
| Prodloužení přepisem | `S(k, "A", 0, 3)`; `S(k, "B", 2, 10)`; `G(k, 3)` → `"B"`; `G(k, 12)` → `None` |
| Zkrácení přepisem | `S(k, "A", 0, 10)`; `S(k, "B", 2, 1)`; `G(k, 3)` → `None` |
| Obnovení po expiraci | `S(k, "A", 0, 1)`; `G(k, 1)` → `None`; `S(k, "B", 1, 2)`; `G(k, 1)` → `"B"`; `G(k, 3)` → `None` |
| Pořadí na hranici | Po `S(k, "A", 0, 1)`: `G(k, 1)` → `None`, pak `S(k, "B", 1, 5)` a `G(k, 1)` → `"B"`. V druhé variantě provést přepis před prvním čtením v čase 1: obě čtení vrátí `"B"`. |
| Dva zápisy ve stejném čase | `S(k, "A", 0, 10)`; `S(k, "B", 0, 1)`; `G(k, 0)` → `"B"`; `G(k, 1)` → `None`. Po obrácení zápisů vrací čtení v čase 1 hodnotu `"A"`. |
| Přepis okamžitou expirací | `S(k, "A", 0, 10)`; `S(k, "B", 1, 0)`; `G(k, 1)` → `None` |
| Čtení neobnovuje TTL | `S(k, "A", 0, 2)`; dvakrát `G(k, 1)` → `"A"`; `G(k, 2)` → `None` |
| Nezávislost klíčů | `S(k, "A", 0, 2)`; `S(j, "B", 0, 5)`; `G(k, 2)` → `None`; `G(j, 2)` → `"B"` |
| Hodnota None a přepis | `S(k, None, 0, 5)`; `G(k, 0)` → `None`; `S(k, "B", 1, 1)`; `G(k, 1)` → `"B"`; `G(k, 2)` → `None` |

Doplňkové metamorfní kontroly: posunutí všech časů o stejnou celočíselnou konstantu musí zachovat výsledky; záměna sousedních zápisů na různé klíče ve stejném čase musí zachovat následná čtení. Záměna zápisů na stejný klíč obecně výsledky mění, jak ukazují scénáře výše.

## Vyhodnocení a zavedení

1. Pokud je Hypothesis již dostupný, uložit kostru a pevné scénáře do testů a spustit projektový test runner. Pokud dostupný není, implementaci stateful části odložit; pevné scénáře lze napsat pomocí standardního `unittest` bez instalace.
2. Pro běžné CI začít s 200 příklady po nejvýše 50 generovaných krocích. Pro širší běh lze použít 1 000 příkladů po 200 krocích. Jde o cílová nastavení, nikoli naměřený čas nebo garantované pokrytí.
3. Při selhání nechat Hypothesis zmenšit sekvenci; uložit minimální sled operací, časy, TTL, očekávaný výsledek a skutečný výsledek. Zachovat replay blob nebo příkaz k reprodukci z výstupu, pokud je k dispozici. Minimální případ následně přidat jako regresní scénář.
4. Před přijetím sady jednorázově ověřit její citlivost na izolovaných kopiích: změnit `<` na `<=`, zachovat starý deadline při přepisu, obnovovat TTL při čtení nebo po expiraci vracet starou hodnotu. Každou takovou mutaci musí některý test odhalit. Mutace nepatří do výsledné implementace.

Hotová testovací sada musí projít na současném kontraktu, mít všechny pevné scénáře a odhalit uvedené mutace. Návrh neověřuje paměťové uvolňování expirovaných záznamů, souběh vláken ani výkon; `cache.py` takové vlastnosti neslibuje. V tomto úkolu vznikl pouze návrh: testy ani mutační kontrola nebyly spuštěny a nic nebylo instalováno.
