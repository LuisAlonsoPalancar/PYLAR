#   is represented by a dictionary.
users = [
{
    'last': 'fermi',
    'first': 'enrico',
    'username': 'efermi',
},
{
    'last': 'curie',
    'first': 'marie',
    'username': 'mcurie',
},
]
# Show all information about each user.
print("User summary:")
for user_dict in users:
    for k  in user_dict.items():
     print(f"{k}")
    print("\n")
