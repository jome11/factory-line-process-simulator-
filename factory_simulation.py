import simpy
import random
import time
import numpy as np
import matplotlib.pyplot as plt

# --- Simulation Parameters ---
RANDOM_SEED = 42
# TARGET_ORDERS_COUNT = 0 # User-defined number of orders to process - REPLACED
TARGET_BOTTLES_TO_PRODUCE = 0 # User-defined number of bottles to produce
BOTTLES_PER_ORDER = 1000 # Number of bottles produced per processed order/batch

NUM_MIXING_STATIONS = 1
NUM_FILLING_LINES = 2
NUM_CAPPING_MACHINES = 2
NUM_LABELING_MACHINES = 2
NUM_PACKAGING_STATIONS = 1

DRINK_ORDER_INTERARRIVAL_TIME_MEAN = 15 # Mean time between new drink orders (minutes)

# Processing times (mean, std dev) in minutes per batch/order
PROCESSING_TIME_MIXING_MEAN = 10
PROCESSING_TIME_MIXING_STD = 2
PROCESSING_TIME_FILLING_MEAN = 8
PROCESSING_TIME_FILLING_STD = 1
PROCESSING_TIME_CAPPING_MEAN = 5
PROCESSING_TIME_CAPPING_STD = 0.5
PROCESSING_TIME_LABELING_MEAN = 4
PROCESSING_TIME_LABELING_STD = 0.5
PROCESSING_TIME_PACKAGING_MEAN = 12
PROCESSING_TIME_PACKAGING_STD = 2


# --- Data Collection ---
order_arrival_times = []
order_departure_times = []
wait_times_mixing = []
wait_times_filling = []
wait_times_capping = []
wait_times_labeling = []
wait_times_packaging = []

orders_processed_mixing = 0
orders_processed_filling = 0
orders_processed_capping = 0
orders_processed_labeling = 0
orders_processed_packaging = 0 # Counts completed orders/batches
total_bottles_produced_count = 0 # Counts total bottles from completed orders

# To store the factory instance for end-of-simulation resource state reporting
factory_instance = None 

class SoftDrinkFactory:
    """
    Represents the soft drink factory environment with production stages.
    """
    def __init__(self, env):
        self.env = env
        self.mixing_stations = simpy.Resource(env, capacity=NUM_MIXING_STATIONS)
        self.filling_lines = simpy.Resource(env, capacity=NUM_FILLING_LINES)
        self.capping_machines = simpy.Resource(env, capacity=NUM_CAPPING_MACHINES)
        self.labeling_machines = simpy.Resource(env, capacity=NUM_LABELING_MACHINES)
        self.packaging_stations = simpy.Resource(env, capacity=NUM_PACKAGING_STATIONS)

    def mix_ingredients(self, order_name):
        """Simulates mixing ingredients for a drink order."""
        global orders_processed_mixing
        processing_time = random.normalvariate(PROCESSING_TIME_MIXING_MEAN, PROCESSING_TIME_MIXING_STD)
        processing_time = max(0.1, processing_time)
        # print(f"{self.env.now:.2f}: {order_name} starts mixing (takes {processing_time:.2f} min).")
        yield self.env.timeout(processing_time)
        # print(f"{self.env.now:.2f}: {order_name} finishes mixing.")
        orders_processed_mixing += 1

    def fill_bottles(self, order_name):
        """Simulates filling bottles."""
        global orders_processed_filling
        processing_time = random.normalvariate(PROCESSING_TIME_FILLING_MEAN, PROCESSING_TIME_FILLING_STD)
        processing_time = max(0.1, processing_time)
        # print(f"{self.env.now:.2f}: {order_name} starts filling (takes {processing_time:.2f} min).")
        yield self.env.timeout(processing_time)
        # print(f"{self.env.now:.2f}: {order_name} finishes filling.")
        orders_processed_filling += 1

    def cap_bottles(self, order_name):
        """Simulates capping bottles."""
        global orders_processed_capping
        processing_time = random.normalvariate(PROCESSING_TIME_CAPPING_MEAN, PROCESSING_TIME_CAPPING_STD)
        processing_time = max(0.1, processing_time)
        # print(f"{self.env.now:.2f}: {order_name} starts capping (takes {processing_time:.2f} min).")
        yield self.env.timeout(processing_time)
        # print(f"{self.env.now:.2f}: {order_name} finishes capping.")
        orders_processed_capping += 1

    def label_bottles(self, order_name):
        """Simulates labeling bottles."""
        global orders_processed_labeling
        processing_time = random.normalvariate(PROCESSING_TIME_LABELING_MEAN, PROCESSING_TIME_LABELING_STD)
        processing_time = max(0.1, processing_time)
        # print(f"{self.env.now:.2f}: {order_name} starts labeling (takes {processing_time:.2f} min).")
        yield self.env.timeout(processing_time)
        # print(f"{self.env.now:.2f}: {order_name} finishes labeling.")
        orders_processed_labeling += 1

    def package_drinks(self, order_name):
        """Simulates packaging finished drinks and updates bottle count."""
        global orders_processed_packaging, total_bottles_produced_count
        processing_time = random.normalvariate(PROCESSING_TIME_PACKAGING_MEAN, PROCESSING_TIME_PACKAGING_STD)
        processing_time = max(0.1, processing_time)
        # print(f"{self.env.now:.2f}: {order_name} starts packaging (takes {processing_time:.2f} min).")
        yield self.env.timeout(processing_time)
        orders_processed_packaging += 1
        total_bottles_produced_count += BOTTLES_PER_ORDER
        # print(f"{self.env.now:.2f}: {order_name} finishes packaging. Bottles from this order: {BOTTLES_PER_ORDER}. Total bottles produced: {total_bottles_produced_count}.")


