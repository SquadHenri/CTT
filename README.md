# Optimale treinplanning CTT Rotterdam
Optimale planning voor het laden van de containers op de wagons bij CTT in Rotterdam. 

## Optimalisatie technieken
Voor de optimalisatie van de treinplanning hebben wij een wiskundig model ontwikkelt.
Ons wiskunde model implementeren we in Python. 
Om de benodigde wiskundige optimalisatie technieken uit te voeren in Python maken we gebruik van OR-Tools van Google.

### OR-tools

#### OR-tools documentatie
OR-tools is een open-source project en biedt een uitgebreide documentatie. 
Bekijk OR-tools documentatie: 
[OR-tools documentatie](https://developers.google.com/optimization/introduction/overview)


#### OR-tools installeren
Om OR-Tools te installeren:
[OR-tools installatie handleiding](https://developers.google.com/optimization/install/python)


#### OR-tools voorbeelden
CTT/examples/OR-Tools-SimpleExample.py geeft een simpel voor beeld van hoe OR-Tools werkt. Het is het voorbeeld wat gebruikt wordt bij deze tutorial:
[Ga naar voorbeeld](https://developers.google.com/optimization/introduction/python)

CTT/examples/ORTools-MKnapsacksProblem.py is een wat complexer probleem, wat veel lijkt op ons probleem. Dit voorbeeld was de basis voor onze oplossing. De tutorial die hier bij hoort: [Ga naar voorbeeld](https://developers.google.com/optimization/bin/multiple_knapsack)

De implementatie van dit voorbeeld is te vinden in [CTT/scripts/TrainLoadingMain.py](https://github.com/SquadHenri/CTT/blob/main/scripts/TrainLoadingMain.py)
. 
