"""
Division Game — Human vs Computer
Rules:
  - Start with a number in [20000..30000] divisible by 2, 3 and 4 (multiple of 12).
  - Players alternate: divide current number by 2, 3 or 4 (whole result only).
  - Even result  -> opponent loses 1 point.
  - Odd  result  -> current player gains 1 point.
  - Game ends when number <= 10. Most points wins.
"""

import tkinter as tk
from tkinter import ttk
import random, time, math


# ── DATA STRUCTURE ─────────────────────────────────────────────────────────────

class GameNode:
    """
    One node in the game tree.
    Children are generated on demand by expand() — tree is never pre-built.
    """
    def __init__(self, number, h_score, c_score, human_turn, move=None):
        self.number     = number      # current number on the board
        self.h_score    = h_score     # player 1 (human side) score
        self.c_score    = c_score     # player 2 (computer side) score
        self.human_turn = human_turn  # True = player 1 moves next
        self.move       = move        # divisor used to reach this node
        self.children   = []          # filled by expand()

    def terminal(self):
        return self.number <= 10

    def valid_moves(self):
        return [d for d in (2, 3, 4) if self.number % d == 0]

    def expand(self):
        """Create child nodes on the fly when the algorithm needs to go deeper."""
        if self.children:
            return self.children
        for d in self.valid_moves():
            r  = self.number // d
            nh, nc = self.h_score, self.c_score
            if r % 2 == 0:
                if self.human_turn: nc -= 1   # even -> opponent loses 1
                else:               nh -= 1
            else:
                if self.human_turn: nh += 1   # odd  -> current player gains 1
                else:               nc += 1
            self.children.append(
                GameNode(r, nh, nc, not self.human_turn, d))
        return self.children


# ── HEURISTIC ──────────────────────────────────────────────────────────────────

def heuristic(node):
    """
    Evaluate a non-terminal node at the depth limit (from computer's view).
    h1: score difference (main signal).
    h2: +0.5 if computer moves next (immediate opportunity), else -0.5.
    h3: number of valid moves for the side that moves next (more = more control).
    """
    h1 = node.c_score - node.h_score
    h2 = 0.5 if not node.human_turn else -0.5
    h3 = len(node.valid_moves()) * (0.3 if not node.human_turn else -0.3)
    return h1 + h2 + h3


# ── MINIMAX ────────────────────────────────────────────────────────────────────

def minimax(node, depth, stats):
    """Computer maximises, human minimises. Depth-limited look-ahead."""
    if node.terminal():
        stats['eval'] += 1
        return float(node.c_score - node.h_score)
    if depth == 0:
        stats['eval'] += 1
        return heuristic(node)
    children = node.expand()
    stats['gen'] += len(children)
    if not children:
        stats['eval'] += 1
        return float(node.c_score - node.h_score)
    if not node.human_turn:
        best = -math.inf
        for c in children:
            best = max(best, minimax(c, depth-1, stats))
        return best
    else:
        best = math.inf
        for c in children:
            best = min(best, minimax(c, depth-1, stats))
        return best


# ── ALPHA-BETA ─────────────────────────────────────────────────────────────────

def alphabeta(node, depth, alpha, beta, stats):
    """Minimax with alpha-beta pruning: skips branches where alpha >= beta."""
    if node.terminal():
        stats['eval'] += 1
        return float(node.c_score - node.h_score)
    if depth == 0:
        stats['eval'] += 1
        return heuristic(node)
    children = node.expand()
    stats['gen'] += len(children)
    if not children:
        stats['eval'] += 1
        return float(node.c_score - node.h_score)
    if not node.human_turn:
        val = -math.inf
        for c in children:
            val = max(val, alphabeta(c, depth-1, alpha, beta, stats))
            alpha = max(alpha, val)
            if alpha >= beta: break
        return val
    else:
        val = math.inf
        for c in children:
            val = min(val, alphabeta(c, depth-1, alpha, beta, stats))
            beta = min(beta, val)
            if alpha >= beta: break
        return val


# ── FIND BEST MOVE ─────────────────────────────────────────────────────────────

