import currency # For buy function

#NFTs are always part of a collection.

collection_name = Variable() # The name of the collection for display
collection_owner = Variable() # Only the owner can mint new NFTs for this collection
collection_nfts = Hash(default_value=0) # All NFTs of the collection
collection_balances = Hash(default_value=0) # All user balances of the NFTs
collection_balances_approvals = Hash(default_value=0) # Approval amounts of certain NFTs
plants = Hash(default_value=0) #store various data related to plants and growing seasons
metadata = Hash()
nicknames = Hash()
emergency = Hash()

random.seed()

@construct
def seed():
    collection_name.set("Harvest Blueberry Plants") # Sets the name
    collection_owner.set(ctx.caller) # Sets the owner
    metadata['operator'] = ctx.caller

    metadata['growing_season_length'] = 14
    metadata['plant price'] = 500
    #metadata['event_handler'] = 'con_bbf_events_01'
    metadata['ipfs_contract'] = 'con_harvest_gen0_ipfs'

    plants['growing_season'] = False
    plants['growing_season_start_time'] = now
    plants['count'] = 0
    plants['active_generation'] = 1
    emergency['addresses'] = {
        'ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d' : 0,
        '49aceeabdccdcb39f8c2c112e110ead1a5fef22c644825c1917b2df3204c433f' : 0,
        'e8dc708028e049397b5baf9579924dde58ce5bebee5655da0b53066117572e73' : 0
    }

    nicknames = {}


@export
def change_metadata(key: str, new_value: str, convert_to_decimal: bool=False):
    assert ctx.caller == metadata['operator'], "only operator can set metadata"
    if convert_to_decimal:
        new_value = decimal(new_value)
    metadata[key] = new_value

# function to mint a new NFT
def mint_nft(name: str, description: str, ipfs_image_url: str, nft_metadata: dict, amount: int):
    assert name != "", "Name cannot be empty"
    assert collection_nfts[name] == 0, "Name already exists"
    assert amount > 0, "You cannot transfer negative amounts"

    collection_nfts[name] = {"description": description, "ipfs_image_url": ipfs_image_url, "nft_metadata": f"See collection_nfts[{name},'nft_metadata']", "amount": amount} # Adds NFT to collection with all details
    collection_nfts[name,"nft_metadata"] = nft_metadata
    collection_balances[ctx.caller, name] = amount # Mints the NFT

# standard transfer function
@export
def transfer(name: str, amount:int, to: str):
    assert amount > 0, "You cannot transfer negative amounts"
    assert name != "", "Please specify the name of the NFT you want to transfer"
    assert collection_balances[ctx.caller, name] >= amount, "You don't have enough NFTs to send"

    collection_balances[ctx.caller, name] -= amount # Removes amount from sender
    collection_balances[to, name] += amount # Adds amount to receiver

# allows other account to spend on your behalf
@export
def approve(amount: int, name: str, to: str):
    assert amount > 0, "Cannot approve negative amounts"

    collection_balances_approvals[ctx.caller, to, name] += amount # Approves certain amount for spending by another account

