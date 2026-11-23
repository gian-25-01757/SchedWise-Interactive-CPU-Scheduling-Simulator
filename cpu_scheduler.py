import tkinter as tk
from tkinter import ttk, messagebox

# ==========================================
# CPU SCHEDULING SIMULATOR
# FCFS, SJF, SRTF, PRIORITY
# ==========================================

BG = "#F3F6FC"
BLUE = "#3157A4"
DARK = "#1D2D50"
WHITE = "#FFFFFF"

PROCESS_COLORS = [
    "#8ECAE6", "#FFB703", "#B7E4C7", "#FFADAD",
    "#CDB4DB", "#A0C4FF", "#FFD6A5", "#BDE0FE",
    "#FFC8DD", "#CAFFBF"
]


# ==========================================
# SCHEDULING ALGORITHM
# ==========================================

def schedule_processes(processes, algorithm):

    data = []

    for index, p in enumerate(processes):
        data.append({
            "pid": p["pid"],
            "arrival": p["arrival"],
            "burst": p["burst"],
            "priority": p["priority"],
            "remaining": p["burst"],
            "index": index,
            "first_start": None,
            "completion": 0
        })

    time = 0
    completed = 0
    gantt = []

    def add_segment(pid, start, end):
        if gantt and gantt[-1]["pid"] == pid and gantt[-1]["end"] == start:
            gantt[-1]["end"] = end
        else:
            gantt.append({
                "pid": pid,
                "start": start,
                "end": end
            })

    while completed < len(data):

        ready = [
            p for p in data
            if p["arrival"] <= time and p["remaining"] > 0
        ]

        if not ready:
            next_arrival = min(
                p["arrival"] for p in data
                if p["remaining"] > 0
            )

            add_segment("IDLE", time, next_arrival)
            time = next_arrival
            continue

        # Select the next process
        if algorithm == "FCFS":
            selected = min(
                ready,
                key=lambda p: (p["arrival"], p["index"])
            )

        elif algorithm == "SJF (Non-Preemptive)":
            selected = min(
                ready,
                key=lambda p: (
                    p["burst"],
                    p["arrival"],
                    p["index"]
                )
            )

        elif algorithm == "SRTF":
            selected = min(
                ready,
                key=lambda p: (
                    p["remaining"],
                    p["arrival"],
                    p["index"]
                )
            )

        elif algorithm == "Priority (Preemptive)":
            selected = min(
                ready,
                key=lambda p: (
                    p["priority"],
                    p["arrival"],
                    p["index"]
                )
            )

        else:
            raise ValueError("Invalid scheduling algorithm.")

        if selected["first_start"] is None:
            selected["first_start"] = time

        # Non-preemptive algorithms run until completion
        if algorithm in ("FCFS", "SJF (Non-Preemptive)"):

            start = time
            end = time + selected["remaining"]

            add_segment(selected["pid"], start, end)

            time = end
            selected["remaining"] = 0
            selected["completion"] = time
            completed += 1

        # Preemptive algorithms run one time unit at a time
        else:

            add_segment(selected["pid"], time, time + 1)

            selected["remaining"] -= 1
            time += 1

            if selected["remaining"] == 0:
                selected["completion"] = time
                completed += 1

    # Calculate process metrics
    results = []

    for p in data:

        ct = p["completion"]
        tat = ct - p["arrival"]
        wt = tat - p["burst"]
        rt = p["first_start"] - p["arrival"]

        results.append({
            "pid": p["pid"],
            "arrival": p["arrival"],
            "burst": p["burst"],
            "priority": p["priority"],
            "ct": ct,
            "tat": tat,
            "wt": wt,
            "rt": rt
        })

    results.sort(key=lambda x: x["pid"])

    return results, gantt


# ==========================================
# MAIN APPLICATION
# ==========================================

