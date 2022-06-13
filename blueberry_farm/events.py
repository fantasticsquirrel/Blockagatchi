random.seed()
last_event = Variable()

@construct
def seed():
    last_event.set(0)

def event(plant_data):

    events = {
        1 : freak_rain, #extra water
        2 : hot_day, #lose water
        3 : swarm, #more bugs
        4 : birds, #less bugs
        5 : toxic_rain, #increase toxicity
        6 : lawn_gnomes, #decrease toxicity
        7 : solar_eclipse, #less photosynthesis
        8 : solar_flare, #more photosynthesis
        9 : extra_manure, #increased nutrients
        10 : greedy_weeds, #decreased nutrients
        11 : fertilizer_backfire, #increased weeds
        12 : friendly_snails #decreased weeds
    }

    event_num = (random.randint(1, 12))
    last_event.set(event_num)
    plant_data = events[event_num](plant_data)
    return plant_data

def freak_rain(plant_data):
    plant_data["current_water"] += (random.randint(3, 15))
    return plant_data

def hot_day(plant_data):
    plant_data["current_water"] -= (random.randint(3, 15))
    return plant_data

def swarm(plant_data):
    plant_data["current_bugs"] += (random.randint(3, 15))
    return plant_data

def birds(plant_data):
    plant_data["current_bugs"] -= (random.randint(3, 15))
    return plant_data

def toxic_rain(plant_data):
    plant_data["current_toxicity"] += (random.randint(3, 15))
    return plant_data

def lawn_gnomes(plant_data):
    plant_data["current_toxicity"] -= (random.randint(3, 15))
    return plant_data

def solar_eclipse(plant_data):
    plant_data["current_photosynthesis"] -= (random.randint(3, 10))
    return plant_data

def solar_flare(plant_data):
    plant_data["current_photosynthesis"] += (random.randint(3, 10))
    return plant_data

def extra_manure(plant_data):
    plant_data["current_nutrients"] += (random.randint(3, 15))
    return plant_data

def greedy_weeds(plant_data):
    plant_data["current_nutrients"] -= (random.randint(3, 15))
    return plant_data

def fertilizer_backfire(plant_data):
    plant_data["current_weeds"] += (random.randint(3, 15))
    return plant_data

def friendly_snails(plant_data):
    plant_data["current_weeds"] -= (random.randint(3, 15))
    return plant_data
