"""Popula o banco com o conteúdo pedagógico inicial (Seções 1, 2 e 3).

Uso, dentro do container do back-end:
    python -m app.seeds.run            # só popula se o conteúdo ainda não existir
    python -m app.seeds.run --reset    # APAGA o conteúdo e recria (apenas desenvolvimento!)

Digitações: flauta doce soprano barroca (dedilhado inglês), notas escritas na
clave de sol. Valores: 1 = furo fechado, 0 = furo aberto.
"""
import argparse
import random

from sqlalchemy import func, select, text

from app.core.database import SessionLocal
from app.models import Exercise, Fingering, Lesson, Note, Section, Unit

rng = random.Random(42)  # semente fixa: o conteúdo gerado é sempre o mesmo

# ---------------------------------------------------------------------------
# Dados das notas e digitações
# ---------------------------------------------------------------------------
HOLE_KEYS = ["thumb", "h1", "h2", "h3", "h4", "h5", "h6", "h7"]

FINGER_NAMES = {
    "thumb": "polegar esquerdo (atrás)",
    "h1": "indicador esquerdo",
    "h2": "médio esquerdo",
    "h3": "anelar esquerdo",
    "h4": "indicador direito",
    "h5": "médio direito",
    "h6": "anelar direito",
    "h7": "mínimo direito",
}


def holes(*closed: str) -> dict:
    return {k: (1 if k in closed else 0) for k in HOLE_KEYS}


def describe(h: dict) -> str:
    return " + ".join(FINGER_NAMES[k] for k in HOLE_KEYS if h[k] == 1)


# Ordem = ordem das unidades da Seção 3.
# freq = frequência do som REAL (a soprano soa uma oitava acima do escrito).
NOTES = [
    {"name": "Si", "sci": "B4", "freq": 987.77, "staff": 4, "holes": holes("thumb", "h1")},
    {"name": "Lá", "sci": "A4", "freq": 880.00, "staff": 3, "holes": holes("thumb", "h1", "h2")},
    {"name": "Sol", "sci": "G4", "freq": 783.99, "staff": 2, "holes": holes("thumb", "h1", "h2", "h3")},
    {"name": "Dó agudo", "sci": "C5", "freq": 1046.50, "staff": 5, "holes": holes("thumb", "h2")},
    {"name": "Ré agudo", "sci": "D5", "freq": 1174.66, "staff": 6, "holes": holes("h2")},
]

# Melodias curtas e originais dos desafios musicais (uma por unidade).
MELODIES = [
    [("Si", "seminima"), ("Si", "seminima"), ("Si", "minima"),
     ("Si", "seminima"), ("Si", "seminima"), ("Si", "minima")],
    [("Si", "seminima"), ("Lá", "seminima"), ("Si", "seminima"), ("Lá", "seminima"),
     ("Si", "minima"), ("Lá", "minima")],
    [("Sol", "seminima"), ("Lá", "seminima"), ("Si", "seminima"), ("Lá", "seminima"),
     ("Sol", "minima"), ("Sol", "seminima"), ("Lá", "seminima"), ("Si", "minima")],
    [("Sol", "seminima"), ("Lá", "seminima"), ("Si", "seminima"), ("Dó agudo", "minima"),
     ("Si", "seminima"), ("Lá", "seminima"), ("Sol", "minima")],
    [("Sol", "seminima"), ("Lá", "seminima"), ("Si", "seminima"), ("Dó agudo", "seminima"),
     ("Ré agudo", "minima"), ("Dó agudo", "seminima"), ("Si", "seminima"),
     ("Lá", "seminima"), ("Sol", "semibreve")],
]


# ---------------------------------------------------------------------------
# Ferramentas para montar lições e exercícios
# ---------------------------------------------------------------------------
def build_options(correct: dict, distractors: list) -> tuple:
    """Embaralha as opções e devolve (opções, gabarito)."""
    items = [correct] + list(distractors)
    rng.shuffle(items)
    options, correct_id = [], ""
    for letter, item in zip("abcd", items):
        options.append({"id": letter, **item})
        if item is correct:
            correct_id = letter
    return options, {"correct": correct_id}


def add_lesson(unit: Unit, title: str, lesson_type: str, xp: int = 10) -> Lesson:
    lesson = Lesson(title=title, lesson_type=lesson_type, xp_reward=xp,
                    position=len(unit.lessons) + 1)
    unit.lessons.append(lesson)
    return lesson


