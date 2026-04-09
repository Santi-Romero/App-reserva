import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from models import reserva as model


class ReservaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Reserva de Cancha - Unidad Residencial")
        self.geometry("980x700")
        self.minsize(900, 620)
        self.configure(background="#eef3fb")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        model.init_db()
        self.dias = model.proximos_dias()
        self.selected_reserva_id = None
        self.admin_logged_in = False

        self._init_style()
        self._create_widgets()
        self.horarios_fecha.set(self.dias[0])
        self._cargar_horarios()

    def _init_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#eef3fb")
        style.configure("Card.TFrame", background="#ffffff", relief="flat")
        style.configure("TLabel", background="#eef3fb", font=("Segoe UI", 11), foreground="#2d4763")
        style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), foreground="#1f4e79")
        style.configure("SubHeader.TLabel", font=("Segoe UI", 13, "bold"), foreground="#1f4e79")
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), foreground="white", background="#2563eb", padding=10)
        style.map("Accent.TButton",
                  background=[("active", "#1d4ed8"), ("pressed", "#1e40af")])
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), foreground="#ffffff", background="#0f172a", padding=10)
        style.map("Primary.TButton",
                  background=[("active", "#1e293b"), ("pressed", "#111827")])
        style.configure("Danger.TButton", font=("Segoe UI", 10, "bold"), foreground="#ffffff", background="#ef4444", padding=10)
        style.map("Danger.TButton",
                  background=[("active", "#dc2626"), ("pressed", "#b91c1c")])
        style.configure("TEntry", padding=6, relief="flat")
        style.configure("TCombobox", padding=6)
        style.configure("Treeview", font=("Segoe UI", 10), background="#fdfdfd", fieldbackground="#fdfdfd", rowheight=30)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e2e8f0", foreground="#1f2937")
        style.configure("TSeparator", background="#d1d5db")
        style.map("Treeview", background=[("selected", "#bfdbfe")])

    def _create_widgets(self):
        header = ttk.Frame(self, padding=(20, 18, 20, 4), style="Card.TFrame")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 4))
        header.grid_columnconfigure(0, weight=1)

        ttk.Label(header, text="Sistema de Reservas de Cancha", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="Interfaz intuitiva, rápida y amigable para los residentes.", font=("Segoe UI", 11), foreground="#475569").grid(row=1, column=0, sticky="w", pady=(6, 0))

        notebook = ttk.Notebook(self)
        notebook.grid(row=1, column=0, sticky="nsew", padx=16, pady=(8, 16))

        self.tab_horarios = ttk.Frame(notebook)
        self.tab_nueva = ttk.Frame(notebook)
        self.tab_mis = ttk.Frame(notebook)
        self.tab_admin = ttk.Frame(notebook)

        notebook.add(self.tab_horarios, text="Horarios")
        notebook.add(self.tab_nueva, text="Nueva Reserva")
        notebook.add(self.tab_mis, text="Mis Reservas")
        notebook.add(self.tab_admin, text="Admin")

        self._build_tab_horarios()
        self._build_tab_nueva_reserva()
        self._build_tab_mis_reservas()
        self._build_tab_admin()

    def _build_tab_horarios(self):
        frame = self.tab_horarios
        container = ttk.Frame(frame, padding=16, style="Card.TFrame")
        container.pack(fill="both", expand=True, padx=8, pady=8)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(3, weight=1)

        header = ttk.Label(container, text="Horarios disponibles", style="SubHeader.TLabel")
        header.grid(row=0, column=0, sticky="w")

        select_frame = ttk.Frame(container, style="Card.TFrame")
        select_frame.grid(row=1, column=0, sticky="ew", pady=(12, 8))
        select_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(select_frame, text="Fecha:").grid(row=0, column=0, sticky="w")
        self.horarios_fecha = ttk.Combobox(select_frame, values=self._dias_display(), state="readonly", width=28)
        self.horarios_fecha.grid(row=0, column=1, padx=(10, 0), sticky="w")
        self.horarios_fecha.bind("<<ComboboxSelected>>", lambda event: self._cargar_horarios())

        resumen = ttk.Frame(container, style="Card.TFrame")
        resumen.grid(row=2, column=0, sticky="ew", pady=(8, 12))
        resumen.grid_columnconfigure(0, weight=1)
        resumen.grid_columnconfigure(1, weight=1)

        self.disponible_label = ttk.Label(resumen, text="Horarios libres: 0", font=("Segoe UI", 11, "bold"))
        self.disponible_label.grid(row=0, column=0, sticky="w", padx=(0, 12))
        self.reservado_label = ttk.Label(resumen, text="Reservas en el día: 0", font=("Segoe UI", 11, "bold"))
        self.reservado_label.grid(row=0, column=1, sticky="w")

        tree_container = ttk.Frame(container, style="Card.TFrame")
        tree_container.grid(row=3, column=0, sticky="nsew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        self.horarios_tree = ttk.Treeview(tree_container, columns=("hora", "estado", "apartamento"), show="headings", height=14)
        self.horarios_tree.heading("hora", text="Hora")
        self.horarios_tree.heading("estado", text="Estado")
        self.horarios_tree.heading("apartamento", text="Apartamento")
        self.horarios_tree.column("hora", width=160, anchor="center")
        self.horarios_tree.column("estado", width=260, anchor="center")
        self.horarios_tree.column("apartamento", width=220, anchor="center")
        self.horarios_tree.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.horarios_tree.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.horarios_tree.configure(yscrollcommand=scroll_y.set)

        self.horarios_tree.tag_configure("pendiente", background="#fff7ed")
        self.horarios_tree.tag_configure("aprobada", background="#ecfdf5")
        self.horarios_tree.tag_configure("cancelada", background="#fce7f3")
        self.horarios_tree.tag_configure("disponible", background="#ecfdf5")

    def _build_tab_nueva_reserva(self):
        frame = self.tab_nueva
        container = ttk.Frame(frame, padding=16)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Crear reserva nueva", style="SubHeader.TLabel").grid(row=0, column=0, sticky="w")

        form = ttk.Frame(container, padding=(0, 16, 0, 0), style="Card.TFrame")
        form.grid(row=1, column=0, sticky="new")
        form.grid_columnconfigure(1, weight=1)

        ttk.Label(form, text="Apartamento:").grid(row=0, column=0, sticky="w", pady=6)
        self.nueva_apto = ttk.Entry(form)
        self.nueva_apto.grid(row=0, column=1, sticky="ew", padx=10)

        ttk.Label(form, text="Fecha:").grid(row=1, column=0, sticky="w", pady=6)
        self.nueva_fecha = ttk.Combobox(form, values=self._dias_display(), state="readonly")
        self.nueva_fecha.grid(row=1, column=1, sticky="ew", padx=10)
        self.nueva_fecha.bind("<<ComboboxSelected>>", lambda event: self._cargar_horarios_nueva())
        self.nueva_fecha.set(self._dias_display()[0])

        ttk.Label(form, text="Hora:").grid(row=2, column=0, sticky="w", pady=6)
        self.nueva_hora = ttk.Combobox(form, state="readonly")
        self.nueva_hora.grid(row=2, column=1, sticky="ew", padx=10)

        self.nueva_resultado = ttk.Label(container, text="", font=("Segoe UI", 11), foreground="#1f2937")
        self.nueva_resultado.grid(row=2, column=0, sticky="w", pady=(10, 0))

        button = ttk.Button(container, text="Reservar ahora", style="Primary.TButton", command=self._crear_reserva)
        button.grid(row=3, column=0, sticky="w", pady=(18, 0))

        self._cargar_horarios_nueva()

    def _build_tab_mis_reservas(self):
        frame = self.tab_mis
        container = ttk.Frame(frame, padding=16)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Mis reservas", style="SubHeader.TLabel").grid(row=0, column=0, sticky="w")

        filtro = ttk.Frame(container, style="Card.TFrame")
        filtro.grid(row=1, column=0, sticky="ew", pady=(14, 10))
        filtro.grid_columnconfigure(1, weight=1)
        ttk.Label(filtro, text="Apartamento:").grid(row=0, column=0, sticky="w")
        self.mis_apto = ttk.Entry(filtro)
        self.mis_apto.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ttk.Button(filtro, text="Buscar", style="Accent.TButton", command=self._cargar_mis_reservas).grid(row=0, column=2, padx=12)

        tree_container = ttk.Frame(container, style="Card.TFrame")
        tree_container.grid(row=2, column=0, sticky="nsew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        self.mis_tree = ttk.Treeview(tree_container, columns=("id", "fecha", "hora", "estado"), show="headings", height=12)
        self.mis_tree.heading("id", text="ID")
        self.mis_tree.heading("fecha", text="Fecha")
        self.mis_tree.heading("hora", text="Hora")
        self.mis_tree.heading("estado", text="Estado")
        self.mis_tree.column("id", width=70, anchor="center")
        self.mis_tree.column("fecha", width=150, anchor="center")
        self.mis_tree.column("hora", width=170, anchor="center")
        self.mis_tree.column("estado", width=210, anchor="center")
        self.mis_tree.grid(row=0, column=0, sticky="nsew")
        self.mis_tree.bind("<<TreeviewSelect>>", self._seleccionar_mi_reserva)

        scroll_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.mis_tree.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.mis_tree.configure(yscrollcommand=scroll_y.set)

        self.mis_tree.tag_configure("pendiente", background="#fff7ed")
        self.mis_tree.tag_configure("aprobada", background="#ecfdf5")
        self.mis_tree.tag_configure("cancelada", background="#fce7f3")

        acciones = ttk.Frame(container, padding=(0, 12, 0, 0))
        acciones.grid(row=3, column=0, sticky="w")
        self.btn_modificar = ttk.Button(acciones, text="Reprogramar", style="Accent.TButton", command=self._modificar_reserva, state="disabled")
        self.btn_modificar.grid(row=0, column=0, padx=(0, 8))
        self.btn_cancelar = ttk.Button(acciones, text="Cancelar", style="Danger.TButton", command=self._cancelar_reserva, state="disabled")
        self.btn_cancelar.grid(row=0, column=1, padx=(0, 8))
        self.btn_eliminar = ttk.Button(acciones, text="Eliminar", style="Danger.TButton", command=self._eliminar_reserva, state="disabled")
        self.btn_eliminar.grid(row=0, column=2)

        container.rowconfigure(2, weight=1)
        container.columnconfigure(0, weight=1)

    def _build_tab_admin(self):
        frame = self.tab_admin
        container = ttk.Frame(frame, padding=16)
        container.pack(fill="both", expand=True)

        header = ttk.Label(container, text="Panel de administrador", style="SubHeader.TLabel")
        header.grid(row=0, column=0, sticky="w")

        auth = ttk.Frame(container, padding=(0, 12, 0, 20))
        auth.grid(row=1, column=0, sticky="w")
        ttk.Label(auth, text="PIN:").grid(row=0, column=0, sticky="w")
        self.admin_pin = ttk.Entry(auth, show="*", width=20)
        self.admin_pin.grid(row=0, column=1, padx=(10, 0))
        ttk.Button(auth, text="Ingresar", style="Accent.TButton", command=self._login_admin).grid(row=0, column=2, padx=12)

        self.admin_status = ttk.Label(container, text="Ingrese el PIN para acceder a las acciones de administrador.", font=("Segoe UI", 11), foreground="#475569")
        self.admin_status.grid(row=2, column=0, sticky="w")

        self.admin_area = ttk.Frame(container, style="Card.TFrame")
        self.admin_area.grid(row=3, column=0, sticky="nsew", pady=(16, 0))
        self.admin_area.grid_rowconfigure(0, weight=1)
        self.admin_area.grid_columnconfigure(0, weight=1)

        self.admin_tree = ttk.Treeview(self.admin_area, columns=("id", "apto", "fecha", "hora", "estado"), show="headings", height=11)
        self.admin_tree.heading("id", text="ID")
        self.admin_tree.heading("apto", text="Apto")
        self.admin_tree.heading("fecha", text="Fecha")
        self.admin_tree.heading("hora", text="Hora")
        self.admin_tree.heading("estado", text="Estado")
        self.admin_tree.column("id", width=70, anchor="center")
        self.admin_tree.column("apto", width=90, anchor="center")
        self.admin_tree.column("fecha", width=140, anchor="center")
        self.admin_tree.column("hora", width=160, anchor="center")
        self.admin_tree.column("estado", width=180, anchor="center")
        self.admin_tree.grid(row=0, column=0, sticky="nsew")
        self.admin_tree.bind("<<TreeviewSelect>>", self._seleccionar_admin_reserva)

        scroll_y = ttk.Scrollbar(self.admin_area, orient="vertical", command=self.admin_tree.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.admin_tree.configure(yscrollcommand=scroll_y.set)

        self.admin_tree.tag_configure("pendiente", background="#fff7ed")
        self.admin_tree.tag_configure("aprobada", background="#ecfdf5")
        self.admin_tree.tag_configure("cancelada", background="#fce7f3")

        actions = ttk.Frame(self.admin_area, padding=(0, 12, 0, 0))
        actions.grid(row=1, column=0, sticky="w")
        self.btn_approve = ttk.Button(actions, text="Aprobar", style="Primary.TButton", command=self._aprobar_reserva, state="disabled")
        self.btn_approve.grid(row=0, column=0, padx=(0, 8))
        self.btn_cancel_admin = ttk.Button(actions, text="Cancelar", style="Danger.TButton", command=self._cancelar_reserva_admin, state="disabled")
        self.btn_cancel_admin.grid(row=0, column=1, padx=(0, 8))
        self.btn_delete_admin = ttk.Button(actions, text="Eliminar", style="Danger.TButton", command=self._eliminar_reserva_admin, state="disabled")
        self.btn_delete_admin.grid(row=0, column=2)

        self.admin_area.grid_remove()
        container.rowconfigure(3, weight=1)
        container.columnconfigure(0, weight=1)

    def _dias_display(self):
        return [f"{d}  ({self._fmt_dia(d)})" for d in self.dias]

    def _fmt_dia(self, fecha_iso):
        return date.fromisoformat(fecha_iso).strftime("%A")

    def _fmt_hora(self, hora):
        return f"{hora:02d}:00 - {hora+1:02d}:00"

    def _fmt_estado(self, estado):
        iconos = {"pendiente": "⏳ Pendiente", "aprobada": "✅ Aprobada", "cancelada": "❌ Cancelada"}
        return iconos.get(estado, estado.capitalize())

    def _select_fecha(self, display_value):
        if not display_value:
            return ""
        return display_value.split()[0]

    def _cargar_horarios(self):
        fecha = self._select_fecha(self.horarios_fecha.get())
        if not fecha:
            return
        reservados = model.reservas_por_fecha(fecha)
        self.horarios_tree.delete(*self.horarios_tree.get_children())

        libres = 0
        for h in model.HORARIOS:
            if h in reservados:
                reserva = reservados[h]
                estado = self._fmt_estado(reserva["estado"])
                apt = reserva["apartamento"]
                tag = reserva["estado"]
            else:
                estado = "🟢 Disponible"
                apt = "-"
                tag = "disponible"
                libres += 1
            self.horarios_tree.insert("", "end", values=(self._fmt_hora(h), estado, apt), tags=(tag,))

        self.disponible_label.config(text=f"Horarios libres: {libres}")
        self.reservado_label.config(text=f"Reservas en el día: {len(model.HORARIOS) - libres}")

    def _cargar_horarios_nueva(self):
        fecha = self._select_fecha(self.nueva_fecha.get())
        if not fecha:
            return
        disponibles = model.horarios_disponibles(fecha)
        valores = [self._fmt_hora(h) for h in disponibles]
        self.nueva_hora.config(values=valores)
        if valores:
            self.nueva_hora.set(valores[0])
        else:
            self.nueva_hora.set("")

    def _crear_reserva(self):
        apartamento = self.nueva_apto.get().strip()
        fecha = self._select_fecha(self.nueva_fecha.get())
        hora_display = self.nueva_hora.get()
        if not apartamento:
            messagebox.showwarning("Datos incompletos", "Ingrese el número de apartamento.")
            return
        if not fecha or not hora_display:
            messagebox.showwarning("Datos incompletos", "Seleccione fecha y hora.")
            return

        hora = int(hora_display.split(":")[0])
        try:
            model.insertar_reserva(apartamento, fecha, hora, datetime.now().isoformat())
            self.nueva_resultado.config(text="Reserva creada correctamente. Espera aprobación del admin.", foreground="#064e3b")
            self._cargar_horarios()
            self._cargar_mis_reservas()
            self._cargar_admin_reservas()
        except Exception as exc:
            self.nueva_resultado.config(text="Ese horario ya está reservado. Elija otro.", foreground="#b91c1c")

    def _cargar_mis_reservas(self):
        apartamento = self.mis_apto.get().strip()
        self.mis_tree.delete(*self.mis_tree.get_children())
        self.selected_reserva_id = None
        self._actualizar_botones_mis(False)
        if not apartamento:
            return
        rows = model.reservas_por_apartamento(apartamento)
        for row in rows:
            tag = row[3]
            self.mis_tree.insert("", "end", values=(row[0], row[1], self._fmt_hora(row[2]), self._fmt_estado(row[3])), tags=(tag,))

    def _seleccionar_mi_reserva(self, event):
        seleccionado = self.mis_tree.selection()
        if seleccionado:
            item = self.mis_tree.item(seleccionado[0])
            self.selected_reserva_id = int(item["values"][0])
            self._actualizar_botones_mis(True)
        else:
            self.selected_reserva_id = None
            self._actualizar_botones_mis(False)

    def _actualizar_botones_mis(self, activo):
        estado = "!disabled" if activo else "disabled"
        self.btn_modificar.config(state=estado)
        self.btn_cancelar.config(state=estado)
        self.btn_eliminar.config(state=estado)

    def _modificar_reserva(self):
        if not self.selected_reserva_id:
            return
        reserva = model.buscar_por_id(self.selected_reserva_id)
        if not reserva:
            messagebox.showerror("Error", "Reserva no encontrada.")
            return
        self._abrir_ventana_reprogramar(reserva)

    def _abrir_ventana_reprogramar(self, reserva):
        modal = tk.Toplevel(self)
        modal.title("Reprogramar reserva")
        modal.transient(self)
        modal.grab_set()
        modal.geometry("420x260")
        modal.configure(background="#f8fafc")

        ttk.Label(modal, text="Reprogramar reserva seleccionada", style="SubHeader.TLabel").pack(anchor="w", padx=18, pady=(18, 8))
        ttk.Label(modal, text=f"ID: {reserva[0]}   Apto: {reserva[1]}", font=("Segoe UI", 11)).pack(anchor="w", padx=18)
        ttk.Label(modal, text=f"Actual: {reserva[2]}  {self._fmt_hora(reserva[3])}", font=("Segoe UI", 11)).pack(anchor="w", padx=18, pady=(0, 12))

        panel = ttk.Frame(modal, padding=18)
        panel.pack(fill="both", expand=True)

        ttk.Label(panel, text="Nueva fecha:").grid(row=0, column=0, sticky="w")
        fecha_combo = ttk.Combobox(panel, values=self._dias_display(), state="readonly", width=28)
        fecha_combo.grid(row=0, column=1, padx=(10, 0), pady=6)
        fecha_combo.set(self._dias_display()[0])

        ttk.Label(panel, text="Nueva hora:").grid(row=1, column=0, sticky="w")
        hora_combo = ttk.Combobox(panel, state="readonly", width=28)
        hora_combo.grid(row=1, column=1, padx=(10, 0), pady=6)

        def actualizar_horas(event=None):
            fecha = self._select_fecha(fecha_combo.get())
            if not fecha:
                return
            disponibles = model.horarios_disponibles(fecha, excluir_hora=reserva[3] if fecha == reserva[2] else None)
            hora_combo.config(values=[self._fmt_hora(h) for h in disponibles])
            if disponibles:
                hora_combo.set(self._fmt_hora(disponibles[0]))

        fecha_combo.bind("<<ComboboxSelected>>", actualizar_horas)
        actualizar_horas()

        def aplicar_cambio():
            nueva_fecha = self._select_fecha(fecha_combo.get())
            hora_text = hora_combo.get()
            if not nueva_fecha or not hora_text:
                messagebox.showwarning("Datos incompletos", "Seleccione fecha y hora.")
                return
            nueva_hora = int(hora_text.split(":")[0])
            try:
                model.mover_reserva(reserva[0], nueva_fecha, nueva_hora)
                messagebox.showinfo("Listo", "Reserva reprogramada a pendiente.")
                modal.destroy()
                self._cargar_mis_reservas()
                self._cargar_horarios()
                self._cargar_admin_reservas()
            except Exception:
                messagebox.showerror("Error", "El horario seleccionado no está disponible.")

        ttk.Button(modal, text="Guardar cambios", style="Primary.TButton", command=aplicar_cambio).pack(anchor="e", padx=18, pady=(14, 0))

    def _cancelar_reserva(self):
        if not self.selected_reserva_id:
            return
        if messagebox.askyesno("Confirmar", "¿Desea cancelar esta reserva?"):
            model.set_estado(self.selected_reserva_id, "cancelada")
            messagebox.showinfo("Cancelada", "La reserva fue cancelada.")
            self._cargar_mis_reservas()
            self._cargar_horarios()
            self._cargar_admin_reservas()

    def _eliminar_reserva(self):
        if not self.selected_reserva_id:
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar permanentemente esta reserva?"):
            model.borrar_reserva(self.selected_reserva_id)
            messagebox.showinfo("Eliminada", "Reserva eliminada con éxito.")
            self._cargar_mis_reservas()
            self._cargar_horarios()
            self._cargar_admin_reservas()

    def _login_admin(self):
        if self.admin_pin.get().strip() == model.ADMIN_PIN:
            self.admin_logged_in = True
            self.admin_area.grid()
            self.admin_status.config(text="Acceso aprobado. Seleccione una reserva para administrar.", foreground="#065f46")
            self._cargar_admin_reservas()
        else:
            self.admin_logged_in = False
            self.admin_area.grid_remove()
            self.admin_status.config(text="PIN incorrecto. Intente nuevamente.", foreground="#b91c1c")

    def _cargar_admin_reservas(self):
        if not self.admin_logged_in:
            return
        self.admin_tree.delete(*self.admin_tree.get_children())
        rows = model.todas_las_reservas()
        for row in rows:
            self.admin_tree.insert("", "end", values=(row[0], row[1], row[2], self._fmt_hora(row[3]), self._fmt_estado(row[4])), tags=(row[4],))

    def _seleccionar_admin_reserva(self, event):
        seleccionado = self.admin_tree.selection()
        activo = bool(seleccionado)
        estado = "!disabled" if activo else "disabled"
        self.btn_approve.config(state=estado)
        self.btn_cancel_admin.config(state=estado)
        self.btn_delete_admin.config(state=estado)
        if activo:
            self.selected_reserva_id = int(self.admin_tree.item(seleccionado[0])["values"][0])
        else:
            self.selected_reserva_id = None

    def _aprobar_reserva(self):
        if not self.selected_reserva_id:
            return
        model.set_estado(self.selected_reserva_id, "aprobada")
        messagebox.showinfo("Aprobada", "Reserva aprobada correctamente.")
        self._cargar_admin_reservas()
        self._cargar_horarios()
        self._cargar_mis_reservas()

    def _cancelar_reserva_admin(self):
        if not self.selected_reserva_id:
            return
        if messagebox.askyesno("Confirmar", "¿Cancelar esta reserva?"):
            model.set_estado(self.selected_reserva_id, "cancelada")
            messagebox.showinfo("Cancelada", "Reserva cancelada correctamente.")
            self._cargar_admin_reservas()
            self._cargar_horarios()
            self._cargar_mis_reservas()

    def _eliminar_reserva_admin(self):
        if not self.selected_reserva_id:
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar permanentemente esta reserva?"):
            model.borrar_reserva(self.selected_reserva_id)
            messagebox.showinfo("Eliminada", "Reserva eliminada correctamente.")
            self._cargar_admin_reservas()
            self._cargar_horarios()
            self._cargar_mis_reservas()


if __name__ == "__main__":
    app = ReservaApp()
    app.mainloop()
