#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R&A Organizador
Organiza los archivos de una carpeta por extensión.
Primera versión gráfica para Windows, desarrollada con Tkinter.
"""

import json
import logging
import os
import shutil
import sys
import threading
import urllib.request
import webbrowser
from collections import Counter
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


# ---------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------------------------

APP_ID = "organizador_archivos"

# Sustituir esta URL cuando esté creado el repositorio de publicidad de esta app.
CONFIG_URL = (
    "https://raw.githubusercontent.com/USUARIO/REPOSITORIO/main/config.json"
)

LOCAL_CONFIG = {
    "banner": {
        "text": "Ritmo y Algoritmo",
        "text2": "Herramientas gratuitas",
        "url": "https://j75.es/herramientas",
        "image_url": "",
        "show_image": False,
        "metrics_url": "",
        "id": "organizador-default",
    }
}

BG = "#1a1a1a"
BG2 = "#242424"
BG3 = "#2e2e2e"
ACCENT = "#cc44cc"
TEXT = "#f0f0f0"
TEXT2 = "#999999"
BORDER = "#3a3a3a"
GREEN = "#44cc77"
ORANGE = "#ffaa33"

FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 17, "bold")


def ruta_recurso(ruta_relativa):
    """Localiza recursos tanto al ejecutar el .py como desde PyInstaller."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent
    return base / ruta_relativa



# ---------------------------------------------------------------------------
# REGISTRO DE ERRORES
# ---------------------------------------------------------------------------

def get_log_path():
    """Guarda el registro en AppData en Windows y en home en otros sistemas."""
    root = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    log_dir = root / "RyA_Organizador"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "organizador.log"