class CPUSchedulerApp:

    def __init__(self, root):

        self.root = root
        self.root.title("SchedWise: Interactive CPU Scheduling Simulator")
        self.root.geometry("1150x850")
        self.root.minsize(900, 650)
        self.root.configure(bg=BG)

        self.processes = []
        self.current_results = []
        self.current_gantt = []

        self.create_interface()

    # ======================================
    # INTERFACE
    # ======================================

    def create_interface(self):

        # Header
        header = tk.Frame(self.root, bg=DARK, height=85)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="CPU SCHEDULING SIMULATOR",
            font=("Arial", 22, "bold"),
            fg=WHITE,
            bg=DARK
        ).pack(pady=(15, 2))

        tk.Label(
            header,
            text="FCFS  |  SJF  |  SRTF  |  Priority Scheduling",
            font=("Arial", 10),
            fg="#DCE6FF",
            bg=DARK
        ).pack()

        # Main scrollable area
        self.main_canvas = tk.Canvas(
            self.root,
            bg=BG,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            self.root,
            orient="vertical",
            command=self.main_canvas.yview
        )

        self.main_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(side="right", fill="y")

        self.main_canvas.configure(
            yscrollcommand=scrollbar.set
        )

        self.content = tk.Frame(self.main_canvas, bg=BG)

        self.canvas_window = self.main_canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw"
        )

        self.content.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(
                scrollregion=self.main_canvas.bbox("all")
            )
        )

        self.main_canvas.bind(
            "<Configure>",
            lambda e: self.main_canvas.itemconfig(
                self.canvas_window,
                width=e.width
            )
        )

        self.create_input_section()
        self.create_algorithm_section()
        self.create_gantt_section()
        self.create_results_section()
        self.create_comparison_section()
        self.create_formula_section()

    # ======================================
    # INPUT SECTION
    # ======================================

    def create_input_section(self):

        frame = tk.LabelFrame(
            self.content,
            text="  PROCESS INPUT  ",
            font=("Arial", 12, "bold"),
            bg=WHITE,
            fg=DARK,
            padx=15,
            pady=12
        )

        frame.pack(
            fill="x",
            padx=20,
            pady=(18, 8)
        )

        labels = [
            "Process ID",
            "Arrival Time",
            "Burst Time",
            "Priority"
        ]

        self.entries = {}

        for i, label in enumerate(labels):

            tk.Label(
                frame,
                text=label,
                bg=WHITE,
                fg=DARK,
                font=("Arial", 10, "bold")
            ).grid(
                row=0,
                column=i,
                padx=8,
                pady=5
            )

            entry = tk.Entry(
                frame,
                width=16,
                font=("Arial", 11),
                justify="center",
                relief="solid",
                bd=1
            )

            entry.grid(
                row=1,
                column=i,
                padx=8,
                pady=5
            )

            self.entries[label] = entry

        self.entries["Process ID"].insert(0, "P1")
        self.entries["Arrival Time"].insert(0, "0")
        self.entries["Burst Time"].insert(0, "5")
        self.entries["Priority"].insert(0, "1")

        button_frame = tk.Frame(frame, bg=WHITE)
        button_frame.grid(
            row=2,
            column=0,
            columnspan=4,
            pady=12
        )

        tk.Button(
            button_frame,
            text="Add Process",
            bg=BLUE,
            fg=WHITE,
            font=("Arial", 10, "bold"),
            width=15,
            command=self.add_process
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="Load Sample",
            bg="#168AAD",
            fg=WHITE,
            font=("Arial", 10, "bold"),
            width=15,
            command=self.load_sample
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="Clear All",
            bg="#D9534F",
            fg=WHITE,
            font=("Arial", 10, "bold"),
            width=15,
            command=self.clear_all
        ).pack(side="left", padx=5)

        # Process table
        self.process_tree = ttk.Treeview(
            frame,
            columns=("PID", "Arrival", "Burst", "Priority"),
            show="headings",
            height=5
        )

        headings = {
            "PID": "Process ID",
            "Arrival": "Arrival Time",
            "Burst": "Burst Time",
            "Priority": "Priority"
        }

        for col, title in headings.items():
            self.process_tree.heading(col, text=title)
            self.process_tree.column(
                col,
                width=150,
                anchor="center"
            )

        self.process_tree.grid(
            row=3,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=5,
            pady=5
        )

    # ======================================
    # ADD PROCESS
    # ======================================

    def add_process(self):

        try:

            pid = self.entries["Process ID"].get().strip()
            arrival = int(self.entries["Arrival Time"].get())
            burst = int(self.entries["Burst Time"].get())
            priority = int(self.entries["Priority"].get())

            if not pid:
                raise ValueError("Please enter a Process ID.")

            if arrival < 0:
                raise ValueError("Arrival Time cannot be negative.")

            if burst <= 0:
                raise ValueError("Burst Time must be greater than zero.")

            if priority < 0:
                raise ValueError("Priority cannot be negative.")

            if any(p["pid"] == pid for p in self.processes):
                raise ValueError("Process ID already exists.")

            process = {
                "pid": pid,
                "arrival": arrival,
                "burst": burst,
                "priority": priority
            }

            self.processes.append(process)

            self.process_tree.insert(
                "",
                "end",
                values=(pid, arrival, burst, priority)
            )

            self.entries["Process ID"].delete(0, tk.END)
            self.entries["Process ID"].insert(
                0,
                f"P{len(self.processes) + 1}"
            )

            for key in ("Arrival Time", "Burst Time", "Priority"):
                self.entries[key].delete(0, tk.END)

            self.entries["Arrival Time"].insert(0, "0")
            self.entries["Burst Time"].insert(0, "5")
            self.entries["Priority"].insert(0, "1")

        except ValueError as error:
            messagebox.showerror("Invalid Input", str(error))

    # ======================================
    # SAMPLE DATA
    # ======================================

    def load_sample(self):

        self.clear_all()

        sample = [
            {"pid": "P1", "arrival": 0, "burst": 7, "priority": 2},
            {"pid": "P2", "arrival": 2, "burst": 4, "priority": 1},
            {"pid": "P3", "arrival": 4, "burst": 1, "priority": 3},
            {"pid": "P4", "arrival": 5, "burst": 4, "priority": 2}
        ]

        for p in sample:
            self.processes.append(p)

            self.process_tree.insert(
                "",
                "end",
                values=(
                    p["pid"],
                    p["arrival"],
                    p["burst"],
                    p["priority"]
                )
            )

        self.entries["Process ID"].delete(0, tk.END)
        self.entries["Process ID"].insert(0, "P5")

        messagebox.showinfo(
            "Sample Loaded",
            "Sample processes have been added successfully."
        )

    # ======================================
    # ALGORITHM SECTION
    # ======================================

    def create_algorithm_section(self):

        frame = tk.LabelFrame(
            self.content,
            text="  SCHEDULING ALGORITHM  ",
            font=("Arial", 12, "bold"),
            bg=WHITE,
            fg=DARK,
            padx=15,
            pady=12
        )

        frame.pack(
            fill="x",
            padx=20,
            pady=8
        )

        self.algorithm = tk.StringVar(
            value="FCFS"
        )

        options = [
            "FCFS",
            "SJF (Non-Preemptive)",
            "SRTF",
            "Priority (Preemptive)"
        ]

        tk.Label(
            frame,
            text="Select Algorithm:",
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=DARK
        ).pack(side="left", padx=10)

        self.algorithm_box = ttk.Combobox(
            frame,
            textvariable=self.algorithm,
            values=options,
            state="readonly",
            width=30,
            font=("Arial", 10)
        )

        self.algorithm_box.pack(side="left", padx=10)

        tk.Button(
            frame,
            text="Run Scheduling",
            bg="#2A9D8F",
            fg=WHITE,
            font=("Arial", 10, "bold"),
            width=18,
            command=self.run_scheduling
        ).pack(side="left", padx=10)

    # ======================================
    # RUN SCHEDULING
    # ======================================

    def run_scheduling(self):

        if not self.processes:
            messagebox.showwarning(
                "No Processes",
                "Please add at least one process first."
            )
            return

        algorithm = self.algorithm.get()

        self.current_results, self.current_gantt = schedule_processes(
            self.processes,
            algorithm
        )

        self.display_results()
        self.draw_gantt()
        self.display_formulas()

    # ======================================
    # GANTT CHART SECTION
    # ======================================

    def create_gantt_section(self):

        frame = tk.LabelFrame(
            self.content,
            text="  GANTT CHART  ",
            font=("Arial", 12, "bold"),
            bg=WHITE,
            fg=DARK,
            padx=12,
            pady=12
        )

        frame.pack(
            fill="x",
            padx=20,
            pady=8
        )

        self.gantt_canvas = tk.Canvas(
            frame,
            height=125,
            bg=WHITE,
            highlightthickness=0
        )

        horizontal = ttk.Scrollbar(
            frame,
            orient="horizontal",
            command=self.gantt_canvas.xview
        )

        self.gantt_canvas.configure(
            xscrollcommand=horizontal.set
        )

        self.gantt_canvas.pack(
            fill="x",
            expand=True
        )

        horizontal.pack(fill="x")

    def draw_gantt(self):

        canvas = self.gantt_canvas
        canvas.delete("all")

        if not self.current_gantt:
            return

        block_width = 75
        start_x = 30
        y1 = 25
        y2 = 75

        color_map = {
            p["pid"]: PROCESS_COLORS[i % len(PROCESS_COLORS)]
            for i, p in enumerate(self.processes)
        }

        for segment in self.current_gantt:

            pid = segment["pid"]
            start = segment["start"]
            end = segment["end"]

            x1 = start_x + start * block_width
            x2 = start_x + end * block_width

            color = (
                "#D9D9D9"
                if pid == "IDLE"
                else color_map.get(pid, "#A0C4FF")
            )

            canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill=color,
                outline=DARK,
                width=2
            )

            canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text=pid,
                font=("Arial", 10, "bold"),
                fill=DARK
            )

            canvas.create_text(
                x1,
                y2 + 18,
                text=str(start),
                font=("Arial", 9),
                fill=DARK
            )

        final_end = self.current_gantt[-1]["end"]

        canvas.create_text(
            start_x + final_end * block_width,
            y2 + 18,
            text=str(final_end),
            font=("Arial", 9),
            fill=DARK
        )

        total_width = start_x + final_end * block_width + 50

        canvas.configure(
            scrollregion=(0, 0, max(total_width, 600), 115)
        )

    # ======================================
    # RESULTS SECTION
    # ======================================

    def create_results_section(self):

        frame = tk.LabelFrame(
            self.content,
            text="  SCHEDULING RESULTS  ",
            font=("Arial", 12, "bold"),
            bg=WHITE,
            fg=DARK,
            padx=12,
            pady=12
        )

        frame.pack(
            fill="x",
            padx=20,
            pady=8
        )

        columns = (
            "PID",
            "AT",
            "BT",
            "Priority",
            "CT",
            "TAT",
            "WT",
            "RT"
        )

        self.result_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=5
        )

        titles = {
            "PID": "Process",
            "AT": "Arrival",
            "BT": "Burst",
            "Priority": "Priority",
            "CT": "CT",
            "TAT": "TAT",
            "WT": "WT",
            "RT": "RT"
        }

        for col in columns:

            self.result_tree.heading(
                col,
                text=titles[col]
            )

            self.result_tree.column(
                col,
                width=95,
                anchor="center"
            )

        self.result_tree.pack(
            fill="x",
            expand=True
        )

        self.average_label = tk.Label(
            frame,
            text="Average CT: --    Average TAT: --    Average WT: --    Average RT: --",
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=BLUE
        )

        self.average_label.pack(pady=10)

    def display_results(self):

        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        for p in self.current_results:

            self.result_tree.insert(
                "",
                "end",
                values=(
                    p["pid"],
                    p["arrival"],
                    p["burst"],
                    p["priority"],
                    p["ct"],
                    p["tat"],
                    p["wt"],
                    p["rt"]
                )
            )

        count = len(self.current_results)

        avg_ct = sum(p["ct"] for p in self.current_results) / count
        avg_tat = sum(p["tat"] for p in self.current_results) / count
        avg_wt = sum(p["wt"] for p in self.current_results) / count
        avg_rt = sum(p["rt"] for p in self.current_results) / count

        self.average_label.config(
            text=(
                f"Average CT: {avg_ct:.2f}     "
                f"Average TAT: {avg_tat:.2f}     "
                f"Average WT: {avg_wt:.2f}     "
                f"Average RT: {avg_rt:.2f}"
            )
        )

    # ======================================
    # COMPARISON SECTION
    # ======================================

    def create_comparison_section(self):

        frame = tk.LabelFrame(
            self.content,
            text="  ALGORITHM COMPARISON  ",
            font=("Arial", 12, "bold"),
            bg=WHITE,
            fg=DARK,
            padx=12,
            pady=12
        )

        frame.pack(
            fill="x",
            padx=20,
            pady=8
        )

        tk.Button(
            frame,
            text="Compare All Algorithms",
            bg="#6A4C93",
            fg=WHITE,
            font=("Arial", 10, "bold"),
            command=self.compare_algorithms
        ).pack(pady=5)

        self.comparison_text = tk.Text(
            frame,
            height=8,
            font=("Consolas", 10),
            bg="#F8F9FA",
            fg=DARK,
            relief="solid",
            bd=1
        )

        self.comparison_text.pack(
            fill="x",
            pady=5
        )

    def compare_algorithms(self):

        if not self.processes:
            messagebox.showwarning(
                "No Processes",
                "Please add processes first."
            )
            return

        algorithms = [
            "FCFS",
            "SJF (Non-Preemptive)",
            "SRTF",
            "Priority (Preemptive)"
        ]

        self.comparison_text.delete("1.0", tk.END)

        self.comparison_text.insert(
            tk.END,
            f"{'ALGORITHM':<30} {'AVG TAT':>10} {'AVG WT':>10} {'AVG RT':>10}\n"
        )

        self.comparison_text.insert(
            tk.END,
            "-" * 65 + "\n"
        )

        for algorithm in algorithms:

            results, _ = schedule_processes(
                self.processes,
                algorithm
            )

            count = len(results)

            avg_tat = sum(p["tat"] for p in results) / count
            avg_wt = sum(p["wt"] for p in results) / count
            avg_rt = sum(p["rt"] for p in results) / count

            line = (
                f"{algorithm:<30} "
                f"{avg_tat:>10.2f} "
                f"{avg_wt:>10.2f} "
                f"{avg_rt:>10.2f}\n"
            )

            self.comparison_text.insert(
                tk.END,
                line
            )

        self.comparison_text.insert(
            tk.END,
            "\nNote: Lower average TAT, WT, and RT generally indicate better performance for those metrics.\n"
        )

    # ======================================
    # FORMULAS SECTION
    # ======================================

    def create_formula_section(self):

        frame = tk.LabelFrame(
            self.content,
            text="  FORMULAS AND COMPUTATIONS  ",
            font=("Arial", 12, "bold"),
            bg=WHITE,
            fg=DARK,
            padx=12,
            pady=12
        )

        frame.pack(
            fill="x",
            padx=20,
            pady=8
        )

        self.formula_text = tk.Text(
            frame,
            height=12,
            font=("Consolas", 10),
            bg="#F8F9FA",
            fg=DARK,
            relief="solid",
            bd=1
        )

        self.formula_text.pack(
            fill="x",
            pady=5
        )

        self.formula_text.insert(
            tk.END,
            "FORMULAS:\n\n"
            "Completion Time (CT) = Time when process finishes\n"
            "Turnaround Time (TAT) = CT - Arrival Time\n"
            "Waiting Time (WT) = TAT - Burst Time\n"
            "Response Time (RT) = First Start Time - Arrival Time\n\n"
            "Run a scheduling algorithm to see the computations here.\n"
        )

    def display_formulas(self):

        self.formula_text.delete("1.0", tk.END)

        self.formula_text.insert(
            tk.END,
            "FORMULAS AND COMPUTATIONS\n"
            "============================================\n\n"
        )

        for p in self.current_results:

            self.formula_text.insert(
                tk.END,
                f"PROCESS {p['pid']}\n"
            )

            self.formula_text.insert(
                tk.END,
                f"CT  = {p['ct']}\n"
            )

            self.formula_text.insert(
                tk.END,
                f"TAT = CT - AT = {p['ct']} - {p['arrival']} = {p['tat']}\n"
            )

            self.formula_text.insert(
                tk.END,
                f"WT  = TAT - BT = {p['tat']} - {p['burst']} = {p['wt']}\n"
            )

            self.formula_text.insert(
                tk.END,
                f"RT  = First Start - AT = {p['rt']}\n\n"
            )

        count = len(self.current_results)

        avg_tat = sum(p["tat"] for p in self.current_results) / count
        avg_wt = sum(p["wt"] for p in self.current_results) / count
        avg_rt = sum(p["rt"] for p in self.current_results) / count

        self.formula_text.insert(
            tk.END,
            "AVERAGE COMPUTATIONS\n"
            "============================================\n"
        )

        self.formula_text.insert(
            tk.END,
            f"Average TAT = {avg_tat:.2f}\n"
        )

        self.formula_text.insert(
            tk.END,
            f"Average WT  = {avg_wt:.2f}\n"
        )

        self.formula_text.insert(
            tk.END,
            f"Average RT  = {avg_rt:.2f}\n"
        )

        self.formula_text.insert(
            tk.END,
            "\nPriority Rule: A smaller priority number means higher priority.\n"
        )

    # ======================================
    # CLEAR ALL
    # ======================================

    def clear_all(self):

        self.processes.clear()
        self.current_results.clear()
        self.current_gantt.clear()

        for item in self.process_tree.get_children():
            self.process_tree.delete(item)

        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        self.gantt_canvas.delete("all")

        self.average_label.config(
            text="Average CT: --    Average TAT: --    Average WT: --    Average RT: --"
        )

        self.comparison_text.delete("1.0", tk.END)

        self.formula_text.delete("1.0", tk.END)

        self.formula_text.insert(
            tk.END,
            "Run a scheduling algorithm to see the computations here."
        )

        self.entries["Process ID"].delete(0, tk.END)
        self.entries["Process ID"].insert(0, "P1")

        self.entries["Arrival Time"].delete(0, tk.END)
        self.entries["Arrival Time"].insert(0, "0")

        self.entries["Burst Time"].delete(0, tk.END)
        self.entries["Burst Time"].insert(0, "5")

        self.entries["Priority"].delete(0, tk.END)
        self.entries["Priority"].insert(0, "1")


# ==========================================
# RUN PROGRAM
# ==========================================

def main():

    root = tk.Tk()

    app = CPUSchedulerApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()