def add_ex(lesson: Lesson, etype: str, content: dict, solution=None, difficulty: int = 1):
    lesson.exercises.append(Exercise(
        exercise_type=etype, content=content, solution=solution,
        difficulty=difficulty, position=len(lesson.exercises) + 1,
    ))


def info(lesson: Lesson, title: str, body: str, **extra):
    add_ex(lesson, "informativo", {"title": title, "text": body, **extra})


def quiz(lesson: Lesson, prompt: str, correct: str, wrongs: list, difficulty: int = 1):
    options, solution = build_options({"label": correct}, [{"label": w} for w in wrongs])
    add_ex(lesson, "multipla_escolha", {"prompt": prompt, "options": options}, solution, difficulty)


def play(lesson: Lesson, prompt: str, assessment: str = "autoavaliacao",
         sequence=None, bpm: int = 60, difficulty: int = 1, checklist=None):
    content = {"prompt": prompt, "assessment": assessment, "bpm": bpm,
               "sequence": sequence or []}
    if checklist:
        content["checklist"] = checklist
    add_ex(lesson, "executar", content, None, difficulty)


def seq(notes_by_name: dict, pairs: list) -> list:
    return [{"note_id": notes_by_name[n].id, "duration": d} for n, d in pairs]


# Exercícios específicos de notas ------------------------------------------
def ex_fingering_diagram(lesson: Lesson, note: Note, all_notes: list, difficulty: int = 1):
    others = rng.sample([n for n in all_notes if n is not note], 3)
    options, solution = build_options(
        {"holes": note.fingering.holes},
        [{"holes": o.fingering.holes} for o in others],
    )
    add_ex(lesson, "identificar_digitacao", {
        "prompt": f"Qual diagrama mostra a digitação da nota {note.name_pt}?",
        "options": options,
    }, solution, difficulty)


def ex_fingers_text(lesson: Lesson, note: Note, all_notes: list, difficulty: int = 1):
    others = rng.sample([n for n in all_notes if n is not note], 3)
    quiz(lesson,
         f"Quais dedos fecham os furos para tocar a nota {note.name_pt}?",
         describe(note.fingering.holes),
         [describe(o.fingering.holes) for o in others], difficulty)


def ex_listen(lesson: Lesson, note: Note, known: list, difficulty: int = 1):
    others = rng.sample([n for n in known if n is not note], min(3, len(known) - 1))
    options, solution = build_options(
        {"label": note.name_pt}, [{"label": o.name_pt} for o in others])
    add_ex(lesson, "ouvir_e_reconhecer", {
        "prompt": "Ouça o som e escolha a nota correspondente.",
        "audio": {"note_ids": [note.id]},
        "options": options,
    }, solution, difficulty)


# ---------------------------------------------------------------------------
# Seção 1 e Seção 2
# ---------------------------------------------------------------------------
def build_section_1() -> Section:
    sec = Section(position=1, title="Familiarização com o instrumento",
                  description="Conheça a flauta doce e os cuidados básicos para começar a tocar.")
    unit = Unit(position=1, title="Conhecendo a flauta doce",
                objective="Identificar as partes do instrumento, a postura, a posição das mãos e os cuidados básicos.")
    sec.units.append(unit)

    l = add_lesson(unit, "Partes da flauta doce", "apresentacao")
    info(l, "Três partes",
         "A flauta doce soprano é formada por três partes: o bocal (onde se sopra), "
         "o corpo (com a maioria dos furos) e o pé (a parte final, com os últimos furos).")
    quiz(l, "Qual parte da flauta fica na boca?", "O bocal", ["O corpo", "O pé"])

    l = add_lesson(unit, "Postura adequada", "apresentacao")
    info(l, "Postura para tocar",
         "Mantenha a coluna ereta e os ombros relaxados. A flauta fica à frente do corpo, "
         "formando um ângulo de aproximadamente 45 graus.")
    quiz(l, "Como deve ficar a coluna ao tocar?", "Ereta, com os ombros relaxados",
         ["Curvada para a frente", "Inclinada para trás"])

    l = add_lesson(unit, "Mãos e dedos", "apresentacao")
    info(l, "Posição das mãos",
         "A mão esquerda fica na parte de cima: o polegar atrás e os três primeiros dedos "
         "nos três primeiros furos. A mão direita fica embaixo. Cubra os furos com a "
         "parte macia da ponta dos dedos, sem apertar demais.")
    quiz(l, "Qual mão fica na parte de cima da flauta?", "A mão esquerda",
         ["A mão direita", "Tanto faz, nenhuma é a correta"])

    l = add_lesson(unit, "Cuidados com o instrumento", "apresentacao")
    info(l, "Cuidando da sua flauta",
         "Evite deixar a flauta ao sol ou em locais quentes, seque o interior depois de "
         "tocar e nunca sopre com muita força.")
    quiz(l, "O que fazer depois de tocar?", "Secar o interior da flauta",
         ["Guardar a flauta ainda úmida", "Deixar a flauta ao sol para secar"])

    l = add_lesson(unit, "Revisão da seção", "revisao", xp=15)
    quiz(l, "Qual parte da flauta fica na boca?", "O bocal", ["O corpo", "O pé"])
    quiz(l, "Qual é a postura correta?", "Coluna ereta e ombros relaxados",
         ["Ombros levantados e tensos", "Corpo curvado sobre a flauta"])
    quiz(l, "Com o que se cobrem os furos?", "Com a parte macia da ponta dos dedos",
         ["Com as unhas", "Com a palma da mão"])
    return sec


