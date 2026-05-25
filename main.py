# ============================================================
# ETAPA 1 - IMPORTAÇÃO DAS BIBLIOTECAS
# ============================================================

import mysql.connector
import json
import os
import tkinter as tk
from tkinter import messagebox, ttk


# ============================================================
# ETAPA 2 - CAMINHOS DO PROJETO
# ============================================================

PASTA_PROGRAMA = os.path.dirname(os.path.abspath(__file__))

CAMINHO_LOGO = os.path.join(PASTA_PROGRAMA, "Estacio_logo.png")


# ============================================================
# ETAPA 3 - CONFIGURAÇÃO DO MYSQL
# ============================================================

MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "#Hssm284540",
    "database": "cadastro_alunos_estacio",
}


# ============================================================
# ETAPA 4 - CONFIGURAÇÃO VISUAL DO SISTEMA
# ============================================================

CORES = {
    "fundo": "#F4F7FB",
    "card": "#FFFFFF",
    "primaria": "#005EB8",
    "primaria_hover": "#004A91",
    "texto": "#1F2937",
    "texto_suave": "#6B7280",
    "borda": "#D9E2EC",
    "cabecalho_tabela": "#E8F1FA",
    "erro": "#DC2626",
}


def configurar_estilo():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "TNotebook",
        background=CORES["fundo"],
        borderwidth=0
    )

    style.configure(
        "TNotebook.Tab",
        font=("Segoe UI", 10, "bold"),
        padding=[18, 8],
        background="#E5E7EB",
        foreground=CORES["texto"]
    )

    style.map(
        "TNotebook.Tab",
        background=[("selected", CORES["primaria"])],
        foreground=[("selected", "white")]
    )

    style.configure(
        "TLabel",
        font=("Segoe UI", 10),
        background=CORES["fundo"],
        foreground=CORES["texto"]
    )

    style.configure(
        "TEntry",
        font=("Segoe UI", 10),
        padding=5
    )

    style.configure(
        "Primary.TButton",
        font=("Segoe UI", 10, "bold"),
        padding=[12, 7],
        background=CORES["primaria"],
        foreground="white",
        borderwidth=0
    )

    style.map(
        "Primary.TButton",
        background=[("active", CORES["primaria_hover"])]
    )

    style.configure(
        "Secondary.TButton",
        font=("Segoe UI", 10),
        padding=[12, 7],
        background="#E5E7EB",
        foreground=CORES["texto"],
        borderwidth=0
    )

    style.map(
        "Secondary.TButton",
        background=[("active", "#D1D5DB")]
    )

    style.configure(
        "Treeview",
        background="white",
        foreground=CORES["texto"],
        rowheight=30,
        fieldbackground="white",
        font=("Segoe UI", 10),
        borderwidth=0
    )

    style.configure(
        "Treeview.Heading",
        background=CORES["cabecalho_tabela"],
        foreground=CORES["texto"],
        font=("Segoe UI", 10, "bold"),
        padding=6
    )

    style.map(
        "Treeview",
        background=[("selected", CORES["primaria"])],
        foreground=[("selected", "white")]
    )


# ============================================================
# ETAPA 5 - CONEXÃO COM O BANCO MYSQL
# ============================================================

def conectar_db():
    return mysql.connector.connect(**MYSQL_CONFIG)


# ============================================================
# ETAPA 6 - CRIAÇÃO DAS TABELAS NO MYSQL
# ============================================================

