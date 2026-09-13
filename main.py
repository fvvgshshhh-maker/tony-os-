from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.utils import platform
from pathlib import Path
import json, time, os, webbrowser, random, math

APP_DIR = Path(__file__).resolve().parent
if platform == 'android':
    try:
        from android.storage import app_storage_path
        DATA_DIR = Path(app_storage_path()) / 'TonyOS'
    except Exception:
        DATA_DIR = APP_DIR / 'TonyOS'
else:
    DATA_DIR = APP_DIR / 'TonyOS'
DATA_DIR.mkdir(parents=True, exist_ok=True)
PHOTO_DIR = DATA_DIR / 'Pictures'; PHOTO_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = DATA_DIR / 'config.json'

DEFAULT = {
    'theme':'dark','accent':'#7c5cff','background':'#0d0f14','password':'1234',
    'notes':[],'photos':[],'installed':['Calculator','Notes','Clock','Weather','Messages','Contacts','Calendar','Music','Gallery','Settings','About','App Store','Browser','Camera','Maps','Mail','Files','Game Center']
}
APPS = {'Calculator':'🧮','Notes':'📝','Clock':'⏰','Weather':'☀️','Messages':'💬','Contacts':'👥','Calendar':'📅','Music':'🎵','Gallery':'🖼️','Settings':'⚙️','About':'ⓘ','App Store':'🛍️','Browser':'🌐','Camera':'📷','Maps':'📍','Mail':'✉️','Files':'📁','Game Center':'🎮'}
STORE = [('🌐','Browser','Open websites from TonyOS'),('📷','Camera','Live camera + photo capture'),('📍','Maps','Launch maps and directions'),('✉️','Mail','TonyOS inbox'),('📁','Files','Browse TonyOS storage'),('🎮','Game Center','Play Tap Rush')]
ACCENTS = [('Violet','#7c5cff'),('Blue','#2878ff'),('Cyan','#00d9ff'),('Pink','#ff4f9a'),('Orange','#ff9142'),('Mint','#34c98f')]
BACKGROUNDS = [('Midnight','#0d0f14'),('Ocean','#071827'),('Purple','#17102b'),('Carbon','#151515'),('Forest','#0a1f18'),('Slate','#18202b'),('Cloud','#eef0f6')]


def load_cfg():
    data = dict(DEFAULT)
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH,'r',encoding='utf-8') as f: data.update(json.load(f))
    except Exception: pass
    return data

def save_cfg(data):
    try:
        with open(CONFIG_PATH,'w',encoding='utf-8') as f: json.dump(data,f,indent=2)
    except Exception: pass

class Rounded(BoxLayout):
    def __init__(self, color='#171a23', radius=18, border=False, **kw):
        super().__init__(**kw); self.card_color=color
        with self.canvas.before:
            Color(*TonyOSApp.hexrgba(color)); self.rect=RoundedRectangle(pos=self.pos,size=self.size,radius=[radius])
            if border:
                Color(*TonyOSApp.hexrgba('#303646')); self.line=Line(rounded_rectangle=(0,0,0,0,radius),width=1)
        self.bind(pos=self._sync,size=self._sync)
    def _sync(self,*_):
        self.rect.pos=self.pos; self.rect.size=self.size
        if hasattr(self,'line'): self.line.rounded_rectangle=(self.x,self.y,self.width,self.height,18)

