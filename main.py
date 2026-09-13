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
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import platform
from pathlib import Path
import json, time, os, shutil, webbrowser, random

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
PHOTO_DIR = DATA_DIR / 'Pictures'
PHOTO_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = DATA_DIR / 'config.json'

DEFAULT = {
    'theme': 'dark', 'accent': '#7c5cff', 'background': '#0d0f14',
    'password': '1234', 'notes': [], 'photos': [],
    'installed': ['Calculator','Notes','Clock','Weather','Messages','Contacts','Calendar','Music','Gallery','Settings','About','App Store','Browser','Camera','Maps','Mail','Files','Game Center']
}

def load_cfg():
    data = DEFAULT.copy()
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f: data.update(json.load(f))
    except Exception: pass
    return data

def save_cfg(data):
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2)
    except Exception: pass

APPS = {
    'Calculator':'🧮','Notes':'📝','Clock':'⏰','Weather':'☀️','Messages':'💬','Contacts':'👥','Calendar':'📅','Music':'🎵',
    'Gallery':'🖼️','Settings':'⚙️','About':'ⓘ','App Store':'🛍️','Browser':'🌐','Camera':'📷','Maps':'📍','Mail':'✉️','Files':'📁','Game Center':'🎮'
}
STORE = [
    ('🌐','Browser','Built-in web browser launcher'),('📷','Camera','Live camera with camera selector'),('📍','Maps','Map app launcher'),
    ('✉️','Mail','Mail inbox simulator'),('📁','Files','Browse TonyOS app files'),('🎮','Game Center','Tap Rush mini-game')
]

class Card(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.padding = 10; self.spacing = 8
        with self.canvas.before:
            Color(*self._rgba('#171a23'))
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
        self.bind(pos=self._upd, size=self._upd)
    def _rgba(self, h):
        h=h.lstrip('#'); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))+(1,)
    def _upd(self,*_): self.rect.pos=self.pos; self.rect.size=self.size

