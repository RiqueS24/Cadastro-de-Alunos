# ============================================================
# ETAPA 1 - IMPORTAÇÃO DAS BIBLIOTECAS
# ============================================================
import sqlite3
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ============================================================
# ETAPA 2 - CAMINHOS DO PROJETO
# ============================================================
PASTA_PROGRAMA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BANCO = os.path.join(PASTA_PROGRAMA, "sistema_estacio.db")
CAMINHO_LOGO = os.path.join(PASTA_PROGRAMA, "Estacio_logo.png")
APP_VERSAO = "versao corrigida - disciplinas"

# ============================================================
# ETAPA 3 - CONFIGURAÇÃO VISUAL DO SISTEMA
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
    """
    Configura o visual do sistema usando ttk.Style.
    """
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
# ETAPA 4 - CONEXÃO COM O BANCO DE DADOS
# ============================================================
def conectar_db():
    """
    Cria conexão com o banco SQLite.
    O timeout ajuda a reduzir erro de 'database is locked'.
    """
    conn = sqlite3.connect(CAMINHO_BANCO, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# ============================================================
# ETAPA 5 - CRIAÇÃO DAS TABELAS
# ============================================================
def init_db():
    """
    Cria as tabelas do sistema.
    """
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ALUNO (
                MATRICULA INTEGER PRIMARY KEY,
                NOME TEXT NOT NULL,
                DT_NASCIMENTO TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS DISCIPLINA (
                ID TEXT PRIMARY KEY,
                NOME TEXT NOT NULL,
                TURNO TEXT,
                SALA TEXT,
                PROFESSOR TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS NOTA (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                VALOR REAL NOT NULL,
                MATRICULA INTEGER NOT NULL,
                DISCIPLINA_ID TEXT NOT NULL,
                FOREIGN KEY (MATRICULA) REFERENCES ALUNO(MATRICULA),
                FOREIGN KEY (DISCIPLINA_ID) REFERENCES DISCIPLINA(ID)
            )
        """)
        conn.commit()
        migrar_banco_antigo(conn)


def coluna_tem_tipo(conn, tabela, coluna, tipo_esperado):
    """
    Verifica se uma coluna existe com o tipo esperado.
    """
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({tabela})")
    for info_coluna in cursor.fetchall():
        nome_coluna = info_coluna[1]
        tipo_coluna = (info_coluna[2] or "").upper()
        if nome_coluna == coluna:
            return tipo_coluna == tipo_esperado.upper()
    return False


def migrar_banco_antigo(conn):
    """
    Corrige bancos criados em versões antigas, onde DISCIPLINA.ID era INTEGER.
    """
    disciplina_id_texto = coluna_tem_tipo(conn, "DISCIPLINA", "ID", "TEXT")
    nota_disciplina_texto = coluna_tem_tipo(conn, "NOTA", "DISCIPLINA_ID", "TEXT")

    if disciplina_id_texto and nota_disciplina_texto:
        return

    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF")

    cursor.execute("ALTER TABLE NOTA RENAME TO NOTA_ANTIGA")
    cursor.execute("ALTER TABLE DISCIPLINA RENAME TO DISCIPLINA_ANTIGA")

    cursor.execute("""
        CREATE TABLE DISCIPLINA (
            ID TEXT PRIMARY KEY,
            NOME TEXT NOT NULL,
            TURNO TEXT,
            SALA TEXT,
            PROFESSOR TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE NOTA (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            VALOR REAL NOT NULL,
            MATRICULA INTEGER NOT NULL,
            DISCIPLINA_ID TEXT NOT NULL,
            FOREIGN KEY (MATRICULA) REFERENCES ALUNO(MATRICULA),
            FOREIGN KEY (DISCIPLINA_ID) REFERENCES DISCIPLINA(ID)
        )
    """)

    cursor.execute("""
        INSERT INTO DISCIPLINA (ID, NOME, TURNO, SALA, PROFESSOR)
        SELECT CAST(ID AS TEXT), NOME, TURNO, SALA, PROFESSOR
        FROM DISCIPLINA_ANTIGA
    """)
    cursor.execute("""
        INSERT INTO NOTA (ID, VALOR, MATRICULA, DISCIPLINA_ID)
        SELECT ID, VALOR, MATRICULA, CAST(DISCIPLINA_ID AS TEXT)
        FROM NOTA_ANTIGA
        WHERE VALOR IS NOT NULL
          AND MATRICULA IS NOT NULL
          AND DISCIPLINA_ID IS NOT NULL
    """)

    cursor.execute("DROP TABLE NOTA_ANTIGA")
    cursor.execute("DROP TABLE DISCIPLINA_ANTIGA")
    cursor.execute("PRAGMA foreign_keys = ON")
    conn.commit()

# ============================================================
# ETAPA 6 - CONVERSÃO DA NOTA
# ============================================================
def converter_nota(valor):
    """
    Converte a nota digitada.
    Aceita vírgula ou ponto.
    Exemplo: 8,5 ou 8.5
    """
    valor = valor.strip().replace(",", ".")
    try:
        nota = float(valor)
    except ValueError:
        raise ValueError("A nota deve ser um número válido. Exemplo: 8,5 ou 8.5")
    if nota < 0 or nota > 10:
        raise ValueError("A nota deve estar entre 0 e 10.")
    return nota

# ============================================================
# ETAPA 7 - EXPORTAÇÃO JSON
# ============================================================
def exportar_json(tabela):
    """
    Exporta os dados da tabela informada para arquivo JSON.
    """
    try:
        tabelas_permitidas = ["ALUNO", "DISCIPLINA", "NOTA"]
        if tabela not in tabelas_permitidas:
            messagebox.showerror("Erro", "Tabela inválida.")
            return
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {tabela}")
            colunas = [description[0] for description in cursor.description]
            dados = [dict(zip(colunas, row)) for row in cursor.fetchall()]

        arquivo = filedialog.asksaveasfilename(
            title=f"Salvar backup da tabela {tabela}",
            initialdir=PASTA_PROGRAMA,
            initialfile=f"backup_{tabela.lower()}.json",
            defaultextension=".json",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )

        if not arquivo:
            return

        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        messagebox.showinfo(
            "Sucesso",
            f"Dados da tabela {tabela} exportados com sucesso!\n\nArquivo salvo em:\n{arquivo}"
        )
    except Exception as e:
        messagebox.showerror("Erro ao exportar JSON", str(e))

# ============================================================
# ETAPA 8 - CLASSE PRINCIPAL DO SISTEMA
# ============================================================
class SistemaEstacio:
    def __init__(self, root):
        """
        Inicializa a janela principal do sistema.
        """
        self.root = root
        self.root.title(f"Sistema de Cadastro Estácio ({APP_VERSAO})")
        self.root.geometry("1050x720")
        self.root.configure(bg=CORES["fundo"])
        self.root.resizable(True, True)
        # Carrega a logo uma única vez para usar em todas as abas.
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
    # ETAPA 9 - FUNÇÕES AUXILIARES VISUAIS
    # ========================================================
    def criar_card(self, parent, largura=None):
        """
        Cria um card branco com borda suave.
        """
        card = tk.Frame(
            parent,
            bg=CORES["card"],
            padx=25,
            pady=22,
            highlightbackground=CORES["borda"],
            highlightthickness=1
        )
        if largura:
            card.config(width=largura)
        return card
    def criar_titulo_secao(self, parent, titulo, subtitulo=None):
        """
        Cria título e subtítulo de seção.
        """
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
        """
        Cria label padronizado para formulários.
        """
        label = tk.Label(
            parent,
            text=texto,
            font=("Segoe UI", 10, "bold"),
            bg=CORES["card"],
            fg=CORES["texto"]
        )
        label.grid(row=row, column=column, padx=6, pady=8, sticky="e")
    def adicionar_logo_no_card(self, parent):
        """
        Adiciona a logo da Estácio no topo de cada card.
        """
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
    # ETAPA 10 - ABA INÍCIO
    # ========================================================
    def setup_tab_inicio(self):
        """
        Tela inicial com logo e apresentação.
        """
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
            text="Utilize as abas superiores para acessar as funcionalidades do sistema.",
            font=("Segoe UI", 10),
            bg=CORES["card"],
            fg=CORES["texto_suave"]
        ).pack(pady=(22, 0))
    # ========================================================
    # ETAPA 11 - ABA ALUNOS
    # ========================================================
    def setup_tab_aluno(self):
        """
        Tela de cadastro de alunos.
        """
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
    # ---------------- CRUD ALUNOS ----------------
    def add_aluno(self):
        try:
            matricula = self.ent_mat.get().strip()
            nome = self.ent_nome.get().strip()
            nascimento = self.ent_nasc.get().strip()
            if not matricula or not nome or not nascimento:
                messagebox.showwarning("Atenção", "Preencha todos os campos.")
                return
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO ALUNO (MATRICULA, NOME, DT_NASCIMENTO) VALUES (?, ?, ?)",
                    (int(matricula), nome, nascimento)
                )
                conn.commit()
            self.limpar_aluno()
            self.list_alunos()
            messagebox.showinfo("Sucesso", "Aluno incluído com sucesso!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Já existe um aluno com essa matrícula.")
        except ValueError:
            messagebox.showerror("Erro", "A matrícula deve ser um número inteiro.")
        except Exception as e:
            messagebox.showerror("Erro ao incluir aluno", str(e))
    def list_alunos(self):
        try:
            for item in self.tree_aluno.get_children():
                self.tree_aluno.delete(item)
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT MATRICULA, NOME, DT_NASCIMENTO
                    FROM ALUNO
                    ORDER BY MATRICULA
                """)
                dados = cursor.fetchall()
            for row in dados:
                self.tree_aluno.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Erro ao listar alunos", str(e))
    def update_aluno(self):
        try:
            matricula = self.ent_mat.get().strip()
            nome = self.ent_nome.get().strip()
            nascimento = self.ent_nasc.get().strip()
            if not matricula or not nome or not nascimento:
                messagebox.showwarning("Atenção", "Preencha todos os campos.")
                return
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE ALUNO
                    SET NOME=?, DT_NASCIMENTO=?
                    WHERE MATRICULA=?
                    """,
                    (nome, nascimento, int(matricula))
                )
                conn.commit()
                alterados = cursor.rowcount
            if alterados == 0:
                messagebox.showwarning("Atenção", "Nenhum aluno encontrado com essa matrícula.")
            else:
                messagebox.showinfo("Sucesso", "Aluno alterado com sucesso!")
            self.limpar_aluno()
            self.list_alunos()
        except ValueError:
            messagebox.showerror("Erro", "A matrícula deve ser um número inteiro.")
        except Exception as e:
            messagebox.showerror("Erro ao alterar aluno", str(e))
    def delete_aluno(self):
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
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM ALUNO WHERE MATRICULA=?",
                    (int(matricula),)
                )
                conn.commit()
                excluidos = cursor.rowcount
            if excluidos == 0:
                messagebox.showwarning("Atenção", "Nenhum aluno encontrado com essa matrícula.")
            else:
                messagebox.showinfo("Sucesso", "Aluno excluído com sucesso!")
            self.limpar_aluno()
            self.list_alunos()
        except ValueError:
            messagebox.showerror("Erro", "A matrícula deve ser um número inteiro.")
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Erro",
                "Não foi possível excluir. Este aluno pode estar vinculado a uma nota."
            )
        except Exception as e:
            messagebox.showerror("Erro ao excluir aluno", str(e))
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
    # ETAPA 12 - ABA DISCIPLINAS
    # ========================================================
    def setup_tab_disciplina(self):
        """
        Tela de cadastro de disciplinas.
        """
        container = tk.Frame(self.tab_disciplina, bg=CORES["fundo"])
        container.pack(fill="both", expand=True, padx=25, pady=25)
        card_form = self.criar_card(container)
        card_form.pack(fill="x")
        self.adicionar_logo_no_card(card_form)
        self.criar_titulo_secao(
            card_form,
            "Cadastro de Disciplinas",
            "Cadastre disciplinas com ID textual. Incluir salva e atualiza a lista."
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
        ttk.Button(frame_btns, text="Listar", command=lambda: self.list_disciplinas(avisar_vazio=True), style="Secondary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Limpar", command=self.limpar_disciplina, style="Secondary.TButton").pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Exportar JSON", command=lambda: exportar_json("DISCIPLINA"), style="Secondary.TButton").pack(side="left", padx=5)
        card_table = self.criar_card(container)
        card_table.pack(fill="both", expand=True, pady=(18, 0))
        frame_tabela = tk.Frame(card_table, bg=CORES["card"])
        frame_tabela.pack(fill="both", expand=True)
        scroll_disciplina = ttk.Scrollbar(frame_tabela, orient="vertical")
        self.tree_disciplina = ttk.Treeview(
            frame_tabela,
            columns=("ID", "Nome", "Turno", "Sala", "Professor"),
            show="headings",
            yscrollcommand=scroll_disciplina.set
        )
        scroll_disciplina.config(command=self.tree_disciplina.yview)
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
        self.tree_disciplina.pack(side="left", fill="both", expand=True)
        scroll_disciplina.pack(side="right", fill="y")
        self.tree_disciplina.bind("<Double-1>", self.selecionar_disciplina)
        self.list_disciplinas()
    # ---------------- CRUD DISCIPLINAS ----------------
    def add_disciplina(self):
        try:
            id_disciplina = self.ent_disc_id.get().strip().upper()
            nome = self.ent_disc_nome.get().strip()
            turno = self.ent_disc_turno.get().strip()
            sala = self.ent_disc_sala.get().strip().upper()
            professor = self.ent_disc_prof.get().strip()
            if not id_disciplina or not nome:
                messagebox.showwarning("Atenção", "Informe o ID e o nome da disciplina.")
                return
            disciplina_existente = self.buscar_disciplina_por_id(id_disciplina)
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO DISCIPLINA
                    (ID, NOME, TURNO, SALA, PROFESSOR)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(ID) DO UPDATE SET
                        NOME=excluded.NOME,
                        TURNO=excluded.TURNO,
                        SALA=excluded.SALA,
                        PROFESSOR=excluded.PROFESSOR
                    """,
                    (id_disciplina, nome, turno, sala, professor)
                )
                conn.commit()
            valores_atualizados = (id_disciplina, nome, turno, sala, professor)
            self.list_disciplinas(id_para_selecionar=id_disciplina)
            self.preencher_campos_disciplina(valores_atualizados)
            if disciplina_existente:
                messagebox.showinfo("Sucesso", "Disciplina já existia e foi atualizada na lista.")
            else:
                messagebox.showinfo("Sucesso", "Disciplina incluída e exibida na lista.")
        except sqlite3.IntegrityError:
            self.list_disciplinas(id_para_selecionar=id_disciplina)
            disciplina_existente = self.buscar_disciplina_por_id(id_disciplina)
            if disciplina_existente:
                self.preencher_campos_disciplina(disciplina_existente)
            messagebox.showerror(
                "Erro",
                "Não foi possível salvar a disciplina. A lista foi atualizada."
            )
        except Exception as e:
            messagebox.showerror("Erro ao incluir disciplina", str(e))
    def list_disciplinas(self, avisar_vazio=False, id_para_selecionar=None):
        try:
            for item in self.tree_disciplina.get_children():
                self.tree_disciplina.delete(item)
            self.tree_disciplina.selection_remove(self.tree_disciplina.selection())
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT ID, NOME, TURNO, SALA, PROFESSOR
                    FROM DISCIPLINA
                    ORDER BY ID
                """)
                dados = cursor.fetchall()
            for row in dados:
                item = self.tree_disciplina.insert("", "end", values=row)
                if id_para_selecionar and row[0] == id_para_selecionar:
                    self.tree_disciplina.selection_set(item)
                    self.tree_disciplina.focus(item)
                    self.tree_disciplina.see(item)
            if avisar_vazio and not dados:
                messagebox.showinfo(
                    "Disciplinas",
                    "Nenhuma disciplina cadastrada neste banco de dados."
                )
        except Exception as e:
            messagebox.showerror("Erro ao listar disciplinas", str(e))
    def buscar_disciplina_por_id(self, id_disciplina):
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT ID, NOME, TURNO, SALA, PROFESSOR
                FROM DISCIPLINA
                WHERE ID=?
                """,
                (id_disciplina,)
            )
            return cursor.fetchone()
    def update_disciplina(self):
        try:
            id_disciplina = self.ent_disc_id.get().strip().upper()
            nome = self.ent_disc_nome.get().strip()
            turno = self.ent_disc_turno.get().strip()
            sala = self.ent_disc_sala.get().strip().upper()
            professor = self.ent_disc_prof.get().strip()
            if not id_disciplina or not nome:
                messagebox.showwarning("Atenção", "Informe o ID e o nome da disciplina.")
                return
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE DISCIPLINA
                    SET NOME=?, TURNO=?, SALA=?, PROFESSOR=?
                    WHERE ID=?
                    """,
                    (nome, turno, sala, professor, id_disciplina)
                )
                conn.commit()
                alterados = cursor.rowcount
            if alterados == 0:
                messagebox.showwarning("Atenção", "Nenhuma disciplina encontrada com esse ID.")
            else:
                messagebox.showinfo("Sucesso", "Disciplina alterada com sucesso!")
            self.limpar_disciplina()
            self.list_disciplinas()
        except Exception as e:
            messagebox.showerror("Erro ao alterar disciplina", str(e))
    def delete_disciplina(self):
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
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM DISCIPLINA WHERE ID=?",
                    (id_disciplina,)
                )
                conn.commit()
                excluidos = cursor.rowcount
            if excluidos == 0:
                messagebox.showwarning("Atenção", "Nenhuma disciplina encontrada com esse ID.")
            else:
                messagebox.showinfo("Sucesso", "Disciplina excluída com sucesso!")
            self.limpar_disciplina()
            self.list_disciplinas()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Erro",
                "Não foi possível excluir. Esta disciplina pode estar vinculada a uma nota."
            )
        except Exception as e:
            messagebox.showerror("Erro ao excluir disciplina", str(e))
    def selecionar_disciplina(self, event):
        item = self.tree_disciplina.selection()
        if item:
            valores = self.tree_disciplina.item(item, "values")
            self.preencher_campos_disciplina(valores)
    def preencher_campos_disciplina(self, valores):
        self.ent_disc_id.delete(0, tk.END)
        self.ent_disc_nome.delete(0, tk.END)
        self.ent_disc_turno.delete(0, tk.END)
        self.ent_disc_sala.delete(0, tk.END)
        self.ent_disc_prof.delete(0, tk.END)
        self.ent_disc_id.insert(0, valores[0])
        self.ent_disc_nome.insert(0, valores[1])
        self.ent_disc_turno.insert(0, valores[2] or "")
        self.ent_disc_sala.insert(0, valores[3] or "")
        self.ent_disc_prof.insert(0, valores[4] or "")
    def limpar_disciplina(self):
        self.ent_disc_id.delete(0, tk.END)
        self.ent_disc_nome.delete(0, tk.END)
        self.ent_disc_turno.delete(0, tk.END)
        self.ent_disc_sala.delete(0, tk.END)
        self.ent_disc_prof.delete(0, tk.END)
    # ========================================================
    # ETAPA 13 - ABA NOTAS
    # ========================================================
    def setup_tab_nota(self):
        """
        Tela de cadastro de notas.
        """
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
    # ---------------- CRUD NOTAS ----------------
    def add_nota(self):
        try:
            valor = self.ent_nota_valor.get().strip()
            matricula = self.ent_nota_mat.get().strip()
            disciplina_id = self.ent_nota_disc.get().strip().upper()
            if not valor or not matricula or not disciplina_id:
                messagebox.showwarning("Atenção", "Preencha todos os campos da nota.")
                return
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO NOTA
                    (VALOR, MATRICULA, DISCIPLINA_ID)
                    VALUES (?, ?, ?)
                    """,
                    (converter_nota(valor), int(matricula), disciplina_id)
                )
                conn.commit()
            self.limpar_nota()
            self.list_notas()
            messagebox.showinfo("Sucesso", "Nota incluída com sucesso!")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Erro",
                "Verifique se a matrícula do aluno e o ID da disciplina existem."
            )
        except Exception as e:
            messagebox.showerror("Erro ao incluir nota", str(e))
    def list_notas(self):
        try:
            for item in self.tree_nota.get_children():
                self.tree_nota.delete(item)
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT ID, VALOR, MATRICULA, DISCIPLINA_ID
                    FROM NOTA
                    ORDER BY ID
                """)
                dados = cursor.fetchall()
            for row in dados:
                self.tree_nota.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Erro ao listar notas", str(e))
    def update_nota(self):
        try:
            id_nota = self.ent_nota_id.get().strip()
            valor = self.ent_nota_valor.get().strip()
            matricula = self.ent_nota_mat.get().strip()
            disciplina_id = self.ent_nota_disc.get().strip().upper()
            if not id_nota or not valor or not matricula or not disciplina_id:
                messagebox.showwarning("Atenção", "Preencha todos os campos.")
                return
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE NOTA
                    SET VALOR=?, MATRICULA=?, DISCIPLINA_ID=?
                    WHERE ID=?
                    """,
                    (converter_nota(valor), int(matricula), disciplina_id, int(id_nota))
                )
                conn.commit()
                alterados = cursor.rowcount
            if alterados == 0:
                messagebox.showwarning("Atenção", "Nenhuma nota encontrada com esse ID.")
            else:
                messagebox.showinfo("Sucesso", "Nota alterada com sucesso!")
            self.limpar_nota()
            self.list_notas()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Erro",
                "Verifique se a matrícula do aluno e o ID da disciplina existem."
            )
        except Exception as e:
            messagebox.showerror("Erro ao alterar nota", str(e))
    def delete_nota(self):
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
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM NOTA WHERE ID=?",
                    (int(id_nota),)
                )
                conn.commit()
                excluidos = cursor.rowcount
            if excluidos == 0:
                messagebox.showwarning("Atenção", "Nenhuma nota encontrada com esse ID.")
            else:
                messagebox.showinfo("Sucesso", "Nota excluída com sucesso!")
            self.limpar_nota()
            self.list_notas()
        except ValueError:
            messagebox.showerror("Erro", "O ID da nota deve ser um número inteiro.")
        except Exception as e:
            messagebox.showerror("Erro ao excluir nota", str(e))
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
# ETAPA 14 - EXECUÇÃO DO PROGRAMA
# ============================================================
if __name__ == "__main__":
    # Cria ou verifica o banco de dados.
    init_db()
    # Cria a janela principal.
    root = tk.Tk()
    # Aplica o estilo visual moderno.
    configurar_estilo()
    # Inicia o sistema.
    app = SistemaEstacio(root)
    # Mantém a janela aberta.
    root.mainloop()
