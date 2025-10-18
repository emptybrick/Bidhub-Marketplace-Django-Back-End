import enum

class Item_Categories(enum.Enum):
    ELECTRONICS = 'Electronics'
    COMPUTERS = 'Computers & Accessories'
    CLOTHING = 'Clothing, Shoes & Jewelry'
    HOME = 'Home & Kitchen'
    BOOKS = 'Books'
    TOYS = 'Toys & Games'
    BEAUTY = 'Beauty & Personal Care'
    SPORTS = 'Sports & Outdoors'
    AUTOMOTIVE = 'Automotive'
    TOOLS = 'Tools & Home Improvement'
    HEALTH = 'Health & Household'
    CELLPHONES = 'Cell Phones & Accessories'
    PETS = 'Pet Supplies'
    VIDEO_GAMES = 'Video Games'
    OFFICE = 'Office Products'
    GARDEN = 'Patio, Lawn & Garden'
    MUSIC = 'Musical Instruments'
    COLLECTIBLES = 'Collectibles & Fine Art'
    MISCELLANEOUS = 'Miscellaneous'

    @classmethod
    def choices(cls):
        return [(key.name, key.value) for key in cls]
    
    
