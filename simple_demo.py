from src.addresschecker import AddressChecker

# Top-K candidates that will be returned
TOP_K = 5

# Pretend that there's a query database. After collecting 
# sufficient queries, perform the incremental training.
TIME_FOR_TRAINING = 5
history_queries = []

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
        print("==================")

        # Reset the DB for the next batch of queries.
        history_queries = []

