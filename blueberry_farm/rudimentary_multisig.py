import currency
emergency = Hash()
metadata = Hash()

@construct
def seed():
    emergency['addresses'] = {
        'address1here' : 0,
        'address2here' : 0,
        'address3here' : 0
    }

    metadata['operator'] = ctx.caller

@export
def e_wdraw_enable(enable:bool):
    emergency_addresses = emergency['addresses']
    call_address = ctx.caller
    assert call_address in emergency_addresses.keys(), "You are not approved to do this."
    emergency_addresses[call_address] = int(enable)
    emergency['addresses'] = emergency_addresses

@export
def safe_emergency_withdraw(amount:float): #can only be run if at least 2 of 3 multisig accounts approve of the emergency_withdraw
    emergency_addresses = emergency['addresses']
    call_address = ctx.caller
    approval_check = sum(emergency_addresses.values())
    assert approval_check >= 2, "An emergency withdrawal is not approved."
    assert metadata['operator'] == call_address, "Only the operator can claim tau."
    currency.transfer(amount=amount, to=call_address)