def drink_order_lifecycle(env, order_name, factory):
    """
    Simulates the lifecycle of a drink order through the factory.
    """
    arrival_time = env.now
    order_arrival_times.append(arrival_time)
    print(f"{arrival_time:.2f}: {order_name} (batch for {BOTTLES_PER_ORDER} bottles) arrives at the factory.")

    # Stage 1: Mixing
    with factory.mixing_stations.request() as request_mix:
        # print(f"{env.now:.2f}: {order_name} requests Mixing Station.")
        req_time_mix = env.now
        yield request_mix
        wait_start_mix = env.now
        wait_times_mixing.append(wait_start_mix - req_time_mix)
        print(f"{env.now:.2f}: {order_name} seizes Mixing Station. Waited {wait_start_mix - req_time_mix:.2f} min.")
        yield env.process(factory.mix_ingredients(order_name))
        print(f"{env.now:.2f}: {order_name} finishes Mixing.")
    arrival_at_filling = env.now

    # Stage 2: Filling
    with factory.filling_lines.request() as request_fill:
        # print(f"{env.now:.2f}: {order_name} requests Filling Line.")
        req_time_fill = env.now
        yield request_fill
        wait_start_fill = env.now
        wait_times_filling.append(wait_start_fill - req_time_fill)
        print(f"{env.now:.2f}: {order_name} seizes Filling Line. Waited {wait_start_fill - req_time_fill:.2f} min.")
        yield env.process(factory.fill_bottles(order_name))
        print(f"{env.now:.2f}: {order_name} finishes Filling.")
    arrival_at_capping = env.now

    # Stage 3: Capping
    with factory.capping_machines.request() as request_cap:
        # print(f"{env.now:.2f}: {order_name} requests Capping Machine.")
        req_time_cap = env.now
        yield request_cap
        wait_start_cap = env.now
        wait_times_capping.append(wait_start_cap - req_time_cap)
        print(f"{env.now:.2f}: {order_name} seizes Capping Machine. Waited {wait_start_cap - req_time_cap:.2f} min.")
        yield env.process(factory.cap_bottles(order_name))
        print(f"{env.now:.2f}: {order_name} finishes Capping.")
    arrival_at_labeling = env.now

    # Stage 4: Labeling
    with factory.labeling_machines.request() as request_label:
        # print(f"{env.now:.2f}: {order_name} requests Labeling Machine.")
        req_time_label = env.now
        yield request_label
        wait_start_label = env.now
        wait_times_labeling.append(wait_start_label - req_time_label)
        print(f"{env.now:.2f}: {order_name} seizes Labeling Machine. Waited {wait_start_label - req_time_label:.2f} min.")
        yield env.process(factory.label_bottles(order_name))
        print(f"{env.now:.2f}: {order_name} finishes Labeling.")
    arrival_at_packaging = env.now

    # Stage 5: Packaging
    with factory.packaging_stations.request() as request_pack:
        # print(f"{env.now:.2f}: {order_name} requests Packaging Station.")
        req_time_pack = env.now
        yield request_pack
        wait_start_pack = env.now
        wait_times_packaging.append(wait_start_pack - req_time_pack)
        print(f"{env.now:.2f}: {order_name} seizes Packaging Station. Waited {wait_start_pack - req_time_pack:.2f} min.")
        yield env.process(factory.package_drinks(order_name))
        print(f"{env.now:.2f}: {order_name} finishes packaging. Bottles from this order: {BOTTLES_PER_ORDER}. Total bottles produced: {total_bottles_produced_count}.")

    departure_time = env.now
    order_departure_times.append(departure_time)
    print(f"{departure_time:.2f}: {order_name} departs the factory. Total time in system: {departure_time - arrival_time:.2f} min.")


