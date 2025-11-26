import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import csv
import os

class StudentResultSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Record Managment System")
        self.root.geometry("1300x700")
        self.root.minsize(1200, 650)
        self.root.config(bg="#c8e6f9")

        self.csv_file_path = None
        self.students_data = []

        # VARIABLES
        self.student_name = tk.StringVar()
        self.father_name = tk.StringVar()
        self.enrollment = tk.StringVar()
        self.gender = tk.StringVar()
        self.department = tk.StringVar()
        self.dob = tk.StringVar()
        self.address = tk.StringVar()
        self.course_entries = {}  # {course_name: Entry widget}

        # TITLE
        tk.Label(root, text="Student Record Managment System",
                 font=("Segoe UI", 22, "bold"), bg="#83c9f4").grid(row=0, column=0, columnspan=3, sticky="ew")

        # Configure grid
        self.root.grid_rowconfigure(1, weight=1)
        for col in range(3):
            self.root.grid_columnconfigure(col, weight=1)

        # LEFT FRAME - Student Info
        self.left_frame = tk.Frame(root, bd=3, relief="ridge", bg="#e3f2fd")
        self.left_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.left_frame.grid_columnconfigure(1, weight=1)

        tk.Label(self.left_frame, text="Student Information", font=("Segoe UI", 14, "bold"),
                 bg="#64b5f6").grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)

        fields = [
            ("Student Name", self.student_name),
            ("Father Name", self.father_name),
            ("Enrollment No.", self.enrollment),
            ("Gender", self.gender),
            ("Department", self.department),
            ("DOB", self.dob),
            ("Address", self.address),
        ]

        for i, (label, var) in enumerate(fields):
            tk.Label(self.left_frame, text=label + ":", font=("Segoe UI", 11),
                     anchor="w", bg="#e3f2fd").grid(row=i+1, column=0, sticky="w", padx=5, pady=2)
            entry = tk.Entry(self.left_frame, textvariable=var, font=("Segoe UI", 11))
            entry.grid(row=i+1, column=1, sticky="ew", padx=5, pady=2)

        # MID FRAME - Subjects & Marks
        self.mid_frame = tk.Frame(root, bd=3, relief="ridge", bg="#e0f7fa")
        self.mid_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.mid_frame.grid_columnconfigure(0, weight=1)
        self.mid_frame.grid_rowconfigure(2, weight=1)

        tk.Label(self.mid_frame, text="Subjects and Marks", font=("Segoe UI", 14, "bold"),
                 bg="#4dd0e1").grid(row=0, column=0, sticky="ew", pady=5)

        tk.Button(self.mid_frame, text="Add Course", font=("Segoe UI", 11, "bold"),
                  bg="#4db6ac", command=self.add_course).grid(row=1, column=0, pady=5)

        self.course_frame = tk.Frame(self.mid_frame, bg="#e0f7fa")
        self.course_frame.grid(row=2, column=0, sticky="nsew")
        self.course_frame.grid_columnconfigure(1, weight=1)

        # RIGHT FRAME - Treeview & Transcript
        self.right_frame = tk.Frame(root, bd=3, relief="ridge", bg="#f0f4c3")
        self.right_frame.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(3, weight=1)

        tk.Label(self.right_frame, text="Student Records", font=("Segoe UI", 14, "bold"),
                 bg="#cddc39").grid(row=0, column=0, sticky="ew", pady=5)

        columns = ("Enrollment", "Name", "Total", "Average", "Percentage", "CGPA")
        self.tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns")

        # Bind selection to autofill
        self.tree.bind("<<TreeviewSelect>>", self.autofill_tree_select)

        tk.Label(self.right_frame, text="Transcript", font=("Segoe UI", 12, "bold"), bg="#cddc39")\
             .grid(row=2, column=0, sticky="ew", pady=5)
        self.transcript_text = tk.Text(self.right_frame, font=("Consolas", 11), height=10)
        self.transcript_text.grid(row=3, column=0, sticky="nsew", pady=5)

        # BOTTOM BUTTONS (includes Search)
        btn_frame = tk.Frame(root, bg="#c8e6f9")
        btn_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)

        buttons = [
            ("Add Student", self.add_student, "#4db6ac"),
            ("Update Student", self.update_student, "#1976d2"),
            ("Delete Student", self.delete_student, "#f44336"),
            ("Search Student", self.search_student, "#6a1b9a"),
            ("Generate Transcript", self.generate_transcript, "#4db6ac"),
            ("Reset", self.reset, "#4db6ac"),
            ("Save CSV", lambda: self.save_csv(auto_save=False), "#4db6ac"),
            ("Load CSV", self.load_csv, "#4db6ac"),
            ("Back", self.back, "#4db6ac"),
            ("Exit", root.quit, "#f44336"),
        ]

        for i, (text, cmd, color) in enumerate(buttons):
            btn = tk.Button(btn_frame, text=text, font=("Segoe UI", 12, "bold"),
                             bg=color, fg="white", command=cmd)
            btn.grid(row=0, column=i, sticky="ew", padx=5, pady=5)
            btn_frame.grid_columnconfigure(i, weight=1)

    # ----------------- METHODS -----------------
    def add_course(self):
        course_name = simpledialog.askstring("Course Name", "Enter Course Name (letters only):")
        if not course_name:
            return
        course_name = course_name.strip()
        if not course_name.replace(" ", "").isalpha():
            messagebox.showerror("Error", "Course name must contain only letters and spaces.")
            return
        if course_name in self.course_entries:
            messagebox.showwarning("Exists", "This course already exists in the current form.")
            return

        row = len(self.course_entries)
        tk.Label(self.course_frame, text=f"{course_name}:", font=("Segoe UI", 11),
                  anchor="w", bg="#e0f7fa").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        entry = tk.Entry(self.course_frame, font=("Segoe UI", 11))
        entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        self.course_frame.grid_columnconfigure(1, weight=1)
        self.course_entries[course_name] = entry

    def add_student(self):
        if self.student_name.get().strip() == "" or self.enrollment.get().strip() == "":
            messagebox.showerror("Error", "Student Name & Enrollment required!")
            return

        if any(s["Enrollment"] == self.enrollment.get().strip() for s in self.students_data):
            messagebox.showerror("Error", "Student with this Enrollment already exists! Use Update if you want to add marks.")
            return

        student_data = self.calculate_student_data()
        if not student_data:
            return

        self.students_data.append(student_data)
        self.tree.insert("", tk.END, values=(
            student_data["Enrollment"], student_data["Name"],
            student_data["Total"], f"{student_data['Average']:.2f}",
            f"{student_data['Percentage']:.2f}", f"{student_data['CGPA']:.2f}"
        ))
        messagebox.showinfo("Success", "Student Added Successfully!")
        self.save_csv(auto_save=True)

    def update_student(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a student to update!")
            return

        old_values = self.tree.item(selected, "values")
        old_enrollment = old_values[0]

        student = next((s for s in self.students_data if s["Enrollment"] == old_enrollment), None)
        if not student:
            messagebox.showerror("Error", "Selected student not found in memory.")
            return

        updated = self.calculate_student_data()
        if not updated:
            return

        new_enroll = updated["Enrollment"].strip()
        if new_enroll != old_enrollment and any(s["Enrollment"] == new_enroll for s in self.students_data):
            messagebox.showerror("Error", "Another student already has this Enrollment number.")
            return

        idx = self.students_data.index(student)
        self.students_data[idx] = updated

        self.tree.item(selected, values=(
            updated["Enrollment"], updated["Name"], updated["Total"],
            f"{updated['Average']:.2f}", f"{updated['Percentage']:.2f}", f"{updated['CGPA']:.2f}"
        ))

        self.save_csv(auto_save=True)
        messagebox.showinfo("Success", "Student Updated Successfully!")

    def calculate_student_data(self):
        student_courses = {}
        for course, entry in self.course_entries.items():
            val = entry.get().strip()
            if val == "":
                messagebox.showerror("Error", f"Marks required for {course}")
                return None
            if not val.isdigit():
                messagebox.showerror("Error", f"Invalid marks for {course}. Use integer values.")
                return None
            marks = int(val)
            if marks < 0 or marks > 100:
                messagebox.showerror("Error", f"Marks for {course} must be between 0 and 100.")
                return None
            student_courses[course] = marks

        total = sum(student_courses.values())
        count = len(student_courses)
        avg = total / count if count else 0
        perc = (total / (count * 100)) * 100 if count else 0
        cgpa = round((perc / 85) * 4, 2) if count else 0.0
        if cgpa > 4.0:
            cgpa = 4.0

        return {
            "Enrollment": self.enrollment.get().strip(),
            "Name": self.student_name.get().strip(),
            "Father": self.father_name.get().strip(),
            "Gender": self.gender.get().strip(),
            "Department": self.department.get().strip(),
            "DOB": self.dob.get().strip(),
            "Address": self.address.get().strip(),
            "Courses": student_courses,
            "Total": total,
            "Average": avg,
            "Percentage": perc,
            "CGPA": cgpa
        }

    def delete_student(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a student to delete!")
            return
        values = self.tree.item(selected, "values")
        enrollment = values[0]
        self.students_data = [s for s in self.students_data if s["Enrollment"] != enrollment]
        self.tree.delete(selected)
        self.transcript_text.delete("1.0", tk.END)
        self.save_csv(auto_save=True)
        messagebox.showinfo("Success", "Student Deleted Successfully!")

    def generate_transcript(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a student from the table first")
            return
        values = self.tree.item(selected, "values")
        enrollment = values[0]
        student = next((s for s in self.students_data if s["Enrollment"] == enrollment), None)
        if not student:
            messagebox.showerror("Error", "Student not found.")
            return

        self.transcript_text.delete("1.0", tk.END)
        self.transcript_text.insert(tk.END, "----- STUDENT TRANSCRIPT -----\n\n")
        self.transcript_text.insert(tk.END, f"Student Name: {student['Name']}\n")
        self.transcript_text.insert(tk.END, f"Father Name: {student['Father']}\n")
        self.transcript_text.insert(tk.END, f"Enrollment No: {student['Enrollment']}\n")
        self.transcript_text.insert(tk.END, f"Gender: {student['Gender']}\n")
        self.transcript_text.insert(tk.END, f"Department: {student['Department']}\n")
        self.transcript_text.insert(tk.END, f"DOB: {student['DOB']}\n")
        self.transcript_text.insert(tk.END, f"Address: {student['Address']}\n\n")
        self.transcript_text.insert(tk.END, "----- SUBJECT MARKS -----\n")
        for course, marks in student["Courses"].items():
            self.transcript_text.insert(tk.END, f"{course}: {marks}\n")
        self.transcript_text.insert(tk.END, f"\nTotal: {student['Total']}")
        self.transcript_text.insert(tk.END, f"\nAverage: {student['Average']:.2f}")
        self.transcript_text.insert(tk.END, f"\nPercentage: {student['Percentage']:.2f}%")
        self.transcript_text.insert(tk.END, f"\nCGPA: {student['CGPA']:.2f}")

    def reset(self):
        self.student_name.set("")
        self.father_name.set("")
        self.enrollment.set("")
        self.gender.set("")
        self.department.set("")
        self.dob.set("")
        self.address.set("")
        self.transcript_text.delete("1.0", tk.END)
        for widget in self.course_frame.winfo_children():
            widget.destroy()
        self.course_entries = {}

    def back(self):
        sel = self.tree.selection()
        if sel:
            self.tree.selection_remove(sel)
        self.reset()

    def save_csv(self, auto_save=False):
        if not self.students_data:
            if not auto_save:
                messagebox.showinfo("Info", "No student data to save.")
            return

        if not self.csv_file_path:
            if auto_save:
                return
            self.csv_file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                               filetypes=[("CSV files", "*.csv")])
            if not self.csv_file_path:
                return

        all_courses = []
        seen = set()
        for s in self.students_data:
            for c in s["Courses"].keys():
                if c not in seen:
                    seen.add(c)
                    all_courses.append(c)

        try:
            with open(self.csv_file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                header = ["Enrollment", "Name", "Father", "Gender", "Department", "DOB", "Address"] + all_courses + ["Total", "Average", "Percentage", "CGPA"]
                writer.writerow(header)
                for s in self.students_data:
                    row = [s["Enrollment"], s["Name"], s["Father"], s["Gender"], s["Department"], s["DOB"], s["Address"]]
                    for course in all_courses:
                        row.append(s["Courses"].get(course, ""))
                    row += [s["Total"], f"{s['Average']:.2f}", f"{s['Percentage']:.2f}", f"{s['CGPA']:.2f}"]
                    writer.writerow(row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV:\n{e}")
            return

        if not auto_save:
            messagebox.showinfo("Success", f"Data saved to {os.path.basename(self.csv_file_path)}")

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        self.csv_file_path = file_path
        self.students_data = []
        self.tree.delete(*self.tree.get_children())

        try:
            with open(file_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    fixed_fields = {"Enrollment","Name","Father","Gender","Department","DOB","Address","Total","Average","Percentage","CGPA"}
                    courses = {}
                    for k, v in row.items():
                        if k not in fixed_fields and v and v.strip() != "":
                            try:
                                courses[k] = int(v)
                            except ValueError:
                                try:
                                    courses[k] = int(float(v))
                                except Exception:
                                    courses[k] = 0
                    total = int(row.get("Total") or 0)
                    avg = float(row.get("Average") or 0.0)
                    perc = float(str(row.get("Percentage") or "0").replace("%",""))
                    cgpa = float(row.get("CGPA") or 0.0)

                    student_data = {
                        "Enrollment": (row.get("Enrollment") or "").strip(),
                        "Name": (row.get("Name") or "").strip(),
                        "Father": (row.get("Father") or "").strip(),
                        "Gender": (row.get("Gender") or "").strip(),
                        "Department": (row.get("Department") or "").strip(),
                        "DOB": (row.get("DOB") or "").strip(),
                        "Address": (row.get("Address") or "").strip(),
                        "Courses": courses,
                        "Total": total,
                        "Average": avg,
                        "Percentage": perc,
                        "CGPA": cgpa
                    }
                    self.students_data.append(student_data)
                    self.tree.insert("", tk.END, values=(
                        student_data["Enrollment"], student_data["Name"], total, f"{avg:.2f}", f"{perc:.2f}", f"{cgpa:.2f}"
                    ))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV:\n{e}")

    def autofill_tree_select(self, event=None):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, "values")
        enrollment = values[0]
        student = next((s for s in self.students_data if s["Enrollment"] == enrollment), None)
        if not student:
            return

        self.student_name.set(student["Name"])
        self.father_name.set(student["Father"])
        self.enrollment.set(student["Enrollment"])
        self.gender.set(student["Gender"])
        self.department.set(student["Department"])
        self.dob.set(student["DOB"])
        self.address.set(student["Address"])

        for widget in self.course_frame.winfo_children():
            widget.destroy()
        self.course_entries = {}

        for i, (course, marks) in enumerate(student["Courses"].items()):
            tk.Label(self.course_frame, text=f"{course}:", font=("Segoe UI", 11),
                      anchor="w", bg="#e0f7fa").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            entry = tk.Entry(self.course_frame, font=("Segoe UI", 11))
            entry.insert(0, str(marks))
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            self.course_frame.grid_columnconfigure(1, weight=1)
            self.course_entries[course] = entry

    def search_student(self):
        search_win = tk.Toplevel(self.root)
        search_win.title("Search Student")
        search_win.geometry("500x400")
        search_win.config(bg="#e1bee7")

        tk.Label(search_win, text="Search Student", font=("Segoe UI", 16, "bold"), bg="#ce93d8").pack(pady=5)

        frame = tk.Frame(search_win, bg="#e1bee7")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(frame, text="Name:", bg="#e1bee7").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        name_entry = tk.Entry(frame)
        name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(frame, text="Enrollment:", bg="#e1bee7").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        enroll_entry = tk.Entry(frame)
        enroll_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(frame, text="Department:", bg="#e1bee7").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        dept_entry = tk.Entry(frame)
        dept_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        frame.grid_columnconfigure(1, weight=1)

        result_tree = ttk.Treeview(frame, columns=("Enrollment", "Name", "Department"), show="headings")
        result_tree.heading("Enrollment", text="Enrollment")
        result_tree.heading("Name", text="Name")
        result_tree.heading("Department", text="Department")
        result_tree.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=10)
        frame.grid_rowconfigure(4, weight=1)

        # SEARCH FUNCTION
        def perform_search(event=None):
            query_name = name_entry.get().strip().lower()
            query_enroll = enroll_entry.get().strip()
            query_dept = dept_entry.get().strip().lower()

            result_tree.delete(*result_tree.get_children())
            for s in self.students_data:
                if ((query_name in s["Name"].lower() or query_name == "") and
                    (query_enroll in s["Enrollment"] or query_enroll == "") and
                    (query_dept in s["Department"].lower() or query_dept == "")):
                    iid = result_tree.insert("", tk.END, values=(s["Enrollment"], s["Name"], s["Department"]))
                    # Only focus the first result automatically, but don't select multiple
                    if not result_tree.selection():
                        result_tree.selection_set(iid)
                        result_tree.focus(iid)
        
        # NEW FUNCTION: Select student from search results, autofill main form, and generate transcript
        def select_and_generate(event=None):
            sel = result_tree.focus()
            if not sel:
                # If no result is focused/selected, run the search again
                return perform_search()
            
            values = result_tree.item(sel, "values")
            enrollment = values[0]
            student = next((s for s in self.students_data if s["Enrollment"] == enrollment), None)
            
            if student:
                # 1. Autofill main window fields AND select in main treeview
                self.autofill_tree_select_in_search(student)
                
                # 2. Generate Transcript in the main window (now possible because main tree is selected)
                self.generate_transcript() 
                
                # 3. Close the search window
                search_win.destroy()
            else:
                messagebox.showerror("Error", "Selected student data not found.")

        # Bind key release for live search
        name_entry.bind("<KeyRelease>", perform_search)
        enroll_entry.bind("<KeyRelease>", perform_search)
        dept_entry.bind("<KeyRelease>", perform_search)
        
        # FIX: Binding the Enter key (<Return>) to the new function
        search_win.bind('<Return>', select_and_generate)

        # ENTER BUTTON
        enter_btn = tk.Button(frame, text="Enter", font=("Segoe UI", 11, "bold"), bg="#ab47bc", fg="white",
                              command=select_and_generate) # Updated command
        enter_btn.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)

        # SELECT ON DOUBLE CLICK (still closes window, but also generates transcript)
        def select_student(event):
            sel = result_tree.focus()
            if not sel:
                return
            values = result_tree.item(sel, "values")
            enrollment = values[0]
            student = next((s for s in self.students_data if s["Enrollment"] == enrollment), None)
            if student:
                self.autofill_tree_select_in_search(student)
                self.generate_transcript() # Generate transcript on double-click too
                search_win.destroy()

        result_tree.bind("<Double-1>", select_student)

    def autofill_tree_select_in_search(self, student):
        # Fill main window fields after selecting in search catalog
        self.student_name.set(student["Name"])
        self.father_name.set(student["Father"])
        self.enrollment.set(student["Enrollment"])
        self.gender.set(student["Gender"])
        self.department.set(student["Department"])
        self.dob.set(student["DOB"])
        self.address.set(student["Address"])

        for widget in self.course_frame.winfo_children():
            widget.destroy()
        self.course_entries = {}

        for i, (course, marks) in enumerate(student["Courses"].items()):
            tk.Label(self.course_frame, text=f"{course}:", font=("Segoe UI", 11),
                      anchor="w", bg="#e0f7fa").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            entry = tk.Entry(self.course_frame, font=("Segoe UI", 11))
            entry.insert(0, str(marks))
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            self.course_frame.grid_columnconfigure(1, weight=1)
            self.course_entries[course] = entry

        # --- NEW LOGIC ADDED HERE ---
        # Find and select the student in the main treeview (self.tree) 
        # so that self.generate_transcript() works correctly afterwards.
        self.tree.selection_remove(self.tree.selection())
        for item_id in self.tree.get_children():
            # Check the enrollment number (the first column value)
            if self.tree.item(item_id, 'values')[0] == student["Enrollment"]:
                self.tree.selection_set(item_id)
                self.tree.focus(item_id)
                break
        # --- END NEW LOGIC ---

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentResultSystem(root)
    root.mainloop()