# transfers on your behalf
@export
def transfer_from(name:str, amount:int, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative balances!'

    assert collection_balances_approvals[main_account, to, name] >= amount, "Not enough NFTs approved to send! You have {} and are trying to spend {}"\
        .format(collection_balances_approvals[main_account, to, name], amount)
    assert collection_balances[main_account, name] >= amount, "Not enough NFTs to send!"

    collection_balances_approvals[main_account, to, name] -= amount # Removes Approval Amount
    collection_balances[main_account, name] -= amount # Removes amount from sender

    collection_balances[to, name] += amount # Adds amount to receiver

@export
def start_growing_season():
    assert collection_owner.get() == ctx.caller, "Only the owner can start a growing season."
    grow_season = plants['growing_season']
    assert grow_season == False, "It is already growing season."
    growing_season_length = metadata['growing_season_length']
    active_gen = plants['active_generation']
    active_gen += 1
    plants['growing_season'] = True
    plants['growing_season_start_time'] = now
    plants['growing_season_end_time'] =  now + datetime.timedelta(days = growing_season_length + 3)
    plants[active_gen, 'finalize_time'] = now + datetime.timedelta(days = growing_season_length + 6)
    plants['active_generation'] = active_gen
    plants[active_gen, 'total_berries'] = 0
    plants[active_gen, 'sellable_berries'] = 0
    plants[active_gen, 'total_tau'] = 0
    plants[active_gen, 'claimable_tau'] = 0
    plants[active_gen,'stale_claim_time'] = now + datetime.timedelta(days = growing_season_length + 30)


@export
def buy_plant(nick : str, referrer : str = False):
    assert plants['growing_season'] == True, 'The growing season has not started, so you cannot buy a plant.'
    assert plants['growing_season_end_time'] >= now + datetime.timedelta(days = 11), "It's too far into the growing season and you cannot buy a plant now."
    assert not nick.isdigit(), "The plant nickname can't be an integer."
    assert bool(collection_nfts[nick]) == False, "This nickname already exists."
    assert nick.isalnum() == True, "Only alphanumeric characters allowed."
    assert nick != "", "Name cannot be empty"
    assert len(nick) >= 3, "The minimum length is 3 characters."
    plant_generation = plants['active_generation']
    growing_season_length = metadata['growing_season_length']

    plant_data = {
        "current_water": (random.randint(70, 90)),
        "current_bugs" : (random.randint(5, 25)),
        "current_photosynthesis" : 0,
        "current_nutrients" : (random.randint(70, 90)),
        "current_weeds" : (random.randint(5, 25)),
        "current_toxicity" : 0,
        "current_weather" : 1,
        "last_interaction" : now,
        "last_daily" : now,
        "last_calc" : now,
        "alive" : True,
        "last_squash_weed" : (now + datetime.timedelta(days = -1)),
        "last_grow_light" : (now + datetime.timedelta(days = -1)),
        "burn_amount" : 0,
        "plant_end_time" : (now + growing_season_length)
    }

    plant_calc_data =  {
        "previous_water": plant_data["current_water"],
        "previous_bugs" : plant_data["current_bugs"],
        "previous_nutrients" : plant_data["current_nutrients"],
        "previous_weeds" : plant_data["current_weeds"],
        "total_water": 0,
        "total_bugs" : 0,
        "total_nutrients" : 0,
        "total_weeds": 0
    }

    p_count = plants['count'] + 1
    name = f"Gen_{plant_generation}_{p_count}"
    collection_nfts[nick] = [plant_generation , p_count]
    payment(plant_generation, metadata['plant price'])

    #assigns random, one time use IPFS image
    ipfs_c = importlib.import_module(metadata['ipfs_contract'])
    ipfs_image_url = ipfs_c.pick_random()

    mint_nft(name,'This is a blueberry plant. Keep it alive and healthy by tending to it during growing season.' , ipfs_image_url , plant_data,1)
    collection_nfts[name,'plant_calc_data'] = plant_calc_data

    if referrer == True:
        collection_nfts[nick,'bonus_berries']  = 3
        collection_nfts[referrer,'bonus_berries']  += 3
    else:
        collection_nfts[nick,'bonus_berries'] = 0

    plants['count'] = p_count
    return [plant_data["current_water"],plant_data["current_photosynthesis"],plant_data["current_bugs"],plant_data["current_nutrients"],plant_data["current_weeds"],plant_data['current_toxicity'],plant_data["burn_amount"],plant_data["current_weather"],ipfs_image_url]

def action_setup(plant_generation : int, plant_number : int):
    name = f'Gen_{plant_generation}_{plant_number}'
    assert collection_balances[ctx.caller, name] == 1, "You do not own this plant."
    plant_data = collection_nfts[name,"nft_metadata"]
    assert plant_data["alive"] == True, 'Your plant is dead due to neglect and you must buy a new plant to try again. Try not to kill it too.'
    assert now <= plant_data['plant_end_time'], "Your plant's growing season has ended."


    #interaction idle check. If idle too long, plant gets penalized.
    if now > plant_data['last_interaction'] + datetime.timedelta(hours = 12):
        plant_data["current_water"] -= (random.randint(5, 15))
        plant_data["current_bugs"] += (random.randint(5, 15))
        plant_data["current_nutrients"] -= (random.randint(5, 15))
        plant_data["current_weeds"] += (random.randint(5, 15))

    plant_data = daily_conditions(plant_data, plant_generation) #checks if weather and other daily conditions need updating
    plant_data = totalizer_calc(plant_data,name) #checks if enough time has passed to add info to the plant totalizer calculations

    #if (random.randint(1, 10)) == 10 : #10% chance of an event happening #RANDOM EVENTS NOT WORKING. COMMENTING OUT UNTIL FIXED
    #    event_contract = importlib.import_module(metadata['event_handler'])
    #    plant_data = event_contract.event(plant_data)

    plant_data = dead_check(plant_data)
    plant_data['last_interaction'] = now #resets the interaction time

    plant_all = {
        'plant_data' : plant_data,
        'name' : name
    }

    return plant_all

def daily_conditions(plant_data, plant_generation):
    while now - plant_data["last_daily"] > datetime.timedelta(hours = 12) and now < (plant_data['plant_end_time']): #Loops through to calculate changes to plant if it's been more than a day since the last day's changes. Does multiple days worth too if needed
        current_weather = random.randint(1, 3) # 1=sunny 2=cloudy 3=rainy
        if current_weather == 1:
            plant_data["current_water"] -= (random.randint(10, 15)) #how much water is lost each sunny day
            plant_data["current_photosynthesis"] += (random.randint(4, 7)) #How much photosynthesis increases each sunny day
        if current_weather == 2:
            plant_data["current_water"] -= (random.randint(5, 9)) #how much water is lost each cloudy day
            plant_data["current_photosynthesis"] += (random.randint(2, 4)) #How much photosynthesis increases each cloudy day
        if current_weather == 3:
            plant_data["current_water"] += (random.randint(3, 12)) #how much water is gained each rainy day
            plant_data["current_photosynthesis"] += (random.randint(1, 2)) #How much photosynthesis increases each rainy day

        plant_data["current_bugs"] += (random.randint(3, 10)) #how many bugs are added each day
        plant_data["current_nutrients"] -= (random.randint(2, 5)) #how many nutrients are consumed each day
        plant_data["current_weeds"] += (random.randint(2, 10)) #how many weeds grow each day
        plant_data["last_daily"] += datetime.timedelta(hours = 12)
        plant_data["current_weather"] = current_weather
        plant_data['current_toxicity'] -= (random.randint(0, 2))
        plant_data['burn_amount'] -= (random.randint(0, 2))

        if plant_data['current_toxicity'] < 0:
            plant_data['current_toxicity'] = 0

        if plant_data['burn_amount'] < 0:
            plant_data['burn_amount'] = 0

        if plant_data['current_water'] > 100 : #water can't be above 100%
            plant_data['current_water'] = 100

        if plant_data["current_photosynthesis"] > 100 :
            plant_data["burn_amount"] += (plant_data["current_photosynthesis"]-100)
            plant_data["current_photosynthesis"] = 100

    return plant_data

def totalizer_calc(plant_data,name):
    if now > plant_data['last_calc'] + datetime.timedelta(hours = 3):
        if now > plant_data['plant_end_time'] :
            delta = plant_data['plant_end_time'] - plant_data['last_calc']
        else:
            delta = now - plant_data['last_calc']
        delta_d = (delta.seconds / 86400)
        plant_calc_data = collection_nfts[name,'plant_calc_data']
        #This sections performs an integral on the various properties for use in determining total berries produced.
        plant_calc_data["total_water"] += (delta_d**2*((plant_data["current_water"]/100-plant_calc_data["previous_water"]/100)/(delta_d))/2)+plant_calc_data["previous_water"]/100*delta_d
        plant_calc_data["total_bugs"] += (delta_d**2*(((1-plant_data["current_bugs"]/100)-(1-plant_calc_data["previous_bugs"]/100))/(delta_d))/2)+(1-plant_calc_data["previous_bugs"]/100)*delta_d
        plant_calc_data["total_nutrients"] += (delta_d**2*((plant_data["current_nutrients"]/100-plant_calc_data["previous_nutrients"]/100)/(delta_d))/2)+plant_calc_data["previous_nutrients"]/100*delta_d
        plant_calc_data["total_weeds"] += (delta_d**2*(((1-plant_data["current_weeds"]/100)-(1-plant_calc_data["previous_weeds"]/100))/(delta_d))/2)+(1-plant_calc_data["previous_weeds"]/100)*delta_d
        plant_data['last_calc'] = now
        #Updates previous values for next calculation period.
        plant_calc_data["previous_water"] = plant_data["current_water"]
        plant_calc_data["previous_bugs"] = plant_data["current_bugs"]
        plant_calc_data["previous_nutrients"] = plant_data["current_nutrients"]
        plant_calc_data["previous_weeds"] = plant_data["current_weeds"]

        collection_nfts[name,'plant_calc_data'] = plant_calc_data

    return plant_data

def dead_check(plant_data): #checks to see if your plant has died.
    if plant_data["current_toxicity"] >= 100 or plant_data["current_bugs"] >= 100 or plant_data["current_weeds"] >= 100 or plant_data["burn_amount"] >= 100 or plant_data["current_water"] <= 0 or plant_data["current_nutrients"] <= 0:
        plant_data["alive"] = False
    return plant_data

@export
def water(plant_generation : int, plant_number : int, num_times : int = 1): #Water your plant to increase its current_water.
    plant_all = action_setup(plant_generation,plant_number) #Runs the main method that performs all of the various checks required for the plant.
    plant_data = plant_all['plant_data']
    name = plant_all['name']

    for x in range(0, num_times):
        plant_data['current_water'] += (random.randint(5, 15))
    if plant_data['current_water'] > 100 : #water can't be above 1
        plant_data['current_water'] = 100

    collection_nfts[name,"nft_metadata"] = plant_data
    return [plant_data["current_water"],plant_data["current_photosynthesis"],plant_data["current_bugs"],plant_data["current_nutrients"],plant_data["current_weeds"],plant_data['current_toxicity'],plant_data["burn_amount"],plant_data["current_weather"]]

@export
def squash(plant_generation : int, plant_number : int): #Squash bugs to reduce current_bugs and takes 5 minutes.  Share's a timer with pullweeds.
    plant_all = action_setup(plant_generation,plant_number) #Runs the main method that performs all of the various checks required for the plant.
    plant_data = plant_all['plant_data']
    name = plant_all['name']

    t_delta = plant_data["last_squash_weed"] + datetime.timedelta(minutes = 5)
    assert now > t_delta, f"You are still squashing bugs or pulling weeds. Try again at {t_delta}."

    plant_data['current_bugs'] -= (random.randint(2, 5))
    if plant_data['current_bugs'] < 0 :
        plant_data['current_bugs'] = 0

    plant_data["last_squash_weed"] = now
    collection_nfts[name,"nft_metadata"] = plant_data
    return [plant_data["current_water"],plant_data["current_photosynthesis"],plant_data["current_bugs"],plant_data["current_nutrients"],plant_data["current_weeds"],plant_data['current_toxicity'],plant_data["burn_amount"],plant_data["current_weather"]]

@export
def spraybugs(plant_generation : int, plant_number : int): #Spray bugs to instantly reduce current_bugs but costs tau and adds small amount of toxicity
    plant_all = action_setup(plant_generation,plant_number) #Runs the main method that performs all of the various checks required for the plant.
    plant_data = plant_all['plant_data']
    name = plant_all['name']

    plant_data['current_toxicity'] += (random.randint(1, 3))

    plant_data['current_bugs'] -= (random.randint(10, 20))
    if plant_data['current_bugs'] < 0 :
        plant_data['current_bugs'] = 0

    payment(plant_generation, 5)
    collection_nfts[name,"nft_metadata"] = plant_data
    return [plant_data["current_water"],plant_data["current_photosynthesis"],plant_data["current_bugs"],plant_data["current_nutrients"],plant_data["current_weeds"],plant_data['current_toxicity'],plant_data["burn_amount"],plant_data["current_weather"]]

@export
def growlights(plant_generation : int, plant_number : int): #add photosynthesis to help plant catchup after several rainy days. Adds amount to current_photosynthesis but if it goes over 100%, burns your plant.
    plant_all = action_setup(plant_generation,plant_number) #Runs the main method that performs all of the various checks required for the plant.
    plant_data = plant_all['plant_data']
    name = plant_all['name']

    t_delta = plant_data["last_grow_light"] + datetime.timedelta(hours = 12)
    assert now > t_delta, f"You have used a grow light or shade too recently. Try again at {t_delta}."

    payment(plant_generation, 5)
    plant_data['current_photosynthesis'] += (random.randint(3, 5))
    plant_data["last_grow_light"] = now

    if plant_data["current_photosynthesis"] > 100 :
        plant_data["burn_amount"] += (plant_data["current_photosynthesis"]-100)
        plant_data["current_photosynthesis"] = 100

    collection_nfts[name,"nft_metadata"] = plant_data
    return [plant_data["current_water"],plant_data["current_photosynthesis"],plant_data["current_bugs"],plant_data["current_nutrients"],plant_data["current_weeds"],plant_data['current_toxicity'],plant_data["burn_amount"],plant_data["current_weather"]]

@export
def shade(plant_generation : int, plant_number : int): #shades your plant to reduce photosynthesis by a small amount
    plant_all = action_setup(plant_generation,plant_number) #Runs the main method that performs all of the various checks required for the plant.
    plant_data = plant_all['plant_data']
    name = plant_all['name']

    t_delta = plant_data["last_grow_light"] + datetime.timedelta(hours = 12)
    assert now > t_delta, f"You have used a grow light or shade too recently. Try again at {t_delta}."

    plant_data['current_photosynthesis'] -= (random.randint(3, 5))
    plant_data["last_grow_light"] = now

    if plant_data["current_photosynthesis"] < 0 :
        plant_data["current_photosynthesis"] = 0

    collection_nfts[name,"nft_metadata"] = plant_data
    return [plant_data["current_water"],plant_data["current_photosynthesis"],plant_data["current_bugs"],plant_data["current_nutrients"],plant_data["current_weeds"],plant_data['current_toxicity'],plant_data["burn_amount"],plant_data["current_weather"]]

@export
def fertilize(plant_generation : int, plant_number : int, num_times : int = 1): #increases current nutrients of the plant but if nutrients go over 100%, it burns your plant.
    plant_all = action_setup(plant_generation,plant_number) #Runs the main method that performs all of the various checks required for the plant.
    plant_data = plant_all['plant_data']
    name = plant_all['name']

    for x in range(0, num_times):
        plant_data['current_nutrients'] += (random.randint(4, 6))

    if plant_data['current_nutrients'] > 100 :
        plant_data["burn_amount"] += (plant_data['current_nutrients']-100)
        plant_data['current_nutrients'] = 100

    collection_nfts[name,"nft_metadata"] = plant_data
    return [plant_data["current_water"],plant_data["current_photosynthesis"],plant_data["current_bugs"],plant_data["current_nutrients"],plant_data["current_weeds"],plant_data['current_toxicity'],plant_data["burn_amount"],plant_data["current_weather"]]

@export
def pullweeds(plant_generation : int, plant_number : int): #reduces current weeds in plant and takes 5 minutes to do. Share's a timer with squash bugs.

    plant_all = action_setup(plant_generation,plant_number) #Runs the main method that performs all of the various checks required for the plant.
    plant_data = plant_all['plant_data']
    name = plant_all['name']

    t_delta = plant_data["last_squash_weed"] + datetime.timedelta(minutes = 5)
    assert now > t_delta, f"You are still squashing bugs or pulling weeds. Try again at {t_delta}."

    plant_data['current_weeds'] -= (random.randint(2, 5))
    if plant_data['current_weeds'] < 0 :
        plant_data['current_weeds'] = 0

    plant_data["last_squash_weed"] = now
    collection_nfts[name,"nft_metadata"] = plant_data
    return [plant_data["current_water"],plant_data["current_photosynthesis"],plant_data["current_bugs"],plant_data["current_nutrients"],plant_data["current_weeds"],plant_data['current_toxicity'],plant_data["burn_amount"],plant_data["current_weather"]]

@export
def sprayweeds(plant_generation : int, plant_number : int): #Spray weeds to instantly reduce current_weeds but costs tau and adds small amount of toxicity
    plant_all = action_setup(plant_generation,plant_number) #Runs the main method that performs all of the various checks required for the plant.
    plant_data = plant_all['plant_data']
    name = plant_all['name']

    plant_data['current_toxicity'] += (random.randint(1, 3))

    plant_data['current_weeds'] -= (random.randint(10, 20))
    if plant_data['current_weeds'] < 0 :
        plant_data['current_weeds'] = 0

    payment(plant_generation, 5)

    collection_nfts[name,"nft_metadata"] = plant_data
    return [plant_data["current_water"],plant_data["current_photosynthesis"],plant_data["current_bugs"],plant_data["current_nutrients"],plant_data["current_weeds"],plant_data['current_toxicity'],plant_data["burn_amount"],plant_data["current_weather"]]

@export
def finalize(plant_generation : int, plant_number : int): #Finalizes your plant at the end of growing season to deterimine your berry yield.
    active_generation = plants['active_generation']
    assert plant_generation == active_generation, f'The plant you are trying to interact with is not part of the current generation. The current generation is {active_generation}.'
    name = f'Gen_{plant_generation}_{plant_number}'
    assert collection_balances[ctx.caller, name] == 1, "You do not own this plant."
    assert collection_nfts[name,'finalized'] == False, 'This plant has already been finalized.'
    end_time = plant_data['plant_end_time']
    finalize_time = plants[plant_generation, 'finalize_time']
    assert now <= finalize_time and now >= end_time, f'It is not time to finalize your plant. Try between {end_time} and {finalize_time}'
    plant_data = collection_nfts[name,"nft_metadata"]
    plant_data = daily_conditions(plant_data, plant_generation) #checks if weather and other daily conditions need updating
    plant_data = dead_check(plant_data)
    if plant_data["alive"] == False:
        plant_data['last_calc'] = now
        collection_nfts[name,"nft_metadata"] = plant_data
        return 'Your plant is dead due to neglect and you cannot grow any berries. Try again next season.'

    if plants['growing_season'] == True : #first person to run this also turns growing_season to false and resets plant counter for next growing season
        plants['growing_season'] = False
        plants['count'] = 0

    plant_data = totalizer_calc(plant_data,name)
    collection_nfts[name,"nft_metadata"] = plant_data

    length = metadata['growing_season_length']
    berries = int(collection_nfts[name,'bonus_berries'] + (1000 * ((plant_calc_data["total_water"]*plant_calc_data["total_bugs"]*plant_calc_data["total_nutrients"]*plant_calc_data["total_weeds"])/(length**4))*(1-plant_data['current_toxicity']/100)*(plant_data["current_photosynthesis"]/100)*(1-plant_data["burn_amount"]/100)))
    collection_nfts[name,'berries'] = berries
    collection_nfts[name,'final_score'] = berries
    plants[plant_generation,'total_berries'] += berries

    if plants[plant_generation, 'claimable_tau'] == 0: #sets the total amount of tau that can be claimed by players.
        plants[plant_generation, 'claimable_tau'] = plants[plant_generation, 'total_tau']

    collection_nfts[name,'finalized'] == True
    berries = str(berries)
    return berries

@export
def sellberries(plant_generation : int, plant_number : int): #redeem berries for TAU. Must be done after plant finalize time is over.
    name = f'Gen_{plant_generation}_{plant_number}'
    assert collection_balances[ctx.caller, name] == 1, "You do not own this plant."
    berries = collection_nfts[name,'berries']
    assert berries > 0, "You don't have any berries to sell."
    assert now >= plants[plant_generation, 'finalize_time'], f"You can't sell yet. Try again after {plants[plant_generation, 'finalize_time']} but do not wait too long."
    sell_price = plants[plant_generation, 'total_tau'] / plants[plant_generation,'total_berries']
    proceeds = sell_price * berries
    currency.transfer(amount=proceeds, to=ctx.caller)
    collection_nfts[name,'berries'] = 0
    plants[plant_generation, 'claimable_tau']  -= proceeds
    proceeds = str(proceeds)
    return proceeds

def payment(plant_generation, amount): #used to process payments
    dev_reward = 0.05
    currency.transfer_from(amount=amount*(1-dev_reward), to=ctx.this, main_account=ctx.caller)
    currency.transfer_from(amount=amount*dev_reward, to=metadata['operator'], main_account=ctx.caller)
    plants[plant_generation, 'total_tau'] += amount*(1-dev_reward)

@export
def manual_reward_add(plant_generation : int, amount : int): #used to manually add more tau to the prize pool
    currency.transfer_from(amount=amount, to=ctx.this, main_account=ctx.caller)
    plants[plant_generation, 'total_tau'] += amount

@export
def stale_claims(plant_generation : int): #used by the operator to claim tau from a plant generation that ended at least 30 days prior. This allows players ample time to sell their berries
    assert metadata['operator'] == ctx.caller, "Only the operator can claim stale tau."
    stale_claim_time = plants[plant_generation,'stale_claim_time']
    assert now >= stale_claim_time, f"The tau is not stale yet and cannot be claimed. Try again after {stale_claim_time}"
    stale_tau = plants[plant_generation, 'claimable_tau']
    assert stale_tau > 0, "There is no stale tau to claim."
    currency.transfer(amount=stale_tau, to=ctx.caller)

@export
def manual_season_end(): #only needed if for some reason there were no finalized plants in the current grow season
    assert metadata['operator'] == ctx.caller, "Only the operator can do this."
    assert now > plants['growing_season_end_time'], "You can't end the season before the end_time."
    plants['growing_season'] = False
    plants['count'] = 0

@export
def new_nickname(plant_generation : int, plant_number : int, nick : str):
    name = f'Gen_{plant_generation}_{plant_number}'
    assert collection_balances[ctx.caller, name] == 1, "You do not own this plant."
    assert not nick.isdigit(), "The plant nickname can't be an integer."
    assert bool(collection_nfts[nick]) == False, "This nickname already exists."
    assert nick.isalnum() == True, "Only alphanumeric characters allowed."
    assert nick != "", "Name cannot be empty"
    assert len(nick) >= 3, "The minimum length is 3 characters."
    payment(plant_generation, 25)
    collection_nfts[nick] = [plant_generation , plant_number]

@export
def nickname_interaction(nickname : str, function_name :str): #allows players to interact with a plant based on its nickname
    nick = collection_nfts[nickname]

    function_names = {
        'water' : water,
        'squash' : squash,
        'spraybugs' : spraybugs,
        'growlights' : growlights,
        'shade' : shade,
        'fertilize' : fertilize,
        'pullweeds' : pullweeds,
        'sprayweeds' : sprayweeds,
        'finalize' : finalize,
        'sellberries' : sellberries
    }

    return function_names[function_name](nick[0],nick[1])

@export
def e_wdraw_enable(enable:bool):
    emergency_addresses = emergency['addresses']
    call_address = ctx.caller
    assert call_address in emergency_addresses.keys(), "You are not approved to do this."
    emergency_addresses[call_address] = int(enable)
    emergency['addresses'] = emergency_addresses

@export
def multisig_emergency_withdraw(amount:float): #can only be run if at least 2 of 3 multisig accounts approve of the emergency_withdraw
    emergency_addresses = emergency['addresses']
    call_address = ctx.caller
    approval_check = sum(emergency_addresses.values())
    assert approval_check >= 2, "An emergency withdrawal is not approved."
    assert metadata['operator'] == call_address, "Only the operator can claim tau."
    currency.transfer(amount=amount, to=call_address)

#@export
#def emergency_withdraw(amount:float): #temporary function used in testing. will be removed from final contract.
#    assert metadata['operator'] == ctx.caller, "Only the operator can claim tau."
#    currency.transfer(amount=amount, to=ctx.caller)