def best_move_for(number, my_score, opp_score, depth, use_ab):
    """
    Find the best divisor for the CURRENT player (always treated as maximiser).
    my_score  = score of the player who is about to move
    opp_score = score of the opponent
    Returns (divisor, stats_dict).
    """
    stats = {'gen': 0, 'eval': 0}
    t0    = time.perf_counter()
    # Frame current player as maximiser: human_turn=False means "computer moves"
    root     = GameNode(number, opp_score, my_score, False)
    children = root.expand()
    stats['gen'] += len(children)

    best_val, best_d = -math.inf, None
    for child in children:
        v = (alphabeta(child, depth-1, -math.inf, math.inf, stats)
             if use_ab else minimax(child, depth-1, stats))
        if v > best_val:
            best_val, best_d = v, child.move

    stats['ms'] = (time.perf_counter() - t0) * 1000
    return best_d, stats


# ── GUI ────────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Division Game")
        self.resizable(False, False)

        # settings
        self.v_first = tk.StringVar(value="human")
        self.v_algo  = tk.StringVar(value="alphabeta")
        self.v_depth = tk.IntVar(value=4)

        # play-tab display vars
        self.v_num    = tk.StringVar(value="—")
        self.v_hs     = tk.StringVar(value="0")
        self.v_cs     = tk.StringVar(value="0")
        self.v_status = tk.StringVar(value="Pick a starting number.")
        self.v_gen    = tk.StringVar(value="—")
        self.v_eval   = tk.StringVar(value="—")
        self.v_ms     = tk.StringVar(value="—")
        self.v_avg    = tk.StringVar(value="—")

        nb = ttk.Notebook(self)
        nb.pack(padx=8, pady=8, fill="both", expand=True)

        t1 = tk.Frame(nb, bg="#f5f5f5"); nb.add(t1, text="  Play  ")
        t2 = tk.Frame(nb, bg="#f5f5f5"); nb.add(t2, text="  Experiments  ")

        self._build_play(t1)
        self._build_exp(t2)
        self._new_game()

    # ── PLAY TAB ───────────────────────────────────────────────────────────────

    def _build_play(self, p):
        tk.Label(p, text="Division Game", font=("Helvetica",16,"bold"),
                 bg="#f5f5f5").pack(pady=(8,4))

        row = tk.Frame(p, bg="#f5f5f5"); row.pack(padx=8)

        # settings card
        L = tk.LabelFrame(row, text="Settings", bg="white", padx=6, pady=6)
        L.pack(side="left", fill="y", padx=(0,6))

        tk.Label(L, text="Who goes first:", bg="white").pack(anchor="w")
        for t,v in [("Human","human"),("Computer","computer")]:
            tk.Radiobutton(L,text=t,variable=self.v_first,value=v,
                           bg="white").pack(anchor="w",padx=8)

        tk.Label(L, text="Algorithm:", bg="white").pack(anchor="w", pady=(6,0))
        for t,v in [("Minimax","minimax"),("Alpha-Beta","alphabeta")]:
            tk.Radiobutton(L,text=t,variable=self.v_algo,value=v,
                           bg="white").pack(anchor="w",padx=8)

        tk.Label(L, text="Depth:", bg="white").pack(anchor="w", pady=(6,0))
        df = tk.Frame(L, bg="white"); df.pack(anchor="w", padx=8)
        for d in range(2,7):
            tk.Radiobutton(df,text=str(d),variable=self.v_depth,
                           value=d,bg="white").pack(side="left")

        tk.Label(L, text="Start number:", bg="white").pack(anchor="w", pady=(8,2))
        self.num_btns = []
        for i in range(5):
            b = tk.Button(L, text="—", width=10,
                          command=lambda x=i: self._pick(x))
            b.pack(pady=1)
            self.num_btns.append(b)

        tk.Button(L, text="New Game", width=10, bg="#555", fg="white",
                  font=("Helvetica",10,"bold"),
                  command=self._new_game).pack(pady=(10,2))

        # board card
        R = tk.LabelFrame(row, text="Board", bg="white", padx=8, pady=8)
        R.pack(side="left", fill="both", expand=True)

        sr = tk.Frame(R, bg="white"); sr.pack()
        for title, var, side in [("Human", self.v_hs, "left"),
                                   ("Computer", self.v_cs, "right")]:
            f = tk.Frame(sr, bg="#e8f4fd", relief="solid", bd=1,
                         padx=14, pady=4)
            f.pack(side=side, padx=6)
            tk.Label(f, text=title, bg="#e8f4fd",
                     font=("Helvetica",9,"bold")).pack()
            tk.Label(f, textvariable=var, bg="#e8f4fd",
                     font=("Helvetica",22,"bold"), fg="#1a6fb5").pack()

        tk.Label(R, text="Current number:", bg="white").pack(pady=(10,0))
        tk.Label(R, textvariable=self.v_num, bg="white",
                 font=("Helvetica",30,"bold"), fg="#2d3748").pack()

        self.lbl_st = tk.Label(R, textvariable=self.v_status, bg="white",
                                font=("Helvetica",10), wraplength=250)
        self.lbl_st.pack(pady=4)

        tk.Label(R, text="Divide by:", bg="white").pack()
        br = tk.Frame(R, bg="white"); br.pack(pady=4)
        self.dbtn = {}
        for d in (2,3,4):
            b = tk.Button(br, text=f"/ {d}", width=5, height=2,
                          bg="#3182ce", fg="white",
                          font=("Helvetica",12,"bold"),
                          command=lambda x=d: self._hmove(x))
            b.pack(side="left", padx=5)
            self.dbtn[d] = b

        self.lbl_think = tk.Label(R, text="", bg="white",
                                   font=("Helvetica",9,"italic"), fg="#888")
        self.lbl_think.pack()

        # stats bar
        S = tk.LabelFrame(p, text="AI stats — last move",
                          bg="white", padx=6, pady=4)
        S.pack(fill="x", padx=8, pady=(4,8))
        sr2 = tk.Frame(S, bg="white"); sr2.pack()
        for lbl, var in [("Generated:", self.v_gen), ("Evaluated:", self.v_eval),
                          ("Time (ms):", self.v_ms),  ("Avg (ms):",  self.v_avg)]:
            tk.Label(sr2, text=lbl, bg="white", fg="#555",
                     font=("Helvetica",9)).pack(side="left", padx=(8,1))
            tk.Label(sr2, textvariable=var, bg="white",
                     font=("Helvetica",9,"bold"), fg="#1a6fb5",
                     width=7).pack(side="left")

    # ── EXPERIMENTS TAB ────────────────────────────────────────────────────────

    def _build_exp(self, p):
        tk.Label(p, text="10 Experiments — Computer vs Computer",
                 font=("Helvetica",13,"bold"), bg="#f5f5f5").pack(pady=(8,4))

        # controls
        C = tk.Frame(p, bg="#f5f5f5"); C.pack(padx=8, pady=2)
        tk.Label(C, text="Algorithm:", bg="#f5f5f5").pack(side="left",padx=(0,2))
        self.e_algo = tk.StringVar(value="alphabeta")
        for t,v in [("Minimax","minimax"),("Alpha-Beta","alphabeta")]:
            tk.Radiobutton(C,text=t,variable=self.e_algo,
                           value=v,bg="#f5f5f5").pack(side="left",padx=2)
        tk.Label(C, text="  Depth:", bg="#f5f5f5").pack(side="left",padx=(8,2))
        self.e_depth = tk.IntVar(value=4)
        for d in range(2,7):
            tk.Radiobutton(C,text=str(d),variable=self.e_depth,
                           value=d,bg="#f5f5f5").pack(side="left",padx=1)
        tk.Button(C, text="▶  Run 10 Experiments", bg="#276749", fg="white",
                  font=("Helvetica",10,"bold"),
                  command=self._run_exp).pack(side="left", padx=(14,4))
        self.lbl_eprog = tk.Label(C, text="", bg="#f5f5f5",
                                   font=("Helvetica",9,"italic"), fg="#555")
        self.lbl_eprog.pack(side="left")

        # results table
        cols = ("#", "Start №", "Algorithm", "Depth",
                "P1 score", "P2 score", "Winner",
                "Nodes Gen.", "Nodes Eval.", "Moves", "Avg Time (ms)")
        self.tree = ttk.Treeview(p, columns=cols, show="headings", height=11)
        widths    = [28, 72, 85, 48, 65, 65, 75, 85, 85, 48, 105]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(padx=8, pady=4, fill="x")

        # ── detailed log box ──────────────────────────────────────────────────
        tk.Label(p, text="Detailed log:", bg="#f5f5f5",
                 font=("Helvetica",10,"bold")).pack(anchor="w", padx=8)

        log_frame = tk.Frame(p, bg="#f5f5f5")
        log_frame.pack(fill="both", expand=True, padx=8, pady=(0,4))

        self.log_box = tk.Text(log_frame, height=10, font=("Courier",9),
                               bg="#1e1e1e", fg="#d4d4d4",
                               wrap="word", state="disabled",
                               relief="flat", padx=6, pady=4)
        sb = ttk.Scrollbar(log_frame, command=self.log_box.yview)
        self.log_box.config(yscrollcommand=sb.set)
        self.log_box.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # text tags for coloured output
        self.log_box.tag_config("header",  foreground="#569cd6", font=("Courier",9,"bold"))
        self.log_box.tag_config("winner1", foreground="#4ec9b0")
        self.log_box.tag_config("winner2", foreground="#f48771")
        self.log_box.tag_config("draw",    foreground="#dcdcaa")
        self.log_box.tag_config("sep",     foreground="#555555")
        self.log_box.tag_config("summary", foreground="#c586c0", font=("Courier",9,"bold"))
        self.log_box.tag_config("label",   foreground="#9cdcfe")
        self.log_box.tag_config("value",   foreground="#b5cea8")

        # summary strip
        Sm = tk.LabelFrame(p, text="Summary", bg="white", padx=6, pady=4)
        Sm.pack(fill="x", padx=8, pady=(0,8))
        sr = tk.Frame(Sm, bg="white"); sr.pack()
        self.v_sp1  = tk.StringVar(value="P1 wins: —")
        self.v_sp2  = tk.StringVar(value="P2 wins: —")
        self.v_sdr  = tk.StringVar(value="Draws: —")
        self.v_sgen = tk.StringVar(value="Avg gen: —")
        self.v_sev  = tk.StringVar(value="Avg eval: —")
        self.v_st   = tk.StringVar(value="Avg time: —")
        for v in (self.v_sp1, self.v_sp2, self.v_sdr,
                  self.v_sgen, self.v_sev, self.v_st):
            tk.Label(sr, textvariable=v, bg="white",
                     font=("Helvetica",9), fg="#1a6fb5").pack(side="left",padx=10)

    # ── LOG HELPER ─────────────────────────────────────────────────────────────

    def _log(self, text, tag=""):
        """Append a line to the experiment log box."""
        self.log_box.config(state="normal")
        if tag:
            self.log_box.insert("end", text + "\n", tag)
        else:
            self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _log_clear(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

    # ── PLAY LOGIC ─────────────────────────────────────────────────────────────

    def _new_game(self):
        lo, hi = 20000//12, 30000//12
        self.cands = [random.randint(lo, hi)*12 for _ in range(5)]
        for i,b in enumerate(self.num_btns):
            b.config(text=str(self.cands[i]), state="normal", bg="#e8e8e8")
        self.num = self.hs = self.cs = 0
        self.moves_done = 0; self.total_ms = 0.0
        self.v_num.set("—"); self.v_hs.set("0"); self.v_cs.set("0")
        self.v_gen.set("—"); self.v_eval.set("—")
        self.v_ms.set("—"); self.v_avg.set("—")
        self.v_status.set("Pick a starting number.")
        self.lbl_st.config(fg="#1a202c")
        self.lbl_think.config(text="")
        self._disdiv()

    def _pick(self, i):
        self.num = self.cands[i]
        self.v_num.set(str(self.num))
        for b in self.num_btns: b.config(state="disabled", bg="#ccc")
        self.hturn = (self.v_first.get() == "human")
        if self.hturn:
            self.v_status.set("Your turn.")
            self._endiv()
        else:
            self.v_status.set("Computer thinking…")
            self._disdiv()
            self.after(300, self._cmove)

    def _hmove(self, d):
        r = self.num // d
        if r % 2 == 0: self.cs -= 1
        else:           self.hs += 1
        self.num = r
        self._refresh()
        if self._endcheck(): return
        self.hturn = False
        self._disdiv()
        self.v_status.set("Computer thinking…")
        self.lbl_think.config(text="Analysing…")
        self.after(100, self._cmove)

    def _cmove(self):
        d, stats = best_move_for(self.num, self.cs, self.hs,
                                  self.v_depth.get(),
                                  self.v_algo.get() == "alphabeta")
        if d is None:
            self._endcheck(); return
        r = self.num // d
        if r % 2 == 0: self.hs -= 1
        else:           self.cs += 1
        self.num = r
        self.moves_done += 1
        self.total_ms   += stats['ms']
        avg = self.total_ms / self.moves_done
        self.v_gen.set(str(stats['gen']))
        self.v_eval.set(str(stats['eval']))
        self.v_ms.set(f"{stats['ms']:.2f}")
        self.v_avg.set(f"{avg:.2f}")
        self._refresh()
        self.lbl_think.config(text=f"Computer: /{d} → {self.num}")
        if self._endcheck(): return
        self.hturn = True
        self.v_status.set("Your turn.")
        self._endiv()

    def _refresh(self):
        self.v_num.set(str(self.num)); self.v_hs.set(str(self.hs))
        self.v_cs.set(str(self.cs))

    def _endcheck(self):
        if self.num > 10 and any(self.num % d == 0 for d in (2,3,4)):
            return False
        h, c = self.hs, self.cs
        if h > c:   msg, col = f"Human wins! ({h} vs {c})", "#276749"
        elif c > h: msg, col = f"Computer wins! ({c} vs {h})", "#c53030"
        else:       msg, col = f"Draw ({h} pts each)", "#975a16"
        self.v_status.set(msg); self.lbl_st.config(fg=col)
        self.lbl_think.config(text="Press 'New Game' to play again.")
        self._disdiv()
        return True

    def _endiv(self):
        for d,b in self.dbtn.items():
            if self.num % d == 0: b.config(state="normal",   bg="#3182ce")
            else:                  b.config(state="disabled", bg="#aaa")

    def _disdiv(self):
        for b in self.dbtn.values(): b.config(state="disabled", bg="#aaa")

    # ── EXPERIMENT LOGIC ───────────────────────────────────────────────────────

    def _run_exp(self):
        """
        Run 10 automated games (Computer vs Computer).
        Both players use the same algorithm and depth.
        Player 1 always goes first.
        Results are shown in the table, log box, and summary strip.
        """
        # clear old results
        for row in self.tree.get_children():
            self.tree.delete(row)
        self._log_clear()

        use_ab = self.e_algo.get() == "alphabeta"
        depth  = self.e_depth.get()
        aname  = "Alpha-Beta" if use_ab else "Minimax"

        self.lbl_eprog.config(text="Running…")
        self.update_idletasks()

        # ── log header ────────────────────────────────────────────────────────
        sep = "─" * 72
        self._log(sep, "sep")
        self._log(f"  EXPERIMENTS   Algorithm: {aname}   Depth: {depth}", "header")
        self._log(f"  Both players use the same AI.  Player 1 always goes first.", "header")
        self._log(sep, "sep")
        self._log(
            f"  {'#':>2}  {'Start':>6}  {'P1':>4}  {'P2':>4}  "
            f"{'Winner':<10}  {'Gen':>7}  {'Eval':>7}  "
            f"{'Moves':>5}  {'AvgT(ms)':>9}", "label")
        self._log(sep, "sep")

        p1w = p2w = draws = 0
        sum_gen = sum_ev = sum_t = 0

        for i in range(1, 11):
            lo, hi    = 20000//12, 30000//12
            num       = random.randint(lo, hi) * 12
            start_num = num
            hs = cs   = 0
            p1_turn   = True
            total_gen = total_ev = total_ms = 0
            move_n    = 0

            # ── play one full game ────────────────────────────────────────────
            while True:
                if num <= 10: break
                if not any(num % d == 0 for d in (2,3,4)): break

                if p1_turn:
                    # Player 1's turn: maximise for P1
                    d, st = best_move_for(num, hs, cs, depth, use_ab)
                    if d is None: break
                    r = num // d
                    if r % 2 == 0: cs -= 1   # even -> P2 loses 1
                    else:           hs += 1   # odd  -> P1 gains 1
                else:
                    # Player 2's turn: maximise for P2
                    d, st = best_move_for(num, cs, hs, depth, use_ab)
                    if d is None: break
                    r = num // d
                    if r % 2 == 0: hs -= 1   # even -> P1 loses 1
                    else:           cs += 1   # odd  -> P2 gains 1

                num     = r
                total_gen += st['gen']
                total_ev  += st['eval']
                total_ms  += st['ms']
                move_n    += 1
                p1_turn    = not p1_turn

            avg_t = total_ms / move_n if move_n else 0.0

            # determine winner
            if hs > cs:   winner = "Player 1"; p1w += 1;  wtag = "winner1"
            elif cs > hs: winner = "Player 2"; p2w += 1;  wtag = "winner2"
            else:         winner = "Draw";     draws += 1; wtag = "draw"

            sum_gen += total_gen
            sum_ev  += total_ev
            sum_t   += avg_t

            # add row to table
            self.tree.insert("", "end", values=(
                i, start_num, aname, depth,
                hs, cs, winner,
                total_gen, total_ev, move_n, f"{avg_t:.3f}"))

            # ── detailed log line ─────────────────────────────────────────────
            line = (f"  {i:>2}  {start_num:>6}  {hs:>4}  {cs:>4}  "
                    f"{winner:<10}  {total_gen:>7}  {total_ev:>7}  "
                    f"{move_n:>5}  {avg_t:>9.3f}")
            self._log(line, wtag)
            self.update_idletasks()

        # ── summary ───────────────────────────────────────────────────────────
        n = 10
        self._log(sep, "sep")
        self._log("  SUMMARY", "summary")
        self._log(f"  Player 1 wins : {p1w}/10", "summary")
        self._log(f"  Player 2 wins : {p2w}/10", "summary")
        self._log(f"  Draws         : {draws}/10", "summary")
        self._log(sep, "sep")
        self._log(f"  AVERAGES ACROSS 10 GAMES", "label")
        self._log(f"  Nodes generated  : {sum_gen//n}", "value")
        self._log(f"  Nodes evaluated  : {sum_ev//n}", "value")
        self._log(f"  Avg move time ms : {sum_t/n:.3f}", "value")
        self._log(sep, "sep")
        self._log("  HOW TO USE THESE NUMBERS IN YOUR REPORT:", "label")
        self._log(f"  - Take 'Nodes Gen.' and 'Nodes Eval.' columns for the table.", "value")
        self._log(f"  - 'Avg Time (ms)' = average time per computer move each game.", "value")
        self._log(f"  - Run again with Minimax at same depth to compare both algorithms.", "value")
        self._log(sep, "sep")

        # update summary strip
        self.v_sp1.set(f"P1 wins: {p1w}")
        self.v_sp2.set(f"P2 wins: {p2w}")
        self.v_sdr.set(f"Draws: {draws}")
        self.v_sgen.set(f"Avg gen: {sum_gen//n}")
        self.v_sev.set(f"Avg eval: {sum_ev//n}")
        self.v_st.set(f"Avg time: {sum_t/n:.3f} ms")
        self.lbl_eprog.config(
            text=f"Done — P1:{p1w}  P2:{p2w}  Draw:{draws}")


# ── ENTRY POINT ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    App().mainloop()