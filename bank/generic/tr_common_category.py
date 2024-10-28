from bank.model.transaction_category import TransactionCategory

COMMON_CATEGORY_MAP = {
    # GROCERIES
    "Lidl": TransactionCategory.GROCERIES,
    "Aldi": TransactionCategory.GROCERIES,
    "Carrefour": TransactionCategory.GROCERIES,
    "Leclerc": TransactionCategory.GROCERIES,
    "Auchan": TransactionCategory.GROCERIES,
    "Monoprix": TransactionCategory.GROCERIES,
    "Casino": TransactionCategory.GROCERIES,
    "Franprix": TransactionCategory.GROCERIES,

    # DINING_ENTERTAINMENT
    "McDonald's": TransactionCategory.DINING_ENTERTAINMENT,
    "KFC": TransactionCategory.DINING_ENTERTAINMENT,
    "Quick": TransactionCategory.DINING_ENTERTAINMENT,
    "Pizza Hut": TransactionCategory.DINING_ENTERTAINMENT,
    "Starbucks": TransactionCategory.DINING_ENTERTAINMENT,
    "Café de Flore": TransactionCategory.DINING_ENTERTAINMENT,
    "Ladurée": TransactionCategory.DINING_ENTERTAINMENT,

    # UTILITIES
    "EDF": TransactionCategory.UTILITIES,
    "Engie": TransactionCategory.UTILITIES,
    "Veolia": TransactionCategory.UTILITIES,
    "SFR": TransactionCategory.UTILITIES,
    "Orange": TransactionCategory.UTILITIES,
    "Bouygues Telecom": TransactionCategory.UTILITIES,

    # HOUSING
    "Airbnb": TransactionCategory.HOUSING,
    "Foncia": TransactionCategory.HOUSING,
    "Orpi": TransactionCategory.HOUSING,
    "Century 21": TransactionCategory.HOUSING,

    # TRANSPORTATION
    "SNCF": TransactionCategory.TRANSPORTATION,
    "Uber": TransactionCategory.TRANSPORTATION,
    "RATP": TransactionCategory.TRANSPORTATION,
    "Blablacar": TransactionCategory.TRANSPORTATION,
    "Total": TransactionCategory.TRANSPORTATION,

    # HEALTH_WELLNESS
    "Pharmacie": TransactionCategory.HEALTH_WELLNESS,
    "Doctolib": TransactionCategory.HEALTH_WELLNESS,
    "Pharmacie Lafayette": TransactionCategory.HEALTH_WELLNESS,
    "Fitness Park": TransactionCategory.HEALTH_WELLNESS,

    # ONLINE_SHOPPING
    "Amazon": TransactionCategory.ONLINE_SHOPPING,
    "Cdiscount": TransactionCategory.ONLINE_SHOPPING,
    "Fnac": TransactionCategory.ONLINE_SHOPPING,
    "Veepee": TransactionCategory.ONLINE_SHOPPING,

    # TRAVEL
    "Air France": TransactionCategory.TRAVEL,
    "Hertz": TransactionCategory.TRAVEL,
    "Booking.com": TransactionCategory.TRAVEL,
    "Expedia": TransactionCategory.TRAVEL,

    # EDUCATION_PROFESSIONAL
    "Udemy": TransactionCategory.EDUCATION_PROFESSIONAL,
    "Coursera": TransactionCategory.EDUCATION_PROFESSIONAL,
    "Acadomia": TransactionCategory.EDUCATION_PROFESSIONAL,

    # PERSONAL_CARE
    "Sephora": TransactionCategory.PERSONAL_CARE,
    "Yves Rocher": TransactionCategory.PERSONAL_CARE,
    "L'Occitane": TransactionCategory.PERSONAL_CARE,
    "Marionnaud": TransactionCategory.PERSONAL_CARE,

    # INVESTMENT_SAVINGS
    "BNP Paribas": TransactionCategory.INVESTMENT_SAVINGS,
    "Société Générale": TransactionCategory.INVESTMENT_SAVINGS,
    "Boursorama": TransactionCategory.INVESTMENT_SAVINGS,

    # CHARITY_DONATIONS
    "Secours Populaire": TransactionCategory.CHARITY_DONATIONS,
    "Croix-Rouge": TransactionCategory.CHARITY_DONATIONS,
    "UNICEF": TransactionCategory.CHARITY_DONATIONS,

    # LOANS_DEBT
    "Crédit Agricole": TransactionCategory.LOANS_DEBT,
    "Crédit Mutuel": TransactionCategory.LOANS_DEBT,

    # MISCELLANEOUS_OTHER
    "Tabac": TransactionCategory.MISCELLANEOUS_OTHER,
    "PMU": TransactionCategory.MISCELLANEOUS_OTHER,
}