def order_source(env, factory):
    """Generates drink orders until the target number of bottles is produced."""
    global total_bottles_produced_count, TARGET_BOTTLES_TO_PRODUCE
    
    if TARGET_BOTTLES_TO_PRODUCE <= 0:
        print("Warning: TARGET_BOTTLES_TO_PRODUCE is not positive. No orders will be generated.")
        return

    # print(f"Order source will generate orders until at least {TARGET_BOTTLES_TO_PRODUCE} bottles are produced.")
    order_id_num = 0
    generated_order_name = "N/A"
    while total_bottles_produced_count < TARGET_BOTTLES_TO_PRODUCE:
        order_id_num += 1
        interarrival = random.expovariate(1.0 / DRINK_ORDER_INTERARRIVAL_TIME_MEAN)
        yield env.timeout(interarrival)
        
        generated_order_name = f"Order-{order_id_num}"
        # print(f"{env.now:.2f}: Source generated {generated_order_name} (aiming for {BOTTLES_PER_ORDER} bottles, current total: {total_bottles_produced_count}/{TARGET_BOTTLES_TO_PRODUCE}).")
        env.process(drink_order_lifecycle(env, generated_order_name, factory))
    
    # print(f"{env.now:.2f}: Source stopping. Target bottles ({TARGET_BOTTLES_TO_PRODUCE}) met or exceeded (current: {total_bottles_produced_count}). Last order generated was {generated_order_name}.")


def plot_wait_time_histogram(wait_times, stage_name, sim_duration):
    """Generates and displays a histogram of wait times for a given stage."""
    if not wait_times:
        print(f"No wait time data to plot for {stage_name}.")
        return

    plt.figure(figsize=(10, 6))
    plt.hist(wait_times, bins=20, edgecolor='black', alpha=0.7)
    plt.title(f'Wait Time Distribution for {stage_name}\n(Simulation up to {sim_duration:.2f} minutes)')
    plt.xlabel("Wait Time (minutes)")
    plt.ylabel("Number of Orders")
    plt.grid(axis='y', alpha=0.75)
    plt.show()

