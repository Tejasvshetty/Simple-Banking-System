import random
import sqlite3

#********************************************************************#
# Section for creating database
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS card
            (id INTEGER,
            number TEXT,
            pin TEXT,
            balance INTEGER)
""")
conn.commit()


#********************************************************************#
class Card:
    all_cards = []
    def __init__(self):
        self.account_id = random.randint(100000000,999999999) #Random ID generation for 9 digits
        self.balance = 0 #Balance of a new card is 0
        luhn_total = 0 #Beginning tally for luhn's algorithmic sum
        count = 1

        for i in ('400000'+str(self.account_id)): #Arthmetic for luhns algo
            if(count % 2 != 0):
                i = int(i)*2
            if(int(i)>9):
                i = int(i)-9
            luhn_total += int (i)
            count += 1

        luhn_remain = luhn_total % 10 #Checking to see what needs to be added to fulfill luhns algo condition, ie. divisible by 10
        
        if (luhn_remain != 0): #checking to see if (luhn_sum) is already divisible by 10
            self.checksum = 10-luhn_remain
        else:
            self.checksum = 0
        
        self.number = int('400000'+str(self.account_id)+str(self.checksum)) #concatenation of all numbers
        self.pin = random.randint(1000,9999)
        Card.all_cards.append(self)
        cur.execute("""INSERT INTO card (id, number, pin, balance) 
        VALUES (?, ?, ?, ?)""",(self.account_id, self.number, self.pin, self.balance)) #adding card to database
        conn.commit() #commiting change to memory

def update_balance(amount, account_id):
    card_balance = (cur.execute("SELECT balance FROM card WHERE number = ?",(account_id,))).fetchone()
    card_update = int(card_balance[0]) + int(amount)
    # print(card_update)
    cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?",(amount,account_id))
    # print(account_id)
    conn.commit()
    # print((cur.execute("SELECT balance FROM card WHERE number = ?",(account_id,))).fetchall())
    conn.commit()
#********************************************************************#

login = True

while (login):
    login2 = True
    print ("1. Create an account")
    print ("2. Log into account")
    print ("0. Exit")
    entry = int(input())
    if (entry == 1):
        blank_card = Card()
        print ("Your card has been created")
        print ("Your card number:")
        print (blank_card.number)
        print ("Your card PIN:")
        print (blank_card.pin)
        
    elif (entry == 2):
        print ("Enter your card number")
        entry_number = int(input())
        print ("Enter your pin")
        entry_pin = int(input())
        card_cred = ((cur.execute("SELECT EXISTS(SELECT * FROM card WHERE number = (?) AND pin = (?))",(entry_number, entry_pin))).fetchone())[0]
        if (card_cred != 0):
            print(card_cred)
            print("")
            print("You have successfully logged in!")
            while (login2):
                print("")
                print("1. Balance")
                print("2. Add Income")
                print("3. Do transfer")
                print("4. Close account")
                print("5. Log out")
                print("0. Exit")
                entry = int(input())
                if (entry == 1):
                    card_balance = (cur.execute("SELECT balance FROM card WHERE number = (?) AND pin = (?)",(entry_number, entry_pin))).fetchone()
                    print ("Balance " + str(card_balance[0]))
                elif (entry == 2):
                    income = int(input("Enter Income\n"))
                    update_balance(income, entry_number)
                    print("Income was added!")
                elif (entry == 3):
                    print("Transfer")
                    print("Enter card number:")
                    transfer_card = int(input())
                    #lets check for error in card
                    transfer_card_cred = ((cur.execute("SELECT EXISTS(SELECT * FROM card WHERE number = ?)",(transfer_card,))).fetchone())[0]
                    if(transfer_card_cred == 0):
                        count = 1
                        luhn_total = 0
                        for i in (str(transfer_card)): #Arthmetic for luhns algo
                            if(count % 2 != 0):
                                i = int(i)*2
                            if(int(i)>9):
                                i = int(i)-9
                            luhn_total += int(i)
                            count += 1
                        print(luhn_total)
                        if (luhn_total%10==0):
                            print("Such a card does not exist.")
                        else:
                            print("Probably you made a mistake in the card number. Please try again!")
                    elif(transfer_card == entry_number):
                        print("You can't transfer money to the same account!")
                    elif(transfer_card_cred != 0):
                        print("Enter how much money you want to transfer:")
                        transfer_amount = int(input())

                        card_balance = (cur.execute("SELECT balance FROM card WHERE number = (?) AND pin = (?)",(entry_number, entry_pin))).fetchone()
                        if (card_balance[0]>transfer_amount):
                            #deducting from this card
                            update_balance((-transfer_amount), entry_number)
                            #adding to this card
                            update_balance(transfer_amount, transfer_card)
                            print("Sucess!")
                        else:
                            print("Not enough money!")
                elif (entry == 4):
                    cur.execute("DELETE from card WHERE number = ?",(entry_number,))
                    conn.commit()
                    print ("The account has been closed!")
                elif (entry == 5):
                    login2 = False
                    print ("You have successfully logged out!")
                elif (entry == 0):
                    login2 = False
                    login = False
                    print("Bye")
        else:
            print("Wrong card number or PIN!")

    elif (entry == 0):
        login = False
        print("Bye!")
conn.close()

#********************************************************************#
