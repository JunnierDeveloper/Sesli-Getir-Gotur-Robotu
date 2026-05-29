
import pygame
import sys, time, math, heapq, threading
from queue import Queue

try:
    import pyttsx3
    TTS_OK = True
except:
    TTS_OK = False

try:
    import speech_recognition as sr
    SR_OK = True
except:
    SR_OK = False

# ─────────────────────────────────────────────
#  AYARLAR
# ─────────────────────────────────────────────
W, H   = 1500, 900
TW, TH = 72, 36          # tile genişlik/yükseklik
FPS    = 60

# ─────────────────────────────────────────────
#  RENK PALETİ  (her yüzey için 3 ton: üst/sol/sağ)
# ─────────────────────────────────────────────
C = {
    # Zemin renkleri (açık, orta, koyu ton)
    "floor_bed1":   ((230,220,210), (210,200,190), (190,180,170)),
    "floor_bed2":   ((215,225,230), (195,205,210), (175,185,190)),
    "floor_kitchen":((245,242,235), (225,222,215), (205,200,195)),
    "floor_hall":   ((200,195,185), (180,175,165), (160,155,145)),
    "floor_salon":  ((205,190,170), (185,170,150), (165,150,130)),
    "floor_bath":   ((225,232,238), (205,212,218), (185,192,198)),
    # Duvar renkleri
    "wall_top":     (240,237,230),
    "wall_left":    (200,197,190),
    "wall_right":   (170,167,160),
    "wall_border":  (120,115,110),
    # Mobilya renkleri
    "bed_frame":    ((160,135,110),(130,108,85),(105,85,65)),
    "bed_sheet":    ((195,185,215),(175,165,195),(155,145,175)),
    "sofa_body":    ((80,65,110),(60,48,85),(42,35,62)),
    "sofa_cushion": ((110,90,145),(90,72,120),(70,55,95)),
    "desk":         ((165,140,105),(140,118,82),(115,95,65)),
    "counter":      ((210,205,195),(185,180,170),(160,155,145)),
    "fridge":       ((225,230,232),(200,205,207),(175,180,182)),
    "stove":        ((80,80,85),(60,60,65),(45,45,50)),
    "sink_base":    ((190,195,200),(165,170,175),(140,145,150)),
    "toilet_body":  ((235,240,242),(210,215,217),(185,190,192)),
    "tv_body":      ((30,32,35),(22,24,27),(15,17,20)),
    "plant_pot":    ((140,100,60),(115,80,45),(90,60,35)),
    "nightstand":   ((145,120,90),(120,98,68),(98,78,52)),
    # Robot
    "robot_body":   ((55,65,80),(40,48,62),(30,36,48)),
    "robot_head":   (0,220,150),
    "robot_eye":    (0,255,200),
    # Item renkler
    "item_book":    (180,60,60),
    "item_cup":     (200,150,50),
    "item_remote":  (40,40,45),
    "item_towel":   (80,160,180),
    "item_toy":     (220,100,100),
    "item_glass":   (150,200,230),
    "item_plant":   (60,160,60),
    "item_candle":  (250,200,80),
    # UI
    "ui_bg":        (18,21,28),
    "ui_accent":    (0,195,255),
    "ui_text":      (200,210,220),
    "ui_dim":       (120,130,140),
    "ui_panel":     (25,30,42),
    "ui_input":     (35,42,55),
    "ui_btn":       (45,55,75),
    "ui_green":     (0,180,110),
    "battery_hi":   (60,200,100),
    "battery_lo":   (220,80,50),
}

# ─────────────────────────────────────────────
#  HARİTA  (kalın duvar sistemi: 1=duvar, 0=geçilebilir, diğerleri=mobilya)
# ─────────────────────────────────────────────
# Kodlar:
#  0  boş          1  duvar
#  2  tezgah       3  yatak
#  4  kanepe       5  sandalye
#  6  TV standı    7  lavabo      8  klozet
#  9  şarj         10 masa        11 buzdolabı
#  12 ocak         13 gece masa   14 yazı masası
#  15 bitki        16 koltuk

ROWS, COLS = 22, 32
MAP = [
    # 0
    [1]*COLS,
    # 1  YATAK OD.1 (sol üst)  |  MUTFAK (orta üst)  |  2.YATAK OD. (sağ üst)
    [1,3,3,0,0,13,0,3,3,1,1,1,1,1,2,2,2,2,2,1,1,1,1,3,3,0,0,13,3,3,0,1],
    # 2
    [1,3,3,0,0,0,0,3,3,1,12,0,0,11,2,0,0,0,2,1,14,0,0,3,3,0,0,0,3,3,0,1],
    # 3
    [1,0,0,0,0,0,0,0,0,1,0,0,0,0,2,2,2,2,2,1,0,0,0,0,0,0,0,15,0,0,0,1],
    # 4
    [1,0,13,0,0,0,0,0,13,1,0,0,0,0,0,0,0,0,0,1,0,5,0,0,5,0,0,0,0,0,0,1],
    # 5
    [1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,10,0,0,0,0,0,0,0,1],
    # 6  KORİDOR (ortada yatay geçit)
    [1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1],
    # 7
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    # 8
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    # 9  ──── ARA BÖLME ────
    [1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1],
    # 10  BANYO (sol)  |  DEPO/HOL (orta)  |  ÇALIŞMA ODASI (sağ)
    [1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    # 11
    [1,8,0,7,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,14,0,0,0,15,0,0,0,0,1],
    # 12
    [1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,5,0,0,1],
    # 13  ──── ARA BÖLME ────
    [1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1],
    # 14  SALON (geniş)
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    # 15
    [1,4,4,4,0,0,0,0,0,0,0,0,0,0,0,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    # 16
    [1,4,0,4,0,0,0,6,0,0,0,0,0,0,0,0,0,0,0,0,0,10,0,0,0,0,0,0,0,0,0,1],
    # 17
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,16,0,0,0,0,0,0,5,0,5,0,0,0,0,0,0,1],
    # 18
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,10,0,0,0,0,0,0,0,0,0,1],
    # 19
    [1,0,15,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,1],
    # 20
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    # 21
    [1]*COLS,
]

