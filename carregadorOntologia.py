import tkinter as tk
from tkinter import filedialog, messagebox, font, simpledialog
from owlready2 import *
import csv
import numpy as np
from decimal import Decimal
from owlready2 import sync_reasoner_hermit
from owlready2 import get_ontology, sync_reasoner
import unicodedata
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
os.environ["JAVA_OPTS"] = "-Xmx8G"

# Funções associadas aos botões
def selecionar_ontologia():
    global arquivo_ontologia
    arquivo_ontologia = filedialog.askopenfilename(
        title="Selecione o arquivo da ontologia",
        filetypes=[("Arquivos RDF", "*.rdf"), ("Todos os arquivos", "*.*")]
    )
    if arquivo_ontologia:
        ontologia_carreada.set(True)  # Marca o checkbox como carregado
        messagebox.showinfo("Sucesso", "Ontologia seleciona com sucesso!")
    else:
        ontologia_carreada.set(False)  # Desmarca o checkbox

def selecionar_alunos_csv():
    global arquivo_alunos
    arquivo_alunos = filedialog.askopenfilename(
        title="Selecione o arquivo CSV de alunos",
        filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
    )
    if arquivo_alunos:
        alunos_carreado.set(True)  # Marca o checkbox como carregado
        messagebox.showinfo("Sucesso", "CSV de alunos selecionado com sucesso!")
    else:
        alunos_carreado.set(False)  # Desmarca o checkbox

def selecionar_historico_csv():
    global arquivo_historico
    arquivo_historico = filedialog.askopenfilename(
        title="Selecione o arquivo CSV de histórico",
        filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
    )
    if arquivo_historico:
        historico_carreado.set(True)  # Marca o checkbox como carregado
        messagebox.showinfo("Sucesso", "CSV de histórico selecionado com sucesso!")
    else:
        historico_carreado.set(False)  # Desmarca o checkbox

def selecionar_bolsas_csv():
    global arquivo_bolsas
    arquivo_bolsas = filedialog.askopenfilename(
        title="Selecione o arquivo CSV de bolsas",
        filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
    )
    if arquivo_bolsas:
        bolsas_carreado.set(True)  # Marca o checkbox como carregado
        messagebox.showinfo("Sucesso", "CSV de bolsas selecionado com sucesso!")
    else:
        bolsas_carreado.set(False)  # Desmarca o checkbox

def remover_acentos(texto):
    # Normaliza o texto para a forma de decomposição
    texto_normalizado = unicodedata.normalize('NFD', texto)
    # Remove os caracteres acentuados
    texto_sem_acentos = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
    return texto_sem_acentos
def nota_valida(valor):
    try:
        float(valor)
        return True
    except ValueError:
        return False
    
