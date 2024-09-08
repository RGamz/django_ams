from faker import Faker
Faker.seed(0)

fake = Faker()

# store
for _ in range(5):
    print(fake.bothify(text='Bricomarche ##'))

# ticket id
for _ in range(5):
    print(fake.bothify(text='5####'))

# station
for _ in range(5):
    print('Station ' + fake.last_name())

# admin
for _ in range(5):
    print(fake.first_name())