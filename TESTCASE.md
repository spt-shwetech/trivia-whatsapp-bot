Test Case

For Host
#create groupname
#init_balance 100 groupname
#game 80 72 groupname
#start groupname

For Member and in group
#register
#stake tiger 100
#check

For Host
#end groupname
#yes


#phoneno and password
credentials = dict(
    phone = '959403948633',
    password = 'ZsE7gjJ34055GI1RgGeWCownQDw=',
)

# Your contacts numbers (Framework will sync)
# Add them here
contacts = {
    "CONTACT_PHONE": "CONTACT_NAME",
    "ANOTHER_CONTACT_PHONE": "ANOTHER_CONTACT_NAME",
}
