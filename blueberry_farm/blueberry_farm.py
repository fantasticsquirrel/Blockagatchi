import currency # For buy function

#NFTs are always part of a collection.

collection_name = Variable() # The name of the collection for display
collection_owner = Variable() # Only the owner can mint new NFTs for this collection
collection_nfts = Hash(default_value=0) # All NFTs of the collection
collection_balances = Hash(default_value=0) # All user balances of the NFTs
collection_balances_approvals = Hash(default_value=0) # Approval amounts of certain NFTs

market = Hash(default_value=0) # Stores NFTs up for sale
plants = Hash(default_value=0)
metadata = Hash()

random.seed()

@construct
def seed(name: str, royalties: int):
    collection_name.set(name) # Sets the name
    collection_owner.set(ctx.caller) # Sets the owner
    metadata['operator'] = ctx.caller
    metadata['royalties'] = royalties/100

    metadata['growing_season_length'] = 30
    metadata['plant price'] = 100

    plants['growing_season'] = False
    plants['growing_season_start_time'] = now
    plants['count'] = 0
    plants['active_generation'] = -1


@export
def change_metadata(key: str, new_value: str):
    assert ctx.caller == metadata['operator'], "only operator can set metadata"
    metadata[key] = new_value

# function to mint a new NFT
@export
def mint_nft(name: str, description: str, ipfs_image_url: str, nft_metadata: dict, amount: int):
    assert name != "", "Name cannot be empty"
    assert collection_nfts[name] == 0, "Name already exists"
    assert amount > 0, "You cannot transfer negative amounts"
    #assert collection_owner.get() == ctx.caller, "Only the collection owner can mint NFTs"

    collection_nfts[name] = {"description": description, "ipfs_image_url": ipfs_image_url, "nft_metadata": nft_metadata, "amount": amount} # Adds NFT to collection with all details
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

# put nft up for sale in collection market
@export
def sell_nft(name: str, amount: int, currency_price: float):
    assert amount > 0, 'Cannot sell negative NFT amount'
    assert currency_price > 0, 'Cannot sell for negative balances!'
    assert collection_balances[ctx.caller, name] > 0,'You dont own that amount of the NFT'

    collection_balances[ctx.caller, name] -= amount # Removes amount from seller
    market[ctx.caller, name] = {"amount": amount, "price": currency_price} # Adds amount to market

# buy nft in collection market
@export
def buy_nft(name: str, seller: str, amount:int):
    assert amount > 0, 'Cannot buy negative NFT amount'
    assert market[seller, name]["amount"] >= amount, 'Not enough for sale'
    royalties = metadata['royalties']

    currency.transfer_from(amount=market[seller, name]["price"] * amount * (1-royalties), to=seller, main_account=ctx.caller) # Transfers TAU (minus royalties) to Seller
    currency.transfer_from(amount=market[seller, name]["price"] * amount * royalties, to=collection_owner.get(), main_account=ctx.caller) # Transfers TAU royalties to creator

    old_market_entry = market[ctx.caller, name] # Saves the old market entry for overwrite
    market[ctx.caller, name] = {"amount": old_market_entry["amount"] - amount, "price": currency_price} # Removing the amount sold of market entry

    collection_balances[ctx.caller, name] += amount # Adds amount bought to buyer

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
    plants['growing_season_end_time'] =  now + datetime.timedelta(days = growing_season_length)
    plants['finalize_time'] = now + datetime.timedelta(days = growing_season_length + 3)
    plants[active_gen, 'total_berries'] = 0
    plants[active_gen, 'total_tau'] = 0
    plants[active_gen,'stale_claim_time'] = now + datetime.timedelta(days = growing_season_length + 30)


