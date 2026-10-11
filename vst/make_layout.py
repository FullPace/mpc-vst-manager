#!/usr/bin/env python3
"""Writes params.json and layout.conf: one MPC tab per category (ALL, INSTRUMENTS, EFFECTS, ADDINS), each with its
own list, scroll position and info overlay. MPC doesn't tell a plugin which of its tabs is showing, so every tab has
its own parameters (prefix a_, i_, e_, d_) and the engine keeps all four lists current. The header, the view tabs
(DISCOVER, INSTALLED, UPDATES) and the footer's buttons are shared. Run after make_thumbs.py (it reads thumbs.txt)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CATS = [("a", "ALL"), ("i", "INSTRUMENTS"), ("e", "EFFECTS"), ("d", "ADDINS")]
ROWS, ROW_Y, ROW_H, ROW_STEP = 6, 208, 72, 73
STATES = ["none", "install", "update", "installed", "q_install", "q_update", "q_remove", "disabled", "menu"]
NBADGES = 24   # channel (none, stable, beta) x high CPU x tested x old install: make_images.py draws them
INFO_LINES = 8


def ro(key, name):
    return {"key": key, "name": name, "type": "readout", "display": "string"}


def opt(key, name, options):
    return {"key": key, "name": name, "options": options}


def trig(key, name):
    return {"key": key, "name": name, "type": "trigger", "momentary": True}


def params(nthumbs):
    p = [opt("tab", "View", ["DISCOVER", "INSTALLED", "UPDATES"]),
         opt("net", "Network", ["online", "offline"]),
         opt("disk", "Disk used", [str(k) for k in range(11)]),
         ro("disk_txt", "Disk free"),
         opt("upd_badge", "Updates badge", ["off", "on"]),
         ro("upd_count", "Updates"),
         opt("problem", "Problem", ["no", "yes"]),
         ro("problem_txt", "Problem text"),
         trig("refresh", "Refresh"),
         opt("foot", "Footer", ["counts", "warn", "error"]),
         ro("status", "Status"),
         opt("progress", "Progress", [str(k) for k in range(21)]),
         trig("update_all", "Update all"),
         opt("upd_all", "Update all on", ["off", "on"]),
         trig("apply", "Apply"),
         opt("apply_state", "Apply state", ["off", "apply", "preparing", "ready", "retry"]),
         trig("noop", "Badge")]
    thumbs = ["%d" % k for k in range(nthumbs)]
    for c, title in CATS:
        t = title.title()
        p += [{"key": c + "_scroll", "name": t + " scroll", "min": 0, "max": 100, "default": 100, "dynamic_display": True},
              opt(c + "_empty", t + " empty", ["no", "offline", "empty"]),
              ro(c + "_empty_txt", t + " empty text"),
              ro(c + "_count", t + " count"),
              opt(c + "_ov", t + " info", ["off", "on"]),
              trig(c + "_info_close", t + " info close"),
              opt(c + "_info_img", t + " info picture", thumbs),
              ro(c + "_info_name", t + " info name"),
              ro(c + "_info_by", t + " info by")]
        p += [ro("%s_info_d%d" % (c, k), "%s info text %d" % (t, k)) for k in range(1, 5)]
        p += [ro("%s_info_l%d" % (c, k), "%s info line %d" % (t, k)) for k in range(1, INFO_LINES + 1)]
        for r in range(1, ROWS + 1):
            n, k = "%s %d" % (t, r), "%s_r%d_" % (c, r)
            p += [{"key": "%s_card%d_1" % (c, r), "name": n, "type": "slot", "display": "string"},
                  opt(k + "vis", n + " shown", ["off", "on"]),
                  opt(k + "img", n + " picture", thumbs),
                  ro(k + "meta", n + " meta"),
                  opt(k + "badges", n + " badges", ["%d" % b for b in range(NBADGES)]),
                  ro(k + "ver", n + " version"),
                  ro(k + "size", n + " size"),
                  opt(k + "state", n + " state", STATES),
                  trig(k + "act", n + " action"),
                  trig(k + "info", n + " info"),
                  opt(k + "trash", n + " trash", ["off", "on", "open"]),
                  trig(k + "del", n + " trash tap"),
                  trig(k + "reinstall", n + " reinstall"),
                  trig(k + "remove", n + " remove")]
    return {"name": "Plugin Manager", "params": p}


HEAD = """# Plugin Manager screen, written by make_layout.py (edit that, not this). Live text sizes are MPC font heights
# = 1.52 x the CSS font size; 1280 x 628 plugin area; shadow coordinates, y = skin y + 86. The artwork is in images/
# (make_images.py, make_thumbs.py); everything live or switched is a parameter the engine computes (src/manager.c).
theme_bg=0c0c0d
theme_ink=9da1a7
theme_seg_active_tx=ffffff
theme_accent=ececed
theme_line=26272a
art_css=skin.css
"""


def tab(c, title, nthumbs):
    L = ["", "[tab %s]" % title, "art file=images/bg.svg"]
    # header (shared): logo and title are in bg.svg; online status, internal storage
    L += ["art file=images/net_on.svg x=880 y=104 w=100 h=24 when=net:online",
          "art file=images/net_off.svg x=880 y=104 w=100 h=24 when=net:offline",
          "readout box=0 w=120 h=23 cx=1196 cy=107 label=\"\" key=disk_txt tsize=21 tcolor=ececed talign=right tpad=0",
          "picture x=1056 y=123 w=200 h=5 key=disk files=\"%s\"" % ",".join("images/disk_%02d.svg" % k for k in range(11))]
    # view tabs (shared) and the device problem banner
    L += ["enum_h cx=314 cy=178 sw=188 sh=46 key=tab img=images/tab_off.svg img_on=images/tab_on.svg",
          "button cx=578 cy=178 label=\"\" key=noop img=images/upd_badge.svg w=24 h=24 when=upd_badge:on",
          "readout box=0 w=24 h=25 cx=578 cy=178 label=\"\" key=upd_count tsize=23 tweight=bold tcolor=1a1205 talign=center tpad=0 when=upd_badge:on",
          "art file=images/banner.svg x=620 y=160 w=636 h=36 when=problem:yes",
          "readout box=0 w=590 h=30 cx=957 cy=178 label=\"\" key=problem_txt tsize=23 tcolor=ffb4ae tpad=0 when=problem:yes"]
    # empty states
    L += ["art file=images/offline.svg x=24 y=208 w=1232 h=438 when=%s_empty:offline" % c,
          "button cx=640 cy=490 label=\"\" key=refresh img=images/btn_refresh.svg w=170 h=48 when=%s_empty:offline" % c,
          "art file=images/empty.svg x=24 y=208 w=1232 h=438 when=%s_empty:empty" % c,
          "readout box=0 w=800 h=32 cx=640 cy=427 label=\"\" key=%s_empty_txt tsize=30 tweight=regular tcolor=9da1a7 talign=center tpad=0" % c]
    # the rows
    for r in range(1, ROWS + 1):
        y = ROW_Y + (r - 1) * ROW_STEP
        cy = y + ROW_H // 2
        k = "%s_r%d_" % (c, r)
        L += ["",
              "list x=24 y=%d w=1190 h=%d cols=1 rows=1 th=%d gap=0 key=%s_card%d img=images/row_off.svg img_on=images/row_on.svg "
              "tx=72 ty=3 ttw=560 tth=30 tsize=27 tweight=bold tcolor=ececed when=%svis:on" % (y, ROW_H, ROW_H, c, r, k),
              "meter cx=54 cy=%d w=48 h=48 key=%simg strip=images/thumbs.png frames=%d when=%svis:on" % (cy, k, nthumbs, k),
              "readout box=0 w=560 h=19 cx=376 cy=%d label=\"\" key=%smeta tsize=18 tweight=regular tcolor=b4b7bc tpad=0" % (y + 41, k),
              "meter cx=246 cy=%d w=300 h=18 key=%sbadges strip=images/badges.svg frames=%d when=%svis:on" % (y + 61, k, NBADGES, k),
              "readout box=0 w=140 h=24 cx=760 cy=%d label=\"\" key=%sver tsize=22 tcolor=ececed tpad=0" % (y + 24, k),
              "readout box=0 w=140 h=19 cx=760 cy=%d label=\"\" key=%ssize tsize=18 tweight=regular tcolor=9da1a7 tpad=0" % (y + 49, k)]
        for st in STATES[1:-1]:
            L.append("button cx=950 cy=%d label=\"\" key=%sact img=images/btn_%s.svg w=160 h=44 when=%sstate:%s" % (cy, k, st, k, st))
        L += ["button cx=885 cy=%d label=\"\" key=%sreinstall img=images/btn_reinstall.svg w=110 h=44 when=%sstate:menu" % (cy, k, k),
              "button cx=1005 cy=%d label=\"\" key=%sremove img=images/btn_remove.svg w=110 h=44 when=%sstate:menu" % (cy, k, k),
              "button cx=1100 cy=%d label=\"\" key=%sinfo img=images/info.svg w=44 h=44 when=%svis:on" % (cy, k, k),
              "button cx=1165 cy=%d label=\"\" key=%sdel img=images/trash.svg w=44 h=44 when=%strash:on" % (cy, k, k),
              "button cx=1165 cy=%d label=\"\" key=%sdel img=images/trash_open.svg w=44 h=44 when=%strash:open" % (cy, k, k)]
    # the scroll bar: drag it, or turn the data wheel while it has focus
    L += ["", "slider_v cx=1241 cy=408 w=22 h=400 bw=36 ns=0 vs=12 label=\"\" key=%s_scroll img=images/scroll_thumb.svg "
              "base=images/scroll_track.svg when=%s_ov:off" % (c, c)]
    # the info overlay (over the list; the rows hide while it shows)
    L += ["", "art file=images/overlay.svg x=24 y=208 w=1232 h=438 when=%s_ov:on" % c,
          "button cx=1222 cy=242 label=\"\" key=%s_info_close img=images/close.svg w=44 h=44 when=%s_ov:on" % (c, c),
          "meter cx=78 cy=252 w=48 h=48 key=%s_info_img strip=images/thumbs.png frames=%d when=%s_ov:on" % (c, nthumbs, c),
          "readout box=0 w=900 h=34 cx=566 cy=240 label=\"\" key=%s_info_name tsize=32 tweight=bold tcolor=ececed tpad=0" % c,
          "readout box=0 w=900 h=22 cx=566 cy=268 label=\"\" key=%s_info_by tsize=20 tweight=regular tcolor=b4b7bc tpad=0" % c]
    for d in range(4):
        L.append("readout box=0 w=1180 h=24 cx=640 cy=%d label=\"\" key=%s_info_d%d tsize=21 tweight=regular tcolor=ececed tpad=0"
                 % (310 + d * 27, c, d + 1))
    for l in range(INFO_LINES):
        col, row = divmod(l, INFO_LINES // 2)
        L.append("readout box=0 w=580 h=22 cx=%d cy=%d label=\"\" key=%s_info_l%d tsize=20 tweight=regular tcolor=c9ccd1 tpad=0"
                 % (340 + col * 600, 452 + row * 30, c, l + 1))
    # footer: counts (or a warning), progress while downloading, UPDATE ALL, APPLY
    L += ["",
          "readout box=0 w=600 h=24 cx=330 cy=679 label=\"\" key=%s_count tsize=22 tweight=regular tcolor=ececed tpad=0 when=foot:counts" % c,
          "readout box=0 w=600 h=24 cx=330 cy=679 label=\"\" key=status tsize=22 tweight=regular tcolor=f0b44a tpad=0 when=foot:warn",
          "readout box=0 w=600 h=24 cx=330 cy=679 label=\"\" key=status tsize=22 tweight=regular tcolor=ff7a72 tpad=0 when=foot:error",
          "picture x=30 y=698 w=360 h=4 key=progress files=\"%s\"" % ",".join("images/progress_%02d.svg" % k for k in range(21)),
          "button cx=930 cy=684 label=\"\" key=update_all img=images/updall_on.svg w=170 h=42 when=upd_all:on",
          "button cx=930 cy=684 label=\"\" key=update_all img=images/updall_off.svg w=170 h=42 when=upd_all:off"]
    for st in ("off", "apply", "preparing", "ready", "retry"):
        L.append("button cx=1140 cy=684 label=\"\" key=apply img=images/apply_%s.svg w=210 h=42 when=apply_state:%s" % (st, st))
    L += ["", "# no Q-Links: nothing on this screen is a continuous control", "qlinks \"%s\" = -" % title]
    return L


def main():
    ids = [l for l in open(os.path.join(HERE, "thumbs.txt")).read().split("\n") if l]
    nthumbs = len(ids) + 1
    json.dump(params(nthumbs), open(os.path.join(HERE, "params.json"), "w"), indent=2)
    out = [HEAD.rstrip("\n")]
    for c, title in CATS:
        out += tab(c, title, nthumbs)
    open(os.path.join(HERE, "layout.conf"), "w").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
