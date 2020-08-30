import logging
import glob
import os
import random
import re
import sys


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def find_sources():
    """ feature 1 """
    logging.info("Searching for source files...")
    files = glob.glob("rsrc/que_*.txt")
    for name in files:
        cat = re.findall(".*que_(.*).txt", name)[0]
        words = cat.split("_")
        topic = ""
        for word in words:
            topic += word.capitalize() + " "
        splice(topic.strip(), name, name.replace("que_", "ans_"),
               name.replace("que_", "questionbank_").replace("rsrc", "questions"))


def splice(topic, qfile, afile, qbfile):
    """ feature 2 """
    logging.info(f"Processing {topic}...")
    with open(qfile, "r", encoding="utf-8") as qf, open(afile, "r", encoding="utf-8") as af, \
            open(qbfile, "w", encoding="utf-8") as qbf:

        # check file pointers
        if not qf:
            logging.critical(f"Can't open {qfile}!")
            return
        if not af:
            logging.critical(f"Can't open {afile}!")
            return
        if not qbf:
            logging.critical(f"Can't open {qbfile}!")
            return

        qbf.write(f"Topic: {topic}\n")
        answers = [re.sub(pattern="\d+.", repl="", string=line) for line in af if line != "\n"]
        for answer in answers:
            qbf.write("\n")
            item = read_question(qf, answer)
            qbf.writelines(item)


def read_question(fp, answer):
    """ read a question from the "que_*" file """
    item = []
    for _ in range(7):
        line = fp.readline()
        if not line:
            break

        if line.strip() == answer.strip():
            s = "*" + line[1:]
        elif line[0].upper() in ["A", "B", "C", "D"]:
            s = ">" + line[1:]
        elif re.match("\d+.", line):
            s = re.sub(pattern="\d+", repl="#", string=line)
        else:
            continue
        item.append(s)

    return item


def get_credentials():
    """ feature 3 """
    clear()
    credentials = None
    print("iPASS! Master Comprehensive Questions")
    u = input("Username: ")
    p = input("Password: ")
    if u == "clarkkent" and p == "123":
        print(f"\nWelcome user, {u}!")
        input("Press Enter key to proceed...")
        credentials = (u, p)
    else:
        print("Incorrect username or password! Exiting...")
    return credentials


def topic_selection():
    """ feature 4 """
    clear()

    print("Which among the topics below to take test?")
    topics = get_topics()
    choices = []
    for i, topic in enumerate(topics, start=1):
        print(f"[{i}] {topic[0]}")
    while True:
        try:
            sel = input("Your choice? ").split(",")
            indices = [int(s)-1 for s in sel]
            sel = ""
            for index in indices:
                if index < 0:               # special cases
                    raise ValueError
                sel += topics[index][0] + ", "
                choices.append(topics[index][1])
            sel = sel[:-2]
            print(f"You chose {sel}\n")
            break
        except:
            print("Your input is not valid!")

    num = [10, 15, 25]
    print("How many questions?")
    for i, n in enumerate(num, start=1):
        print(f"[{i}] {n} questions")
    while True:
        try:
            index = int(input("Your choice? "))-1
            if index < 0:  # special cases
                raise ValueError
            q = num[index]
            print(f"You will answer {q} questions.", end=" ")
            break
        except:
            print("Your input is not valid!")

    input("Press Enter key when ready...")
    return sel, choices, q


def get_topics():
    """ get the question banks and their corresponding topics """
    l = []
    files = glob.glob("questions/questionbank_*.txt")
    for name in files:
        with open(name, "r", encoding="utf-8") as f:
            line = f.readline()
            l.append([line.split(" ", maxsplit=1)[1].strip(), name])
    return l


def create_exam(student, topics, files, qcount):
    """ feature 5 """
    logging.info(f"Generating {qcount} questions from {files}...")
    questions = []
    for name in files:
        logging.info(f"Now reading {name}...")
        with open(name, "r", encoding="utf-8") as f:
            f.readline()
            f.readline()
            while True:
                item = read_item(f)
                if not item:
                    break
                questions.append(item)

    if qcount < len(questions):
        questions = random.sample(questions, qcount)
    exam = {"student": student, "topics": topics, "questions": questions,
            "total": len(questions), "score": 0, "grade": 0}
    return exam