@export
def buy_plant():
    assert plants['growing_season'] == True, 'The growing season has not started, so you cannot buy a plant.'
    assert plants['growing_season_end_time'] >= now + datetime.timedelta(days = 25), "It's too far into the growing season and you cannot buy a plant now."
    plant_generation = plants['active_generation']

    plant_data = {
        #"drought_resist": (random.randint(0, 25))/100,
        #"crop_yield": (random.randint(90, 110))/100,
        #"bug_resist": (random.randint(0, 25))/100,
        #"photosynthesis_rate": (random.randint(90, 110))/100,
        "current_water": (random.randint(60, 80))/100,
        "current_bugs" : (random.randint(5, 25))/100,
        "current_photosynthesis" : 0,
        "current_nutrients" : (random.randint(60, 80))/100,
        "current_weeds" : (random.randint(5, 25))/100,
        "current_toxicity" : 0,
        "current_weather" : 1,
        "last_interaction" : now,
        "last_daily" : now,
        "last_calc" : now,
        "alive" : True,
        "generation" : plant_generation,
        "last_squash_weed" : (now + datetime.timedelta(days = -1)),
        "last_grow_light" : (now + datetime.timedelta(days = -1))
    }

    plant_calc_data =  {
        "previous_water": plant_data["current_water"],
        "previous_bugs" : plant_data["current_bugs"],
        "previous_photosynthesis" : plant_data["current_photosynthesis"],
        "previous_nutrients" : plant_data["current_nutrients"],
        "previous_weeds" : plant_data["current_weeds"],
        "total_water": 0,
        "total_bugs" : 0,
        "total_photosynthesis" : 0,
        "total_nutrients" : 0,
        "total_weeds": 0
    }

    p_count = plants['count'] + 1
    name = f"Gen_{plant_generation}_{p_count}"
    payment(plant_generation, metadata['plant price'])
    mint_nft(name,'placeholder description','placeholder image URL',plant_data,1)
    collection_nfts[name,'plant_calc_data'] = plant_calc_data
    plants['count'] = p_count

def action_setup(plant_generation : int, plant_number : int):
    active_generation = plants['active_generation']
    assert plant_generation == active_generation, f'The plant you are trying to interact with is not part of the current generation. The current generation is {active_generation}.'
    name = f'Gen_{plant_generation}_{plant_number}'
    assert collection_balances[ctx.caller, name] == 1, "You do not own this plant."
    assert now <= plants['growing_season_end_time'], 'The growing season is not active, so you cannot interact with your plant.'
    # if ctx.caller.startswith('con_'): return "It's over!" #maybe go back and add whitelistable contracts here?
    plant_name = collection_nfts[name]
    plant_data = plant_name['nft_metadata']
    assert plant_data["alive"] == True, 'Your plant is dead due to neglect and you must buy a new plant to try again. Try not to kill it too.'

    #interaction idle check. If idle too long, plant gets penalized.
    if now > plant_data['last_interaction'] + datetime.timedelta(hours = 12):
        plant_data["current_water"] -= (random.randint(1, 10))/100
        plant_data["current_bugs"] += (random.randint(1, 10))/100
        plant_data["current_nutrients"] -= (random.randint(1, 10))/100
        plant_data["current_weeds"] += (random.randint(1, 10))/100

    plant_data = daily_conditions(plant_data)

    #NEED TO ADD CHECKS FOR IF WATER AND NUTRIENTS ARE TOO HIGH

    plant_data = totalizer_calc(plant_data,name)

    plant_data = dead_check(plant_data)

    plant_data['last_interaction'] = now #resets the interaction time

    plant_all = {
        'plant_name' : plant_name,
        'plant_data' : plant_data,
        'name' : name
    }

    return plant_all

