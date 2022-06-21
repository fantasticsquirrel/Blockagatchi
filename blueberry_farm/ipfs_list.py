random.seed()
ipfs = Hash()
metadata  = Hash()


@construct
def seed():
    metadata['operator'] = ctx.caller
    metadata['contract'] = 'con_bbf_001'

    ipfs['list'] = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40']

    ipfs['1'] = 'https://ipfs.io/ipfs/Qmf4PyfeVA5Vg6TAoQMB4gXPwiexVW8vZzdjF5i2GpakAP?filename=01.png'
    ipfs['2'] = 'https://ipfs.io/ipfs/Qmf2dcCJEM6Wub7c44mdNVzXWm6rozBwXRH85pqsYsYzmg?filename=02.png'
    ipfs['3'] = 'https://ipfs.io/ipfs/QmdQabFxHnYCNCuwhaun15s1T4VyaMZ6JU9H8bo7xc8noF?filename=03.png'
    ipfs['4'] = 'https://ipfs.io/ipfs/QmQzw83Kf6g7YiWarTYzv4oYP6NJk7TBawE46uKNrryPYi?filename=04.png'
    ipfs['5'] = 'https://ipfs.io/ipfs/QmP7GMEXDMbrLGvBWmGDNBZYgejKhNTe6dgKKxbayysVRb?filename=05.png'
    ipfs['6'] = 'https://ipfs.io/ipfs/QmUa2iy7ueoZhqmZ227bs5vjffeTRRjW5xubvuMUN8Vs51?filename=06.png'
    ipfs['7'] = 'https://ipfs.io/ipfs/QmYc2KnaZFnTWp1zhjKsQACR5EwSSGn3pgA7xBvXJbnE9v?filename=07.png'
    ipfs['8'] = 'https://ipfs.io/ipfs/QmddmaFb5uzpEYXicxxcYV7yqPhqADSDee2MD9JQ91WuMX?filename=08.png'
    ipfs['9'] = 'https://ipfs.io/ipfs/QmYmaHk87mLAGMCTTyUDrBV7ews9od4KAmBGruBtgmPhnD?filename=09.png'
    ipfs['10'] = 'https://ipfs.io/ipfs/QmTvYECXqXxUbbWHsKZTPdK2gR4Zg5FQvzFDUcXVLmLc2J?filename=10.png'
    ipfs['11'] = 'https://ipfs.io/ipfs/QmZKhZ7My9yZ4uPm8J42Trp1WfMZjTBFgUJ76ZiLdrwh2z?filename=11.png'
    ipfs['12'] = 'https://ipfs.io/ipfs/QmVWNqEbaCXBaDzhewS3c3Xf1ABWTHmFpyexNk9HKDUcZM?filename=12.png'
    ipfs['13'] = 'https://ipfs.io/ipfs/QmVWZ4vGQfMpehhA8xUUBqMSXGgC1M63g7EFy8VERCQjGG?filename=13.png'
    ipfs['14'] = 'https://ipfs.io/ipfs/QmWANtyyRcZ6Dd4Txe5LpkgN77FDsps4YDC2XhZVJUsZ5R?filename=14.png'
    ipfs['15'] = 'https://ipfs.io/ipfs/QmbeLYfzzfMchUnysGZgTvwL1QUpAKnCJHxA7VUCYu8HR7?filename=15.png'
    ipfs['16'] = 'https://ipfs.io/ipfs/QmdPejekudMwKbru9kUFf8zBfBDVknFdG5rc1gAdU15xFx?filename=16.png'
    ipfs['17'] = 'https://ipfs.io/ipfs/QmTfxmWrusMSwvdqCJiHiwJVjUkFtCNaEU3QS3JVgdzgo5?filename=17.png'
    ipfs['18'] = 'https://ipfs.io/ipfs/QmbB7wjqf9hv4RFDsPbjGYkGZDFipKN5wohHQpFrxBBkrm?filename=18.png'
    ipfs['19'] = 'https://ipfs.io/ipfs/QmXD5ExD4aBNYZpn3ts4pZ9EJ1nApiVypJBpJa7SEzMgPR?filename=19.png'
    ipfs['20'] = 'https://ipfs.io/ipfs/QmW8S5JddRvxoajw6Tg8vRLazPezeLqUjJ3QrVpLvsT9KW?filename=20.png'
    ipfs['21'] = 'https://ipfs.io/ipfs/Qmc7jsom4jph9ovmW9DMsQWDFTK66CyjtvoRnkZv99EQ5R?filename=21.png'
    ipfs['22'] = 'https://ipfs.io/ipfs/Qmb2hzmURTshe4azQdVnAX5zP8ZbejnYWdsqUe7u3Fm8gL?filename=22.png'
    ipfs['23'] = 'https://ipfs.io/ipfs/Qmbh5HdUpiG5cu3Ffm2tVisFc35Xhx7tiJA9dWve7yXTHL?filename=23.png'
    ipfs['24'] = 'https://ipfs.io/ipfs/QmdHjdwMZG5AMCqsFnzzBMi9KRjLCsEtpAVFUXGU2EiniZ?filename=24.png'
    ipfs['25'] = 'https://ipfs.io/ipfs/Qmc616fGM8mRNzK6HHUwXLwsXUh6hQghzW6gZnQWPHam9U?filename=25.png'
    ipfs['26'] = 'https://ipfs.io/ipfs/QmYSUMo7ngU6Rg2bm3Xc1Bb3QwoXNyUKk35qAdXUew9wGK?filename=26.png'
    ipfs['27'] = 'https://ipfs.io/ipfs/QmUUR27765ThJ7Gd9w1MvV95XQLrxehwxmxkSz3LwS6QCX?filename=27.png'
    ipfs['28'] = 'https://ipfs.io/ipfs/QmT2Aef9jqjdXHSMafLccXvNgvk4dX9qB78qYpyk2dsuJx?filename=28.png'
    ipfs['29'] = 'https://ipfs.io/ipfs/QmPxLdCP9TBqoiaVnqTPwwfUXLse3Uta3Uvc5WXAueLsLJ?filename=29.png'
    ipfs['30'] = 'https://ipfs.io/ipfs/QmXEAwignZjES9GUN1skFRS7txPXMgezSPUuP2B2mLyvZF?filename=30.png'
    ipfs['31'] = 'https://ipfs.io/ipfs/QmW8Kea6MeSog2TjXer3EGScvQuViZXhpy4mYWqN9TNhDf?filename=31.png'
    ipfs['32'] = 'https://ipfs.io/ipfs/QmZ4Ns7VzL5wV82ZuWHLfZsE92woWU6c7JrVdvh4mpZ9ko?filename=32.png'
    ipfs['33'] = 'https://ipfs.io/ipfs/QmP9KgYEZtC3FRDzH3WuEKzZJMRBBm1ZHfFagnJLL4SCov?filename=33.png'
    ipfs['34'] = 'https://ipfs.io/ipfs/QmZUdhvW6UCAjvb4W6R56k7U46DMuHKrga3krbc6Xuuna1?filename=34.png'
    ipfs['35'] = 'https://ipfs.io/ipfs/QmTXXJELaoeJNmiPxyeubb9PB865WSrv6bwDUQzZLU6XvH?filename=35.png'
    ipfs['36'] = 'https://ipfs.io/ipfs/QmWKvLiL5c5kUPZbwHBzJLGNr7SS4YyNQjQHfrMYSM3C7V?filename=36.png'
    ipfs['37'] = 'https://ipfs.io/ipfs/QmTNLLGZZ1XFxErSQLma3dk1RheyuKad8SpFWAcoJ3YDi1?filename=37.png'
    ipfs['38'] = 'https://ipfs.io/ipfs/QmfS1rHGvpMYTYh3hrPEfduWpjwCkwY13FY3zFj1xtV9Q8?filename=38.png'
    ipfs['39'] = 'https://ipfs.io/ipfs/QmTr6cDQAJW5f8AymgEERCuHCvmV9D9Y5nuwdBimkWgLPL?filename=39.png'
    ipfs['40'] = 'https://ipfs.io/ipfs/QmZuKo9FUg6AmBHJTCnHM8gCJj1F3WfQbURes7ofGTuX7U?filename=40.png'
    ipfs['generic'] = 'https://ipfs.io/ipfs/QmRSDPJ8F85jQp9VC6XAUpvc1tfQo3apjPGYoJq9gqLVkQ?filename=Generic.png'

@export
def change_metadata(key: str, new_value: str):
    assert ctx.caller == metadata['operator'], "only operator can set metadata"
    metadata[key] = new_value

@export
def pick_random():
    assert ctx.caller == metadata['contract'], 'You are not allowed.'
    pics = ipfs['list']
    if pics:
        r_choice = random.choice(pics)
        pics.remove(r_choice)
        pic_choice = ipfs[r_choice]
        ipfs['list'] = (pics)
    else:
        pic_choice = (ipfs['generic'])

    return pic_choice
