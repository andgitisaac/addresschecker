from src.addresschecker import AddressChecker

# Top-K candidates that will be returned
TOP_K = 5

# Pretend that there's a query database. After collecting 
# sufficient queries, perform the incremental training.
TIME_FOR_TRAINING = 5
history_queries = []

# history_queries = [
#     'Suzzallo and Allen Libraries',
#     'Sylvan Grove Theater and Columns',
#     'Odegaard Undergraduate Library',
#     '3800 Montlake Blvd NE, Seattle, WA 98195',
#     'Alleyway, 4214 University Way NE, Seattle, WA 98105'
# ]

# Initialize the Address Checker instance
address_checker = AddressChecker()

# Prettify the stdout
def pretty_print(data):
    for k, v in data:
        print("{:<10} => {}".format(k, " ".join(v)))

while True:
    query = input("Input Query: ")
    if not query: break


    outputs = address_checker.corrections(query, k=TOP_K)    
    pretty_print(outputs)


    history_queries.append(query)
    if len(history_queries) == TIME_FOR_TRAINING:
        # TODO: Incremental Training
        print("==================")
        print("  Updating Model  ")
        print(address_checker._word_frequency)

        address_checker._word_frequency.load_sentence(history_queries)

        print(address_checker._word_frequency)
        print("==================")


        # Reset the DB for the next batch of queries.
        history_queries = []