SOLID = {1,2,3,4,6,7,8,10,11,12,13,14,15,16}   # robot geçemez

def get_room(x, y):
    if y <= 5:
        if x <= 8: return "bed1"
        elif x <= 19: return "kitchen"
        else:          return "bed2"
    elif y <= 8: return "hall"
    elif y <= 12:
        if x <= 8: return "bath"
        elif x <= 21: return "hall"
        else: return "study"
    else: return "salon"

ROOM_FLOOR = {
    "bed1":   "floor_bed1",
    "bed2":   "floor_bed2",
    "kitchen":"floor_kitchen",
    "hall":   "floor_hall",
    "salon":  "floor_salon",
    "bath":   "floor_bath",
    "study":  "floor_bed2",
}
ROOM_NAME_TR = {
    "bed1":"YATAK ODASI 1","bed2":"YATAK ODASI 2",
    "kitchen":"MUTFAK","hall":"KORİDOR",
    "salon":"SALON","bath":"BANYO","study":"ÇALIŞMA ODASI",
}
ROOM_LABEL_POS = {
    "bed1":(3,2),"kitchen":(13,2),"bed2":(26,2),
    "hall":(15,7),"bath":(3,11),"study":(25,11),"salon":(15,16),
}

# ─────────────────────────────────────────────
#  A* PATHFINDING
# ─────────────────────────────────────────────
def astar(start, goal):
    if MAP[goal[1]][goal[0]] in SOLID: return None
    nbrs = [(0,1),(0,-1),(1,0),(-1,0)]
    came, g, f = {}, {start:0}, {start:abs(start[0]-goal[0])+abs(start[1]-goal[1])}
    heap = [(f[start], start)]; closed = set()
    while heap:
        _, cur = heapq.heappop(heap)
        if cur == goal:
            p=[]
            while cur in came: p.append(cur); cur=came[cur]
            return p[::-1]
        closed.add(cur)
        for dx,dy in nbrs:
            nb=(cur[0]+dx, cur[1]+dy)
            if not(0<=nb[0]<COLS and 0<=nb[1]<ROWS): continue
            if MAP[nb[1]][nb[0]] in SOLID: continue
            if nb in closed: continue
            ng = g[cur]+1
            if ng < g.get(nb,1e9):
                came[nb]=cur; g[nb]=ng
                f[nb]=ng+abs(nb[0]-goal[0])+abs(nb[1]-goal[1])
                heapq.heappush(heap,(f[nb],nb))
    return None

# ─────────────────────────────────────────────
#  ROBOT
# ─────────────────────────────────────────────
class Robot:
    def __init__(self):
        self.gx=float(15); self.gy=float(7)
        self.path=[]; self.state="IDLE"; self.final_act=None
        self.inventory=None; self.queue=[]
        self.speed=0.10; self.angle=0
        self.arm=0.0; self.battery=100.0; self.timer=0
        self.msg=""; self.msg_t=0
        self.sq=Queue()
        if TTS_OK: threading.Thread(target=self._tts,daemon=True).start()

    def _tts(self):
        eng=pyttsx3.init(); eng.setProperty('rate',155)
        while True:
            t=self.sq.get(); self.msg=t; self.msg_t=time.time()+3.5
            eng.say(t); eng.runAndWait()

    def say(self,t):
        self.msg=t; self.msg_t=time.time()+3.5
        if TTS_OK: self.sq.put(t)

    def add(self,x,y,act=None):
        self.queue.append((x,y,act))
        if self.state=="IDLE": self._next()

    def _next(self):
        if not self.queue: self.state="IDLE"; return
        tx,ty,act = self.queue.pop(0)
        p=astar((int(self.gx),int(self.gy)),(tx,ty))
        if p is None:
            self.say("Yol bulunamadı."); self.state="IDLE"; self._next(); return
        self.path=p; self.final_act=act
        if not self.path:
            self._start_action()
        else:
            self.state="MOVING"
            room=get_room(tx,ty)
            self.say(f"{ROOM_NAME_TR.get(room,'hedefe')} gidiyorum.")

    def _start_action(self):
        if self.final_act=="PICK": self.state="PICKING"; self.timer=time.time()+0.7
        elif self.final_act=="DROP": self.state="DROPPING"; self.timer=time.time()+0.7
        elif self.final_act=="DANCE": self.state="DANCING"; self.timer=time.time()+5
        else: self._next()

    def update(self, items):
        if self.state=="MOVING" and self.path:
            tx,ty=self.path[0]
            dx,dy=tx-self.gx, ty-self.gy
            d=math.hypot(dx,dy)
            if d>self.speed:
                self.gx+=dx/d*self.speed; self.gy+=dy/d*self.speed
                self.angle=math.atan2(dy,dx)
            else:
                self.gx,self.gy=float(tx),float(ty); self.path.pop(0)
                if not self.path: self._start_action()

        if self.state=="MOVING":
            self.arm=math.sin(time.time()*9)*0.35; self.battery-=0.008
        elif self.state=="DANCING":
            self.arm=math.sin(time.time()*18)*0.9
            self.gx+=math.sin(time.time()*5)*0.025
            self.gy+=math.cos(time.time()*4)*0.025
            if time.time()>self.timer: self.state="IDLE"
        else:
            self.arm*=0.85
            if int(self.gx)==30 and int(self.gy)==19 and self.battery<100: self.battery=min(100,self.battery+0.15)
            elif self.battery<100: self.battery=min(100,self.battery+0.003)

        if self.state in ("PICKING","DROPPING") and time.time()>self.timer:
            if self.state=="PICKING":
                for it in items:
                    if not it.carried and math.hypot(it.x-self.gx,it.y-self.gy)<1.8:
                        self.inventory=it; it.carried=True; self.say(f"{it.label} aldım."); break
            else:
                if self.inventory:
                    self.inventory.carried=False; self.inventory.x=self.gx; self.inventory.y=self.gy
                    self.say(f"{self.inventory.label} bıraktım."); self.inventory=None
            self._next()

