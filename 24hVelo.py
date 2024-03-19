import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel, ttk
import time

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("24h Vélo du Bois de la Cambre - Liste des Cyclistes")
        self.configure(bg='light gray')
        
        self.liste_cyclistes = []
        self.temps_cyclistes = []
        Chronometre(self)
        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style(self)
        style.configure('TButton', font=('Helvetica', 12), background='light blue')
        style.configure('TLabel', font=('Helvetica', 14), background='light gray')
        
        self.frame_liste = tk.Frame(self, bg='light gray')
        self.frame_liste.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.bouton_ajouter = ttk.Button(self.frame_liste, text="Ajouter un cycliste", command=self.ajouter_nom)
        self.bouton_ajouter.pack(pady=5, fill=tk.X)
        
        self.bouton_supprimer = ttk.Button(self.frame_liste, text="Supprimer sélectionné", command=self.supprimer_nom)
        self.bouton_supprimer.pack(pady=5, fill=tk.X)
        
        self.listbox_cyclistes = tk.Listbox(self.frame_liste, height=20, width=50, font=('Helvetica', 12))
        self.listbox_cyclistes.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

        self.bouton_statistiques = ttk.Button(self.frame_liste, text="Ouvrir Meilleur Tour", command=self.ouvrir_statistiques)
        self.bouton_statistiques.pack(pady=5, fill=tk.X)

        self.frame_meilleurs_temps = tk.Frame(self, bg='light gray')
        self.frame_meilleurs_temps.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.label_meilleurs_temps = ttk.Label(self.frame_meilleurs_temps, text="20 Meilleurs Temps", background='light gray')
        self.label_meilleurs_temps.pack()
        
        self.listbox_meilleurs_temps = tk.Listbox(self.frame_meilleurs_temps, height=20, width=50, font=('Helvetica', 12))
        self.listbox_meilleurs_temps.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)


    def ajouter_nom(self):
        nom = simpledialog.askstring("Ajouter un cycliste", "Nom du cycliste:")
        if nom:
            self.liste_cyclistes.append(nom)
            self.actualiser_liste()

    def supprimer_nom(self):
        selection = self.listbox_cyclistes.curselection()
        if selection:
            index = selection[0]
            del self.liste_cyclistes[index]
            self.actualiser_liste()
        else:
            messagebox.showwarning("Attention", "Veuillez sélectionner un cycliste à supprimer.")

    def actualiser_liste(self):
        self.listbox_cyclistes.delete(0, tk.END)
        for nom in self.liste_cyclistes:
            self.listbox_cyclistes.insert(tk.END, nom)
        self.actualiser_meilleurs_temps()

    def actualiser_meilleurs_temps(self):
        self.listbox_meilleurs_temps.delete(0, tk.END)
        # Tri et limitation à 20 entrées
        temps_tries = sorted(self.temps_cyclistes, key=lambda x: x[1])[:20]
        for index, (nom, temps) in enumerate(temps_tries, start=1):
            self.listbox_meilleurs_temps.insert(tk.END, f"{index}e {nom} {temps}s")

    def ouvrir_statistiques(self):
        fenetre_statistiques = Toplevel(self)
        fenetre_statistiques.title("Statistiques des Tours")
        fenetre_statistiques.configure(bg='light gray')

        # Calcul et affichage des statistiques
        statistiques = self.calculer_statistiques()
        for coureur, stats in statistiques.items():
            ttk.Label(fenetre_statistiques, text=f"{coureur}: Meilleur Tour = {stats['meilleur']}s, Moyenne = {stats['moyenne']}s").pack(padx=10, pady=5, anchor='w')

    def calculer_statistiques(self):
        statistiques = {}
        for nom, temps in self.temps_cyclistes:
            if nom not in statistiques:
                statistiques[nom] = {'temps': [], 'meilleur': float('inf'), 'moyenne': 0}
            statistiques[nom]['temps'].append(temps)
            statistiques[nom]['meilleur'] = min(statistiques[nom]['meilleur'], temps)

        for stats in statistiques.values():
            stats['moyenne'] = sum(stats['temps']) / len(stats['temps']) if stats['temps'] else 0

        return statistiques


class Chronometre(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Chronomètre")
        self.configure(bg='light gray')
        self.chrono_en_marche = False
        self.temps_debut = 0
        self.temps_actuel = 0
        self.setup_ui()

    def setup_ui(self):
        self.label_cycliste = ttk.Label(self, text="En attente...", font=("Helvetica", 16), background='light gray')
        self.label_cycliste.pack(pady=10)
        
        self.label_chrono = ttk.Label(self, text="00:00:00", font=("Helvetica", 24), background='light gray')
        self.label_chrono.pack(pady=20)

        self.bouton_demarrer = ttk.Button(self, text="Démarrer", command=self.demarrer_chrono)
        self.bouton_demarrer.pack(side=tk.LEFT, padx=5)

        self.bouton_arreter = ttk.Button(self, text="Arrêter & Enregistrer", command=self.arreter_chrono)
        self.bouton_arreter.pack(side=tk.LEFT, padx=5)

    def demarrer_chrono(self):
        if not self.chrono_en_marche and self.master.liste_cyclistes:
            self.cycliste_en_piste = self.master.liste_cyclistes[0]  # Prendre le premier cycliste
            self.label_cycliste.config(text=f"En piste : {self.cycliste_en_piste}")
            self.chrono_en_marche = True
            self.temps_debut = time.time()
            self.actualiser_chrono()
        elif not self.master.liste_cyclistes:
            messagebox.showwarning("Attention", "Aucun cycliste dans la liste.")

    def arreter_chrono(self):
        if self.chrono_en_marche:
            self.chrono_en_marche = False
            temps_ecoule = int(time.time() - self.temps_debut)
            cycliste = self.master.liste_cyclistes.pop(0)
            # Enregistrer chaque temps sans écraser
            self.master.temps_cyclistes.append((cycliste, temps_ecoule))
            self.master.actualiser_liste()
            self.label_cycliste.config(text="En attente...")
            self.afficher_temps(0)  # Réinitialiser l'affichage du chrono

    def actualiser_chrono(self):
        if self.chrono_en_marche:
            self.temps_actuel = int(time.time() - self.temps_debut)
            self.afficher_temps(self.temps_actuel)
            self.after(1000, self.actualiser_chrono)

    def afficher_temps(self, total_sec):
        heures = total_sec // 3600
        minutes = (total_sec % 3600) // 60
        secondes = total_sec % 60
        self.label_chrono.config(text=f"{heures:02}:{minutes:02}:{secondes:02}")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