def carregar_alunos():
    global arquivo_ontologia, arquivo_alunos
    if arquivo_ontologia and arquivo_alunos:
        # Carregar a ontologia
        onto = get_ontology(arquivo_ontologia).load()
        
        # Processar o arquivo CSV de alunos
        try:
            with open(arquivo_alunos, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Aqui você pode mapear os dados do CSV para as classes da ontologia
                    id_usuario = row['IDUSUARIO']
                    genero = row['GENERO']
                    data_nascimento = row['DATANASCIMENTO']
                    ano_ingresso = row['ANO_INGRESSO']
                    semestre_ingresso = row['SEMESTRE_INGRESSO']
                    municipio = row['MUNICIPIO']
                    uf = row['UF']
                    sigla_uf = row['SIGLA_UF']
                    ingresso = row['INGRESSO']
                    grupo_ingresso = row['GRUPO_INGRESSO']
                    cotista = row['COTISTA']
                    total_pontos = float(row['TOTALPONTOS']) if row['TOTALPONTOS'] else None
                    situacao = row['SITUACAO']
                    motivosaida = remover_acentos(row['MOTIVOSAIDA'])
                    ano_formado = row['ANO_FORMADO']
                    semestre_formado = row['SEMESTRE_FORMADO']
                    etnia = row['ETNIA']
                    rendimento_academico = float(row['RENDIMENTO_ACADEMICO']) if row['RENDIMENTO_ACADEMICO'] else None
                    grupo_cota = row['GRUPO_INGRESSO']

                    #carrega os dados do estudante
                    Estudante = onto.Estudante
                    novo_estudante = Estudante()
                    novo_estudante.label.append(id_usuario)
                    novo_estudante.dataDeNascimento = data_nascimento
                    novo_estudante.anoIngresso = ano_ingresso
                    if int(semestre_ingresso) == 1:
                         novo_estudante.semestreIngresso = 1
                    else:
                        novo_estudante.semestreIngresso = 3
                        
                    novo_estudante.rendimentoAcademico = rendimento_academico

                    # Carrega os municípios e verifica se já existe com a mesma UF
                    municipio_existente = None
                    for m in onto.Municipio.instances():
                        if municipio == m.label[0]:
                            municipio_existente = m
                            break

                    # Se já existe e UF coincide
                    if municipio_existente and municipio_existente.UF == uf:
                        novo_estudante.EstudanteEdoMunicipio = municipio_existente
                    else:
                        novo_municipio = onto.Municipio()
                        if municipio_existente:
                            # Já existia município com nome igual, mas UF diferente
                            novo_municipio.label.append(f"{municipio}_{sigla_uf}")
                        else:
                            # Município totalmente novo
                            novo_municipio.label.append(municipio)
                        novo_municipio.UF = uf
                        novo_estudante.EstudanteEdoMunicipio = novo_municipio

                    #carrega os dados das etnias
                    Etnias = onto.Etnia
                    etnia_existente = None
                    for list_etnias in Etnias.instances():
                        if etnia in list_etnias.label[0]:
                           etnia_existente = list_etnias
                           break
                    if etnia_existente != None:
                        novo_estudante.EstudanteTemEtnia = etnia_existente
                    else:
                        nova_etnia = Etnias()
                        nova_etnia.label.append(etnia)
                        novo_estudante.EstudanteTemEtnia = nova_etnia

                   #Carrega os generos e verifica se é existente

                    genero = genero.strip().lower()

                    if genero == 'masculino':
                        novo_genero = onto.Masculino()
                    elif genero == 'feminino':
                        novo_genero = onto.Feminino()
                    else:
                        novo_genero = onto.Outros_Generos()

                    novo_genero.label.append(f'Genero_{id_usuario}')
                    novo_estudante.EstudanteTemGenero = novo_genero  # substitua pelo nome correto se não for esse

   
                    #metodos de ingresso
                    ingresso_normalizado = ingresso.strip().upper()

                    if 'SISU' in ingresso_normalizado:
                        ClasseMetodo = onto.Sisu
                    elif 'SELETIVO MISTO' in ingresso_normalizado:
                        ClasseMetodo = onto.Pism
                    elif 'VESTIBULAR' in ingresso_normalizado:
                        ClasseMetodo = onto.Vestibular
                    else:
                        ClasseMetodo = onto.OutrosMetodosIngresso

                    novo_metodoIngresso = ClasseMetodo()
                    novo_metodoIngresso.label.append(f'Ingresso_{id_usuario}')
                    novo_metodoIngresso.notaIngresso = total_pontos
                    novo_metodoIngresso.metodoIngresso = ingresso
                    novo_estudante.EstudanteTemMetodoIngresso = novo_metodoIngresso

            # Mapeamento dos nomes de grupos para as respectivas classes da ontologia
                    mapa_cotas = {
                        'Grupo A - antigo': onto.GrupoA_antigo,
                        'Grupo B - antigo': onto.GrupoB_antigo,
                        'Grupo C - antigo': onto.GrupoC_antigo,
                        'Grupo A': onto.GrupoA,
                        'Grupo B': onto.GrupoB,
                        'Grupo C': onto.GrupoC,
                        'Grupo D': onto.GrupoD,
                        'Grupo E': onto.GrupoE,
                        'Grupo F': onto.GrupoF,
                        'Grupo G': onto.GrupoG,
                        'Grupo H': onto.GrupoH,
                        'Grupo I': onto.GrupoI,
                        'Grupo J': onto.GrupoJ,
                        'Grupo A1': onto.GrupoA1,
                        'Grupo B1': onto.GrupoB1,
                        'Grupo D1': onto.GrupoD1,
                        'Vaga Ociosa': onto.VagaOciosa,
                        'PARFOR': onto.PARFOR,
                        'DEMANDA SOCIAL': onto.Demanda_Social
                    }

                    if grupo_ingresso in mapa_cotas:
                        classe_cota = mapa_cotas[grupo_ingresso]
                        nova_cota = classe_cota()
                        nova_cota.label.append(f'Cota_{id_usuario}')
                        novo_estudante.EstudanteTemTipoCota = nova_cota
                    
                    
                    situacao_normalizada = situacao.strip().lower()

                    if situacao_normalizada == 'ativo':
                        Situacao = onto.Ativo
                        nova_situacao = Situacao()
                        nova_situacao.label.append('Situacao_' + id_usuario)
                        novo_estudante.EstudanteTemSituacao = nova_situacao

                    elif situacao_normalizada == 'cancelado':
                        Situacao = onto.Cancelado
                        nova_situacao = Situacao()
                        nova_situacao.label.append('Situacao_' + id_usuario)
                        nova_situacao.motivoCancelado = motivosaida
                        novo_estudante.EstudanteTemSituacao = nova_situacao

                    elif situacao_normalizada == 'concluido':
                        Situacao = onto.Concluido
                        nova_situacao = Situacao()
                        nova_situacao.label.append('Situacao_' + id_usuario)
                        nova_situacao.anoFormatura = ano_formado
                        nova_situacao.semestreFormatura = int(semestre_formado)
                        novo_estudante.EstudanteTemSituacao = nova_situacao

                    elif situacao_normalizada == 'trancado':
                        Situacao = onto.Trancado
                        nova_situacao = Situacao()
                        nova_situacao.label.append('Situacao_' + id_usuario)
                        novo_estudante.EstudanteTemSituacao = nova_situacao

                    else:
                        Situacao = onto.OutrasSituacoes
                        nova_situacao = Situacao()
                        nova_situacao.label.append('Situacao_' + id_usuario)
                        nova_situacao.outraSituacao = situacao
                        novo_estudante.EstudanteTemSituacao = nova_situacao
                                        
                    
                    # Adicione a lógica para criar instâncias na ontologia ou fazer qualquer outra coisa necessária
                    # Por exemplo:
                    # student = Student(id_usuario=id_usuario, sexo=sexo, ...)
                onto.save(file='ontologia_carregada.rdf')
                onto.destroy()
                messagebox.showinfo("Sucesso", "Dados dos alunos carregados com sucesso!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao carregar o CSV de alunos: {e}")
    else:
        messagebox.showwarning("Aviso", "Nenhum arquivo de ontologia ou de alunos carregado.")
        
def calcular_periodo(ano_ingresso: int, semestre_ingresso: int, ano_turma: int, semestre_turma: int) -> int:
    """
    Calcula o período do aluno considerando que os semestres seguem a lógica de 1 e 3.
    Exemplo: ingresso em 2011/1 → 2011/1 = período 1, 2011/3 = período 2, 2012/1 = período 3, etc.
    """
    # Mapeia ano e semestre para um índice linear considerando apenas semestres 1 e 3
    def index(ano: int, semestre: int) -> int:
        if semestre not in [1, 3]:
            return 99
        return (ano * 2) + (0 if semestre == 1 else 1)

    idx_ingresso = index(ano_ingresso, semestre_ingresso)
    idx_turma = index(ano_turma, semestre_turma)

    periodo = idx_turma - idx_ingresso + 1  # +1 porque o período começa em 1
    return max(periodo, 1)

def normalizar_desempenho(valor):
    if valor is None:
        return None
    
    # Converter para string e remover espaços
    v = str(valor).strip().lower()

    # Se for número, retorna convertido direto
    try:
        return float(v)
    except ValueError:
        pass

    # Se for aprovação textual
    if "aprov" in v:      # pega "aprovado", "aprov", etc.
        return 100.0
    if "reprov" in v:     # pega "reprovado", "reprov", etc.
        return 0.0

    # Se não identificar, retorne None ou outro valor padrão
    return None


def carregar_historico():
    global arquivo_ontologia, arquivo_historico

    if not (arquivo_ontologia and arquivo_historico):
        messagebox.showwarning("Aviso", "Nenhum arquivo de ontologia ou de históricos carregado.")
        return

    # Carregar a ontologia
    try:
        onto = get_ontology("ontologia_carregada.rdf").load()
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível carregar a ontologia: {e}")
        return

    # Função auxiliar: remove estudante e tudo que depende dele
    def remover_estudante_e_relacoes(id_usuario):
        estudante_removido = False

        for estudante in list(onto.Estudante.instances()):
            if estudante.label and id_usuario in estudante.label[0]:
                # Remove desempenhos ligados ao estudante
                for desempenho in list(estudante.EstudanteObteveDesempenhoTurma):
                    destroy_entity(desempenho)

                # Limpa relação com turmas (não apaga as turmas em si)
                estudante.EstudanteFrequentouTurma.clear()

                # Remove o estudante
                destroy_entity(estudante)
                estudante_removido = True
                print(f"[LIMPEZA] Estudante {id_usuario} removido da ontologia devido a erro no histórico.")
                break

        if not estudante_removido:
            print(f"[LIMPEZA] Estudante {id_usuario} não encontrado para remoção.")

    # Processar o arquivo CSV de histórico
    try:
        with open(arquivo_historico, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                historico_id_usuario = row["IDUSUARIO"]

                try:
                    print(f"Carregando histórico: {historico_id_usuario}")

                    historico_disciplina = remover_acentos(row["DISCIPLINA"])
                    historico_turma = row["TURMA"]
                    historico_cod_disciplina = row["COD_DISCIPLINA"]
                    historico_depto = row["DEPTO"]
                    historico_nota = row["NOTA"]
                    historico_situacao = row["SITUACAO"]

                    # Conversões de ANO e SEMESTRE – se der erro, esse aluno será descartado
                    try:
                        historico_ano = int(row["ANO"])
                    except ValueError:
                        raise ValueError(
                            f"Valor inválido em ANO: '{row['ANO']}' para IDUSUARIO {historico_id_usuario}"
                        )

                    try:
                        historico_semestre = int(row["SEMESTRE"])
                    except ValueError:
                        raise ValueError(
                            f"Valor inválido em SEMESTRE: '{row['SEMESTRE']}' para IDUSUARIO {historico_id_usuario}"
                        )

                    historico_creditos = row["CREDITO"]
                    historico_datainicio = row["DATAINICIO"]
                    historico_datafim = row["DATAFIM"]

                    # Localizar estudante na ontologia
                    estudante_existente = None
                    for estudante in onto.Estudante.instances():
                        if estudante.label and historico_id_usuario in estudante.label[0]:
                            estudante_existente = estudante
                            break

                    if estudante_existente is not None:
                        # Localizar turma
                        turma_existente = None
                        for turma in onto.Turma.instances():
                            if turma.label and historico_turma in turma.label[0]:
                                turma_existente = turma
                                break

                        # Criar turma se ainda não existir
                        if turma_existente is None:
                            turma_existente = onto.Turma()
                            turma_existente.label.append(historico_turma)
                            turma_existente.anoTurma = historico_ano
                            turma_existente.semestreTurma = historico_semestre
                            turma_existente.dataInicioTurma = historico_datainicio
                            turma_existente.dataFimTurma = historico_datafim

                        # Relacionar estudante com turma
                        estudante_existente.EstudanteFrequentouTurma.append(turma_existente)

                        # Verificar se a disciplina já existe
                        disciplina_existente = None
                        for disciplina in onto.Disciplina.instances():
                            if (
                                disciplina.label
                                and historico_disciplina.lower().strip()
                                in disciplina.label[0].lower().strip()
                            ):
                                disciplina_existente = disciplina
                                break

                        # Se a disciplina não existir, cria uma nova
                        if disciplina_existente is None:
                            disciplina_existente = onto.Disciplina()
                            disciplina_existente.label.append(
                                f"{historico_cod_disciplina}_{historico_disciplina.strip()}"
                            )

                            # Créditos com conversão segura (se der erro, define 0)
                            try:
                                disciplina_existente.creditoDisciplina = int(historico_creditos)
                            except (ValueError, TypeError):
                                disciplina_existente.creditoDisciplina = 0

                            # Verifica se o departamento existe
                            departamento_existente = None
                            for departamento in onto.Departamento.instances():
                                if (
                                    departamento.label
                                    and historico_depto.lower().strip()
                                    in departamento.label[0].lower().strip()
                                ):
                                    departamento_existente = departamento
                                    break

                            # Cria o departamento se não existir
                            if departamento_existente is None:
                                departamento_existente = onto.Departamento()
                                departamento_existente.label.append(historico_depto.strip())

                            # Relaciona a disciplina ao departamento
                            disciplina_existente.DisciplinaPertenceAoDepartamento = (
                                departamento_existente
                            )

                        # Relaciona a turma à disciplina
                        turma_existente.TurmaPertenceADisciplina = disciplina_existente

                        # Criar desempenho da turma
                        novo_desempenhoTurma = onto.DesempenhoTurma()
                        novo_desempenhoTurma.label.append(
                            f"Desempenho_{historico_id_usuario}_{historico_turma}"
                        )
                        novo_desempenhoTurma.valorDesempenho = normalizar_desempenho(historico_nota)
                        novo_desempenhoTurma.situacaoDesempenho = historico_situacao
                        novo_desempenhoTurma.DesempenhoTurmaReferenteATurma = turma_existente

                        # Cálculo do período do aluno
                        novo_desempenhoTurma.periodoAluno = calcular_periodo(
                            int(estudante_existente.anoIngresso),
                            int(estudante_existente.semestreIngresso),
                            historico_ano,
                            historico_semestre,
                        )

                        estudante_existente.EstudanteObteveDesempenhoTurma.append(
                            novo_desempenhoTurma
                        )
                    else:
                        print(f"Estudante inexistente na ontologia: {historico_id_usuario}")

                except Exception as e_linha:
                    # Se deu erro para essa linha, remove o estudante e segue o próximo
                    print(f"[ERRO LINHA] Problema ao processar histórico do ID {historico_id_usuario}: {e_linha}")
                    remover_estudante_e_relacoes(historico_id_usuario)
                    # Não levanta o erro de novo, apenas ignora esse aluno
                    continue

        # Depois de processar todo o arquivo (ignorando alunos problemáticos), salva
        onto.save(file="ontologia_carregada.rdf")
        onto.destroy()
        messagebox.showinfo(
            "Sucesso",
            "Dados dos históricos carregados com sucesso! "
            "(Alunos com erros de dados foram desconsiderados.)",
        )

    except Exception as e:
        # Aqui são erros mais gerais: arquivo errado, permissão, etc.
        messagebox.showerror("Erro", f"Ocorreu um erro ao carregar o CSV de históricos: {e}")


def carregar_bolsas():

    
    global arquivo_ontologia, arquivo_bolsas
    if arquivo_ontologia and arquivo_bolsas:
        # Carregar a ontologia
        onto = get_ontology('ontologia_carregada.rdf').load()
        
        # Processar o arquivo CSV de alunos
        try:
            with open(arquivo_bolsas, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Aqui você pode mapear os dados do CSV para as classes da ontologia
                    bolsa_id_vaga_projeto = row['IDVAGAPROJETO']
                    bolsa_id_usuario = row['IDUSUARIO']
                    bolsa_bolsa = remover_acentos(row['BOLSA'])
                    bolsa_id_bolsa = row['IDBOLSA']
                    bolsa_projeto = remover_acentos(row['PROJETO'])
                    bolsa_id_projeto = row['IDPROJETO']
                    bolsa_remunerada = row['REMUNERADA']
                    bolsa_sigla = remover_acentos(row['SIGLA'])
                    bolsa_modalidade = remover_acentos(row['MODALIDADE'])
                    bolsa_data_inicio = row['DATAINICIO']
                    bolsa_data_fim = row['DATAFIM']
                    #cria relação estudante turma
                    Estudante = onto.Estudante
                    estudante_existente = None
                    for list_estudantes in Estudante.instances():
                        if bolsa_id_usuario in list_estudantes.label[0]:
                            estudante_existente = list_estudantes
                            break
                    if estudante_existente != None:
                        VagaProjeto = onto.VagaProjeto
                        nova_vaga_projeto = VagaProjeto()
                        nova_vaga_projeto.label.append(bolsa_id_vaga_projeto)
                        nova_vaga_projeto.dataInicioVagaProjeto = bolsa_data_inicio
                        nova_vaga_projeto.dataFimVagaProjeto = bolsa_data_fim
                        estudante_existente.EstudanteOcupaVagaProjeto.append(nova_vaga_projeto)
                        
                        Projeto = onto.Projeto
                        projeto_existente = None
                        for list_projetos in Projeto.instances():
                            if bolsa_id_projeto in list_projetos.label[0]:
                                projeto_existente = list_projetos
                                break
                        if projeto_existente!=None:
                            nova_vaga_projeto.VagaProjetoReferenteProjeto = projeto_existente
                        else:
                            novo_projeto = Projeto()
                            novo_projeto.label.append(bolsa_id_projeto)
                            novo_projeto.descricaoProjeto = bolsa_projeto
                            nova_vaga_projeto.VagaProjetoReferenteProjeto = novo_projeto
                            Bolsa = onto.Bolsa
                            bolsa_existente = None
                            for list_bolsas in Bolsa.instances():
                                if bolsa_id_bolsa in list_bolsas.label[0]:
                                    bolsa_existente = list_bolsas
                                    break
                            if bolsa_existente != None:
                                novo_projeto.ProjetoPertenceABolsa = bolsa_existente
                            else:
                                nova_bolsa = Bolsa()
                                nova_bolsa.label.append(bolsa_id_bolsa)
                                nova_bolsa.descricaoBolsa = bolsa_bolsa
                                nova_bolsa.remunerada = bolsa_remunerada
                                nova_bolsa.modalidadeBolsa = bolsa_modalidade
                                novo_projeto.ProjetoPertenceABolsa = nova_bolsa
                    
                    
                onto.save(file='ontologia_carregada.rdf')
                onto.destroy()
                messagebox.showinfo("Sucesso", "Dados das bolsas carregadas com sucesso!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao carregar o CSV de bolsas: {e}")
    else:
        messagebox.showwarning("Aviso", "Nenhum arquivo de ontologia ou de bolsas carregado.")


def str_to_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

# Função para verificar interseção de datas
def datas_em_comum(data_inicio_turma, data_fim_turma, data_inicio_projeto, data_fim_projeto):
    # Converte as strings em objetos datetime
    inicio_turma = str_to_date(data_inicio_turma)
    fim_turma = str_to_date(data_fim_turma)
    inicio_projeto = str_to_date(data_inicio_projeto)
    fim_projeto = str_to_date(data_fim_projeto)
    
    # Verifica se há interseção entre os períodos
    return max(inicio_turma, inicio_projeto) <= min(fim_turma, fim_projeto)

def obter_nome_arquivo():
    # Cria uma janela oculta para usar a caixa de diálogo
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal
    
    # Solicita ao usuário o nome do arquivo
    nome_arquivo = simpledialog.askstring(
        "Nome do Arquivo",
        "Digite o nome do arquivo para salvar:",
        initialvalue="arquivo_ml"
    )
    
    # Verifica se o usuário forneceu um nome
    if nome_arquivo:
        print(f"Nome do arquivo fornecido: {nome_arquivo}")
        return nome_arquivo
    else:
        print("Nenhum nome de arquivo fornecido.")
        return None



def gerar_arquivo():
    # Carregar a ontologia
    onto = get_ontology('ontologia_carregada.rdf').load()

    nome_base = obter_nome_arquivo()
    if not nome_base:
        messagebox.showwarning("Aviso", "Nenhum nome de arquivo fornecido.")
        return

    Estudantes = onto.Estudante

    # Vamos gerar arquivos para os períodos máximos 2, 3, 4 e 5
    for Max_Periodo in [2, 3, 4, 5]:
        print(f'Gerando arquivo para Max_Periodo = {Max_Periodo}')
        arquivo = []

        for estudante in Estudantes.instances():
            try:
                dados = {
                    'id_estudante': '',
                    'etnia': '',
                    'NOTA_INGRESSO': 0.0,
                    'TIPO_INGRESSO_PISM': 0,
                    'TIPO_INGRESSO_SISU': 0,
                    'TIPO_INGRESSO_VESTIBULAR': 0,
                    'TIPO_INGRESSO_OUTROS': 0,
                    'status': 0,
                    'cota_racial': 0,
                    'cota_ampla_concorrencia': 0,
                    'cota_escola_publica': 0,
                    'cota_renda': 0,
                    'cota_pcd': 0,
                    'genero_masculino': 0,
                    'genero_feminino': 0,
                    'genero_outros': 0
                }

                # Inicializa colunas dos períodos de 1 até Max_Periodo
                for i in range(1, Max_Periodo + 1):
                    dados[f'periodo_{i}_disciplinas_aprovadas'] = 0
                    dados[f'periodo_{i}_disciplinas_reprovadas'] = 0
                    dados[f'periodo_{i}_disciplinas_ri'] = 0
                    dados[f'periodo_{i}_disciplinas_trancadas'] = 0
                    dados[f'periodo_{i}_disciplinas_outros_status'] = 0
                    dados[f'periodo_{i}_bolsa_remunerada'] = ''
                    dados[f'periodo_{i}_bolsa_n_remunerada'] = ''
                    dados[f'periodo_{i}_AE'] = ''

                dados['id_estudante'] = estudante.label[0]
                dados['etnia'] = estudante.EstudanteTemEtnia.label[0]

                # Tipo de ingresso
                metodo_ingresso_classe = estudante.EstudanteTemMetodoIngresso.is_a[0]
                nota_ingresso = estudante.EstudanteTemMetodoIngresso.notaIngresso

                if metodo_ingresso_classe.name.upper() == 'SISU':
                    dados['TIPO_INGRESSO_SISU'] = 1
                    dados['NOTA_INGRESSO'] = nota_ingresso if nota_ingresso else 0
                elif metodo_ingresso_classe.name.upper() == 'PISM':
                    dados['TIPO_INGRESSO_PISM'] = 1
                    dados['NOTA_INGRESSO'] = nota_ingresso if nota_ingresso else 0
                elif metodo_ingresso_classe.name.upper() == 'VESTIBULAR':
                    dados['TIPO_INGRESSO_VESTIBULAR'] = 1
                    dados['NOTA_INGRESSO'] = nota_ingresso if nota_ingresso else 0
                else:
                    dados['TIPO_INGRESSO_OUTROS'] = 1
                    dados['NOTA_INGRESSO'] = 0

                # Cotas
                tipo_cota = estudante.EstudanteTemTipoCota.is_a[0]

                if tipo_cota in [onto.GrupoA, onto.GrupoD, onto.GrupoA1, onto.GrupoD1, onto.GrupoA_antigo]:
                    dados['cota_racial'] = 1

                if tipo_cota in [onto.GrupoA, onto.GrupoB, onto.GrupoG, onto.GrupoH,
                                 onto.GrupoA1, onto.GrupoB1, onto.GrupoH, onto.GrupoA_antigo, onto.GrupoB_antigo]:
                    dados['cota_renda'] = 1

                if tipo_cota not in [onto.GrupoC, onto.GrupoC_antigo, onto.Demanda_Social, onto.PARFOR, onto.VagaOciosa]:
                    dados['cota_escola_publica'] = 1

                if tipo_cota in [onto.GrupoF, onto.GrupoH, onto.GrupoJ,
                                 onto.GrupoA1, onto.GrupoB1, onto.GrupoD1, onto.GrupoE1]:
                    dados['cota_pcd'] = 1

                if tipo_cota in [onto.GrupoC, onto.GrupoC_antigo]:
                    dados['cota_ampla_concorrencia'] = 1

                # Gênero
                genero_classe = estudante.EstudanteTemGenero.is_a[0]
                if genero_classe is onto.Masculino:
                    dados['genero_masculino'] = 1
                elif genero_classe is onto.Feminino:
                    dados['genero_feminino'] = 1
                else:
                    dados['genero_outros'] = 1

                # Situação (status)
                situacao_classe = estudante.EstudanteTemSituacao.is_a[0]
                if situacao_classe.name.lower() == 'cancelado':
                    dados['status'] = 1
                else:
                    dados['status'] = 0

                # Desempenho por turma/período
                for turma_cursada in estudante.EstudanteObteveDesempenhoTurma:
                    periodo = turma_cursada.periodoAluno

                    if periodo <= Max_Periodo:
                        situacao = turma_cursada.situacaoDesempenho.upper()

                        if 'APR' in situacao:
                            dados[f'periodo_{periodo}_disciplinas_aprovadas'] += 1
                        elif 'REPNOTA' in situacao:
                            dados[f'periodo_{periodo}_disciplinas_reprovadas'] += 1
                        elif 'REPFREQ' in situacao:
                            dados[f'periodo_{periodo}_disciplinas_ri'] += 1
                        elif 'TRANC' in situacao:
                            dados[f'periodo_{periodo}_disciplinas_trancadas'] += 1
                        else:
                            dados[f'periodo_{periodo}_disciplinas_outros_status'] += 1

                        # Bolsa remunerada / não remunerada
                        if (dados[f'periodo_{periodo}_bolsa_remunerada'] == '' and
                            dados[f'periodo_{periodo}_bolsa_n_remunerada'] == ''):

                            data_inicio_turma = turma_cursada.DesempenhoTurmaReferenteATurma.dataInicioTurma
                            data_fim_turma = turma_cursada.DesempenhoTurmaReferenteATurma.dataFimTurma

                            if data_inicio_turma and data_fim_turma:
                                for vagaProjeto in estudante.EstudanteOcupaVagaProjeto:
                                    data_inicio_vaga_projeto = vagaProjeto.dataInicioVagaProjeto
                                    data_fim_vaga_projeto = vagaProjeto.dataFimVagaProjeto
                                    if datas_em_comum(data_inicio_turma, data_fim_turma,
                                                      data_inicio_vaga_projeto, data_fim_vaga_projeto):
                                        bolsa = vagaProjeto.VagaProjetoReferenteProjeto.ProjetoPertenceABolsa
                                        modalidade = bolsa.modalidadeBolsa.upper()
                                        if bolsa.remunerada == "1" and "PROAE" not in modalidade:
                                            dados[f'periodo_{periodo}_bolsa_remunerada'] = '1'
                                            break
                                        elif "PROAE" not in modalidade:
                                            dados[f'periodo_{periodo}_bolsa_n_remunerada'] = '1'
                                            break

                                if dados[f'periodo_{periodo}_bolsa_remunerada'] == '':
                                    dados[f'periodo_{periodo}_bolsa_remunerada'] = '0'
                                if dados[f'periodo_{periodo}_bolsa_n_remunerada'] == '':
                                    dados[f'periodo_{periodo}_bolsa_n_remunerada'] = '0'

                        # Ações de AE (PROAE)
                        if dados[f'periodo_{periodo}_AE'] == '':
                            data_inicio_turma = turma_cursada.DesempenhoTurmaReferenteATurma.dataInicioTurma
                            data_fim_turma = turma_cursada.DesempenhoTurmaReferenteATurma.dataFimTurma
                            if data_inicio_turma and data_fim_turma:
                                for vagaProjeto in estudante.EstudanteOcupaVagaProjeto:
                                    data_inicio_vaga_projeto = vagaProjeto.dataInicioVagaProjeto
                                    data_fim_vaga_projeto = vagaProjeto.dataFimVagaProjeto
                                    if datas_em_comum(data_inicio_turma, data_fim_turma,
                                                      data_inicio_vaga_projeto, data_fim_vaga_projeto):
                                        modalidade = vagaProjeto.VagaProjetoReferenteProjeto.ProjetoPertenceABolsa.modalidadeBolsa.upper()
                                        if "PROAE" in modalidade:
                                            dados[f'periodo_{periodo}_AE'] = '1'
                                            break
                                if dados[f'periodo_{periodo}_AE'] == '':
                                    dados[f'periodo_{periodo}_AE'] = '0'

                # Verifica se o aluno tem pelo menos uma disciplina em TODOS os períodos até Max_Periodo
                valido = True
                for i in range(1, Max_Periodo + 1):
                    if (
                        dados[f'periodo_{i}_disciplinas_aprovadas'] == 0 and
                        dados[f'periodo_{i}_disciplinas_reprovadas'] == 0 and
                        dados[f'periodo_{i}_disciplinas_ri'] == 0 and
                        dados[f'periodo_{i}_disciplinas_trancadas'] == 0 and
                        dados[f'periodo_{i}_disciplinas_outros_status'] == 0
                    ):
                        valido = False
                        break

                if valido:
                    arquivo.append(dados)

            except Exception as e:
                print(f'Pulando aluno com erro: {e}')

        if not arquivo:
            print(f"Nenhum dado válido para gerar arquivo para Max_Periodo={Max_Periodo}.")
            continue

        df = pd.DataFrame(arquivo)
        df.replace('', np.nan, inplace=True)
        df_encoded = pd.get_dummies(df, columns=['etnia'], drop_first=True)
        df_encoded.replace({True: 1, False: 0}, inplace=True)
        df_encoded.fillna(0, inplace=True)

        # Com ID
        df_encoded.to_csv(f"{nome_base}_p{Max_Periodo}_com_id.csv", index=False)
        # Sem ID
        df_sem_id = df_encoded.drop(columns=['id_estudante'], errors='ignore')
        df_sem_id.to_csv(f"{nome_base}_p{Max_Periodo}.csv", index=False)

    onto.destroy()
    messagebox.showinfo("Sucesso", "Arquivos de ML gerados para os períodos 2, 3, 4 e 5!")

            
            
    
    
  


root = tk.Tk()
root.title("Gerenciamento de Arquivos")

# Definindo o tamanho da janela (largura x altura)
root.geometry("800x400")  # Ajuste a altura conforme necessário

# Fontes
font_padrao = font.Font(family="Helvetica", size=12)
font_botao = font.Font(family="Helvetica", size=12, weight="bold")

# Definindo o layout com grid
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Frame para selecionar arquivos
frame_selecao = tk.Frame(root, padx=20, pady=20, bg="#f0f0f0")
frame_selecao.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

# Frame para carregar dados
frame_carregar = tk.Frame(root, padx=20, pady=20, bg="#f0f0f0")
frame_carregar.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

# Variáveis para os checkboxes
ontologia_carreada = tk.BooleanVar()
alunos_carreado = tk.BooleanVar()
historico_carreado = tk.BooleanVar()
bolsas_carreado = tk.BooleanVar()

# Definição do tamanho dos botões
button_width = 20

# Caixa de seleção para carregar a ontologia
btn_selecionar_ontologia = tk.Button(frame_selecao, text="Selecionar Ontologia", command=selecionar_ontologia, font=font_botao, bg="#4CAF50", fg="white", width=button_width, pady=5, relief="raised")
btn_selecionar_ontologia.pack(pady=5, anchor='w')
checkbox_ontologia = tk.Checkbutton(frame_selecao, text="Ontologia Selecionada", variable=ontologia_carreada, state='disabled', font=font_padrao, bg="#f0f0f0")
checkbox_ontologia.pack(pady=2, anchor='w')

# Caixa de seleção para carregar os alunos
btn_selecionar_alunos = tk.Button(frame_selecao, text="Selecionar Alunos .csv", command=selecionar_alunos_csv, font=font_botao, bg="#2196F3", fg="white", width=button_width, pady=5, relief="raised")
btn_selecionar_alunos.pack(pady=5, anchor='w')

checkbox_alunos = tk.Checkbutton(frame_selecao, text="Alunos Selecionados", variable=alunos_carreado, state='disabled', font=font_padrao, bg="#f0f0f0")
checkbox_alunos.pack(pady=2, anchor='w')

# Caixa de seleção para carregar o histórico
btn_selecionar_historico = tk.Button(frame_selecao, text="Selecionar Histórico .csv", command=selecionar_historico_csv, font=font_botao, bg="#FF5722", fg="white", width=button_width, pady=5, relief="raised")
btn_selecionar_historico.pack(pady=5, anchor='w')

checkbox_historico = tk.Checkbutton(frame_selecao, text="Histórico Selecionado", variable=historico_carreado, state='disabled', font=font_padrao, bg="#f0f0f0")
checkbox_historico.pack(pady=2, anchor='w')

# Caixa de seleção para carregar as bolsas
btn_selecionar_bolsas = tk.Button(frame_selecao, text="Selecionar Bolsas .csv", command=selecionar_bolsas_csv, font=font_botao, bg="#FFC107", fg="white", width=button_width, pady=5, relief="raised")
btn_selecionar_bolsas.pack(pady=5, anchor='w')

checkbox_bolsas = tk.Checkbutton(frame_selecao, text="Bolsas Selecionadas", variable=bolsas_carreado, state='disabled', font=font_padrao, bg="#f0f0f0")
checkbox_bolsas.pack(pady=2, anchor='w')

# Botões para carregar os dados
btn_carregar_alunos = tk.Button(frame_carregar, text="Carregar Alunos", command=carregar_alunos, font=font_botao, bg="#4CAF50", fg="white", width=button_width, pady=5, relief="raised")
btn_carregar_alunos.pack(pady=5)

btn_carregar_historico = tk.Button(frame_carregar, text="Carregar Histórico", command=carregar_historico, font=font_botao, bg="#2196F3", fg="white", width=button_width, pady=5, relief="raised")
btn_carregar_historico.pack(pady=5)

btn_carregar_bolsas = tk.Button(frame_carregar, text="Carregar Bolsas", command=carregar_bolsas, font=font_botao, bg="#FF5722", fg="white", width=button_width, pady=5, relief="raised")
btn_carregar_bolsas.pack(pady=5)

btn_carregar_bolsas = tk.Button(frame_carregar, text="Gerar Arquivo de ML", command=gerar_arquivo, font=font_botao, bg="#FF5722", fg="white", width=button_width, pady=5, relief="raised")
btn_carregar_bolsas.pack(pady=5)
# Inicializa as variáveis globais dos arquivos
arquivo_ontologia = None
arquivo_alunos = None
arquivo_historico = None
arquivo_bolsas = None

# Executar a interface gráfica
root.mainloop()