class TonyOSApp(App):
    accent = StringProperty('#7c5cff')
    background = StringProperty('#0d0f14')
    theme = StringProperty('dark')
    current = StringProperty('Home')
    score = NumericProperty(0)
    running = BooleanProperty(False)

    def build(self):
        self.cfg=load_cfg(); self.accent=self.cfg.get('accent',DEFAULT['accent']); self.background=self.cfg.get('background',DEFAULT['background']); self.theme=self.cfg.get('theme','dark')
        self.title='TonyOS'
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.CAMERA])
            except Exception: pass
        Window.clearcolor=self._rgb(self.background)
        self.root=BoxLayout(orientation='vertical')
        self.body=BoxLayout(orientation='vertical')
        self.root.add_widget(self.body)
        self.nav=BoxLayout(size_hint_y=None,height=54,spacing=6,padding=6)
        self.root.add_widget(self.nav)
        self.go_home(); self._clock_event=Clock.schedule_interval(lambda dt:self._update_clock(),1)
        return self.root

    def _rgb(self,h):
        h=h.lstrip('#'); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))+(1,)
    def save(self):
        self.cfg['accent']=self.accent; self.cfg['background']=self.background; self.cfg['theme']=self.theme; save_cfg(self.cfg)
    def clear(self): self.body.clear_widgets()
    def label(self,text,size=18,bold=False,**kw): return Label(text=text,font_size=size,bold=bold,color=self._rgb('#f2f2f7'),halign='left',valign='middle',**kw)
    def button(self,text,fn=None, **kw):
        b=Button(text=text, background_normal='', background_color=self._rgb(self.accent), color=(1,1,1,1), size_hint_y=None,height=46,**kw)
        if fn: b.bind(on_release=fn)
        return b
    def top(self,title):
        bar=BoxLayout(size_hint_y=None,height=58,padding=(12,8),spacing=8)
        bar.add_widget(self.button('‹',lambda *_: self.go_home(),size_hint_x=None,width=48))
        bar.add_widget(self.label(title,19,True))
        self.body.add_widget(bar)
    def show_list(self,items):
        sv=ScrollView(); box=BoxLayout(orientation='vertical',size_hint_y=None,spacing=8,padding=10); box.bind(minimum_height=box.setter('height'))
        for item in items: box.add_widget(item)
        sv.add_widget(box); self.body.add_widget(sv)
    def app_available(self,name): return name in self.cfg.get('installed',[])
    def go_home(self):
        self.current='Home'; self.clear(); self.nav.clear_widgets()
        self._make_nav()
        self.body.add_widget(self.label('TonyOS',24,True,size_hint_y=None,height=45,padding=(16,0)))
        self.body.add_widget(self.label(time.strftime('%H:%M'),42,True,size_hint_y=None,height=62,padding=(16,0)))
        self.body.add_widget(self.label(time.strftime('%A, %B %d'),14,size_hint_y=None,height=28,padding=(16,0)))
        installed=[x for x in self.cfg.get('installed',[]) if x in APPS]
        grid=GridLayout(cols=3,spacing=10,padding=14,size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        for name in installed:
            card=BoxLayout(orientation='vertical',padding=6,size_hint_y=None,height=105)
            card.add_widget(Label(text=APPS[name],font_size=30))
            b=Button(text=name,background_normal='',background_color=(0,0,0,0),color=self._rgb('#f2f2f7'),size_hint_y=None,height=34)
            b.bind(on_release=lambda *_ ,n=name:self.open_app(n)); card.add_widget(b); grid.add_widget(card)
        sv=ScrollView(); sv.add_widget(grid); self.body.add_widget(sv)
    def _make_nav(self):
        for text,fn in [('Home',self.go_home),('Store',lambda *_:self.open_app('App Store')),('Settings',lambda *_:self.open_app('Settings'))]:
            b=Button(text=text,background_normal='',background_color=self._rgb('#171a23'),color=self._rgb('#f2f2f7')); b.bind(on_release=fn); self.nav.add_widget(b)
    def open_app(self,name):
        if not self.app_available(name): return
        self.current=name; self.clear()
        fn=getattr(self,'app_'+name.lower().replace(' ','_'),self.app_generic); fn()
    def _update_clock(self):
        if self.current=='Home' and self.body.children:
            pass

    def app_calculator(self):
        self.top('Calculator')
        col=BoxLayout(orientation='vertical',padding=12,spacing=8)
        expr=TextInput(font_size=28,multiline=False,halign='right',background_color=self._rgb('#171a23'),foreground_color=self._rgb('#f2f2f7'))
        col.add_widget(expr)
        grid=GridLayout(cols=4,spacing=6)
        for k in '789/456*123-0.=+':
            b=self.button(k); b.bind(on_release=lambda *_ ,k=k:self._calc_press(expr,k)); grid.add_widget(b)
        col.add_widget(grid); self.body.add_widget(col)
    def _calc_press(self,entry,k):
        if k=='=':
            try: entry.text=str(eval(entry.text,{'__builtins__':{}},{}))
            except Exception: entry.text='Error'
        else: entry.text+=k
    def app_notes(self):
        self.top('Notes'); inp=TextInput(hint_text='Write a note…',size_hint_y=None,height=46); self.body.add_widget(inp); self.body.add_widget(self.button('Save Note',lambda *_:self._save_note(inp))); sv=ScrollView(); box=BoxLayout(orientation='vertical',size_hint_y=None,spacing=8); box.bind(minimum_height=box.setter('height'))
        for n in self.cfg.get('notes',[]): box.add_widget(self.label('• '+n,size_hint_y=None,height=40)); sv.add_widget(box); self.body.add_widget(sv)
    def _save_note(self,inp):
        if inp.text.strip(): self.cfg.setdefault('notes',[]).insert(0,inp.text.strip()); self.save(); inp.text=''; self.app_notes()
    def app_clock(self): self.top('Clock'); self.body.add_widget(self.label(time.strftime('%H:%M:%S'),54,True,size_hint_y=None,height=100)); self.body.add_widget(self.label(time.strftime('%A, %B %d, %Y'),18,size_hint_y=None,height=48))
    def app_weather(self): self.top('Weather'); self.body.add_widget(self.label('☀️  Sunny\n72°F\nTonyOS Weather',26,True))
    def app_messages(self): self.top('Messages'); self.body.add_widget(self.label('💬 No messages yet.',18))
    def app_contacts(self): self.top('Contacts'); self.body.add_widget(self.label('👥 Contacts\nNo contacts yet.',18))
    def app_calendar(self): self.top('Calendar'); self.body.add_widget(self.label(time.strftime('%B %Y'),24,True)); self.body.add_widget(self.label(time.strftime('%A, %B %d'),18))
    def app_music(self): self.top('Music'); self.body.add_widget(self.label('🎵 TonyOS Music\nNo songs loaded.',20,True)); self.body.add_widget(self.button('▶ Play',lambda *_:None))
    def app_browser(self): self.top('Browser'); url=TextInput(text='https://www.google.com',multiline=False,size_hint_y=None,height=46); self.body.add_widget(url); self.body.add_widget(self.button('Open in Browser',lambda *_:self._open_url(url.text))); self.body.add_widget(self.label('TonyOS Browser launches web pages using the device browser on Android.',12))
    def _open_url(self,url):
        if not url.startswith(('http://','https://')): url='https://'+url
        try: webbrowser.open(url)
        except Exception: pass
    def app_maps(self): self.top('Maps'); self.body.add_widget(self.label('📍 TonyOS Maps',22,True)); self.body.add_widget(self.button('Open Maps',lambda *_:self._open_url('https://maps.google.com')))
    def app_mail(self): self.top('Mail'); self.body.add_widget(self.label('✉ Mail\nInbox is empty.',18))
    def app_files(self):
        self.top('Files')
        files=sorted([p for p in DATA_DIR.rglob('*') if p.is_file()], key=lambda p:p.stat().st_mtime, reverse=True)
        if not files:
            self.body.add_widget(self.label('📁 No TonyOS files yet.',16))
            return
        sv=ScrollView(); box=BoxLayout(orientation='vertical',size_hint_y=None,spacing=6,padding=10); box.bind(minimum_height=box.setter('height'))
        for p in files:
            box.add_widget(self.label('📄 '+str(p.relative_to(DATA_DIR)),13,size_hint_y=None,height=36))
        sv.add_widget(box); self.body.add_widget(sv)
    def app_gallery(self):
        self.top('Gallery'); files=sorted([p for p in PHOTO_DIR.iterdir() if p.suffix.lower() in ('.jpg','.jpeg','.png')], key=lambda p:p.stat().st_mtime, reverse=True)
        if not files: self.body.add_widget(self.label('🖼️ No photos yet.\nTake a photo in Camera and it will appear here.',16)); return
        grid=GridLayout(cols=2,spacing=8,padding=10,size_hint_y=None); grid.bind(minimum_height=grid.setter('height'))
        for p in files:
            grid.add_widget(Image(source=str(p),allow_stretch=True,keep_ratio=True,size_hint_y=None,height=150))
        sv=ScrollView(); sv.add_widget(grid); self.body.add_widget(sv)
    def app_camera(self):
        self.top('Camera'); row=BoxLayout(size_hint_y=None,height=46,spacing=8); row.add_widget(Label(text='Camera ID',size_hint_x=None,width=90,color=self._rgb('#f2f2f7'))); inp=TextInput(text='0',input_filter='int',multiline=False); row.add_widget(inp); self.body.add_widget(row)
        cam=Camera(index=0,resolution=(640,480),play=False); self.body.add_widget(cam)
        status=self.label('Camera stopped',12,size_hint_y=None,height=30); self.body.add_widget(status)
        def start(*_):
            try: cam.index=int(inp.text or 0); cam.play=True; status.text='Live camera'
            except Exception as e: status.text='Camera unavailable: '+str(e)
        def stop(*_): cam.play=False; status.text='Camera stopped'
        def snap(*_):
            if not cam.play: start()
            name=PHOTO_DIR/f'tony_{time.strftime("%Y%m%d_%H%M%S")}.png'; cam.export_to_png(str(name)); status.text='Saved to Gallery'; self.app_gallery() if False else None
        r=BoxLayout(size_hint_y=None,height=52,spacing=8,padding=8); r.add_widget(self.button('Start',start)); r.add_widget(self.button('Stop',stop)); r.add_widget(self.button('📸 Take Photo',snap)); self.body.add_widget(r)
    def app_game_center(self):
        self.top('Game Center'); self.score=0; self.running=False; count=self.label('Score: 0',30,True,size_hint_y=None,height=70); self.body.add_widget(count); info=self.label('Tap the button as many times as possible in 10 seconds!',15,size_hint_y=None,height=55); self.body.add_widget(info); tap=self.button('🔥 TAP!',lambda *_: self._tap(count),size_hint_y=None,height=160); self.body.add_widget(tap); self.body.add_widget(self.button('Start 10 Second Round',lambda *_: self._game_start(count,info)))
    def _game_start(self,count,info): self.score=0; self.running=True; count.text='Score: 0'; info.text='GO!'; Clock.unschedule(self._game_end); Clock.schedule_once(lambda dt:self._game_end(count,info),10)
    def _tap(self,count):
        if self.running: self.score+=1; count.text=f'Score: {self.score}'
    def _game_end(self,count,info): self.running=False; info.text=f'Round over! Final score: {self.score}'
    def app_settings(self):
        self.top('Settings'); self.body.add_widget(self.label('Personalize TonyOS',20,True,size_hint_y=None,height=50))
        for name,val in [('Violet','#7c5cff'),('Blue','#2878ff'),('Cyan','#00d9ff'),('Pink','#ff4f9a'),('Orange','#ff9142'),('Mint','#34c98f')]:
            self.body.add_widget(self.button(name,lambda *_ ,v=val:self._set_accent(v)))
        bgbox=BoxLayout(size_hint_y=None,height=52,spacing=8); bgbox.add_widget(self.button('Dark',lambda *_:self._set_bg('#0d0f14'))); bgbox.add_widget(self.button('Cloud',lambda *_:self._set_bg('#eef0f6'))); self.body.add_widget(bgbox)
        self.body.add_widget(self.label('Camera photos: '+str(len(list(PHOTO_DIR.glob('*')))),13))
    def _set_accent(self,v): self.accent=v; self.save(); self.go_home()
    def _set_bg(self,v): self.background=v; Window.clearcolor=self._rgb(v); self.save(); self.go_home()
    def app_about(self): self.top('About'); self.body.add_widget(self.label('ⓘ TonyOS\nAndroid Edition\n\nBuilt with Python + Kivy',20,True))
    def app_app_store(self):
        self.top('App Store'); sv=ScrollView(); box=BoxLayout(orientation='vertical',size_hint_y=None,spacing=8,padding=10); box.bind(minimum_height=box.setter('height'))
        for icon,name,desc in STORE:
            row=Card(size_hint_y=None,height=92); row.add_widget(Label(text=icon,font_size=30,size_hint_x=None,width=55)); text=BoxLayout(orientation='vertical'); text.add_widget(self.label(name,17,True)); text.add_widget(self.label(desc,11)); row.add_widget(text); b=self.button('INSTALLED' if self.app_available(name) else 'GET',lambda *_ ,n=name:self._toggle_install(n),size_hint_x=None,width=110); row.add_widget(b); box.add_widget(row)
        sv.add_widget(box); self.body.add_widget(sv)
    def _toggle_install(self,name):
        installed=self.cfg.setdefault('installed',[])
        if name in installed and name not in ('App Store','Settings','About'):
            installed.remove(name)
        elif name not in installed: installed.append(name)
        self.save(); self.app_app_store()
    def app_generic(self): self.top(self.current); self.body.add_widget(self.label(self.current+' app is available in TonyOS.',18))
    def on_stop(self):
        save_cfg(self.cfg)

if __name__ == '__main__': TonyOSApp().run()
