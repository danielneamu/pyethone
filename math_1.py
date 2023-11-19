import random
import time
# import termcolor
# from termcolor import colored
import re
def generate_question():
    num1 = random.randint(1, 12)
    num2 = random.randint(1, 12)
    operator = random.choice(['+', '-'])
    
    if operator == '-':
        
        num1, num2 = max(num1, num2), min(num1, num2)
    
    expresie = f"{num1} {operator} {num2}"
    rezultat_corect = eval(expresie)
    return expresie, rezultat_corect

def main():
    print("Bine ați venit în Aplicația pentru Teste de Matematică!")
    print("Vi se vor da 10 probleme de adunare și scădere (rezultate până la 12). Încercați să le rezolvați cât mai rapid posibil.")
    input("Apăsați Enter pentru a începe...")

    while True:
        numar_corect = 0
        timp_inceput = time.time()

        for i in range(10):
            expresie, raspuns_corect = generate_question()
            print(f"\nÎntrebarea {i + 1}: {expresie}")
            raspuns_utilizator = input("Răspunsul tău: ")

            try:
                raspuns_utilizator = int(raspuns_utilizator)
            except ValueError:
                raspuns_utilizator = None

            if raspuns_utilizator is not None and raspuns_utilizator == raspuns_corect:
                print("Corect!")
                numar_corect += 1
            else:
                print(f"Gresit! Răspunsul corect este {raspuns_corect}")

        timp_sfarsit = time.time()
        timp_total = timp_sfarsit - timp_inceput
        scor = (numar_corect / 10) * (1 / timp_total) * 100

        print("\nTestul a fost completat!")
        print(f"Timp total: {timp_total:.2f} secunde")
        print(f"Număr de răspunsuri corecte: {numar_corect}")
        print(f"Scorul tău: {scor:.2f}%")

        # Salvați și afișați scorurile TOATE
        scoruri = []
        with open("scoruri.txt", "a") as fisier_scor:
            fisier_scor.write(f"Scor: {scor:.2f}%\n")
            fisier_scor.close()
        with open("scoruri.txt", "r") as fisier_scor:
            scoruri = fisier_scor.readlines()
            fisier_scor.close()
        
        # Highlight the latest score in red
        # Highlight the latest score in green
        if scoruri:
            latest_score = scoruri[-1].strip()
            scoruri[-1] = f"\033[92m{latest_score}\033[0m"  # Green color
        # Sort the scores in descending order
        scoruri.sort(key=lambda s: float(re.sub(r'\x1b\[[0-9;]*m', '', s).split(":")[1].replace('%', '').strip()), reverse=True)

        print("\nClasament:")
        for s in scoruri:
            print(s.strip())

        repornire = input("\nDoriți să reporniți testul? (da/nu): ")
        if repornire.lower() != 'da':
            print("Vă mulțumim pentru joc!")
            break

if __name__ == "__main__":
    main()
