def build_beer_record(location, name, style=None, brewery=None, city=None):
    beer = {
        'location': location,
        'name': name,
        'style': style,
        'brewery': brewery,
        'city': city
    }
    
    return prettify(beer)

def prettify(beer):
    if 'style' in beer:
        capitals = ['Imperial', 'IPA', 'Russian', 'Scottish', 'Scotch', 'Cascadian', 'Belgian', 'German', 'American', 'British', 'Munich', 'Flanders', 'Christmas', 'Double', 'Triple']
        for item in capitals:
            if item.lower() in beer['style']:
                beer['style'] = beer['style'].replace(item.lower(), item)

        hyphenated = ['barrel-aged']
        for item in hyphenated:
            unhyphenated = item.replace('-', ' ')
            if unhyphenated in beer['style']:
                beer['style'] = beer['style'].replace(unhyphenated, item)

    return beer
