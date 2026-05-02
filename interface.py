import os, sys

import tkinter as tk
from tkinter import ttk

from version import __VERSION__, __AUTHOR__, __AUTHOR_EMAIL__, __LICENSE__
from serial_win_list import get_serial_comm_ports, SerialController

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.selected_type = None
        self.connection = None
        self.selected_com = None
        self.title("Serial Communication Interface")
        self.geometry("720x420")

        self._icon = tk.PhotoImage(file=resource_path("icon.png"))
        self.iconphoto(True, self._icon)

        # self.resizable(False, False)

        self.items_list, self.ports_info = self.get_itens_safe()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0, minsize=50)
        self.grid_rowconfigure(5, weight=1)


        ttk.Label(self, text="Escolha a porta COM:").grid(column=2, row=0, sticky="ne", padx=20, pady=(10, 4))

        self.modo_var = tk.StringVar(value="Selecione...")
        self.modo_cb = ttk.Combobox(
            self,
            textvariable=self.modo_var,
            values=self.items_list,
            state="readonly"
        )
        self.modo_cb.grid(column=2, row=1, sticky="ne", padx=10, pady=4)
        self.modo_cb.bind("<<ComboboxSelected>>", self.on_select_com)

        ttk.Label(self, text="Escolha o tipo de mensagem:").grid(column=0, row=0, sticky="nw", padx=10, pady=(10, 4))

        self.modo_var1 = tk.StringVar(value="Selecione...")
        self.modo_cb1 = ttk.Combobox(
            self,
            textvariable=self.modo_var1,
            values=["bit", "bytes", "string"],
            state="readonly"
        )
        self.modo_cb1.grid(column=0, row=1, sticky="nw", padx=10, pady=4)
        self.modo_cb1.bind("<<ComboboxSelected>>", self.on_select_type)

        self.txt_entry = ttk.Entry(self, width=30)
        self.txt_entry.grid(column=1, row=1, sticky="nw", padx=10, pady=4)

        ttk.Label(self, text="Mensagem:").grid(column=1, row=0, sticky="nw", padx=70,pady=(10,4))

        btns = tk.Frame(self)
        btns.grid(column=2, row=2, sticky="ne", padx=25, pady=4)

        self.btn_connect = tk.Button(btns, text="Connect", command=self.connect_serial)
        self.btn_connect.grid(row=0, column=1)

        self.btn_refresh = tk.Button(btns, text="Refresh", command=self.refresh)
        self.btn_refresh.grid(row=0, column=0, padx=(4, 6))

        self.btn_disconnect = tk.Button(self, text="Disconnect", command=self.disconnect) #command=self.disconnect
        self.btn_disconnect.grid(row=5, column=1, sticky="nw", padx=70,pady=(10,4)) #, padx=70,pady=(10,4)

        self.btn_exit = tk.Button(self, text="Sair", command=self.exit_application)  # command=self.disconnect
        self.btn_exit.grid(row=5, column=1, sticky="nw", padx=30,pady=(10,4))  # , padx=70,pady=(10,4)

        self.btn_send = tk.Button(self, text="Enviar", command=self.send_msg)  # command=self.disconnect
        self.btn_send.grid(row=2, column=1, sticky="nw", padx=80, pady=(10, 4))  # , padx=70,pady=(10,4)

        self.lbl = ttk.Label(self, text="No COM port connected")
        self.lbl.grid(column=2, row=5, sticky="se", padx=10, pady=(4, 10))

        ttk.Label(self, text="Logs:").grid(column=0, row=3, sticky="nw", padx=10, pady=(10, 4))

        log_frame = tk.Frame(self)
        log_frame.grid(column=0, row=4, columnspan=3, sticky="nsew", padx=10, pady=10)

        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, height=10)
        self.log_text.grid(row=0, column=0, sticky="nsew")

        footer = ttk.Label(
            self,
            text=f"Versão {globals().get('__VERSION__', '?')}",
                 #f" • {globals().get('__AUTHOR__', '')} • "
                 #f"{globals().get('__LICENSE__', '')}",
            font=("Segoe UI", 9),
            foreground="#777"
        )

        footer.grid(
            row=99,
            column=0,
            columnspan=3,
            sticky="se",
            padx=10,
            pady=5
        )

        self.grid_rowconfigure(99, weight=1)

    def send_msg(self):
        texto = self.txt_entry.get()

        if self.connection is None:
            self.add_log("Nenhuma conexão para enviar a mensagem.", type_msg="warn")
            return

        if self.selected_type is None:
            self.add_log("Nenhum tipo de mensagem selecionado.", type_msg="warn")
            return

        if not texto.strip():
            self.add_log("Nenhuma mensagem digitada.", type_msg="warn")
            return

        try:
            resp = self.connection.send_data(texto, self.selected_type, wait=False)

            if isinstance(resp, Exception):
                raise resp

            self.add_log(
                f"Mensagem '{texto}' enviada para {self.selected_com} - {self.ports_info.get(self.selected_com, '')}", type_msg="msg")

            self.txt_entry.delete(0, tk.END)


        except Exception as e:
            self.add_log(f"Erro ao enviar msg: {e}", type_msg="error")

    def connect_serial(self):
        if self.selected_com and self.connection is None:
            try:
                desc = self.ports_info.get(self.selected_com, "")
                self.connection = SerialController(self.selected_com, desc)
                self.lbl.config(text=f"COM port connected: {self.selected_com}")
                self.add_log(f"Conectado em {self.selected_com} - {desc}", type_msg="info")
            except Exception as e:
                self.add_log(f"Erro ao conectar: {e}", type_msg="error")

    def disconnect(self):
        if self.connection is None:
            self.add_log("Nenhuma conexão ativa para desconectar.", type_msg="warn")
            return

        try:

            if hasattr(self.connection, "close"):
                self.connection.close()
            elif hasattr(self.connection, "disconnect"):
                self.connection.disconnect()

            self.add_log(f"Desconectado da {self.selected_com}", type_msg="info")
            self.lbl.config(text="No COM port connected")

        except Exception as e:
            self.add_log(f"Erro ao desconectar: {e}", type_msg="error")

        finally:
            self.connection = None
            self.selected_com = None
            self.modo_var.set("Selecione...")

    def exit_application(self):
        try:
            if self.connection:
                if hasattr(self.connection, "close"):
                    self.connection.close()
                elif hasattr(self.connection, "disconnect"):
                    self.connection.disconnect()
                self.add_log("Conexão serial fechada antes de sair.", type_msg="info")
        except Exception as e:
            print("Erro ao fechar conexão:", e)
        finally:
            self.destroy()

    def add_log(self, msg: str, type_msg: str = "info"):
        self.log_text.tag_config("info", foreground="green")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("warn", background="yellow")
        self.log_text.tag_config("msg", foreground="blue")

        self.log_text.insert("end", msg + "\n", type_msg)
        self.log_text.see("end")

    def get_itens_safe(self):
        result = get_itens()
        if not result:
            return ["No COM ports available"], {}
        lista_itens, portas_dict = result
        return lista_itens, portas_dict

    def refresh(self):
        self.items_list, self.ports_info = self.get_itens_safe()

        self.modo_cb["values"] = self.items_list

        if self.connection is None:
            self.modo_var.set("Selecione...")
        #self.lbl.config(text="Lista atualizada")

    def on_select_com(self, event=None):
        valor = self.modo_var.get()
        #self.lbl.config(text=f"Selecionado: {valor}")

        self.selected_com = valor.split(" - ")[0] if " - " in valor else None

    def on_select_type(self, event=None):
        valor = self.modo_var1.get()
        #self.lbl.config(text=f"Selecionado: {valor}")
        self.selected_type = valor



def get_itens():
    ports = get_serial_comm_ports()
    portas_dict = {}
    lista_itens = []

    if ports:
        for porta in ports:
            portas_dict[porta.device] = porta.description
            lista_itens.append(f"{porta.device} - {porta.description}")

    return lista_itens, portas_dict

def resource_path(rel_path: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, rel_path)


if __name__ == "__main__":
    app = App()
    app.mainloop()






