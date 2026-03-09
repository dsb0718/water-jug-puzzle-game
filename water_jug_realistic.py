import tkinter as tk
import time
import math
from collections import deque

class RealisticJugGame:

    def __init__(self, root):

        self.root = root
        self.root.title("Realistic Water Jug Game")
        self.root.state("zoomed")

        self.levels = [
            {"cap1":4,"cap2":3,"target":2},
            {"cap1":5,"cap2":7,"target":6},
            {"cap1":8,"cap2":5,"target":4},
        ]

        self.level_index = 0
        self.level_completed = False
        self.load_level()

        self.selected=None
        self.score=0
        self.start_time=time.time()
        self.wave_phase=0
        self.is_pouring=False

        # ⭐ NEW HINT STORAGE
        self.hint_text=""

        self.canvas=tk.Canvas(root,bg="#0b1020",highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.info=tk.Label(root,font=("Segoe UI",12),bg="#0b1020",fg="white")
        self.info.pack()

        frame=tk.Frame(root,bg="#0b1020")
        frame.pack(pady=8)

        tk.Button(frame,text="Fill",width=8,command=self.fill_selected).pack(side="left",padx=5)
        tk.Button(frame,text="Empty",width=8,command=self.empty_selected).pack(side="left",padx=5)
        tk.Button(frame,text="Reset",width=8,command=self.reset).pack(side="left",padx=5)
        tk.Button(frame,text="💡 Hint",width=8,command=self.show_hint).pack(side="left",padx=5)

        self.next_btn=tk.Button(frame,text="Next Level ▶",width=12,
                                command=self.next_level,
                                bg="#2ecc71",fg="black")
        self.next_btn.pack(side="left",padx=10)
        self.next_btn.pack_forget()

        self.canvas.bind("<Button-1>",self.click_jug)
        self.root.bind("<Configure>", self.on_resize)

        self.update_ui()
        self.animate()

    def load_level(self):
        lvl=self.levels[self.level_index]
        self.cap1=lvl["cap1"]
        self.cap2=lvl["cap2"]
        self.target=lvl["target"]

        self.logic_j1=0
        self.logic_j2=0

        self.j1=0.0
        self.j2=0.0

    def on_resize(self,event):
        self.update_ui()

    def draw(self):
        self.canvas.delete("all")

        w=self.canvas.winfo_width()
        h=self.canvas.winfo_height()

        center_x=w//2
        left_x=center_x-120
        right_x=center_x+120

        self.left_x=left_x
        self.right_x=right_x

        self.draw_jug(left_x,self.j1,self.cap1,1)
        self.draw_jug(right_x,self.j2,self.cap2,2)

        self.canvas.create_text(left_x,h-60,
                                text=f"{self.logic_j1} / {self.cap1}",
                                fill="white",
                                font=("Segoe UI",13,"bold"))

        self.canvas.create_text(right_x,h-60,
                                text=f"{self.logic_j2} / {self.cap2}",
                                fill="white",
                                font=("Segoe UI",13,"bold"))

        if self.level_completed:
            self.canvas.create_rectangle(0,0,w,h,fill="#000000",stipple="gray50")
            self.canvas.create_text(w//2,h//2,
                                    text="LEVEL COMPLETED!",
                                    fill="#00ffcc",
                                    font=("Segoe UI",26,"bold"))

    def draw_jug(self,x,amount,cap,jug_id):

        top=120
        base=self.canvas.winfo_height()-100
        w=40

        self.canvas.create_rectangle(x-w,top,x+w,base,
                                     outline="#9fbaff",width=3)

        if self.selected==jug_id:
            self.canvas.create_rectangle(x-w-5,top-5,x+w+5,base+5,
                                         outline="red",width=2)

        self.draw_water(x-w,x+w,amount,cap,top,base)

    def draw_water(self,x1,x2,amount,cap,top,base):

        if amount<=0: return

        height=(amount/cap)*(base-top)
        top_y=base-height

        margin=3
        x1+=margin
        x2-=margin

        pts=[]
        for x in range(int(x1),int(x2)+1,4):
            wave=4*math.sin((x*0.05)+self.wave_phase)
            y=top_y+wave

            if y<top: y=top
            if y>base: y=base

            pts.append((x,y))

        poly=[]
        for p in pts:
            poly.append(p[0]); poly.append(p[1])

        poly.append(x2); poly.append(base)
        poly.append(x1); poly.append(base)

        self.canvas.create_polygon(poly,fill="#52d6ff",outline="")

    def click_jug(self,event):

        if self.level_completed or self.is_pouring:
            return

        x,y=event.x,event.y
        h=self.canvas.winfo_height()

        if self.left_x-40 < x < self.left_x+40 and 120 < y < h-100:
            self.handle_selection(1)

        elif self.right_x-40 < x < self.right_x+40 and 120 < y < h-100:
            self.handle_selection(2)

    def handle_selection(self,j):

        # ⭐ clear hint when user acts
        self.hint_text=""

        if self.selected is None:
            self.selected=j
        else:
            if self.selected!=j:
                self.animate_pour(self.selected,j)
            self.selected=None
        self.update_ui()

    def fill_selected(self):
        self.hint_text=""
        if self.selected==1:
            self.logic_j1=self.cap1
            self.j1=float(self.cap1)
        elif self.selected==2:
            self.logic_j2=self.cap2
            self.j2=float(self.cap2)
        self.update_ui()

    def empty_selected(self):
        self.hint_text=""
        if self.selected==1:
            self.logic_j1=0
            self.j1=0
        elif self.selected==2:
            self.logic_j2=0
            self.j2=0
        self.update_ui()

    def reset(self):
        self.load_level()
        self.hint_text=""
        self.update_ui()

    def animate_pour(self,f,t):

        if f==1:
            transfer=min(self.logic_j1,self.cap2-self.logic_j2)
        else:
            transfer=min(self.logic_j2,self.cap1-self.logic_j1)

        if transfer<=0: return

        self.is_pouring=True

        steps=25
        flow=transfer/steps

        def step():
            nonlocal steps

            if steps>0:

                if f==1:
                    self.j1-=flow
                    self.j2+=flow
                else:
                    self.j2-=flow
                    self.j1+=flow

                steps-=1
                self.update_ui()
                self.root.after(20,step)
            else:
                if f==1:
                    self.logic_j1-=transfer
                    self.logic_j2+=transfer
                else:
                    self.logic_j2-=transfer
                    self.logic_j1+=transfer

                self.j1=float(self.logic_j1)
                self.j2=float(self.logic_j2)

                self.is_pouring=False
                self.check_win()

        step()

    def show_hint(self):

        start=(self.logic_j1,self.logic_j2)
        target=self.target
        cap1=self.cap1
        cap2=self.cap2

        visited=set()
        q=deque()
        q.append((start,[]))

        while q:
            (a,b),path=q.popleft()

            if a==target or b==target:
                if path:
                    self.hint_text=f"💡 Hint: {path[0]}"
                    self.update_ui()
                return

            if (a,b) in visited: continue
            visited.add((a,b))

            moves=[
                ((cap1,b),"Fill Jug 1"),
                ((a,cap2),"Fill Jug 2"),
                ((0,b),"Empty Jug 1"),
                ((a,0),"Empty Jug 2"),
            ]

            t=min(a,cap2-b)
            moves.append(((a-t,b+t),"Pour Jug 1 → Jug 2"))

            t=min(b,cap1-a)
            moves.append(((a+t,b-t),"Pour Jug 2 → Jug 1"))

            for nxt,move in moves:
                q.append((nxt,path+[move]))

    def check_win(self):
        if self.logic_j1==self.target or self.logic_j2==self.target:
            self.level_completed=True
            self.next_btn.pack(side="left",padx=10)
            self.update_ui()

    def next_level(self):
        self.level_completed=False
        self.next_btn.pack_forget()
        self.level_index=(self.level_index+1)%len(self.levels)
        self.load_level()
        self.update_ui()

    def update_ui(self):
        self.draw()
        elapsed=int(time.time()-self.start_time)

        base_text=f"Level:{self.level_index+1}   Target:{self.target}   Time:{elapsed}s"

        if self.hint_text:
            base_text+="   |   "+self.hint_text

        self.info.config(text=base_text)

    def animate(self):
        self.wave_phase+=0.12
        self.draw()
        self.root.after(30,self.animate)


root=tk.Tk()
game=RealisticJugGame(root)
root.mainloop()