def daily_conditions(plant_data):
    while now - plant_data["last_daily"] > datetime.timedelta(days = 1): #Loops through to calculate changes to plant if it's been more than a day since the last day's changes. Does multiple days worth too if needed
        current_weather = random.randint(1, 3) # 1=sunny 2=cloudy 3=rainy
        if current_weather == 1:
            plant_data["current_water"] -= (random.randint(15, 25))/100 #how much water is lost each sunny day
            plant_data["current_photosynthesis"] += (random.randint(4, 6))/100 #How much photosynthesis increases each sunny day
        if current_weather == 2:
            plant_data["current_water"] -= (random.randint(5, 15))/100 #how much water is lost each cloudy day
            plant_data["current_photosynthesis"] += (random.randint(2, 4))/100 #How much photosynthesis increases each cloudy day
        if current_weather == 3:
            plant_data["current_water"] += (random.randint(5, 40))/100 #how much water is gained each rainy day
            plant_data["current_photosynthesis"] += (random.randint(1, 2))/100 #How much photosynthesis increases each rainy day

        plant_data["current_bugs"] += (random.randint(3, 15))/100 #how many bugs are added each day
        plant_data["current_nutrients"] -= (random.randint(5, 10))/100 #how many nutrients are consumed each day
        plant_data["current_weeds"] += (random.randint(3, 15))/100 #how many weeds grow each day
        plant_data["last_daily"] += datetime.timedelta(days = 1)
        plant_data["current_weather"] = current_weather
        plant_data['current_toxicity'] -= (random.randint(0, 2))/100

        if plant_data['current_water'] > 1 :
            plant_data['current_water'] = 1

    return plant_data

def totalizer_calc(plant_data,name):
    if now > plant_data['last_calc'] + datetime.timedelta(hours = 3):
        delta = now - plant_data['last_calc']
        delta_d = (delta.seconds / 86400)

        plant_calc_data = collection_nfts[name,'plant_calc_data']

        plant_calc_data["total_water"] += (delta_d**2*((plant_data["current_water"]-plant_calc_data["previous_water"])/(delta_d))/2)+plant_calc_data["previous_water"]*delta_d
        plant_calc_data["total_bugs"] += (delta_d**2*(((1-plant_data["current_bugs"])-(1-plant_calc_data["previous_bugs"]))/(delta_d))/2)+(1-plant_calc_data["previous_bugs"])*delta_d
        plant_calc_data["total_photosynthesis"] += (delta_d**2*((plant_data["current_photosynthesis"]-plant_calc_data["previous_photosynthesis"])/(delta_d))/2)+plant_calc_data["previous_photosynthesis"]*delta_d
        plant_calc_data["total_nutrients"] += (delta_d**2*((plant_data["current_nutrients"]-plant_calc_data["previous_nutrients"])/(delta_d))/2)+plant_calc_data["previous_nutrients"]*delta_d
        plant_calc_data["total_weeds"] += (delta_d**2*(((1-plant_data["current_weeds"])-(1-plant_calc_data["previous_weeds"]))/(delta_d))/2)+(1-plant_calc_data["previous_weeds"])*delta_d

        collection_nfts[name,'plant_calc_data'] = plant_calc_data
        plant_data['last_calc'] = now

    return plant_data

def dead_check(plant_data):
    if plant_data["current_toxicity"] >= 1 or plant_data["current_bugs"] >= 1 or plant_data["current_weeds"] >= 1:
        plant_data["alive"] = False

    if plant_data["current_water"] <= 0 or plant_data["current_nutrients"] <= 0:
        plant_data["alive"] = False

    return plant_data

@export
def water(plant_generation : int, plant_number : int, num_times : int):
    plant_all = action_setup(plant_generation,plant_number)
    plant_data = plant_all['plant_data']
    plant_name = plant_all['plant_name']
    name = plant_all['name']

    for x in range(0, num_times):
        plant_data['current_water'] += (random.randint(5, 15))/100
    if plant_data['current_water'] > 1 :
        plant_data['current_water'] = 1

    plant_name['nft_metadata'] = plant_data
    collection_nfts[name] = plant_name

@export
def squash_bugs(plant_generation : int, plant_number : int):
    plant_all = action_setup(plant_generation,plant_number)
    plant_data = plant_all['plant_data']
    plant_name = plant_all['plant_name']
    name = plant_all['name']

    t_delta = plant_data["last_squash_weed"] + datetime.timedelta(minutes = 5)
    assert now > t_delta, f"You are still squashing bugs. Try again at {t_delta}."

    plant_data['current_bugs'] -= (random.randint(2, 5))/100
    if plant_data['current_bugs'] < 0 :
        plant_data['current_bugs'] = 0

    plant_data["last_squash_weed"] = now
    plant_name['nft_metadata'] = plant_data
    collection_nfts[name] = plant_name