logging.basicConfig(
    filename=get_log_path(),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(APP_ID)


# ---------------------------------------------------------------------------
# LÓGICA DE ORGANIZACIÓN
# ---------------------------------------------------------------------------

def extension_de(archivo: Path) -> str:
    """Devuelve la extensión en mayúsculas o SIN_EXTENSION."""
    extension = archivo.suffix.lower().lstrip(".")
    return extension.upper() if extension else "SIN_EXTENSION"


def nombre_disponible(destino: Path, reservados: set) -> Path:
    """Evita sobrescribir archivos existentes o destinos ya reservados."""
    candidato = destino
    contador = 1

    while candidato.exists() or str(candidato).casefold() in reservados:
        candidato = destino.with_name(
            f"{destino.stem}_{contador}{destino.suffix}"
        )
        contador += 1

    reservados.add(str(candidato).casefold())
    return candidato


def analizar_carpeta(ruta: str):
    """
    Analiza solo los archivos que están directamente dentro de la carpeta.
    No entra en subcarpetas ni mueve nada.
    """
    carpeta = Path(ruta).expanduser().resolve()

    if not carpeta.exists():
        raise FileNotFoundError("La carpeta seleccionada ya no existe.")
    if not carpeta.is_dir():
        raise NotADirectoryError("La ruta seleccionada no es una carpeta.")

    archivos = sorted(
        (p for p in carpeta.iterdir() if p.is_file()),
        key=lambda p: p.name.casefold()
    )

    plan = []
    reservados = set()

    for archivo in archivos:
        extension = extension_de(archivo)
        carpeta_destino = carpeta / extension
        destino_inicial = carpeta_destino / archivo.name
        destino_final = nombre_disponible(destino_inicial, reservados)

        plan.append({
            "origen": archivo,
            "extension": extension,
            "carpeta_destino": carpeta_destino,
            "destino": destino_final,
        })

    return carpeta, plan


def ejecutar_plan(plan, callback_progreso=None):
    """Ejecuta el plan. Devuelve (movidos, errores)."""
    movidos = 0
    errores = []

    total = len(plan)

    for indice, item in enumerate(plan, start=1):
        origen = item["origen"]
        carpeta_destino = item["carpeta_destino"]

        try:
            if not origen.exists() or not origen.is_file():
                raise FileNotFoundError("El archivo ya no está disponible.")

            carpeta_destino.mkdir(parents=True, exist_ok=True)

            # Volver a comprobar el nombre justo antes de moverlo, por si
            # apareció un archivo con el mismo nombre desde el análisis.
            destino = nombre_disponible(
                carpeta_destino / origen.name,
                set()
            )

            shutil.move(str(origen), str(destino))
            movidos += 1
            logger.info("Movido: %s -> %s", origen, destino)

        except Exception as exc:
            errores.append(f"{origen.name}: {exc}")
            logger.exception("Error moviendo %s", origen)

        if callback_progreso:
            callback_progreso(indice, total, movidos, len(errores))

    return movidos, errores


# ---------------------------------------------------------------------------
# CONFIGURACIÓN PUBLICITARIA REMOTA
# ---------------------------------------------------------------------------

def cargar_configuracion():
    """Carga la configuración remota; si falla, utiliza LOCAL_CONFIG."""
    try:
        request = urllib.request.Request(
            CONFIG_URL,
            headers={"User-Agent": "RyA-Organizador/1.0"}
        )
        with urllib.request.urlopen(request, timeout=3) as response:
            remota = json.loads(response.read().decode("utf-8"))

        return {
            "banner": {
                **LOCAL_CONFIG["banner"],
                **remota.get("banner", {}),
            }
        }
    except Exception as exc:
        logger.info("Se utiliza configuración publicitaria local: %s", exc)
        return LOCAL_CONFIG


def enviar_metrica(config, evento):
    """Envía métricas opcionales en segundo plano. Si falla, no afecta a la app."""
    metrics_url = config.get("metrics_url")
    if not metrics_url:
        return

    def tarea():
        try:
            payload = json.dumps({
                "app": APP_ID,
                "banner_id": config.get("id", "default"),
                "event": evento,
            }).encode("utf-8")
            request = urllib.request.Request(
                metrics_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(request, timeout=5).close()
        except Exception:
            logger.debug("No se pudo enviar la métrica publicitaria.")

    threading.Thread(target=tarea, daemon=True).start()


# ---------------------------------------------------------------------------
# INTERFAZ GRÁFICA
# ---------------------------------------------------------------------------

class OrganizadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("R&A Organizador")
        try:
            self.root.iconbitmap(str(ruta_recurso("assets/logo.ico")))
        except tk.TclError:
            logger.warning("No se pudo cargar el icono de la aplicación.")
        self.root.geometry("700x790")
        self.root.minsize(640, 730)
        self.root.configure(bg=BG)

        self.carpeta_var = tk.StringVar()
        self.estado_var = tk.StringVar(
            value="Selecciona una carpeta para comenzar."
        )
        self.resumen_var = tk.StringVar(value="")
        self.plan_actual = []
        self.config_banner = LOCAL_CONFIG["banner"]
        self.banner_photo = None
        self.procesando = False

        self._configurar_estilos()
        self._crear_interfaz()
        self.root.after(150, self._cargar_configuracion_async)

    def _configurar_estilos(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background=BG2,
            foreground=TEXT,
            fieldbackground=BG2,
            rowheight=25,
            bordercolor=BORDER,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading",
            background=BG3,
            foreground=TEXT,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", "#ffffff")],
        )
        style.configure(
            "Horizontal.TProgressbar",
            troughcolor=BG3,
            background=ACCENT,
            bordercolor=BG3,
            lightcolor=ACCENT,
            darkcolor=ACCENT,
        )

    def _crear_interfaz(self):
        contenedor = tk.Frame(self.root, bg=BG, padx=22, pady=15)
        contenedor.pack(fill="both", expand=True)

        # Cabecera al estilo de las herramientas R&A.
        cabecera = tk.Frame(contenedor, bg=BG)
        cabecera.pack(fill="x", pady=(0, 12))
        tk.Label(
            cabecera, text="R&A Organizador", bg=BG, fg=ACCENT,
            font=("Helvetica", 20, "bold")
        ).pack(side="left")
        tk.Label(
            cabecera, text="powered by Ritmo & Algoritmo", bg=BG,
            fg=TEXT2, font=("Helvetica", 10)
        ).pack(side="left", padx=(11, 0), pady=(5, 0))

        tk.Frame(contenedor, bg=BORDER, height=1).pack(fill="x", pady=(0, 13))

        # Panel de selección de carpeta.
        self._titulo_seccion(contenedor, "1. CARPETA DE TRABAJO")
        selector = tk.Frame(
            contenedor, bg=BG2, highlightbackground=BORDER,
            highlightthickness=1, padx=12, pady=12
        )
        selector.pack(fill="x", pady=(0, 12))
        tk.Label(
            selector, text="Carpeta a organizar", bg=BG2, fg=TEXT2,
            font=("Helvetica", 9)
        ).pack(anchor="w", pady=(0, 6))
        fila_ruta = tk.Frame(selector, bg=BG2)
        fila_ruta.pack(fill="x")
        self.entrada_carpeta = tk.Entry(
            fila_ruta, textvariable=self.carpeta_var,
            bg=BG3, fg=TEXT, insertbackground=TEXT,
            relief="flat", font=("Helvetica", 10),
            state="readonly", readonlybackground=BG3,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT
        )
        self.entrada_carpeta.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 9))
        self._boton(
            fila_ruta, "ELEGIR...", self.elegir_carpeta,
            color=BG3, hover=ACCENT, padx=14
        ).pack(side="right")

        # Acciones principales.
        acciones = tk.Frame(contenedor, bg=BG)
        acciones.pack(fill="x", pady=(0, 13))
        self.btn_analizar = self._boton(
            acciones, "Analizar archivos", self.analizar,
            color=ACCENT, hover="#b638b6", padx=17
        )
        self.btn_analizar.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.btn_organizar = self._boton(
            acciones, "Confirmar y organizar", self.confirmar_organizacion,
            color=GREEN, hover="#35b968", padx=17
        )
        self.btn_organizar.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self.btn_organizar.configure(state="disabled")

        # Vista previa en panel independiente.
        self._titulo_seccion(contenedor, "2. VISTA PREVIA")
        panel = tk.Frame(
            contenedor, bg=BG2, highlightbackground=BORDER,
            highlightthickness=1, padx=12, pady=10
        )
        panel.pack(fill="both", expand=True)
        self.lbl_resumen = tk.Label(
            panel, textvariable=self.resumen_var, bg=BG2, fg=TEXT2,
            font=("Helvetica", 9), justify="left", anchor="w"
        )
        self.lbl_resumen.pack(fill="x", pady=(0, 8))

        tabla_frame = tk.Frame(panel, bg=BG2)
        tabla_frame.pack(fill="both", expand=True)
        columnas = ("extension", "cantidad")
        self.tabla = ttk.Treeview(
            tabla_frame, columns=columnas, show="headings", height=6
        )
        self.tabla.heading("extension", text="CARPETA / EXTENSIÓN")
        self.tabla.heading("cantidad", text="ARCHIVOS")
        self.tabla.column("extension", width=390, anchor="w")
        self.tabla.column("cantidad", width=110, anchor="center")
        scroll = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Estado y progreso.
        pie_estado = tk.Frame(contenedor, bg=BG)
        pie_estado.pack(fill="x", pady=(11, 0))
        self.progreso = ttk.Progressbar(
            pie_estado, mode="determinate", style="Horizontal.TProgressbar"
        )
        self.progreso.pack(fill="x", pady=(0, 6))
        tk.Label(
            pie_estado, textvariable=self.estado_var, bg=BG, fg=TEXT2,
            font=("Helvetica", 9), anchor="w", justify="left",
            wraplength=640
        ).pack(fill="x")

        # Banner publicitario fijo y visible, inspirado en QuitaFondo.
        self.banner_frame = tk.Frame(
            contenedor, bg="#ffffff", height=104, cursor="hand2",
            highlightbackground="#dedede", highlightthickness=1
        )
        self.banner_frame.pack(fill="x", pady=(13, 8))
        self.banner_frame.pack_propagate(False)
        self.banner_frame.bind("<Button-1>", self._clic_banner)

        banner_inner = tk.Frame(self.banner_frame, bg="#ffffff", cursor="hand2")
        banner_inner.pack(fill="both", expand=True, padx=14, pady=8)
        self.banner_img_label = tk.Label(
            banner_inner, text="R&A", bg="#f2e8f5", fg="#6a0080",
            font=("Helvetica", 17, "bold"), width=6, height=2, cursor="hand2"
        )
        self.banner_img_label.pack(side="left", padx=(0, 13))
        self.banner_img_label.bind("<Button-1>", self._clic_banner)

        banner_textos = tk.Frame(banner_inner, bg="#ffffff", cursor="hand2")
        banner_textos.pack(side="left", fill="both", expand=True)
        tk.Label(
            banner_textos, text="PUBLICIDAD", bg="#ffffff", fg="#888888",
            font=("Helvetica", 7, "bold")
        ).pack(anchor="w")
        self.lbl_banner = tk.Label(
            banner_textos, text="Ritmo y Algoritmo", bg="#ffffff", fg="#6a0080",
            font=("Helvetica", 12, "bold"), anchor="w", justify="left",
            wraplength=390, cursor="hand2"
        )
        self.lbl_banner.pack(anchor="w", pady=(2, 0))
        self.lbl_banner2 = tk.Label(
            banner_textos, text="Herramientas gratuitas para crear y trabajar mejor",
            bg="#ffffff", fg="#9933aa", font=("Helvetica", 9),
            anchor="w", justify="left", wraplength=390, cursor="hand2"
        )
        self.lbl_banner2.pack(anchor="w", pady=(2, 0))
        self.banner_cta = tk.Label(
            banner_inner, text="VISITAR  ›", bg="#ffffff", fg="#6a0080",
            font=("Helvetica", 9, "bold"), cursor="hand2"
        )
        self.banner_cta.pack(side="right", padx=(8, 2))
        for widget in (banner_inner, banner_textos, self.lbl_banner, self.lbl_banner2, self.banner_cta):
            widget.bind("<Button-1>", self._clic_banner)

        tk.Label(
            contenedor, text="Ritmo y Algoritmo  ·  j75.es/herramientas",
            bg=BG, fg="#666666", font=("Helvetica", 8)
        ).pack()

    def _titulo_seccion(self, parent, texto):
        tk.Label(
            parent, text=texto, bg=BG, fg=TEXT,
            font=("Helvetica", 9, "bold")
        ).pack(anchor="w", pady=(0, 7))

    def _boton(self, parent, texto, comando, color, hover, padx=15):
        boton = tk.Button(
            parent, text=texto, command=comando,
            bg=color, fg="#ffffff", activebackground=hover,
            activeforeground="#ffffff", relief="flat",
            bd=0, padx=padx, pady=10,
            font=("Segoe UI", 9, "bold"), cursor="hand2",
            disabledforeground="#777777"
        )
        boton.bind("<Enter>", lambda _e: boton.configure(bg=hover)
                   if str(boton["state"]) != "disabled" else None)
        boton.bind("<Leave>", lambda _e: boton.configure(bg=color)
                   if str(boton["state"]) != "disabled" else None)
        return boton

    def elegir_carpeta(self):
        seleccion = filedialog.askdirectory(
            title="Selecciona la carpeta que deseas organizar"
        )
        if seleccion:
            self.carpeta_var.set(seleccion)
            self._limpiar_vista_previa()
            self.estado_var.set(
                "Carpeta seleccionada. Pulsa «Analizar archivos» para continuar."
            )

    def _limpiar_vista_previa(self):
        self.plan_actual = []
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        self.resumen_var.set("")
        self.btn_organizar.configure(state="disabled")
        self.progreso["value"] = 0

    def analizar(self):
        ruta = self.carpeta_var.get().strip()
        if not ruta:
            messagebox.showwarning(
                "Falta seleccionar una carpeta",
                "Primero selecciona la carpeta que deseas organizar."
            )
            return

        try:
            carpeta, plan = analizar_carpeta(ruta)
        except Exception as exc:
            messagebox.showerror("No se pudo analizar la carpeta", str(exc))
            logger.exception("Error analizando carpeta")
            return

        self._limpiar_vista_previa()
        self.plan_actual = plan

        if not plan:
            self.resumen_var.set("No se encontraron archivos en esta carpeta.")
            self.estado_var.set("No hay nada que organizar.")
            return

        cantidades = Counter(item["extension"] for item in plan)
        self.resumen_var.set(
            f"Carpeta: {carpeta}\n"
            f"Archivos encontrados: {len(plan)}  |  "
            f"Tipos diferentes: {len(cantidades)}"
        )

        for extension, cantidad in sorted(cantidades.items()):
            self.tabla.insert(
                "", "end", values=(extension, cantidad)
            )

        self.btn_organizar.configure(state="normal")
        self.estado_var.set(
            "Vista previa lista. Revisa el resumen y confirma cuando quieras."
        )
        logger.info("Análisis: %s archivos en %s", len(plan), carpeta)

    def confirmar_organizacion(self):
        if not self.plan_actual:
            return

        cantidad = len(self.plan_actual)
        respuesta = messagebox.askyesno(
            "Confirmar organización",
            f"Se van a mover {cantidad} archivos a carpetas según su extensión.\n\n"
            "No se eliminarán archivos ni se modificarán sus contenidos. "
            "Los archivos con nombres repetidos conservarán ambos nombres "
            "mediante un sufijo numérico.\n\n"
            "Esta primera versión solo organiza los archivos que están "
            "directamente dentro de la carpeta seleccionada; no entra "
            "en sus subcarpetas.\n\n"
            "¿Quieres continuar?"
        )
        if not respuesta:
            return

        self._iniciar_proceso()

    def _iniciar_proceso(self):
        self.procesando = True
        self.btn_analizar.configure(state="disabled")
        self.btn_organizar.configure(state="disabled")
        self.estado_var.set("Organizando archivos...")
        self.progreso["value"] = 0

        # Ejecutar el movimiento en un hilo para no congelar la ventana.
        threading.Thread(
            target=self._trabajo_organizacion,
            daemon=True
        ).start()

    def _trabajo_organizacion(self):
        def progreso(indice, total, movidos, errores):
            self.root.after(
                0, self._actualizar_progreso,
                indice, total, movidos, errores
            )

        movidos, errores = ejecutar_plan(self.plan_actual, progreso)

        self.root.after(
            0, self._finalizar_proceso, movidos, errores
        )

    def _actualizar_progreso(self, indice, total, movidos, errores):
        self.progreso["maximum"] = max(total, 1)
        self.progreso["value"] = indice
        self.estado_var.set(
            f"Procesando {indice} de {total} · "
            f"Movidos: {movidos} · Errores: {errores}"
        )

    def _finalizar_proceso(self, movidos, errores):
        self.procesando = False
        self.btn_analizar.configure(state="normal")
        self.plan_actual = []
        self.btn_organizar.configure(state="disabled")

        mensaje = f"Organización finalizada.\n\nArchivos movidos: {movidos}"
        if errores:
            mensaje += f"\nArchivos con errores: {len(errores)}"
            mensaje += "\n\nPrimeros errores:\n" + "\n".join(errores[:8])
            self.estado_var.set(
                f"Finalizado con {len(errores)} error(es). Consulta el registro."
            )
            logger.warning("Finalizado con errores: %s", errores)
        else:
            self.estado_var.set(
                f"¡Listo! Se organizaron {movidos} archivos correctamente."
            )

        messagebox.showinfo("Proceso terminado", mensaje)

        if messagebox.askyesno(
            "Abrir carpeta",
            "¿Quieres abrir la carpeta organizada?"
        ):
            try:
                os.startfile(self.carpeta_var.get())
            except Exception as exc:
                messagebox.showerror("No se pudo abrir la carpeta", str(exc))

        # Actualizar la vista previa para reflejar el estado real.
        self.analizar()

    def _cargar_configuracion_async(self):
        def tarea():
            config = cargar_configuracion().get("banner", {})
            self.root.after(0, self._aplicar_configuracion_banner, config)

        threading.Thread(target=tarea, daemon=True).start()

    def _aplicar_configuracion_banner(self, config):
        self.config_banner = config
        texto = config.get("text", "Ritmo y Algoritmo")
        texto2 = config.get("text2", "")
        self.lbl_banner.configure(text=texto)
        self.lbl_banner2.configure(text=texto2 or "")

        image_url = config.get("image_url", "")
        if config.get("show_image") and image_url:
            threading.Thread(
                target=self._descargar_banner,
                args=(image_url,),
                daemon=True
            ).start()

    def _descargar_banner(self, url):
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "RyA-Organizador/1.0"}
            )
            with urllib.request.urlopen(request, timeout=6) as response:
                datos = response.read()

            # La descarga ocurre en segundo plano, pero PhotoImage se crea
            # en el hilo principal de Tkinter.
            import base64
            datos_codificados = base64.b64encode(datos).decode("ascii")
            self.root.after(0, self._mostrar_banner, datos_codificados)
        except Exception as exc:
            logger.info("No se pudo cargar el banner remoto: %s", exc)

    def _mostrar_banner(self, datos_codificados):
        try:
            imagen = tk.PhotoImage(data=datos_codificados)
            self.banner_photo = imagen
            self.banner_img_label.configure(image=imagen, text="", width=1, height=1)
        except tk.TclError as exc:
            logger.info("Formato de banner no compatible con Tkinter: %s", exc)

    def _clic_banner(self, _event=None):
        url = self.config_banner.get("url", "")
        if url:
            enviar_metrica(self.config_banner, "click")
            webbrowser.open(url)


def main():
    root = tk.Tk()
    app = OrganizadorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