def init_db():
    conn = None
    cursor = None

    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ALUNO (
                MATRICULA INT PRIMARY KEY,
                NOME VARCHAR(150) NOT NULL,
                DT_NASCIMENTO VARCHAR(20) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS DISCIPLINA (
                ID VARCHAR(20) PRIMARY KEY,
                NOME VARCHAR(150) NOT NULL,
                TURNO VARCHAR(50),
                SALA VARCHAR(50),
                PROFESSOR VARCHAR(150)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS NOTA (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                VALOR DECIMAL(4,2) NOT NULL,
                MATRICULA INT NOT NULL,
                DISCIPLINA_ID VARCHAR(20) NOT NULL,
                CONSTRAINT FK_NOTA_ALUNO
                    FOREIGN KEY (MATRICULA)
                    REFERENCES ALUNO(MATRICULA),
                CONSTRAINT FK_NOTA_DISCIPLINA
                    FOREIGN KEY (DISCIPLINA_ID)
                    REFERENCES DISCIPLINA(ID)
            )
        """)

        conn.commit()

    except mysql.connector.Error as e:
        messagebox.showerror("Erro no MySQL", str(e))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============================================================
# ETAPA 7 - CONVERSÃO DA NOTA
# ============================================================

def converter_nota(valor):
    valor = valor.strip().replace(",", ".")

    try:
        nota = float(valor)
    except ValueError:
        raise ValueError("A nota deve ser um número válido. Exemplo: 8,5 ou 8.5")

    if nota < 0 or nota > 10:
        raise ValueError("A nota deve estar entre 0 e 10.")

    return nota


# ============================================================
# ETAPA 8 - EXPORTAÇÃO JSON
# ============================================================

def exportar_json(tabela):
    conn = None
    cursor = None

    try:
        tabelas_permitidas = ["ALUNO", "DISCIPLINA", "NOTA"]

        if tabela not in tabelas_permitidas:
            messagebox.showerror("Erro", "Tabela inválida.")
            return

        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {tabela}")

        colunas = [description[0] for description in cursor.description]
        dados = [dict(zip(colunas, row)) for row in cursor.fetchall()]

        arquivo = os.path.join(PASTA_PROGRAMA, f"backup_{tabela.lower()}.json")

        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False, default=str)

        messagebox.showinfo(
            "Sucesso",
            f"Dados da tabela {tabela} exportados com sucesso!"
        )

    except Exception as e:
        messagebox.showerror("Erro ao exportar JSON", str(e))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============================================================
# ETAPA 9 - CLASSE PRINCIPAL DO SISTEMA
# ============================================================

class SistemaEstacio:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Cadastro Estácio")
        self.root.geometry("1050x720")
        self.root.configure(bg=CORES["fundo"])
        self.root.resizable(True, True)

        self.logo_estacio = None

        try:
            self.logo_estacio = tk.PhotoImage(file=CAMINHO_LOGO)
        except Exception:
            self.logo_estacio = None

        self.tabs = ttk.Notebook(root)

        self.tab_inicio = tk.Frame(self.tabs, bg=CORES["fundo"])
        self.tab_aluno = tk.Frame(self.tabs, bg=CORES["fundo"])
        self.tab_disciplina = tk.Frame(self.tabs, bg=CORES["fundo"])
        self.tab_nota = tk.Frame(self.tabs, bg=CORES["fundo"])

        self.tabs.add(self.tab_inicio, text="Início")
        self.tabs.add(self.tab_aluno, text="Alunos")
        self.tabs.add(self.tab_disciplina, text="Disciplinas")
        self.tabs.add(self.tab_nota, text="Notas")

        self.tabs.pack(expand=True, fill="both")

        self.setup_tab_inicio()
        self.setup_tab_aluno()
        self.setup_tab_disciplina()
        self.setup_tab_nota()

    # ========================================================
    # ETAPA 10 - FUNÇÕES VISUAIS AUXILIARES
    # ========================================================

    def criar_card(self, parent):
        card = tk.Frame(
            parent,
            bg=CORES["card"],
            padx=25,
            pady=22,
            highlightbackground=CORES["borda"],
            highlightthickness=1
        )

        return card

    def criar_titulo_secao(self, parent, titulo, subtitulo=None):
        tk.Label(
            parent,
            text=titulo,
            font=("Segoe UI", 18, "bold"),
            bg=CORES["card"],
            fg=CORES["texto"]
        ).pack(anchor="w")

        if subtitulo:
            tk.Label(
                parent,
                text=subtitulo,
                font=("Segoe UI", 10),
                bg=CORES["card"],
                fg=CORES["texto_suave"]
            ).pack(anchor="w", pady=(4, 15))

    def criar_label(self, parent, texto, row, column):
        label = tk.Label(
            parent,
            text=texto,
            font=("Segoe UI", 10, "bold"),
            bg=CORES["card"],
            fg=CORES["texto"]
        )

        label.grid(row=row, column=column, padx=6, pady=8, sticky="e")

    def adicionar_logo_no_card(self, parent):
        if self.logo_estacio:
            tk.Label(
                parent,
                image=self.logo_estacio,
                bg=CORES["card"]
            ).pack(anchor="center", pady=(0, 15))
        else:
            tk.Label(
                parent,
                text="Logo da Estácio não encontrada",
                font=("Segoe UI", 11, "bold"),
                bg=CORES["card"],
                fg=CORES["erro"]
            ).pack(anchor="center", pady=(0, 15))

    # ========================================================
    # ETAPA 11 - ABA INÍCIO
    # ========================================================

    def setup_tab_inicio(self):
        container = tk.Frame(self.tab_inicio, bg=CORES["fundo"])
        container.pack(expand=True, fill="both")

        card = self.criar_card(container)
        card.place(relx=0.5, rely=0.5, anchor="center")

        self.adicionar_logo_no_card(card)

        tk.Label(
            card,
            text="Sistema de Cadastro Estácio",
            font=("Segoe UI", 28, "bold"),
            bg=CORES["card"],
            fg=CORES["texto"]
        ).pack(pady=8)

        tk.Label(
            card,
            text="Cadastro de Alunos, Disciplinas e Notas",
            font=("Segoe UI", 15),
            bg=CORES["card"],
            fg=CORES["texto_suave"]
        ).pack(pady=5)

        tk.Label(
            card,
            text="Sistema conectado ao banco MySQL",
            font=("Segoe UI", 10),
            bg=CORES["card"],
            fg=CORES["texto_suave"]
        ).pack(pady=(22, 0))

    # ========================================================
    # ETAPA 12 - ABA ALUNOS
    # ========================================================

    def setup_tab_aluno(self):
        container = tk.Frame(self.tab_aluno, bg=CORES["fundo"])
        container.pack(fill="both", expand=True, padx=25, pady=25)

        card_form = self.criar_card(container)
        card_form.pack(fill="x")

        self.adicionar_logo_no_card(card_form)

        self.criar_titulo_secao(
            card_form,
            "Cadastro de Alunos",
            "Inclua, altere, exclua e consulte os alunos cadastrados."
        )

        frame_inputs = tk.Frame(card_form, bg=CORES["card"])
        frame_inputs.pack(pady=5)

        self.criar_label(frame_inputs, "Matrícula:", 0, 0)
        self.ent_mat = ttk.Entry(frame_inputs, width=35)
        self.ent_mat.grid(row=0, column=1, padx=6, pady=8)

        self.criar_label(frame_inputs, "Nome:", 1, 0)
        self.ent_nome = ttk.Entry(frame_inputs, width=35)
        self.ent_nome.grid(row=1, column=1, padx=6, pady=8)

        self.criar_label(frame_inputs, "Nascimento:", 2, 0)
        self.ent_nasc = ttk.Entry(frame_inputs, width=35)
        self.ent_nasc.grid(row=2, column=1, padx=6, pady=8)

        frame_btns = tk.Frame(card_form, bg=CORES["card"])
        frame_btns.pack(pady=(10, 0))

        ttk.Button(frame_btns, text="Incluir", command=self.add_aluno, style="Primary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Alterar", command=self.update_aluno, style="Primary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Excluir", command=self.delete_aluno, style="Secondary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Listar", command=self.list_alunos, style="Secondary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Limpar", command=self.limpar_aluno, style="Secondary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Exportar JSON", command=lambda: exportar_json("ALUNO"), style="Secondary.TButton").pack(side="left", padx=5)

        card_table = self.criar_card(container)
        card_table.pack(fill="both", expand=True, pady=(18, 0))

        self.tree_aluno = ttk.Treeview(
            card_table,
            columns=("Matricula", "Nome", "Nascimento"),
            show="headings"
        )

        self.tree_aluno.heading("Matricula", text="Matrícula")
        self.tree_aluno.heading("Nome", text="Nome")
        self.tree_aluno.heading("Nascimento", text="Nascimento")

        self.tree_aluno.column("Matricula", width=120, anchor="center")
        self.tree_aluno.column("Nome", width=500)
        self.tree_aluno.column("Nascimento", width=180, anchor="center")

        self.tree_aluno.pack(fill="both", expand=True)
        self.tree_aluno.bind("<Double-1>", self.selecionar_aluno)

        self.list_alunos()

    def add_aluno(self):
        conn = None
        cursor = None

        try:
            matricula = self.ent_mat.get().strip()
            nome = self.ent_nome.get().strip()
            nascimento = self.ent_nasc.get().strip()

            if not matricula or not nome or not nascimento:
                messagebox.showwarning("Atenção", "Preencha todos os campos.")
                return

            conn = conectar_db()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO ALUNO
                (MATRICULA, NOME, DT_NASCIMENTO)
                VALUES (%s, %s, %s)
                """,
                (int(matricula), nome, nascimento)
            )

            conn.commit()

            self.limpar_aluno()
            self.list_alunos()

            messagebox.showinfo("Sucesso", "Aluno incluído com sucesso!")

        except mysql.connector.IntegrityError:
            messagebox.showerror("Erro", "Já existe um aluno com essa matrícula.")

        except ValueError:
            messagebox.showerror("Erro", "A matrícula deve ser um número inteiro.")

        except Exception as e:
            messagebox.showerror("Erro ao incluir aluno", str(e))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def list_alunos(self):
        conn = None
        cursor = None

        try:
            for item in self.tree_aluno.get_children():
                self.tree_aluno.delete(item)

            conn = conectar_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT MATRICULA, NOME, DT_NASCIMENTO
                FROM ALUNO
                ORDER BY MATRICULA
            """)

            for row in cursor.fetchall():
                self.tree_aluno.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Erro ao listar alunos", str(e))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def update_aluno(self):
        conn = None
        cursor = None

        try:
            matricula = self.ent_mat.get().strip()
            nome = self.ent_nome.get().strip()
            nascimento = self.ent_nasc.get().strip()

            if not matricula or not nome or not nascimento:
                messagebox.showwarning("Atenção", "Preencha todos os campos.")
                return

            conn = conectar_db()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE ALUNO
                SET NOME=%s, DT_NASCIMENTO=%s
                WHERE MATRICULA=%s
                """,
                (nome, nascimento, int(matricula))
            )

            conn.commit()

            if cursor.rowcount == 0:
                messagebox.showwarning("Atenção", "Nenhum aluno encontrado com essa matrícula.")
            else:
                messagebox.showinfo("Sucesso", "Aluno alterado com sucesso!")

            self.limpar_aluno()
            self.list_alunos()

        except ValueError:
            messagebox.showerror("Erro", "A matrícula deve ser um número inteiro.")

        except Exception as e:
            messagebox.showerror("Erro ao alterar aluno", str(e))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def delete_aluno(self):
        conn = None
        cursor = None

        try:
            matricula = self.ent_mat.get().strip()

            if not matricula:
                messagebox.showwarning("Atenção", "Informe a matrícula.")
                return

            resposta = messagebox.askyesno(
                "Confirmar exclusão",
                "Deseja realmente excluir este aluno?"
            )

            if not resposta:
                return

            conn = conectar_db()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM ALUNO WHERE MATRICULA=%s",
                (int(matricula),)
            )

            conn.commit()

            if cursor.rowcount == 0:
                messagebox.showwarning("Atenção", "Nenhum aluno encontrado com essa matrícula.")
            else:
                messagebox.showinfo("Sucesso", "Aluno excluído com sucesso!")

            self.limpar_aluno()
            self.list_alunos()

        except ValueError:
            messagebox.showerror("Erro", "A matrícula deve ser um número inteiro.")

        except mysql.connector.IntegrityError:
            messagebox.showerror(
                "Erro",
                "Não foi possível excluir. Este aluno pode estar vinculado a uma nota."
            )

        except Exception as e:
            messagebox.showerror("Erro ao excluir aluno", str(e))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def selecionar_aluno(self, event):
        item = self.tree_aluno.selection()

        if item:
            valores = self.tree_aluno.item(item, "values")

            self.ent_mat.delete(0, tk.END)
            self.ent_nome.delete(0, tk.END)
            self.ent_nasc.delete(0, tk.END)

            self.ent_mat.insert(0, valores[0])
            self.ent_nome.insert(0, valores[1])
            self.ent_nasc.insert(0, valores[2])

    def limpar_aluno(self):
        self.ent_mat.delete(0, tk.END)
        self.ent_nome.delete(0, tk.END)
        self.ent_nasc.delete(0, tk.END)

    # ========================================================
    # ETAPA 13 - ABA DISCIPLINAS
    # ========================================================

    def setup_tab_disciplina(self):
        container = tk.Frame(self.tab_disciplina, bg=CORES["fundo"])
        container.pack(fill="both", expand=True, padx=25, pady=25)

        card_form = self.criar_card(container)
        card_form.pack(fill="x")

        self.adicionar_logo_no_card(card_form)

        self.criar_titulo_secao(
            card_form,
            "Cadastro de Disciplinas",
            "Cadastre disciplinas com ID textual, por exemplo: ARA0095."
        )

        frame_inputs = tk.Frame(card_form, bg=CORES["card"])
        frame_inputs.pack(pady=5)

        self.criar_label(frame_inputs, "ID:", 0, 0)
        self.ent_disc_id = ttk.Entry(frame_inputs, width=35)
        self.ent_disc_id.grid(row=0, column=1, padx=6, pady=8)

        self.criar_label(frame_inputs, "Nome:", 1, 0)
        self.ent_disc_nome = ttk.Entry(frame_inputs, width=35)
        self.ent_disc_nome.grid(row=1, column=1, padx=6, pady=8)

        self.criar_label(frame_inputs, "Turno:", 2, 0)
        self.ent_disc_turno = ttk.Entry(frame_inputs, width=35)
        self.ent_disc_turno.grid(row=2, column=1, padx=6, pady=8)

        self.criar_label(frame_inputs, "Sala:", 3, 0)
        self.ent_disc_sala = ttk.Entry(frame_inputs, width=35)
        self.ent_disc_sala.grid(row=3, column=1, padx=6, pady=8)

        self.criar_label(frame_inputs, "Professor:", 4, 0)
        self.ent_disc_prof = ttk.Entry(frame_inputs, width=35)
        self.ent_disc_prof.grid(row=4, column=1, padx=6, pady=8)

        frame_btns = tk.Frame(card_form, bg=CORES["card"])
        frame_btns.pack(pady=(10, 0))

        ttk.Button(frame_btns, text="Incluir", command=self.add_disciplina, style="Primary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Alterar", command=self.update_disciplina, style="Primary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Excluir", command=self.delete_disciplina, style="Secondary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Listar", command=self.list_disciplinas, style="Secondary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Limpar", command=self.limpar_disciplina, style="Secondary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Exportar JSON", command=lambda: exportar_json("DISCIPLINA"), style="Secondary.TButton").pack(side="left", padx=5)

        card_table = self.criar_card(container)
        card_table.pack(fill="both", expand=True, pady=(18, 0))

        self.tree_disciplina = ttk.Treeview(
            card_table,
            columns=("ID", "Nome", "Turno", "Sala", "Professor"),
            show="headings"
        )

        self.tree_disciplina.heading("ID", text="ID")
        self.tree_disciplina.heading("Nome", text="Nome")
        self.tree_disciplina.heading("Turno", text="Turno")
        self.tree_disciplina.heading("Sala", text="Sala")
        self.tree_disciplina.heading("Professor", text="Professor")

        self.tree_disciplina.column("ID", width=140, anchor="center")
        self.tree_disciplina.column("Nome", width=350)
        self.tree_disciplina.column("Turno", width=120, anchor="center")
        self.tree_disciplina.column("Sala", width=120, anchor="center")
        self.tree_disciplina.column("Professor", width=280)

        self.tree_disciplina.pack(fill="both", expand=True)
        self.tree_disciplina.bind("<Double-1>", self.selecionar_disciplina)

        self.list_disciplinas()

    def add_disciplina(self):
        conn = None
        cursor = None

        try:
            id_disciplina = self.ent_disc_id.get().strip().upper()
            nome = self.ent_disc_nome.get().strip()
            turno = self.ent_disc_turno.get().strip()
            sala = self.ent_disc_sala.get().strip().upper()
            professor = self.ent_disc_prof.get().strip()

            if not id_disciplina or not nome:
                messagebox.showwarning("Atenção", "Informe o ID e o nome da disciplina.")
                return

            conn = conectar_db()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO DISCIPLINA
                (ID, NOME, TURNO, SALA, PROFESSOR)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (id_disciplina, nome, turno, sala, professor)
            )

            conn.commit()

            self.limpar_disciplina()
            self.list_disciplinas()

            messagebox.showinfo("Sucesso", "Disciplina incluída com sucesso!")

        except mysql.connector.IntegrityError:
            messagebox.showerror("Erro", "Já existe uma disciplina cadastrada com esse ID.")

        except Exception as e:
            messagebox.showerror("Erro ao incluir disciplina", str(e))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def list_disciplinas(self):
        conn = None
        cursor = None

        try:
            for item in self.tree_disciplina.get_children():
                self.tree_disciplina.delete(item)

            conn = conectar_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT ID, NOME, TURNO, SALA, PROFESSOR
                FROM DISCIPLINA
                ORDER BY ID
            """)

            for row in cursor.fetchall():
                self.tree_disciplina.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Erro ao listar disciplinas", str(e))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def update_disciplina(self):
        conn = None
        cursor = None

        try:
            id_disciplina = self.ent_disc_id.get().strip().upper()
            nome = self.ent_disc_nome.get().strip()
            turno = self.ent_disc_turno.get().strip()
            sala = self.ent_disc_sala.get().strip().upper()
            professor = self.ent_disc_prof.get().strip()

            if not id_disciplina or not nome:
                messagebox.showwarning("Atenção", "Informe o ID e o nome da disciplina.")
                return

            conn = conectar_db()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE DISCIPLINA
                SET NOME=%s, TURNO=%s, SALA=%s, PROFESSOR=%s
                WHERE ID=%s
                """,
                (nome, turno, sala, professor, id_disciplina)
            )

            conn.commit()

            if cursor.rowcount == 0:
                messagebox.showwarning("Atenção", "Nenhuma disciplina encontrada com esse ID.")
            else:
                messagebox.showinfo("Sucesso", "Disciplina alterada com sucesso!")

            self.limpar_disciplina()
            self.list_disciplinas()

        except Exception as e:
            messagebox.showerror("Erro ao alterar disciplina", str(e))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def delete_disciplina(self):
        conn = None
        cursor = None

        try:
            id_disciplina = self.ent_disc_id.get().strip().upper()

            if not id_disciplina:
                messagebox.showwarning("Atenção", "Informe o ID da disciplina.")
                return

            resposta = messagebox.askyesno(
                "Confirmar exclusão",
                "Deseja realmente excluir esta disciplina?"
            )

            if not resposta:
                return

            conn = conectar_db()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM DISCIPLINA WHERE ID=%s",
                (id_disciplina,)
            )

            conn.commit()

            if cursor.rowcount == 0:
                messagebox.showwarning("Atenção", "Nenhuma disciplina encontrada com esse ID.")
            else:
                messagebox.showinfo("Sucesso", "Disciplina excluída com sucesso!")

            self.limpar_disciplina()
            self.list_disciplinas()

        except mysql.connector.IntegrityError:
            messagebox.showerror(
                "Erro",
                "Não foi possível excluir. Esta disciplina pode estar vinculada a uma nota."
            )

        except Exception as e:
            messagebox.showerror("Erro ao excluir disciplina", str(e))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def selecionar_disciplina(self, event):
        item = self.tree_disciplina.selection()

        if item:
            valores = self.tree_disciplina.item(item, "values")

            self.ent_disc_id.delete(0, tk.END)
            self.ent_disc_nome.delete(0, tk.END)
            self.ent_disc_turno.delete(0, tk.END)
            self.ent_disc_sala.delete(0, tk.END)
            self.ent_disc_prof.delete(0, tk.END)

            self.ent_disc_id.insert(0, valores[0])
            self.ent_disc_nome.insert(0, valores[1])
            self.ent_disc_turno.insert(0, valores[2])
            self.ent_disc_sala.insert(0, valores[3])
            self.ent_disc_prof.insert(0, valores[4])

    def limpar_disciplina(self):
        self.ent_disc_id.delete(0, tk.END)
        self.ent_disc_nome.delete(0, tk.END)
        self.ent_disc_turno.delete(0, tk.END)
        self.ent_disc_sala.delete(0, tk.END)
        self.ent_disc_prof.delete(0, tk.END)

    # ========================================================
    # ETAPA 14 - ABA NOTAS
    # ========================================================

    def setup_tab_nota(self):
        container = tk.Frame(self.tab_nota, bg=CORES["fundo"])
        container.pack(fill="both", expand=True, padx=25, pady=25)

        card_form = self.criar_card(container)
        card_form.pack(fill="x")

        self.adicionar_logo_no_card(card_form)

        self.criar_titulo_secao(
            card_form,
            "Cadastro de Notas",
            "Registre as notas dos alunos por disciplina."
        )

        frame_inputs = tk.Frame(card_form, bg=CORES["card"])
        frame_inputs.pack(pady=5)

        self.criar_label(frame_inputs, "ID Nota:", 0, 0)
        self.ent_nota_id = ttk.Entry(frame_inputs, width=35)
        self.ent_nota_id.grid(row=0, column=1, padx=6, pady=8)

        self.criar_label(frame_inputs, "Valor:", 1, 0)
        self.ent_nota_valor = ttk.Entry(frame_inputs, width=35)
        self.ent_nota_valor.grid(row=1, column=1, padx=6, pady=8)

        self.criar_label(frame_inputs, "Matrícula do Aluno:", 2, 0)
        self.ent_nota_mat = ttk.Entry(frame_inputs, width=35)
        self.ent_nota_mat.grid(row=2, column=1, padx=6, pady=8)

        self.criar_label(frame_inputs, "ID da Disciplina:", 3, 0)
        self.ent_nota_disc = ttk.Entry(frame_inputs, width=35)
        self.ent_nota_disc.grid(row=3, column=1, padx=6, pady=8)

        frame_btns = tk.Frame(card_form, bg=CORES["card"])
        frame_btns.pack(pady=(10, 0))

        ttk.Button(frame_btns, text="Incluir", command=self.add_nota, style="Primary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Alterar", command=self.update_nota, style="Primary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Excluir", command=self.delete_nota, style="Secondary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Listar", command=self.list_notas, style="Secondary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Limpar", command=self.limpar_nota, style="Secondary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Exportar JSON", command=lambda: exportar_json("NOTA"), style="Secondary.TButton").pack(side="left", padx=5)

        card_table = self.criar_card(container)
        card_table.pack(fill="both", expand=True, pady=(18, 0))

        self.tree_nota = ttk.Treeview(
            card_table,
            columns=("ID", "Valor", "Matricula", "DisciplinaID"),
            show="headings"
        )

        self.tree_nota.heading("ID", text="ID")
        self.tree_nota.heading("Valor", text="Valor")
        self.tree_nota.heading("Matricula", text="Matrícula")
        self.tree_nota.heading("DisciplinaID", text="ID Disciplina")

        self.tree_nota.column("ID", width=100, anchor="center")
        self.tree_nota.column("Valor", width=120, anchor="center")
        self.tree_nota.column("Matricula", width=160, anchor="center")
        self.tree_nota.column("DisciplinaID", width=180, anchor="center")

        self.tree_nota.pack(fill="both", expand=True)
        self.tree_nota.bind("<Double-1>", self.selecionar_nota)

        self.list_notas()

    def add_nota(self):
        conn = None
        cursor = None

        try:
            valor = self.ent_nota_valor.get().strip()
            matricula = self.ent_nota_mat.get().strip()
            disciplina_id = self.ent_nota_disc.get().strip().upper()

            if not valor or not matricula or not disciplina_id:
                messagebox.showwarning("Atenção", "Preencha todos os campos da nota.")
                return

            conn = conectar_db()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO NOTA
                (VALOR, MATRICULA, DISCIPLINA_ID)
                VALUES (%s, %s, %s)
                """,
                (converter_nota(valor), int(matricula), disciplina_id)
            )

            conn.commit()

            self.limpar_nota()
            self.list_notas()

            messagebox.showinfo("Sucesso", "Nota incluída com sucesso!")

        except ValueError as e:
            messagebox.showerror("Erro", str(e))

        except mysql.connector.IntegrityError:
            messagebox.showerror(
                "Erro",
                "Verifique se a matrícula do aluno e o ID da disciplina existem."
            )

        except Exception as e:
            messagebox.showerror("Erro ao incluir nota", str(e))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def list_notas(self):
        conn = None
        cursor = None

        try:
            for item in self.tree_nota.get_children():
                self.tree_nota.delete(item)

            conn = conectar_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT ID, VALOR, MATRICULA, DISCIPLINA_ID
                FROM NOTA
                ORDER BY ID
            """)

            for row in cursor.fetchall():
                self.tree_nota.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Erro ao listar notas", str(e))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def update_nota(self):
        conn = None
        cursor = None

        try:
            id_nota = self.ent_nota_id.get().strip()
            valor = self.ent_nota_valor.get().strip()
            matricula = self.ent_nota_mat.get().strip()
            disciplina_id = self.ent_nota_disc.get().strip().upper()

            if not id_nota or not valor or not matricula or not disciplina_id:
                messagebox.showwarning("Atenção", "Preencha todos os campos.")
                return

            conn = conectar_db()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE NOTA
                SET VALOR=%s, MATRICULA=%s, DISCIPLINA_ID=%s
                WHERE ID=%s
                """,
                (converter_nota(valor), int(matricula), disciplina_id, int(id_nota))
            )

            conn.commit()

            if cursor.rowcount == 0:
                messagebox.showwarning("Atenção", "Nenhuma nota encontrada com esse ID.")
            else:
                messagebox.showinfo("Sucesso", "Nota alterada com sucesso!")

            self.limpar_nota()
            self.list_notas()

        except ValueError as e:
            messagebox.showerror("Erro", str(e))

        except mysql.connector.IntegrityError:
            messagebox.showerror(
                "Erro",
                "Verifique se a matrícula do aluno e o ID da disciplina existem."
            )

        except Exception as e:
            messagebox.showerror("Erro ao alterar nota", str(e))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def delete_nota(self):
        conn = None
        cursor = None

        try:
            id_nota = self.ent_nota_id.get().strip()

            if not id_nota:
                messagebox.showwarning("Atenção", "Informe o ID da nota.")
                return

            resposta = messagebox.askyesno(
                "Confirmar exclusão",
                "Deseja realmente excluir esta nota?"
            )

            if not resposta:
                return

            conn = conectar_db()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM NOTA WHERE ID=%s",
                (int(id_nota),)
            )

            conn.commit()

            if cursor.rowcount == 0:
                messagebox.showwarning("Atenção", "Nenhuma nota encontrada com esse ID.")
            else:
                messagebox.showinfo("Sucesso", "Nota excluída com sucesso!")

            self.limpar_nota()
            self.list_notas()

        except ValueError:
            messagebox.showerror("Erro", "O ID da nota deve ser um número inteiro.")

        except Exception as e:
            messagebox.showerror("Erro ao excluir nota", str(e))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def selecionar_nota(self, event):
        item = self.tree_nota.selection()

        if item:
            valores = self.tree_nota.item(item, "values")

            self.ent_nota_id.delete(0, tk.END)
            self.ent_nota_valor.delete(0, tk.END)
            self.ent_nota_mat.delete(0, tk.END)
            self.ent_nota_disc.delete(0, tk.END)

            self.ent_nota_id.insert(0, valores[0])
            self.ent_nota_valor.insert(0, valores[1])
            self.ent_nota_mat.insert(0, valores[2])
            self.ent_nota_disc.insert(0, valores[3])

    def limpar_nota(self):
        self.ent_nota_id.delete(0, tk.END)
        self.ent_nota_valor.delete(0, tk.END)
        self.ent_nota_mat.delete(0, tk.END)
        self.ent_nota_disc.delete(0, tk.END)


# ============================================================
# ETAPA 15 - EXECUÇÃO DO PROGRAMA
# ============================================================

if __name__ == "__main__":
    init_db()

    root = tk.Tk()

    configurar_estilo()

    app = SistemaEstacio(root)

    root.mainloop()