@export
def spray_bugs(plant_generation : int, plant_number : int):
    plant_all = action_setup(plant_generation,plant_number)
    plant_data = plant_all['plant_data']
    plant_name = plant_all['plant_name']
    name = plant_all['name']

    plant_data['current_toxicity'] += (random.randint(1, 3))/100

    plant_data['current_bugs'] -= (random.randint(10, 20))/100
    if plant_data['current_bugs'] < 0 :
        plant_data['current_bugs'] = 0

    payment(plant_generation, 5)
    plant_name['nft_metadata'] = plant_data
    collection_nfts[name] = plant_name

@export
def grow_lights(plant_generation : int, plant_number : int):
    plant_all = action_setup(plant_generation,plant_number)
    plant_data = plant_all['plant_data']
    plant_name = plant_all['plant_name']
    name = plant_all['name']

    t_delta = plant_data["last_grow_light"] + datetime.timedelta(days = 1)
    assert now > t_delta, f"You have used a grow light too recently. Try again at {t_delta}."

    payment(plant_generation, 5)
    plant_data['current_photosynthesis'] += (random.randint(3, 5))/100
    plant_data["last_grow_light"] = now

    plant_name['nft_metadata'] = plant_data
    collection_nfts[name] = plant_name

@export
def fertilize(plant_generation : int, plant_number : int, num_times : int):
    plant_all = action_setup(plant_generation,plant_number)
    plant_data = plant_all['plant_data']
    plant_name = plant_all['plant_name']
    name = plant_all['name']

    payment(plant_generation, 2*num_times)
    for x in range(0, num_times):
        plant_data['current_nutrients'] += (random.randint(3, 5))/100

    if plant_data['current_nutrients'] > 1 :
        plant_data['current_nutrients'] = 1

    plant_name['nft_metadata'] = plant_data
    collection_nfts[name] = plant_name

@export
def pull_weeds(plant_generation : int, plant_number : int):

    plant_all = action_setup(plant_generation,plant_number)
    plant_data = plant_all['plant_data']
    plant_name = plant_all['plant_name']
    name = plant_all['name']

    t_delta = plant_data["last_squash_weed"] + datetime.timedelta(minutes = 5)
    assert now > t_delta, f"You are still squashing bugs or pulling weeds. Try again at {t_delta}."

    plant_data['current_weeds'] -= (random.randint(2, 5))/100
    if plant_data['current_weeds'] < 0 :
        plant_data['current_weeds'] = 0

    plant_data["last_squash_weed"] = now
    plant_name['nft_metadata'] = plant_data
    collection_nfts[name] = plant_name

@export
def spray_weeds(plant_generation : int, plant_number : int):
    plant_all = action_setup(plant_generation,plant_number)
    plant_data = plant_all['plant_data']
    plant_name = plant_all['plant_name']
    name = plant_all['name']

    plant_data['current_toxicity'] += (random.randint(1, 3))/100

    plant_data['current_weeds'] -= (random.randint(10, 20))/100
    if plant_data['current_weeds'] < 0 :
        plant_data['current_weeds'] = 0

    plant_name['nft_metadata'] = plant_data
    collection_nfts[name] = plant_name