def build_section_2() -> Section:
    sec = Section(position=2, title="Respiração e produção sonora",
                  description="Produza seus primeiros sons e desenvolva o controle do sopro.")
    unit = Unit(position=1, title="Primeiros sons",
                objective="Soprar com a intensidade adequada e produzir sons curtos, longos e estáveis.")
    sec.units.append(unit)

    l = add_lesson(unit, "Posição da boca no bocal", "apresentacao")
    info(l, "Boca e bocal",
         "Coloque apenas a ponta do bocal entre os lábios, sem apertar com os dentes. "
         "Sopre suavemente, como se pronunciasse 'tu'.")
    quiz(l, "Como devem ficar os dentes?", "Sem apertar o bocal",
         ["Mordendo o bocal", "Apoiados com força no bocal"])

    l = add_lesson(unit, "Intensidade do sopro", "apresentacao")
    info(l, "Sopro suave e constante",
         "Um sopro forte demais deixa o som estridente e muito agudo. Um sopro fraco demais "
         "deixa o som sem definição. Procure um sopro suave e contínuo.")
    quiz(l, "O que acontece se soprar forte demais?", "O som fica estridente e muito agudo",
         ["O som fica mais bonito", "Nada muda"])

    l = add_lesson(unit, "Sons curtos e longos", "pratica")
    info(l, "Duração dos sons", "Use o 'tu' para começar cada som. Para sons curtos, interrompa o sopro logo em seguida.")
    play(l, "Produza três sons curtos, em sequência: tu, tu, tu.")
    play(l, "Produza um som longo, sustentando o sopro por 4 segundos.")

    l = add_lesson(unit, "Emissão sonora estável", "pratica")
    info(l, "Som estável", "Procure manter o mesmo volume do início ao fim do som, sem oscilar.")
    play(l, "Sustente um som por 6 segundos, sem variar a intensidade.", assessment="audio")

    l = add_lesson(unit, "Desafio: seus primeiros sons", "desafio", xp=20)
    play(l, "Produza um som curto, um som longo e um som estável, nesta ordem.",
         assessment="audio",
         checklist=["Som curto limpo", "Som longo de 4 segundos", "Som estável de 6 segundos"])
    return sec


# ---------------------------------------------------------------------------
# Seção 3 (notas e digitação)
# ---------------------------------------------------------------------------
def build_section_3() -> tuple:
    sec = Section(position=3, title="Primeiras notas e digitação",
                  description="Aprenda as primeiras notas, associando nome, som e digitação.")
    objectives = [
        "Apresentar a primeira nota do curso e ensinar sua digitação básica.",
        "Introduzir uma nova nota e desenvolver a alternância entre posições dos dedos.",
        "Ampliar as notas conhecidas e coordenar pequenas sequências melódicas.",
        "Introduzir uma nota aguda e desenvolver maior controle do sopro.",
        "Consolidar as habilidades com outra nota aguda e revisar as cinco notas.",
    ]
    units = []
    for i, data in enumerate(NOTES):
        unit = Unit(position=i + 1, title=f"Nota {data['name']}", objective=objectives[i])
        sec.units.append(unit)
        units.append(unit)
    return sec, units