def run_simulation():
    """Sets up and runs the SimPy simulation for the soft drink factory until target bottles are produced."""
    global TARGET_BOTTLES_TO_PRODUCE, factory_instance 
    
    if TARGET_BOTTLES_TO_PRODUCE <= 0:
        print("Cannot run simulation: Number of bottles to produce must be positive.")
        return

    print(f"--- Soft Drink Factory Simulation Starting: Target {TARGET_BOTTLES_TO_PRODUCE} Bottles ---")
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    global order_arrival_times, order_departure_times, wait_times_mixing, wait_times_filling, wait_times_capping, wait_times_labeling, wait_times_packaging
    global orders_processed_mixing, orders_processed_filling, orders_processed_capping, orders_processed_labeling, orders_processed_packaging, total_bottles_produced_count
    order_arrival_times = []
    order_departure_times = []
    wait_times_mixing = []
    wait_times_filling = []
    wait_times_capping = []
    wait_times_labeling = []
    wait_times_packaging = []
    orders_processed_mixing = 0
    orders_processed_filling = 0
    orders_processed_capping = 0
    orders_processed_labeling = 0
    orders_processed_packaging = 0
    total_bottles_produced_count = 0
    
    env = simpy.Environment()
    factory_instance = SoftDrinkFactory(env) # Store the instance
    env.process(order_source(env, factory_instance))
    env.run()

    actual_simulation_duration = env.now

    print("\n--- Simulation Ended ---")
    print(f"Target bottles to produce: {TARGET_BOTTLES_TO_PRODUCE}")
    print(f"Actual bottles produced: {total_bottles_produced_count} (from {orders_processed_packaging} completed orders/batches)")
    print(f"Total simulation time: {actual_simulation_duration:.2f} minutes")
    
    print(f"\n--- Order / Batch Summary ---")
    print(f"Total orders (batches) arrived at system: {len(order_arrival_times)}")
    print(f"Total orders (batches) departed from system: {len(order_departure_times)}") 
    print(f"Orders (batches) processed by Mixing: {orders_processed_mixing}")
    print(f"Orders (batches) processed by Filling: {orders_processed_filling}")
    print(f"Orders (batches) processed by Capping: {orders_processed_capping}")
    print(f"Orders (batches) processed by Labeling: {orders_processed_labeling}")
    print(f"Orders (batches) completed packaging: {orders_processed_packaging}")

    print(f"\n--- Wait Time Statistics (for orders/batches) ---")
    def print_avg_wait_time(wait_times_list, stage_name):
        if wait_times_list:
            avg_wait = np.mean(wait_times_list)
            print(f"Average wait time for {stage_name}: {avg_wait:.2f} minutes")
        else:
            print(f"No orders recorded waiting for {stage_name}.")

    print_avg_wait_time(wait_times_mixing, "Mixing Station")
    print_avg_wait_time(wait_times_filling, "Filling Line")
    print_avg_wait_time(wait_times_capping, "Capping Machine")
    print_avg_wait_time(wait_times_labeling, "Labeling Machine")
    print_avg_wait_time(wait_times_packaging, "Packaging Station")

    print(f"\n--- System Performance ---")
    if order_departure_times and order_arrival_times:
        completed_orders_count_for_cycle_time = len(order_departure_times)
        if completed_orders_count_for_cycle_time > 0:
            relevant_arrivals = order_arrival_times[:completed_orders_count_for_cycle_time]
            total_cycle_time = sum(dep - arr for arr, dep in zip(relevant_arrivals, order_departure_times))
            avg_cycle_time = total_cycle_time / completed_orders_count_for_cycle_time
            print(f"Average cycle time for {completed_orders_count_for_cycle_time} completed orders/batches: {avg_cycle_time:.2f} minutes")
        else:
            print("No orders completed processing for cycle time calculation.")
    else:
        print("Not enough data for cycle time calculation.")

    print(f"\n--- Resource Utilization (Estimated for Orders/Batches) ---")
    def print_utilization(num_machines, items_processed_at_stage, mean_processing_time_per_item, stage_name, total_sim_time):
        if total_sim_time <= 0:
            print(f"Cannot calculate utilization for {stage_name} (simulation time is zero or negative).")
            return
        
        total_capacity_time = num_machines * total_sim_time 
        approx_busy_time = items_processed_at_stage * mean_processing_time_per_item
        utilization = (approx_busy_time / total_capacity_time) * 100 if total_capacity_time > 0 else 0
        utilization = min(utilization, 100.0)
        print(f"Estimated utilization for {stage_name}: {utilization:.2f}% (based on {items_processed_at_stage} orders over {total_sim_time:.2f} min)")

    if actual_simulation_duration > 0:
        print_utilization(NUM_MIXING_STATIONS, orders_processed_mixing, PROCESSING_TIME_MIXING_MEAN, "Mixing Station(s)", actual_simulation_duration)
        print_utilization(NUM_FILLING_LINES, orders_processed_filling, PROCESSING_TIME_FILLING_MEAN, "Filling Line(s)", actual_simulation_duration)
        print_utilization(NUM_CAPPING_MACHINES, orders_processed_capping, PROCESSING_TIME_CAPPING_MEAN, "Capping Machine(s)", actual_simulation_duration)
        print_utilization(NUM_LABELING_MACHINES, orders_processed_labeling, PROCESSING_TIME_LABELING_MEAN, "Labeling Machine(s)", actual_simulation_duration)
        print_utilization(NUM_PACKAGING_STATIONS, orders_processed_packaging, PROCESSING_TIME_PACKAGING_MEAN, "Packaging Station(s) (completed orders)", actual_simulation_duration)
    else:
        print("Simulation duration was zero. Cannot calculate utilization.")

    print(f"\n--- Resource State at End of Simulation (Time: {actual_simulation_duration:.2f}) ---")
    if factory_instance:
        print(f"Mixing Station(s):     Processing: {factory_instance.mixing_stations.count}, In Queue: {len(factory_instance.mixing_stations.queue)}")
        print(f"Filling Line(s):       Processing: {factory_instance.filling_lines.count}, In Queue: {len(factory_instance.filling_lines.queue)}")
        print(f"Capping Machine(s):    Processing: {factory_instance.capping_machines.count}, In Queue: {len(factory_instance.capping_machines.queue)}")
        print(f"Labeling Machine(s):   Processing: {factory_instance.labeling_machines.count}, In Queue: {len(factory_instance.labeling_machines.queue)}")
        print(f"Packaging Station(s):  Processing: {factory_instance.packaging_stations.count}, In Queue: {len(factory_instance.packaging_stations.queue)}")
    else:
        print("Factory instance not available for final resource state.")

    # --- Plotting Results ---
    print("\n--- Visualizations ---")
    plot_wait_time_histogram(wait_times_packaging, "Packaging Station", actual_simulation_duration)