class TonyOSApp(App):
    accent=StringProperty('#7c5cff'); background=StringProperty('#0d0f14'); theme=StringProperty('dark')
    current=StringProperty('Home'); score=NumericProperty(0); running=BooleanProperty(False)

    @staticmethod
    def hexrgba(h):
        h=h.lstrip('#'); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))+(1,)

    def build(self):
        self.cfg=load_cfg(); self.accent=self.cfg.get('accent',DEFAULT['accent']); self.background=self.cfg.get('background',DEFAULT['background']); self.theme=self.cfg.get('theme','dark')
        self.title='TonyOS'; Window.clearcolor=self.hexrgba(self.background)
        self.root=BoxLayout(orientation='vertical'); self.body=BoxLayout(orientation='vertical'); self.root.add_widget(self.body)
        self.nav=BoxLayout(size_hint_y=None,height=66,padding=(10,8),spacing=8); self.root.add_widget(self.nav)
        if platform=='android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.CAMERA])
            except Exception: pass
        self.go_home(); Clock.schedule_interval(lambda dt:self._update_clock(),1)
        return self.root

    def fg(self): return '#f5f5fa' if self.theme=='dark' else '#1b1c20'
    def muted(self): return '#9aa0b4' if self.theme=='dark' else '#6c7080'
    def panel(self): return '#171a23' if self.theme=='dark' else '#ffffff'
    def panel2(self): return '#1e2330' if self.theme=='dark' else '#f4f5f9'
    def save(self): self.cfg.update(accent=self.accent,background=self.background,theme=self.theme); save_cfg(self.cfg)
    def clear(self): self.body.clear_widgets()
    def lbl(self,text,size=16,bold=False,color=None,**kw):
        return Label(text=text,font_size=size,bold=bold,color=self.hexrgba(color or self.fg()),halign='left',valign='middle',**kw)
    def btn(self,text,fn=None,accent=False,**kw):
        bg=self.accent if accent else self.panel2()
        b=Button(text=text,background_normal='',background_color=self.hexrgba(bg),color=self.hexrgba('#ffffff' if accent else self.fg()),font_size=14,bold=accent,size_hint_y=None,height=48,border=(0,0,0,0),**kw)
        if fn: b.bind(on_release=fn)
        return b
    def section(self,text): self.body.add_widget(self.lbl(text,13,True,self.muted(),size_hint_y=None,height=34,padding=(18,0)))
    def top(self,title,subtitle=None):
        bar=BoxLayout(size_hint_y=None,height=72,padding=(14,10),spacing=10)
        back=self.btn('‹',lambda *_:self.go_home(),size_hint_x=None,width=46); bar.add_widget(back)
        texts=BoxLayout(orientation='vertical')
        texts.add_widget(self.lbl(title,20,True))
        if subtitle: texts.add_widget(self.lbl(subtitle,11,False,self.muted()))
        bar.add_widget(texts); self.body.add_widget(bar)
    def _make_nav(self):
        for text,icon,fn in [('Home','⌂',self.go_home),('Apps','▦',lambda *_:self.open_app('App Store')),('Settings','⚙',lambda *_:self.open_app('Settings'))]:
            b=Button(text=f'{icon}\n{text}',background_normal='',background_color=self.hexrgba(self.panel()),color=self.hexrgba(self.muted() if text!='Home' else self.accent),font_size=12)
            b.bind(on_release=fn); self.nav.add_widget(b)
    def go_home(self):
        self.current='Home'; self.clear(); self.nav.clear_widgets(); self._make_nav()
        hero=Rounded(color=self.panel(),orientation='vertical',size_hint_y=None,height=174,padding=(20,14),spacing=2)
        hero.add_widget(self.lbl('TonyOS',16,True,self.accent)); self.home_clock=self.lbl(time.strftime('%H:%M'),48,True,size_hint_y=None,height=65); hero.add_widget(self.home_clock)
        hero.add_widget(self.lbl(time.strftime('%A, %B %d'),14,False,self.muted(),size_hint_y=None,height=28)); hero.add_widget(self.lbl('Your device. Your OS.',12,False,self.muted()))
        self.body.add_widget(hero); self.section('FAVORITES')
        installed=[x for x in self.cfg.get('installed',[]) if x in APPS]
        grid=GridLayout(cols=4,spacing=10,padding=(14,4),size_hint_y=None); grid.bind(minimum_height=grid.setter('height'))
        for name in installed:
            cell=BoxLayout(orientation='vertical',spacing=3,size_hint_y=None,height=88)
            icon=Button(text=APPS[name],font_size=27,background_normal='',background_color=self.hexrgba(self.panel2()),color=self.hexrgba(self.fg()),size_hint_y=None,height=58)
            icon.bind(on_release=lambda *_ ,n=name:self.open_app(n)); cell.add_widget(icon)
            cell.add_widget(self.lbl(name,10,False,self.muted(),halign='center',size_hint_y=None,height=24)); grid.add_widget(cell)
        sv=ScrollView(); sv.add_widget(grid); self.body.add_widget(sv)
    def _update_clock(self):
        if self.current=='Home' and hasattr(self,'home_clock'): self.home_clock.text=time.strftime('%H:%M')

    def open_app(self,name):
        if name not in self.cfg.get('installed',[]): return
        self.current=name; self.clear(); getattr(self,'app_'+name.lower().replace(' ','_'),self.app_generic)()

    def app_calculator(self):
        self.top('Calculator','Quick calculations')
        wrap=BoxLayout(orientation='vertical',padding=14,spacing=10)
        expr=TextInput(text='',hint_text='0',multiline=False,font_size=30,halign='right',background_normal='',background_color=self.hexrgba(self.panel()),foreground_color=self.hexrgba(self.fg()),cursor_color=self.hexrgba(self.accent()),size_hint_y=None,height=72,padding=(12,16)); wrap.add_widget(expr)
        grid=GridLayout(cols=4,spacing=8)
        for k in '789/456*123-0.C+=':
            b=self.btn(k,accent=k in '=+',size_hint_y=None,height=56); b.bind(on_release=lambda *_ ,k=k:self._calc(expr,k)); grid.add_widget(b)
        wrap.add_widget(grid); self.body.add_widget(wrap)
    def _calc(self,e,k):
        if k=='C': e.text=''; return
        if k=='=':
            try: e.text=str(round(eval(e.text,{'__builtins__':{}},{}),10))
            except Exception: e.text='Error'
        else: e.text+=k

    def app_notes(self):
        self.top('Notes','Simple and fast')
        inp=TextInput(hint_text='Write something…',multiline=True,background_normal='',background_color=self.hexrgba(self.panel()),foreground_color=self.hexrgba(self.fg()),cursor_color=self.hexrgba(self.accent()),size_hint_y=None,height=100,padding=12)
        self.body.add_widget(inp); self.body.add_widget(self.btn('＋ Save note',lambda *_:self._save_note(inp),accent=True))
        self.section('SAVED NOTES')
        sv=ScrollView(); box=BoxLayout(orientation='vertical',size_hint_y=None,spacing=10,padding=(12,4)); box.bind(minimum_height=box.setter('height'))
        notes=self.cfg.get('notes',[])
        if not notes: box.add_widget(self.lbl('No notes yet.',14,False,self.muted(),size_hint_y=None,height=60))
        for n in notes:
            card=Rounded(color=self.panel(),size_hint_y=None,height=70,padding=(14,8)); card.add_widget(self.lbl('📝  '+str(n),13)); box.add_widget(card)
        sv.add_widget(box); self.body.add_widget(sv)
    def _save_note(self,inp):
        if inp.text.strip(): self.cfg.setdefault('notes',[]).insert(0,inp.text.strip()); self.save(); inp.text=''; self.app_notes()

    def app_clock(self):
        self.top('Clock','Time, stopwatch & timer')
        card=Rounded(color=self.panel(),orientation='vertical',size_hint_y=None,height=190,padding=18,spacing=4)
        self.clock_big=self.lbl(time.strftime('%H:%M:%S'),46,True,self.accent(),halign='center'); card.add_widget(self.clock_big); card.add_widget(self.lbl(time.strftime('%A, %B %d, %Y'),14,False,self.muted(),halign='center')); self.body.add_widget(card)
        self.section('TIMER'); row=BoxLayout(size_hint_y=None,height=52,spacing=8,padding=(12,0)); mins=TextInput(text='5',multiline=False,input_filter='float',background_normal='',background_color=self.hexrgba(self.panel()),foreground_color=self.hexrgba(self.fg()),padding=12); row.add_widget(mins); row.add_widget(self.btn('Start',lambda *_:self._start_timer(mins),accent=True)); self.body.add_widget(row); self.timer_label=self.lbl('05:00',24,True,self.fg(),halign='center',size_hint_y=None,height=55); self.body.add_widget(self.timer_label)
    def _start_timer(self,mins):
        try: self.timer_left=max(1,int(float(mins.text)*60))
        except: self.timer_left=300
        if hasattr(self,'timer_event'): self.timer_event.cancel()
        self.timer_event=Clock.schedule_interval(self._timer_tick,1)
    def _timer_tick(self,dt):
        self.timer_left-=1; self.timer_label.text=f'{self.timer_left//60:02d}:{self.timer_left%60:02d}'
        if self.timer_left<=0: self.timer_event.cancel()

    def app_weather(self):
        self.top('Weather','Today in TonyOS Weather')
        hero=Rounded(color=self.panel(),orientation='vertical',padding=20,size_hint_y=None,height=180); hero.add_widget(self.lbl('☀️',48,halign='center')); hero.add_widget(self.lbl('72°',40,True,halign='center')); hero.add_widget(self.lbl('Sunny · Feels like 74°',14,False,self.muted(),halign='center')); self.body.add_widget(hero)
        self.section('FORECAST'); days=[('Today','☀️','72°'),('Tomorrow','⛅','75°'),('Wed','🌤️','70°')]
        for d,ic,t in days:
            c=Rounded(color=self.panel(),size_hint_y=None,height=62,padding=(16,6)); c.add_widget(self.lbl(d,14,True)); c.add_widget(self.lbl(ic,22,halign='center',size_hint_x=None,width=55)); c.add_widget(self.lbl(t,16,True,halign='right')); self.body.add_widget(c)

    def simple_card_app(self,title,icon,message):
        self.top(title); c=Rounded(color=self.panel(),orientation='vertical',padding=22,size_hint_y=None,height=190); c.add_widget(self.lbl(icon,42,halign='center')); c.add_widget(self.lbl(message,16,True,halign='center')); self.body.add_widget(c)
    def app_messages(self): self.simple_card_app('Messages','💬','No messages yet')
    def app_contacts(self): self.simple_card_app('Contacts','👥','No contacts yet')
    def app_mail(self): self.simple_card_app('Mail','✉️','Inbox is empty')
    def app_calendar(self):
        self.top('Calendar'); self.body.add_widget(self.lbl(time.strftime('%B %Y'),25,True,padding=(18,8),size_hint_y=None,height=54)); self.simple_card_app_body('📅',time.strftime('%A, %B %d'))
    def simple_card_app_body(self,icon,message):
        c=Rounded(color=self.panel(),orientation='vertical',padding=20,size_hint_y=None,height=150); c.add_widget(self.lbl(icon,38,halign='center')); c.add_widget(self.lbl(message,16,True,halign='center')); self.body.add_widget(c)
    def app_music(self):
        self.top('Music','Your library'); self.simple_card_app_body('🎵','No songs loaded'); self.body.add_widget(self.btn('▶  Play',lambda *_:None,accent=True))
    def app_about(self):
        self.top('About','TonyOS Android Edition'); self.simple_card_app_body('◉','TonyOS\nVersion 3.0\nBuilt with Python + Kivy')

    def app_browser(self):
        self.top('Browser','Fast access to the web'); url=TextInput(text='https://www.google.com',multiline=False,background_normal='',background_color=self.hexrgba(self.panel()),foreground_color=self.hexrgba(self.fg()),padding=12,size_hint_y=None,height=52); self.body.add_widget(url); self.body.add_widget(self.btn('Open website',lambda *_:self._open_url(url.text),accent=True)); self.body.add_widget(self.lbl('The page opens in your device browser.',12,False,self.muted(),padding=(18,12),size_hint_y=None,height=50))
    def _open_url(self,url):
        if not url.startswith(('http://','https://')): url='https://'+url
        try: webbrowser.open(url)
        except: pass
    def app_maps(self): self.top('Maps','Directions & places'); self.simple_card_app_body('📍','Maps'); self.body.add_widget(self.btn('Open Maps',lambda *_:self._open_url('https://maps.google.com'),accent=True))

    def app_camera(self):
        self.top('Camera','Choose a camera and capture')
        row=BoxLayout(size_hint_y=None,height=50,spacing=8,padding=(12,0)); row.add_widget(self.lbl('Camera',13,True,size_hint_x=None,width=70)); inp=TextInput(text='0',input_filter='int',multiline=False,background_normal='',background_color=self.hexrgba(self.panel()),foreground_color=self.hexrgba(self.fg()),padding=10); row.add_widget(inp); self.body.add_widget(row)
        cam=Camera(index=0,resolution=(720,1280),play=False); self.body.add_widget(cam); status=self.lbl('Camera is off',12,False,self.muted(),halign='center',size_hint_y=None,height=34); self.body.add_widget(status)
        def start(*_):
            try: cam.index=int(inp.text or 0); cam.play=True; status.text='● Live camera'
            except Exception as e: status.text='Camera unavailable: '+str(e)
        def stop(*_): cam.play=False; status.text='Camera is off'
        def snap(*_):
            if not cam.play: start()
            name=PHOTO_DIR/f'tony_{time.strftime("%Y%m%d_%H%M%S")}_{random.randint(100,999)}.png'
            try: cam.export_to_png(str(name)); status.text='✓ Photo saved to Gallery'
            except Exception as e: status.text='Could not save photo: '+str(e)
        r=BoxLayout(size_hint_y=None,height=62,spacing=8,padding=(10,6)); r.add_widget(self.btn('Start',start)); r.add_widget(self.btn('Stop',stop)); r.add_widget(self.btn('● Capture',snap,accent=True)); self.body.add_widget(r)

    def app_gallery(self):
        self.top('Gallery','Your TonyOS photos'); files=sorted([p for p in PHOTO_DIR.iterdir() if p.suffix.lower() in ('.jpg','.jpeg','.png')],key=lambda p:p.stat().st_mtime,reverse=True)
        if not files: self.body.add_widget(self.lbl('🖼️  No photos yet.\nTake a picture with Camera.',16,False,self.muted(),halign='center',valign='middle')); return
        grid=GridLayout(cols=2,spacing=10,padding=10,size_hint_y=None); grid.bind(minimum_height=grid.setter('height'))
        for p in files:
            card=Rounded(color=self.panel(),orientation='vertical',size_hint_y=None,height=190,padding=6); card.add_widget(Image(source=str(p),allow_stretch=True,keep_ratio=True)); card.add_widget(self.lbl(p.name,9,False,self.muted(),halign='center',size_hint_y=None,height=24)); grid.add_widget(card)
        sv=ScrollView(); sv.add_widget(grid); self.body.add_widget(sv)

    def app_files(self):
        self.top('Files','TonyOS storage'); files=sorted([p for p in DATA_DIR.rglob('*') if p.is_file()],key=lambda p:p.stat().st_mtime,reverse=True)
        sv=ScrollView(); box=BoxLayout(orientation='vertical',size_hint_y=None,spacing=8,padding=12); box.bind(minimum_height=box.setter('height'))
        if not files: box.add_widget(self.lbl('📁 No files yet.',15,False,self.muted(),size_hint_y=None,height=70))
        for p in files:
            c=Rounded(color=self.panel(),size_hint_y=None,height=58,padding=(14,6)); c.add_widget(self.lbl('📄  '+str(p.relative_to(DATA_DIR)),12)); box.add_widget(c)
        sv.add_widget(box); self.body.add_widget(sv)

    def app_game_center(self):
        self.top('Game Center','Tap Rush'); self.score=0; self.running=False
        self.game_score=self.lbl('0',58,True,self.accent(),halign='center',size_hint_y=None,height=90); self.body.add_widget(self.game_score); self.body.add_widget(self.lbl('TAPS',11,True,self.muted(),halign='center',size_hint_y=None,height=24))
        self.body.add_widget(self.btn('🔥  TAP!',lambda *_:self._tap(),accent=True,size_hint_y=None,height=150)); self.body.add_widget(self.btn('Start 10 second round',lambda *_:self._game_start(),size_hint_y=None,height=54)); self.game_info=self.lbl('Press Start to play.',13,False,self.muted(),halign='center',size_hint_y=None,height=50); self.body.add_widget(self.game_info)
    def _game_start(self):
        self.score=0; self.running=True; self.game_score.text='0'; self.game_info.text='GO!'; Clock.unschedule(self._game_end); Clock.schedule_once(lambda dt:self._game_end(),10)
    def _tap(self):
        if self.running: self.score+=1; self.game_score.text=str(self.score)
    def _game_end(self): self.running=False; self.game_info.text=f'Round over · {self.score} taps'

    def app_settings(self):
        self.top('Settings','Make TonyOS yours')
        self.section('ACCENT COLOR')
        for name,val in ACCENTS:
            self.body.add_widget(self.btn(('✓  ' if self.accent==val else '    ')+name,lambda *_ ,v=val:self._set_accent(v),accent=self.accent==val))
        self.section('BACKGROUND')
        for name,val in BACKGROUNDS:
            self.body.add_widget(self.btn(('✓  ' if self.background==val else '    ')+name,lambda *_ ,v=val:self._set_bg(v),accent=self.background==val))
        self.section('DISPLAY')
        self.body.add_widget(self.btn('☼  Toggle light / dark mode',lambda *_:self._toggle_theme()))
        self.body.add_widget(self.btn('↺  Reset TonyOS settings',lambda *_:self._reset()))
    def _set_accent(self,v): self.accent=v; self.save(); self.go_home()
    def _set_bg(self,v): self.background=v; Window.clearcolor=self.hexrgba(v); self.save(); self.go_home()
    def _toggle_theme(self): self.theme='light' if self.theme=='dark' else 'dark'; self.save(); self.go_home()
    def _reset(self): self.cfg=dict(DEFAULT); self.accent=DEFAULT['accent']; self.background=DEFAULT['background']; self.theme='dark'; self.save(); self.go_home()

    def app_app_store(self):
        self.top('App Store','Extend your TonyOS')
        search=TextInput(hint_text='🔎  Search apps',multiline=False,background_normal='',background_color=self.hexrgba(self.panel()),foreground_color=self.hexrgba(self.fg()),padding=12,size_hint_y=None,height=52); self.body.add_widget(search)
        sv=ScrollView(); box=BoxLayout(orientation='vertical',size_hint_y=None,spacing=10,padding=12); box.bind(minimum_height=box.setter('height'))
        for icon,name,desc in STORE:
            row=Rounded(color=self.panel(),size_hint_y=None,height=88,padding=(12,8),spacing=10); row.add_widget(self.lbl(icon,30,halign='center',size_hint_x=None,width=50)); info=BoxLayout(orientation='vertical'); info.add_widget(self.lbl(name,16,True)); info.add_widget(self.lbl(desc,11,False,self.muted())); row.add_widget(info); row.add_widget(self.btn('OPEN' if self.app_available(name) else 'GET',lambda *_ ,n=name:self._store_action(n),accent=True,size_hint_x=None,width=92)); box.add_widget(row)
        sv.add_widget(box); self.body.add_widget(sv)
    def _store_action(self,name):
        if self.app_available(name): self.open_app(name)
        else: self.cfg.setdefault('installed',[]).append(name); self.save(); self.app_app_store()

    def app_generic(self): self.top(self.current); self.body.add_widget(self.lbl(self.current+' is ready.',18,True,padding=(18,20)))
    def on_stop(self): save_cfg(self.cfg)

if __name__=='__main__': TonyOSApp().run()