def fill_section_3_lessons(units: list, notes: list):
    by_name = {n.name_pt: n for n in notes}

    for i, (unit, note) in enumerate(zip(units, notes)):
        known = notes[: i + 1]          # notas já ensinadas, incluindo a nova
        previous = notes[:i]
        diff = i + 1                    # a dificuldade cresce com a unidade
        name = note.name_pt

        # 1. Apresentação
        l = add_lesson(unit, f"Conhecendo a nota {name}", "apresentacao")
        info(l, f"A nota {name}",
             f"Esta é a nota {name}. Na partitura ela fica na posição indicada abaixo e "
             f"seu som é demonstrado pelo botão de áudio.",
             note_id=note.id, show="nota_e_pauta")
        info(l, f"Digitação do {name}",
             f"Para tocar {name}, feche os furos com: {describe(note.fingering.holes)}.",
             note_id=note.id, show="digitacao")

        # 2. Reconhecimento
        l = add_lesson(unit, f"Reconhecendo o {name}", "reconhecimento")
        ex_fingering_diagram(l, note, notes, diff)
        ex_fingers_text(l, note, notes, diff)
        if len(known) >= 2:
            ex_listen(l, note, known, diff)
        ex_fingering_diagram(l, note, notes, diff)

        # 3. Prática individual
        l = add_lesson(unit, f"Praticando o {name}", "pratica")
        play(l, f"Toque a nota {name} e sustente o som por 4 segundos.",
             sequence=seq(by_name, [(name, "semibreve")]), difficulty=diff)
        play(l, f"Toque a nota {name} três vezes, com sons curtos.",
             sequence=seq(by_name, [(name, "seminima")] * 3), difficulty=diff)

        # 4. Combinação
        if previous:
            prev = previous[-1].name_pt
            l = add_lesson(unit, f"Alternando {prev} e {name}", "combinacao")
            play(l, f"Alterne entre {prev} e {name}, devagar.",
                 sequence=seq(by_name, [(prev, "minima"), (name, "minima")] * 2),
                 bpm=50, difficulty=diff)
            ex_listen(l, rng.choice(known), known, diff)
        else:
            l = add_lesson(unit, f"Ritmos simples com {name}", "combinacao")
            play(l, f"Toque {name} seguindo o ritmo: longo, curto, curto.",
                 sequence=seq(by_name, [(name, "minima"), (name, "seminima"), (name, "seminima")]),
                 bpm=60, difficulty=diff)

        # 5. Revisão
        l = add_lesson(unit, f"Revisão: {name}" if not previous else "Revisão das notas", "revisao", xp=15)
        for n in rng.sample(known, min(3, len(known))):
            ex_fingers_text(l, n, notes, diff)
        if len(known) >= 2:
            for n in rng.sample(known, min(2, len(known))):
                ex_listen(l, n, known, diff)
        ex_fingering_diagram(l, rng.choice(known), notes, diff)

        # 6. Desafio musical
        l = add_lesson(unit, "Desafio musical", "desafio", xp=25)
        play(l, "Toque a melodia abaixo do início ao fim, mantendo o ritmo.",
             assessment="audio", sequence=seq(by_name, MELODIES[i]), bpm=60 + 5 * i,
             difficulty=diff)


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------
def run(reset: bool = False):
    with SessionLocal() as db:
        if reset:
            db.execute(text(
                "TRUNCATE TABLE fingerings, notes, exercises, lessons, units, sections "
                "RESTART IDENTITY CASCADE"))
            db.commit()
            print("Conteúdo anterior apagado.")
        elif db.scalar(select(func.count()).select_from(Section)):
            print("O conteúdo já existe. Nada foi alterado (use --reset para recriar).")
            return

        sec1, sec2 = build_section_1(), build_section_2()
        sec3, units3 = build_section_3()
        db.add_all([sec1, sec2, sec3])
        db.flush()  # gera os ids das unidades

        notes = []
        for unit, data in zip(units3, NOTES):
            note = Note(name_pt=data["name"], scientific_name=data["sci"],
                        frequency_hz=data["freq"], staff_position=data["staff"],
                        introduced_in_unit_id=unit.id)
            note.fingering = Fingering(holes=data["holes"])
            notes.append(note)
        db.add_all(notes)
        db.flush()  # gera os ids das notas

        fill_section_3_lessons(units3, notes)
        db.commit()

        for label, model in [("seções", Section), ("unidades", Unit), ("lições", Lesson),
                             ("exercícios", Exercise), ("notas", Note), ("digitações", Fingering)]:
            print(f"  {label}: {db.scalar(select(func.count()).select_from(model))}")
        print("Conteúdo criado com sucesso.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Popula o conteúdo pedagógico.")
    parser.add_argument("--reset", action="store_true", help="apaga e recria o conteúdo")
    run(reset=parser.parse_args().reset)