def read_item(fp):
    """ read an item from the "questionbank_*" file """
    item = {"selected": None}
    choices = []

    line = fp.readline()
    if not line:
        return None

    item["question"] = line.strip()[1:]
    for _ in range(4):
        d = {}
        line = fp.readline()
        d["text"] = line.strip()[1:]
        d["correct"] = line.startswith("*")
        choices.append(d)

    random.shuffle(choices)
    for i in range(4):
        letter = chr(ord("A")+i)
        choices[i]["letter"] = letter
        if choices[i]["correct"]:
            item["answer"] = letter

    item["choices"] = choices
    fp.readline()
    return item


def show_exam(exam):
    """ feature 6 """
    clear()
    score = 0
    print("---! EXAM PROPER !---")
    for i, item in enumerate(exam["questions"], start=1):
        print(f'{i}{item["question"]}')
        for c in item["choices"]:
            print(f'  {c["letter"]}{c["text"]}')
        while True:
            s = input("Answer? ")
            answer = s.upper().strip()
            if answer in ["A", "B", "C", "D"]:
                item["selected"] = s
                if item["answer"] == answer:
                    score += 1
                break
            print("Invalid choice! Valid choices are A, B, C and D")
        print()

    print("---! END OF EXAM !---")
    exam["score"] = score
    exam["grade"] = score/exam["total"]
    input("Press Enter key to see results...")
    return exam


def process_results(exam):
    """ features 7 & 8 """
    clear()
    choice = 0
    print("Would you want to...")
    print("[1] Review the exam results")
    print("[2] Show my exam score then exit")
    print("[3] Show my exam score, save the results in a file then exit")
    while True:
        try:
            choice = int(input("Your choice? "))
            if not 0 < choice < 4:  # invalid
                raise ValueError
            break
        except:
            print("Your input is not valid!")
    if choice == 1:
        write_exam(exam, fn=print)
    print(f'\nEXAM SCORE: {exam["score"]}/{exam["total"]} ({exam["grade"]:.0%})')
    if choice == 3:
        save_exam_to_file(exam)

    print("\nTo take another exam, run this program again.")
    print("KEEP REVIEWING! iPASS IT! CLAIM IT!")


def write_exam(exam, fn):
    """ output the exam to a stream, depending on what the function fn is """
    logging.info(f"Using {fn} to write out the exam...")
    end = "" if fn == print else "\n"         # necessary since file.write doesn't automatically append \n
    fn(f"\n---! EXAM RESULTS !---{end}")
    for i, item in enumerate(exam["questions"], start=1):
        fn(f'\n{i}{item["question"]}{end}')
        for c in item["choices"]:
            fn(f'  {c["letter"]}{c["text"]}{end}')
        answer = item["answer"]
        selected = item["selected"]
        result = "Correct!" if selected.strip().upper() == answer else "Incorrect"
        fn(f'Correct Answer: {answer}{end}')
        fn(f'Your answer: {selected} ({result}){end}')
        if fn == print and i < exam["total"]:
            input("Press Enter key to proceed to the next question...")


def save_exam_to_file(exam):
    """ save exam to a file """
    while True:
        try:
            location = input("Enter the filename: ")
            with open(location, "w", encoding="utf-8") as f:
                lines = [
                    "iPASS! Master Comprehensive Questions (MCQ) Exam Results\n",
                    f'Student: {exam["student"][0]}\n',
                    f'ID number: {exam["student"][1]}\n',
                    f'Exam Taken: {exam["topics"]}\n',
                    f'Number of Questions: {exam["total"]}\n',
                ]
                f.writelines(lines)
                write_exam(exam, fn=f.write)
            print("File saved!")
            break
        except Exception as e:
            print(e)
            s = input('Press Enter to try again, or "q" to quit: ')
            if s == "q":
                break


def main_menu():
    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.DEBUG)

    # to enable logging, comment the next line
    logging.disable(sys.maxsize)

    logging.info("Program START")
    student = get_credentials()
    if not student:
        return
    if len(glob.glob("questions/questionbank_*.txt")) == 0:
        find_sources()
    topics, files, qcount = topic_selection()
    exam = create_exam(student=student, topics=topics, files=files, qcount=qcount)
    completed = show_exam(exam)
    process_results(completed)
    logging.info("Program END")


if __name__ == "__main__":
    main_menu()