if __name__ == "__main__":
    # Reduce console output for cleaner testing of plots, can be re-enabled.
    verbose_simulation_output = False # Set to True to see detailed per-order logs

    # Quick way to toggle print statements within processes by wrapping them
    def conditional_print(*args, **kwargs):
        if verbose_simulation_output:
            print(*args, **kwargs)

    # Overwrite original print in process functions if needed, or pass conditional_print
    # For this example, I will comment out prints in process methods directly for brevity
    # and adjust a few key prints in drink_order_lifecycle to always show.

    while True:
        try:
            num_bottles_str = input("Enter the total number of bottles to produce (e.g., 5000): ")
            TARGET_BOTTLES_TO_PRODUCE = int(num_bottles_str)
            if TARGET_BOTTLES_TO_PRODUCE > 0:
                break
            else:
                print("Please enter a positive number of bottles.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")

    print(f"Simulating production of {TARGET_BOTTLES_TO_PRODUCE} bottles, with {BOTTLES_PER_ORDER} bottles per order/batch.")
    start_real_time = time.time()
    run_simulation()
    end_real_time = time.time()
    print(f"\nActual wall-clock time for simulation run: {end_real_time - start_real_time:.4f} seconds")

    # Example of using time.sleep for a delay (not typically used within SimPy processes)
    # print("\nDemonstrating a time.sleep delay (not part of simulation logic):")
    # time.sleep(0.1) # Simulate a 0.1-second delay for some external reason
    # print("Delay finished.") 