# ─────────────────────────────────────────────
#  EŞYA
# ─────────────────────────────────────────────
class Item:
    def __init__(self, label, x, y, kind):
        self.label=label; self.x=float(x); self.y=float(y)
        self.kind=kind; self.carried=False

# ─────────────────────────────────────────────
#  İZOMETRİK YARDIMCILAR
# ─────────────────────────────────────────────
def iso(gx, gy, gz=0, tw=TW, th=TH, ox=0, oy=0):
    px = (gx - gy) * (tw // 2) + ox
    py = (gx + gy) * (th // 2) + oy - gz
    return (px, py)

def tile_poly(x, y, tw=TW, th=TH, ox=0, oy=0):
    return [
        iso(x,   y,   0, tw,th,ox,oy),
        iso(x+1, y,   0, tw,th,ox,oy),
        iso(x+1, y+1, 0, tw,th,ox,oy),
        iso(x,   y+1, 0, tw,th,ox,oy),
    ]

def draw_box(surf, x, y, h, col_top, col_l, col_r, tw, th, ox, oy, border=None):
    """Basit isometrik kutu çiz"""
    top = [iso(x,y,h,tw,th,ox,oy), iso(x+1,y,h,tw,th,ox,oy),
           iso(x+1,y+1,h,tw,th,ox,oy), iso(x,y+1,h,tw,th,ox,oy)]
    bot = [iso(x,y,0,tw,th,ox,oy), iso(x+1,y,0,tw,th,ox,oy),
           iso(x+1,y+1,0,tw,th,ox,oy), iso(x,y+1,0,tw,th,ox,oy)]
    # sol yüz (y+1 kenarı)
    pygame.draw.polygon(surf, col_l, [bot[2],bot[3],top[3],top[2]])
    # sağ yüz (x+1 kenarı)
    pygame.draw.polygon(surf, col_r, [bot[1],bot[2],top[2],top[1]])
    # üst yüz
    pygame.draw.polygon(surf, col_top, top)
    if border:
        pygame.draw.polygon(surf, border, top, 1)
        pygame.draw.polygon(surf, border, [bot[2],bot[3],top[3],top[2]], 1)
        pygame.draw.polygon(surf, border, [bot[1],bot[2],top[2],top[1]], 1)

def draw_partial_box(surf, x, y, x2, y2, h, col_top, col_l, col_r, tw, th, ox, oy):
    """Kısmi boyutlu kutu (mobilya detayları için)"""
    top = [iso(x,y,h,tw,th,ox,oy), iso(x2,y,h,tw,th,ox,oy),
           iso(x2,y2,h,tw,th,ox,oy), iso(x,y2,h,tw,th,ox,oy)]
    bot = [iso(x,y,0,tw,th,ox,oy), iso(x2,y,0,tw,th,ox,oy),
           iso(x2,y2,0,tw,th,ox,oy), iso(x,y2,0,tw,th,ox,oy)]
    pygame.draw.polygon(surf, col_l, [bot[2],bot[3],top[3],top[2]])
    pygame.draw.polygon(surf, col_r, [bot[1],bot[2],top[2],top[1]])
    pygame.draw.polygon(surf, col_top, top)

# ─────────────────────────────────────────────
#  MOBILYA ÇİZİM FONKSİYONLARI
# ─────────────────────────────────────────────
def draw_bed(surf, x, y, tw, th, ox, oy):
    # Çerçeve
    draw_box(surf, x, y, 8, *C["bed_frame"], tw, th, ox, oy, (80,60,42))
    # Yatak örtüsü (biraz içerde)
    draw_partial_box(surf, x+0.1, y+0.1, x+0.9, y+0.9, 14, *C["bed_sheet"], tw, th, ox, oy)
    # Yastık
    draw_partial_box(surf, x+0.12, y+0.12, x+0.88, y+0.38, 18, (250,248,252),(230,228,235),(210,208,215), tw, th, ox, oy)

def draw_sofa(surf, x, y, w, tw, th, ox, oy):
    # Oturma kısmı
    draw_box(surf, x, y, 12, *C["sofa_body"], tw, th, ox, oy, (35,28,50))
    # Sırt
    draw_partial_box(surf, x, y, x+w, y+0.25, 28, *C["sofa_body"], tw, th, ox, oy)
    # Yastıklar
    for i in range(int(w)):
        px = x + i + 0.08
        draw_partial_box(surf, px, y+0.15, px+0.84, y+0.85, 20, *C["sofa_cushion"], tw, th, ox, oy)

def draw_tv(surf, x, y, tw, th, ox, oy):
    # Stand
    draw_box(surf, x, y, 12, *C["desk"], tw, th, ox, oy, (90,70,45))
    # Ekran çerçeve
    draw_partial_box(surf, x+0.05, y+0.1, x+0.95, y+0.9, 30, *C["tv_body"], tw, th, ox, oy)
    # Ekran
    draw_partial_box(surf, x+0.1, y+0.15, x+0.9, y+0.85, 32, (15,40,80),(10,30,65),(8,25,55), tw, th, ox, oy)
    # Parlama efekti
    draw_partial_box(surf, x+0.12, y+0.18, x+0.4, y+0.45, 33, (40,80,160),(30,65,140),(20,50,120), tw, th, ox, oy)

def draw_counter(surf, x, y, tw, th, ox, oy):
    draw_box(surf, x, y, 20, *C["counter"], tw, th, ox, oy, (140,135,125))
    # Tezgah üstü çizgi
    draw_partial_box(surf, x+0.05, y+0.05, x+0.95, y+0.95, 22, (220,215,205),(200,195,185),(180,175,165), tw, th, ox, oy)

def draw_fridge(surf, x, y, tw, th, ox, oy):
    draw_box(surf, x, y, 38, *C["fridge"], tw, th, ox, oy, (150,155,157))
    # Kapı çizgisi
    draw_partial_box(surf, x+0.1, y+0.1, x+0.9, y+0.9, 40, (240,245,247),(215,220,222),(190,195,197), tw, th, ox, oy)
    # Kol
    draw_partial_box(surf, x+0.75, y+0.3, x+0.85, y+0.7, 42, (170,175,178),(150,155,158),(130,135,138), tw, th, ox, oy)

def draw_stove(surf, x, y, tw, th, ox, oy):
    draw_box(surf, x, y, 22, *C["stove"], tw, th, ox, oy, (30,30,33))
    # Ocak halkaları
    for bx, by in [(0.2,0.2),(0.7,0.2),(0.2,0.7),(0.7,0.7)]:
        cp = iso(x+bx, y+by, 24, tw, th, ox, oy)
        pygame.draw.circle(surf, (55,55,60), (int(cp[0]),int(cp[1])), 5)
        pygame.draw.circle(surf, (35,35,38), (int(cp[0]),int(cp[1])), 4)

def draw_desk(surf, x, y, tw, th, ox, oy):
    draw_box(surf, x, y, 18, *C["desk"], tw, th, ox, oy, (100,78,55))
    # Çekmece
    draw_partial_box(surf, x+0.1, y+0.1, x+0.9, y+0.4, 20, (178,152,115),(155,130,95),(130,108,78), tw, th, ox, oy)

def draw_table(surf, x, y, tw, th, ox, oy):
    # Yüzey
    draw_box(surf, x, y, 16, *C["desk"], tw, th, ox, oy, (100,78,55))
    # Bacaklar (köşelerde ince)
    for lx,ly in [(x+0.05,y+0.05),(x+0.85,y+0.05),(x+0.05,y+0.85),(x+0.85,y+0.85)]:
        draw_partial_box(surf, lx, ly, lx+0.1, ly+0.1, 16, (110,88,65),(90,70,50),(75,58,40), tw, th, ox, oy)

def draw_sink(surf, x, y, tw, th, ox, oy):
    draw_box(surf, x, y, 20, *C["sink_base"], tw, th, ox, oy, (130,135,140))
    # Havuz
    draw_partial_box(surf, x+0.15, y+0.15, x+0.85, y+0.85, 22, (175,210,230),(155,190,210),(135,170,190), tw, th, ox, oy)
    # Musluk
    draw_partial_box(surf, x+0.42, y+0.3, x+0.58, y+0.45, 30, (190,195,200),(165,170,175),(140,145,150), tw, th, ox, oy)

def draw_toilet(surf, x, y, tw, th, ox, oy):
    draw_box(surf, x, y, 18, *C["toilet_body"], tw, th, ox, oy, (160,165,167))
    draw_partial_box(surf, x+0.1, y+0.3, x+0.9, y+0.95, 22, (245,250,252),(220,225,227),(195,200,202), tw, th, ox, oy)
    draw_partial_box(surf, x+0.1, y+0.1, x+0.9, y+0.35, 20, (238,243,245),(213,218,220),(188,193,195), tw, th, ox, oy)

def draw_nightstand(surf, x, y, tw, th, ox, oy):
    draw_box(surf, x, y, 14, *C["nightstand"], tw, th, ox, oy, (90,72,52))

def draw_plant(surf, x, y, tw, th, ox, oy):
    # Saksı
    draw_partial_box(surf, x+0.3, y+0.3, x+0.7, y+0.7, 12, *C["plant_pot"], tw, th, ox, oy)
    # Yapraklar (birkaç çember)
    base=iso(x+0.5, y+0.5, 16, tw, th, ox, oy)
    for dx,dy,r in [(-5,-10,8),(5,-12,9),(0,-8,7),(-8,-5,6),(8,-5,6)]:
        pygame.draw.circle(surf,(55,155,60),(int(base[0]+dx),int(base[1]+dy)),r)
    for dx,dy,r in [(-4,-9,5),(4,-10,6),(0,-7,5)]:
        pygame.draw.circle(surf,(70,185,70),(int(base[0]+dx),int(base[1]+dy)),r)

def draw_chair(surf, x, y, tw, th, ox, oy):
    draw_box(surf, x+0.1, y+0.1, 12, *C["desk"], tw, th, ox, oy, (90,70,45))
    draw_partial_box(surf, x+0.1, y+0.1, x+0.9, y+0.3, 22, *C["sofa_cushion"], tw, th, ox, oy)

def draw_armchair(surf, x, y, tw, th, ox, oy):
    draw_box(surf, x+0.05, y+0.05, 14, *C["sofa_body"], tw, th, ox, oy, (35,28,50))
    draw_partial_box(surf, x+0.05, y+0.05, x+0.95, y+0.3, 26, *C["sofa_body"], tw, th, ox, oy)
    draw_partial_box(surf, x+0.15, y+0.2, x+0.85, y+0.85, 20, *C["sofa_cushion"], tw, th, ox, oy)

def draw_charger(surf, x, y, tw, th, ox, oy):
    draw_partial_box(surf, x+0.2, y+0.2, x+0.8, y+0.8, 6, (50,55,65),(38,42,50),(28,32,40), tw, th, ox, oy)
    p=iso(x+0.5, y+0.5, 8, tw, th, ox, oy)
    pygame.draw.circle(surf,(60,200,100),(int(p[0]),int(p[1])),7)
    pygame.draw.circle(surf,(100,240,140),(int(p[0]),int(p[1])),5)

FURN_DRAW = {
    2: draw_counter,
    3: draw_bed,
    6: draw_tv,
    7: draw_sink,
    8: draw_toilet,
    9: draw_charger,
    10: draw_table,
    11: draw_fridge,
    12: draw_stove,
    13: draw_nightstand,
    14: draw_desk,
    15: draw_plant,
    16: draw_armchair,
}

# ─────────────────────────────────────────────
#  EŞYA ÇİZİMİ
# ─────────────────────────────────────────────
def draw_item(surf, it, tw, th, ox, oy, font_sm):
    cx, cy = iso(it.x+0.5, it.y+0.5, 0, tw, th, ox, oy)
    k = it.kind
    if k == "book":
        # Kitap: ince dikdörtgen
        pts = [iso(it.x+0.2,it.y+0.3,6,tw,th,ox,oy), iso(it.x+0.8,it.y+0.3,6,tw,th,ox,oy),
               iso(it.x+0.8,it.y+0.7,6,tw,th,ox,oy), iso(it.x+0.2,it.y+0.7,6,tw,th,ox,oy)]
        pygame.draw.polygon(surf,(170,55,55),pts)
        pygame.draw.polygon(surf,(140,38,38),pts,1)
        # Dikey çizgiler (sayfalar görüntüsü)
        for i in range(2):
            p1 = iso(it.x+0.3+i*0.2, it.y+0.35, 7, tw,th,ox,oy)
            p2 = iso(it.x+0.3+i*0.2, it.y+0.65, 7, tw,th,ox,oy)
            pygame.draw.line(surf,(255,240,220),p1,p2,1)
    elif k == "cup":
        pygame.draw.circle(surf,(185,100,35),(int(cx),int(cy-8)),7)
        pygame.draw.circle(surf,(220,140,70),(int(cx),int(cy-8)),5)
        pygame.draw.circle(surf,(255,200,100),(int(cx),int(cy-9)),2)
    elif k == "remote":
        pts = [iso(it.x+0.3,it.y+0.25,5,tw,th,ox,oy), iso(it.x+0.7,it.y+0.25,5,tw,th,ox,oy),
               iso(it.x+0.7,it.y+0.75,5,tw,th,ox,oy), iso(it.x+0.3,it.y+0.75,5,tw,th,ox,oy)]
        pygame.draw.polygon(surf,(35,38,42),pts)
        for i in range(3):
            p=iso(it.x+0.5, it.y+0.35+i*0.12, 7, tw,th,ox,oy)
            pygame.draw.circle(surf,(70,75,80),(int(p[0]),int(p[1])),2)
    elif k == "towel":
        pts = [iso(it.x+0.15,it.y+0.3,5,tw,th,ox,oy), iso(it.x+0.85,it.y+0.3,5,tw,th,ox,oy),
               iso(it.x+0.85,it.y+0.7,5,tw,th,ox,oy), iso(it.x+0.15,it.y+0.7,5,tw,th,ox,oy)]
        pygame.draw.polygon(surf,(75,155,175),pts)
        pygame.draw.polygon(surf,(55,135,155),pts,1)
    elif k == "toy":
        pygame.draw.circle(surf,(210,80,80),(int(cx),int(cy-8)),8)
        pygame.draw.circle(surf,(240,120,120),(int(cx),int(cy-9)),5)
        pygame.draw.circle(surf,(255,200,200),(int(cx-2),int(cy-12)),3)
    elif k == "glass":
        pygame.draw.circle(surf,(130,190,220),(int(cx),int(cy-8)),6)
        pygame.draw.circle(surf,(180,225,245),(int(cx),int(cy-9)),4)
    elif k == "candle":
        pygame.draw.circle(surf,(240,195,80),(int(cx),int(cy-7)),5)
        # Alev
        for dy in range(8):
            t2=time.time()*3
            fx = cx + math.sin(t2+dy)*1.5
            pygame.draw.circle(surf,(255,140,30),(int(fx),int(cy-12-dy//2)),2)
        pygame.draw.circle(surf,(255,220,100),(int(cx),int(cy-14)),2)
    elif k == "plant_s":
        pygame.draw.circle(surf,(50,145,55),(int(cx),int(cy-10)),7)
        pygame.draw.circle(surf,(65,175,65),(int(cx-3),int(cy-14)),5)
    else:
        pygame.draw.circle(surf,(200,200,200),(int(cx),int(cy-6)),7)

    # Etiket
    lbl = font_sm.render(it.label, True, (240,240,240))
    surf.blit(lbl, (cx - lbl.get_width()//2, cy - 26))

# ─────────────────────────────────────────────
#  SİMÜLASYON
# ─────────────────────────────────────────────
class Sim:
    def __init__(self):
        pygame.init()
        self.W, self.H = W, H
        self.screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
        pygame.display.set_caption("Ev Robotu — Gerçekçi Simülasyon")
        self.clock = pygame.time.Clock()

        self.font_lg = pygame.font.SysFont("Segoe UI",  22, bold=True)
        self.font_md = pygame.font.SysFont("Segoe UI",  16)
        self.font_sm = pygame.font.SysFont("Consolas",  12)
        self.font_room= pygame.font.SysFont("Segoe UI", 14, bold=True)

        self.robot = Robot()
        self.items = [
            # Yatak Odası 1
            Item("Gece Kitabı",  2,   3,  "book"),
            Item("Çalar Saat",   6,   3,  "cup"),
            # Yatak Odası 2
            Item("Oyuncak Ayı",  24,  3,  "toy"),
            Item("Kitap",        27,  3,  "book"),
            # Mutfak
            Item("Kahve",        13,  3,  "cup"),
            # Koridor
            Item("Vazo",         15,  8,  "candle"),
            # Çalışma Odası
            Item("Not Defteri",  25,  12, "book"),
            # Salon
            Item("Uzaktan K.",   2,   16, "remote"),
            Item("Dergi",        4,   18, "book"),
            Item("Mum",          20,  18, "candle"),
            # Banyo
            Item("Havlu",        3,   11, "towel"),
        ]

        self.input_txt = ""
        self.mode = "TEXT"
        self.logs = ["Sistem hazır.", "Komut girin veya konuşun."]
        self.zoom = 1.0
        self.offset = [W//2 - 580, 60]
        self.drag = False; self.drag_start = (0,0); self.offset_start = [0,0]
        self.help_scroll = 0
        self.cmds_help = [
            "── HAREKET ──","Yatak odasına git","Mutfağa git",
            "Salona git","Banyoya git","Çalışma odasına git",
            "Koridora git",
            "── ETKİLEŞİM ──","Eşyayı getir","Eşyayı bırak",
            "── GÖREVLER ──","Devriye gez","Temizlik yap","Dans et",
            "── SİSTEM ──","Durumun ne?","Dur","Şarj'a git",
        ]

        if SR_OK: threading.Thread(target=self._mic, daemon=True).start()

    # ── Ses tanıma ──────────────────────────────
    def _mic(self):
        r=sr.Recognizer()
        with sr.Microphone() as src:
            while True:
                if self.mode=="VOICE":
                    r.adjust_for_ambient_noise(src)
                    try:
                        a=r.listen(src,timeout=4)
                        t=r.recognize_google(a,language="tr-TR")
                        self.log(f"Ses: {t}"); self.parse(t)
                    except: pass
                time.sleep(0.2)

    def log(self, t): self.logs.append(t); self.logs=self.logs[-30:]

    # ── Komut Çözümleme ─────────────────────────
    def parse(self, raw):
        raw=raw.lower()
        for cmd in raw.replace("sonra","ve").replace("ardından","ve").split("ve"):
            cmd=cmd.strip()
            if not cmd: continue

            salon = any(x in cmd for x in ["salon","oturma","tv"])
            yatak = any(x in cmd for x in ["yatak","uyku"])
            yatak2= "ikinci" in cmd or "2." in cmd or "çocuk" in cmd
            mutfak= any(x in cmd for x in ["mutfak","yemek","tezgah"])
            banyo = any(x in cmd for x in ["banyo","tuvalet","lavabo"])
            calisma=any(x in cmd for x in ["çalışma","ofis","study"])
            koridor=any(x in cmd for x in ["koridor","hol","geçit"])

            if any(x in cmd for x in ["git","geç","yürü","ilerle"]):
                if mutfak:    self.robot.add(14,2)
                elif yatak2:  self.robot.add(25,2)
                elif yatak:   self.robot.add(3,2)
                elif salon:   self.robot.add(15,16)
                elif banyo:   self.robot.add(4,11)
                elif calisma: self.robot.add(25,11)
                elif koridor: self.robot.add(15,7)
                elif "şarj" in cmd: self.robot.add(30,19)
                else: self.log("Nereye gideyim?")

            elif any(x in cmd for x in ["getir","al","topla"]):
                near = min(self.items, key=lambda i: math.hypot(i.x-self.robot.gx, i.y-self.robot.gy), default=None)
                if near and not near.carried:
                    self.robot.add(int(near.x),int(near.y),"PICK")
                    self.log(f"{near.label} alınıyor.")

            elif "bırak" in cmd:
                self.robot.add(int(self.robot.gx),int(self.robot.gy),"DROP")

            elif "devriye" in cmd:
                for p in [(3,2),(25,2),(14,2),(15,7),(4,11),(25,11),(15,16)]:
                    self.robot.add(*p)
                self.log("Devriye başladı.")
            elif "temizlik" in cmd or "süpür" in cmd:
                for p in [(2,2),(25,2),(14,2),(4,11),(15,16),(15,7)]:
                    self.robot.add(*p)
                self.log("Temizlik başladı.")
            elif "dans" in cmd:
                self.robot.add(int(self.robot.gx),int(self.robot.gy),"DANCE")
            elif "şarj" in cmd:
                self.robot.add(30,19); self.log("Şarj'a gidiliyor.")
            elif "durum" in cmd:
                r=ROOM_NAME_TR.get(get_room(int(self.robot.gx),int(self.robot.gy)),"bilinmiyor")
                self.robot.say(f"Ben {r} bölgesindeyim, batarya %{int(self.robot.battery)}.")
            elif "dur" in cmd:
                self.robot.queue=[]; self.robot.state="IDLE"
                self.robot.say("Durdum.")
            else:
                self.log(f"Anlaşılamadı: {cmd}")

    # ── DRAW ────────────────────────────────────
    def tw(self): return int(TW * self.zoom)
    def th(self): return int(TH * self.zoom)
    def ox(self): return int(self.offset[0])
    def oy(self): return int(self.offset[1])

    def draw(self):
        self.screen.fill(C["ui_bg"])
        tw,th,ox,oy = self.tw(), self.th(), self.ox(), self.oy()

        # ── ZEMİN & DUVAR ───────────────────────
        for y in range(ROWS):
            for x in range(COLS):
                t = MAP[y][x]
                room = get_room(x,y)
                fkey = ROOM_FLOOR.get(room,"floor_hall")
                ft,fl,fr = C[fkey]

                p = tile_poly(x, y, tw, th, ox, oy)

                if t == 1:  # DUVAR
                    h = int(52 * self.zoom)
                    wall_pts_front = [
                        iso(x,y+1,0,tw,th,ox,oy), iso(x+1,y+1,0,tw,th,ox,oy),
                        iso(x+1,y+1,h,tw,th,ox,oy), iso(x,y+1,h,tw,th,ox,oy)
                    ]
                    wall_pts_side = [
                        iso(x+1,y,0,tw,th,ox,oy), iso(x+1,y+1,0,tw,th,ox,oy),
                        iso(x+1,y+1,h,tw,th,ox,oy), iso(x+1,y,h,tw,th,ox,oy)
                    ]
                    wall_top_pts = [
                        iso(x,y,h,tw,th,ox,oy), iso(x+1,y,h,tw,th,ox,oy),
                        iso(x+1,y+1,h,tw,th,ox,oy), iso(x,y+1,h,tw,th,ox,oy)
                    ]
                    pygame.draw.polygon(self.screen, C["wall_left"],  wall_pts_front)
                    pygame.draw.polygon(self.screen, C["wall_right"], wall_pts_side)
                    pygame.draw.polygon(self.screen, C["wall_top"],   wall_top_pts)
                    pygame.draw.polygon(self.screen, C["wall_border"],wall_top_pts,1)
                    pygame.draw.polygon(self.screen, C["wall_border"],wall_pts_front,1)
                    pygame.draw.polygon(self.screen, C["wall_border"],wall_pts_side,1)
                else:
                    # Zemin çiz
                    pygame.draw.polygon(self.screen, ft, p)
                    # Zemin deseni (ince grid çizgileri)
                    pygame.draw.polygon(self.screen, fl, p, 1)

        # ── MOBİLYA ─────────────────────────────
        for y in range(ROWS):
            for x in range(COLS):
                t = MAP[y][x]
                if t in FURN_DRAW:
                    FURN_DRAW[t](self.screen, x, y, tw, th, ox, oy)
                elif t == 4:
                    pass  # kanepe ayrıca işlenecek
                elif t == 5:
                    draw_chair(self.screen, x, y, tw, th, ox, oy)

        # Kanepe gruplarını çiz
        drawn_sofa = set()
        for y in range(ROWS):
            for x in range(COLS):
                if MAP[y][x]==4 and (x,y) not in drawn_sofa:
                    # Yatay kaç tile birleşik?
                    w=1
                    while x+w < COLS and MAP[y][x+w]==4: w+=1
                    draw_sofa(self.screen, x, y, w, tw, th, ox, oy)
                    for i in range(w): drawn_sofa.add((x+i,y))

        # ── EŞYALAR ─────────────────────────────
        for it in self.items:
            if not it.carried:
                draw_item(self.screen, it, tw, th, ox, oy, self.font_sm)

        # ── ODA ETİKETLERİ ──────────────────────
        for room, (lx,ly) in ROOM_LABEL_POS.items():
            p = iso(lx, ly, 0, tw, th, ox, oy)
            name = ROOM_NAME_TR[room]
            txt = self.font_room.render(name, True, (255,255,255,180))
            shd = self.font_room.render(name, True, (0,0,0))
            self.screen.blit(shd, (p[0]-txt.get_width()//2+1, p[1]+1))
            self.screen.blit(txt, (p[0]-txt.get_width()//2, p[1]))

        # ── ROBOT ───────────────────────────────
        self._draw_robot(tw, th, ox, oy)

        # ── UI PANELİ ───────────────────────────
        self._draw_ui()

        pygame.display.flip()

    def _draw_robot(self, tw, th, ox, oy):
        gx,gy = self.robot.gx+0.5, self.robot.gy+0.5
        cx,cy = iso(gx, gy, 0, tw, th, ox, oy)
        bh = int(36*self.zoom)

        # Gölge
        pygame.draw.ellipse(self.screen,(0,0,0,80),(cx-16,cy-4,32,10))

        # Gövde
        body_pts = [
            (cx-12, cy-8), (cx+12, cy-8),
            (cx+12, cy-8-bh), (cx-12, cy-8-bh)
        ]
        pygame.draw.polygon(self.screen, C["robot_body"][0],
            [(cx-12,cy-8),(cx+12,cy-8),(cx+12,cy-8-bh),(cx-12,cy-8-bh)])
        # Gövde kenarları
        pygame.draw.line(self.screen,(80,90,110),(cx-12,cy-8),(cx-12,cy-8-bh),2)
        pygame.draw.line(self.screen,(80,90,110),(cx+12,cy-8),(cx+12,cy-8-bh),2)

        # Kafa
        kh = cy - 8 - bh
        pygame.draw.circle(self.screen, (50,60,78), (cx,kh-12), 14)
        pygame.draw.circle(self.screen, C["robot_head"], (cx,kh-12), 12)
        # Göz
        eye_c = C["robot_eye"] if self.robot.state in ("MOVING","DANCING") else (0,180,130)
        pygame.draw.circle(self.screen, eye_c, (cx,kh-12), 5)
        pygame.draw.circle(self.screen, (255,255,255), (cx+1,kh-14), 2)

        # Kollar
        for side in (-1,1):
            ax = cx + side*14
            ay = kh + bh//2
            hx = ax + side*int(12*math.cos(self.robot.arm))*int(self.zoom)
            hy = ay + int(10*math.sin(self.robot.arm))*int(self.zoom)
            pygame.draw.line(self.screen,(80,95,115),(ax,ay),(hx,hy),5)
            pygame.draw.circle(self.screen,(100,115,135),(int(hx),int(hy)),4)

        # Taşınan eşya
        if self.robot.inventory:
            draw_item(self.screen, self.robot.inventory, tw, th, ox, oy, self.font_sm)

        # Konuşma balonu
        if self.robot.msg and time.time()<self.robot.msg_t:
            mw,mh = self.font_md.size(self.robot.msg)
            bx,by = cx-mw//2-10, kh-60
            pygame.draw.rect(self.screen,(255,255,255),(bx,by,mw+20,mh+10),border_radius=8)
            pygame.draw.polygon(self.screen,(255,255,255),[(cx-5,by+mh+10),(cx+5,by+mh+10),(cx,by+mh+18)])
            self.screen.blit(self.font_md.render(self.robot.msg,True,(20,20,30)),(bx+10,by+5))

        # Batarya
        batt_x, batt_y = cx-20, kh-bh-35
        pygame.draw.rect(self.screen,(40,45,55),(batt_x,batt_y,40,7),border_radius=3)
        bc = C["battery_hi"] if self.robot.battery>25 else C["battery_lo"]
        pygame.draw.rect(self.screen,bc,(batt_x,batt_y,int(40*self.robot.battery/100),7),border_radius=3)
        pygame.draw.rect(self.screen,(120,130,145),(batt_x,batt_y,40,7),3,border_radius=3)

    def _draw_ui(self):
        PANEL = 290
        # Panel arkaplan
        pnl = pygame.Surface((PANEL, self.H), pygame.SRCALPHA)
        pnl.fill((*C["ui_panel"],245))
        self.screen.blit(pnl, (self.W-PANEL, 0))

        px = self.W - PANEL + 15
        py = 18

        # Başlık
        self.screen.blit(self.font_lg.render("EV ROBOTU", True, C["ui_accent"]), (px, py))
        room = ROOM_NAME_TR.get(get_room(int(self.robot.gx),int(self.robot.gy)),"─")
        self.screen.blit(self.font_sm.render(f"📍 {room}", True, C["ui_dim"]), (px, py+26))
        py += 55

        # Batarya
        bpct = int(self.robot.battery)
        bc = C["battery_hi"] if bpct>25 else C["battery_lo"]
        self.screen.blit(self.font_sm.render(f"⚡ Batarya  {bpct}%", True, C["ui_text"]), (px, py))
        pygame.draw.rect(self.screen,(40,45,58),(px,py+18,PANEL-30,8),border_radius=4)
        pygame.draw.rect(self.screen,bc,(px,py+18,int((PANEL-30)*bpct/100),8),border_radius=4)
        py += 36

        # Durum
        state_map={"IDLE":"Bekliyor","MOVING":"Hareket","PICKING":"Alıyor",
                   "DROPPING":"Bırakıyor","DANCING":"Dans ediyor"}
        stxt = state_map.get(self.robot.state, self.robot.state)
        sc = C["ui_green"] if self.robot.state=="IDLE" else C["ui_accent"]
        pygame.draw.rect(self.screen,sc,(px,py,PANEL-30,24),border_radius=6)
        self.screen.blit(self.font_md.render(stxt,True,(10,10,20)),(px+8,py+4))
        py += 36

        # Separat çizgi
        pygame.draw.line(self.screen,C["ui_btn"],(px,py),(self.W-15,py),1); py+=10

        # Komut listesi
        self.screen.blit(self.font_sm.render("KOMUTLAR", True, C["ui_accent"]), (px, py))
        py += 18
        clip = pygame.Surface((PANEL-30, 190), pygame.SRCALPHA)
        for i,c in enumerate(self.cmds_help):
            col = (180,160,255) if c.startswith("─") else C["ui_text"]
            clip.blit(self.font_sm.render(c, True, col), (0, i*17 - self.help_scroll))
        self.screen.blit(clip, (px, py)); py += 195

        # Kamera butonları
        pygame.draw.line(self.screen,C["ui_btn"],(px,py),(self.W-15,py),1); py+=10
        self.screen.blit(self.font_sm.render("KAMERA", True, C["ui_accent"]), (px, py)); py+=18
        for i,(lbl,act) in enumerate([("Q Döndür◄",(-1,0)),("E Döndür►",(1,0)),
                                       ("+ Yaklaş",(0,1)),("− Uzaklaş",(0,-1))]):
            bx=px+(i%2)*(130); by=py+(i//2)*30
            r=pygame.Rect(bx,by,120,24)
            pygame.draw.rect(self.screen,C["ui_btn"],r,border_radius=5)
            self.screen.blit(self.font_sm.render(lbl,True,C["ui_text"]),(bx+6,by+5))
        py += 75

        # Günlük
        pygame.draw.line(self.screen,C["ui_btn"],(px,py),(self.W-15,py),1); py+=10
        self.screen.blit(self.font_sm.render("GÜNLÜK", True, C["ui_accent"]), (px, py)); py+=18
        for l in self.logs[-8:]:
            self.screen.blit(self.font_sm.render(f"› {l}",True,C["ui_dim"]),(px,py)); py+=17

        # Input kutusu
        ip_rect=pygame.Rect(self.W-PANEL+10, self.H-80, PANEL-20, 38)
        pygame.draw.rect(self.screen,C["ui_input"],ip_rect,border_radius=8)
        pygame.draw.rect(self.screen,C["ui_btn"],ip_rect,2,border_radius=8)
        cursor = "│" if time.time()%1>0.5 else ""
        self.screen.blit(self.font_md.render(self.input_txt+cursor,True,(255,255,255)),
                         (ip_rect.x+10, ip_rect.y+10))

        # Mod
        md_r=pygame.Rect(self.W-PANEL+10, self.H-36, PANEL-20, 28)
        mc = C["ui_green"] if self.mode=="VOICE" else C["ui_btn"]
        pygame.draw.rect(self.screen,mc,md_r,border_radius=6)
        self.screen.blit(self.font_sm.render(f"MOD: {self.mode}  [TAB]",True,(255,255,255)),
                         (md_r.x+8, md_r.y+7))

    # ── MAIN LOOP ───────────────────────────────
    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type==pygame.QUIT: pygame.quit(); sys.exit()

                if e.type==pygame.VIDEORESIZE:
                    self.W,self.H=e.w,e.h
                    self.screen=pygame.display.set_mode((self.W,self.H),pygame.RESIZABLE)

                if e.type==pygame.MOUSEBUTTONDOWN:
                    if e.button==1:
                        self.drag=True
                        self.drag_start=e.pos
                        self.offset_start=self.offset[:]
                    if e.button==4: self.zoom=min(self.zoom*1.08, 2.5)
                    if e.button==5: self.zoom=max(self.zoom/1.08, 0.4)

                if e.type==pygame.MOUSEBUTTONUP and e.button==1:
                    self.drag=False

                if e.type==pygame.MOUSEMOTION and self.drag:
                    dx=e.pos[0]-self.drag_start[0]
                    dy=e.pos[1]-self.drag_start[1]
                    self.offset=[self.offset_start[0]+dx, self.offset_start[1]+dy]

                if e.type==pygame.MOUSEWHEEL:
                    # Panel scroll
                    if e.x==0:
                        self.help_scroll=max(0,min(self.help_scroll-e.y*14,
                                             len(self.cmds_help)*17-180))

                if e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_TAB:
                        self.mode="VOICE" if self.mode=="TEXT" else "TEXT"
                    elif e.key==pygame.K_RETURN:
                        if self.input_txt:
                            self.log(f"↩ {self.input_txt}")
                            self.parse(self.input_txt)
                            self.input_txt=""
                    elif e.key==pygame.K_BACKSPACE:
                        self.input_txt=self.input_txt[:-1]
                    elif e.key==pygame.K_q:
                        pass  # kamera dönüşü kaldırıldı (sürükleme sistemi var)
                    elif e.key==pygame.K_PLUS or e.key==pygame.K_EQUALS:
                        self.zoom=min(self.zoom*1.1, 2.5)
                    elif e.key==pygame.K_MINUS:
                        self.zoom=max(self.zoom/1.1, 0.4)
                    elif e.key==pygame.K_r:
                        self.zoom=1.0; self.offset=[W//2-580, 60]
                    else:
                        self.input_txt+=e.unicode

            self.robot.update(self.items)
            self.draw()
            self.clock.tick(FPS)

if __name__=="__main__": Sim().run()
