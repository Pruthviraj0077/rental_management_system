import mysql.connector
from  datetime import date

class rental:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "admin123",
            database = "rental_system"
        )

        if self.connection.is_connected():
            print("connected to mysql server")

        self.cursor = self.connection.cursor()
        # self.cursor.execute("show tables;")
        # results = self.cursor.fetchall()
        # for row in results:
        #     print(row)
        
        while True:
            print("*********Welcome rental management system ************")
            print("1.Tenants\n2.payments\n3.exit")
            choice = int(input("Enter your choice:- "))
            if choice == 1:
                self.add_tenants()
            elif choice == 2:
                self.payment()
            elif choice == 3:
                    break
            else:
                print("invalid choice try again")


    def add_tenants(self):
        while True:
            print("1.add tenant\n2.list tenant\n3.remove tenant\n4.exit")
            choice = int(input("Enter your choice:- "))
            if choice == 1:
                name = input("enter your name:- ")
                address = input("enter your address:- ")
                contact_number = int(input("enter your contact_number:- "))
                sql = "INSERT INTO tenants (name, address, contact_number) VALUES(%s,%s,%s)"
                values =  (name, address, contact_number)
                self.cursor.execute(sql,values)
                self.connection.commit()
                print(self.cursor.rowcount, "record inserted.")
            elif choice == 2:
                self.cursor.execute("SELECT * FROM tenants")
                results = self.cursor.fetchall()
                print(results)
            elif choice == 3:
                id = int(input("enter tenant_id to remove tenant :- "))
                sql = "DELETE FROM tenants WHERE id = %s"
                values = (id,)
                self.cursor.execute(sql,values)
                self.connection.commit()
                print(self.cursor.rowcount, "record(s) deleted.")
            elif choice == 4:
                break
            else:
                print("invalid choice try again")

    # add_tenants()

    def payment(self):
        while True:
            print("1.add_paymetn\n2.list_payments\n3.exit")
            choice = int(input("Enter your choice:- "))
            if choice == 1:
                tenant_id = int(input("Enter tenant ID: "))
                rent = float(input("Enter monthly rent amount: "))
                amount_paid = float(input("Enter amount paid by tenant: "))
                payment_date = date.today()

                # --- Get previous balance (advance or pending)
                self.cursor.execute(
                    "SELECT COALESCE(SUM(balance_change), 0) FROM payments WHERE tenant_id = %s",
                    (tenant_id,)
                )
                prev_balance = float(self.cursor.fetchone()[0] or 0.0)
                print(f"\nPrevious balance for Tenant {tenant_id}: ₹{prev_balance:.2f} "
                      "(positive = advance, negative = owes)")

                # --- Calculate this payment’s impact ---
                balance_change = round(amount_paid - rent, 2)
                new_balance = round(prev_balance + balance_change, 2)

                # --- Determine status and derived fields ---
                if new_balance < 0:
                    pending_amount = abs(new_balance)
                    advance_amount = 0.0
                    status = "pending"
                elif new_balance == 0:
                    pending_amount = 0.0
                    advance_amount = 0.0
                    status = "completed"
                else:
                    pending_amount = 0.0
                    advance_amount = new_balance
                    status = "advance"

                # --- Insert transaction into DB ---
                sql = """
                INSERT INTO payments
                  (tenant_id, rent, amount_paid, payment_date, status, balance_change, pending_amount, advance_amount)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """
                values = (tenant_id, rent, amount_paid, payment_date,status, balance_change, pending_amount, advance_amount)

                self.cursor.execute(sql, values)
                self.connection.commit()

                print(f"\n✅ Payment recorded successfully!")
                print(f"   ➤ balance_change: {balance_change}")
                print(f"   ➤ new_balance: {new_balance}")
                print(f"   ➤ status: {status}")
            elif choice == 2:
                self.cursor.execute("SELECT * FROM payments")
                results = self.cursor.fetchall()
                print(results)
            elif choice == 3:
                break
            else:
                print("invalid choice try again")

    # payment()
                    
            
if __name__ == '__main__':
    rental_instance = rental()
    
    
        


