"""v13 runtime validation tests. No game or private memory dump required."""
import sys
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from d2r.reader import GameReader
from d2r.watcher import PotionWatcher
from d2r import models as m

base_stats={
    m.STAT["Level"]: 87, m.STAT["Life"]: 1250,
    m.STAT["MaxLife"]: 1500, m.STAT["Mana"]: 400,
    m.STAT["MaxMana"]: 500,
}
def player(stats=base_stats, name="AmazonHero", cls="Amazon"):
    return {"stats": stats, "name": name, "class": cls}
assert GameReader._kvhao_player_plausible(player())
assert not GameReader._kvhao_player_plausible(player(
    stats={m.STAT["Level"]:0},name="[]"))
assert not GameReader._kvhao_player_plausible(player(
    stats={m.STAT["Level"]:0,m.STAT["MaxLife"]:1,m.STAT["MaxMana"]:1},
    name="AmazonHero"))
assert not GameReader._kvhao_player_plausible(player(
    stats=base_stats, name="\u0000"))
assert not GameReader._kvhao_player_plausible(player(
    stats={**base_stats,m.STAT["MaxMana"]:0}))
assert GameReader._kvhao_player_plausible(player(
    stats={**base_stats,m.STAT["Level"]:256},name="Hero256"))

w=PotionWatcher.__new__(PotionWatcher)
w.config=SimpleNamespace(enabled=True,behavior={"pause_when_menus_open":True})
w.reader=SimpleNamespace(_kvhao_data_valid=False,offsets=SimpleNamespace(ok=True))
snap=SimpleNamespace(in_game=True,alive=True,menus_open=False,potion_counts=SimpleNamespace(ok=True),
    error=None,max_hp=1500,max_mana=500,hp=1250,mana=400)
assert not w._should_act(snap), "Must not use potions before character validation"
w.reader._kvhao_data_valid=True
assert w._should_act(snap), "Genuinely valid game state should retain normal behavior"
snap.error="INVALID_PLAYER_DATA"
assert not w._should_act(snap), "Unsafe snapshot must always block automatic keypresses"
print("V13_PLAYER_TEST_OK: false character stats rejected, valid and modded levels supported")