@export
def finalize_plant(plant_generation : int, plant_number : int):
    assert plant_generation == active_generation, f'The plant you are trying to interact with is not part of the current generation. The current generation is {active_generation}.'
    name = f'Gen_{plant_generation}_{plant_number}'
    assert collection_balances[ctx.caller, name] == 1, "You do not own this plant."
    assert collection_nfts[name,'finalized'] == False, 'This plant has already been finalized.'
    end_time = plants['growing_season_end_time']
    assert now <= plants['finalize_time'] and now >= end_time, 'It is not time to finalize your plant.'
    # if ctx.caller.startswith('con_'): return "It's over!" #maybe go back and add whitelistable contracts here?
    plant_name = collection_nfts[name]
    plant_data = plant_name['nft_metadata']
    assert plant_data["alive"] == True, 'Your plant is dead due to neglect and you must buy a new plant to try again. Try not to kill it too.'

    delta = end_time - plant_data['last_calc']
    delta_d = (delta.seconds / 86400)

    plant_calc_data = collection_nfts[name,'plant_calc_data']

    plant_calc_data["total_water"] += (delta_d**2*((plant_calc_data["current_water"]-plant_calc_data["previous_water"])/(delta_d))/2)+plant_calc_data["previous_water"]*delta_d
    plant_calc_data["total_bugs"] += (delta_d**2*(((1-plant_calc_data["current_bugs"])-(1-plant_calc_data["previous_bugs"]))/(delta_d))/2)+(1-plant_calc_data["previous_bugs"])*delta_d
    plant_calc_data["total_photosynthesis"] += (delta_d**2*((plant_calc_data["current_photosynthesis"]-plant_calc_data["previous_photosynthesis"])/(delta_d))/2)+plant_calc_data["previous_photosynthesis"]*delta_d
    plant_calc_data["total_nutrients"] += (delta_d**2*((plant_calc_data["current_nutrients"]-plant_calc_data["previous_nutrients"])/(delta_d))/2)+plant_calc_data["previous_nutrients"]*delta_d
    plant_calc_data["total_weeds"] += (delta_d**2*(((1-plant_calc_data["current_weeds"])-(1-plant_calc_data["previous_weeds"]))/(delta_d))/2)+(1-plant_calc_data["previous_weeds"])*delta_d

    collection_nfts[name,'plant_calc_data'] = plant_calc_data

    plant_data['last_calc'] = now
    plant_name['nft_metadata'] = plant_data
    collection_nfts[name] = plant_name

    length = metadata['growing_season_length']
    berries = int(((plant_calc_data["total_water"]*plant_calc_data["total_bugs"]*plant_calc_data["total_photosynthesis"]*plant_calc_data["total_nutrients"]*plant_calc_data["total_weeds"])/(length**5))*(1-plant_data['current_toxicity']))
    collection_nfts[name,'berries'] = berries
    collection_nfts[name,'final_score'] = berries
    plants[plant_generation,'total_berries'] += berries
    collection_nfts[name,'finalized'] == True

def sell_berries(plant_generation : int, plant_number : int):
    name = f'Gen_{plant_generation}_{plant_number}'
    assert collection_balances[ctx.caller, name] == 1, "You do not own this plant."
    berries = collection_nfts[name,'berries']
    assert berries > 0, "You don't have any berries to sell."
    assert now >= plants['finalize_time'], f"You can't sell yet. Try again after {plants['finalize_time']} but do not wait too long."
    sell_price = plants[plant_generation, 'total_tau'] / plants[plant_generation,'total_berries']
    proceeds = sell_price * berries
    currency.transfer(amount=proceeds, to=ctx.caller)
    collection_nfts[name,'berries'] = 0
    plants[plant_generation, 'total_tau']  -= proceeds

def payment(plant_generation, amount): #used to process payments
    currency.transfer_from(amount=amount*0.95, to=ctx.this, main_account=ctx.caller)
    currency.transfer_from(amount=amount*0.05, to=metadata['operator'], main_account=ctx.caller)
    plants[plant_generation, 'total_tau'] += amount

@export
def manual_reward_add(plant_generation : int, amount : int):
    currency.transfer_from(amount=amount, to=ctx.this, main_account=ctx.caller)
    plants[plant_generation, 'total_tau'] += amount

@export
def stale_claims(plant_generation : int):
    assert metadata['operator'] == ctx.caller, "Only the operator can claim stale tau."
    assert now >= plants[plant_generation,'stale_claim_time'], "The tau is not stale yet and cannot be claimed."
    stale_tau = plants[plant_generation, 'total_tau']
    assert stale_tau > 0, "There is no stale tau to claim."
    currency.transfer(amount=stale_tau, to=ctx.caller)

@export
def emergency_withdraw():
    #add ability to withdraw tau from contract by operator only
