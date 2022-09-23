from owlready2 import*
print("OWL.Datei Management")
User = input()
print("die mögliche Klassen sind : ")
onto=get_ontology("/users/rimtghazouisni/Desktop/TU.BS/IFR/Teamprojekt/Pizza.owl").load()
print(list(onto.classes()))
User = input()
print("Wie soll die Instanz heißen ")
User = input()
print("Wähle bitte eine Klasse")
print(onto.search(iri="*Base"))
User = input()
print("Wähle bitte eine Klasse")
print(onto.search(iri="*Topping"))
User = input()
print(onto.search(iri="*Cheese"))
User = input()
with onto:
  class Pizza (Thing):pass
  class PizzaBase (Thing):pass
  class PizzaTopping (Thing):pass
Inst_01 = Pizza("Inst_01")
Inst_01.has_Base = [onto.DeepPanBase]
Inst_01.has_Topping = [onto.CheeseTopping]
print("Eine Instanz ist created : ")
for i in Pizza.instances(): print(i)
print("End des Programme")
