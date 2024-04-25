import pandas as pd
import numpy as np

##TODO: A recept listát kiegészíteni egy új oszloppal amiben a étel jellege van, (reggeli, ebéd, vacsora, kiskaja)
##TODO: Hozzáadni, hogy vegye figyelembe a tervezésnél az étel jellegét is.
##TODO: Bevezetni, hogy hány főételből lehessen választani, tehát hány ételt tud főzni egyszerre


# Pandas megjelenítési beállításainak módosítása
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def get_float_input(prompt, default):
    while True:
        input_value = input(f"{prompt} (alapértelmezett: {default}): ") or str(default)
        try:
            value = float(input_value)
            return value
        except ValueError:
            print("Érvénytelen bemenet, kérlek adj meg egy számot.")

# Adatok bekérése a felhasználótól
daily_calories = int(input("Add meg a napi kalóriaigényed: (alapértelmezett: 2600) ") or "2600")

# Makrótápanyagok százalékos eloszlása
protein_ratio = get_float_input("Add meg a fehérje százalékos arányát", 30)
fat_ratio = get_float_input("Add meg a zsír százalékos arányát", 20)
carbs_ratio = get_float_input("Add meg a szénhidrát százalékos arányát", 50)

# Az étkezések számának és kalóriaeloszlásának bekérése
meals_per_day = int(input("Hány étkezést szeretnél naponta? (alapértelmezett: 5) ") or "5")
meal_distribution_percents = []
default_percents = [25, 10, 35, 10, 20]  # Alapértelmezett százalékok az étkezésekhez
print("Add meg az egyes étkezések kalória-százalékos eloszlását:")

for i in range(meals_per_day):
    percent = get_float_input(f"Étkezés {i+1} százalékos aránya", default_percents[i])
    meal_distribution_percents.append(percent)

# Receptek beolvasása CSV-ből
recipes = pd.read_csv('./receptek.csv', delimiter=';')
recipes['Energy'] = recipes['Energy'].str.extract(r'(\d+)').astype(int)
recipes['Fat'] = recipes['Fat'].str.extract(r'(\d+)').astype(int)
recipes['Carbs'] = recipes['Carbs'].str.extract(r'(\d+)').astype(int)
recipes['Fiber'] = recipes['Fiber'].str.replace(' g', '').astype(int)
recipes['Protein'] = recipes['Protein'].str.extract(r'(\d+)').astype(int)

# Napi kalóriaigény százalékos eloszlása
meal_calories = [daily_calories * perc / 100 for perc in meal_distribution_percents]

# Heti étkezési terv létrehozása
meal_plan = pd.DataFrame()
all_recipes_used = set()

for day in range(7):  # Egy hét minden napjára
    daily_plan = pd.DataFrame()
    daily_recipes = recipes.copy()

    for meal, target_calories_per_meal in enumerate(meal_calories):  # Naponta meghatározott számú étkezés
        unused_recipes = daily_recipes[~daily_recipes.index.isin(all_recipes_used)]
        if unused_recipes.empty:
            unused_recipes = recipes.copy()
            all_recipes_used.clear()

        closest_recipe_index = (unused_recipes['Energy'] - target_calories_per_meal).abs().idxmin()
        chosen_recipe = unused_recipes.loc[closest_recipe_index].copy()
        potential_servings = np.arange(0.5, 3.1, 0.5)
        servings = potential_servings[np.abs(potential_servings * chosen_recipe['Energy'] - target_calories_per_meal).argmin()]

        chosen_recipe['Servings'] = servings
        chosen_recipe['day'] = day + 1
        daily_plan = pd.concat([daily_plan, chosen_recipe.to_frame().T])
        all_recipes_used.add(closest_recipe_index)

    total_calories = daily_plan['Energy'].mul(daily_plan['Servings']).sum()
    total_fat = daily_plan['Fat'].mul(daily_plan['Servings']).sum() * 9
    total_carbs = daily_plan['Carbs'].mul(daily_plan['Servings']).sum() * 4
    total_protein = daily_plan['Protein'].mul(daily_plan['Servings']).sum() * 4
    fat_percentage = total_fat / total_calories * 100
    carbs_percentage = total_carbs / total_calories * 100
    protein_percentage = total_protein / total_calories * 100

    daily_summary = pd.DataFrame({
        "Recipe Name": ["Total"],
        "Energy": [total_calories],
        "Fat": [f"{total_fat / 9:.1f}g ({fat_percentage:.1f}%)"],
        "Sodium": ["-"],
        "Carbs": [f"{total_carbs / 4:.1f}g ({carbs_percentage:.1f}%)"],
        "Fiber": [daily_plan['Fiber'].mul(daily_plan['Servings']).sum()],
        "Protein": [f"{total_protein / 4:.1f}g ({protein_percentage:.1f}%)"],
        "day": [day + 1]
    })
    daily_plan = pd.concat([daily_plan, daily_summary])
    meal_plan = pd.concat([meal_plan, daily_plan])

# Eredmények megjelenítése
print(meal_plan)

