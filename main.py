"""Evolution simulator code for KID Museum.

Generates zorks (winged giraffe-like animals) with random traits.  Grades each zork's survivability based on its
traits.  Culls zorks that fall below a certain threshold.  Zorks mate in random pairs to create new zorks.

New in this version of the code, the user sets starting parameters via a GUI.

The idea for kid interaction is that kids can set the initial parameters, watch a run of the simulation, and repeat.
By tweaking their parameters and seeing the effect on the simulation, kids can gain some intuition about the effects of
these parameters on evolution.

On invalid user entries, and in cases where there's a generation of 0 or 1 zorks, the code avoids crashing, and instead
the input panel provides helpful advice.

Moved helper function definitions outside of the "while True:" loop.
"""

# Imports
import random
import statistics
from matplotlib import pyplot as plt
from tqdm import tqdm
import tkinter

# Todos
    # Within the scope of KID Museum:
        # TODO: Remove occasional single-zork reproduction?
        # TODO: Plot live so that kids don't get bored waiting, and so kids can see if there's a slowdown due to too many Zorks and can terminate.
        # TODO: Draw zorks graphically or build them in TinkerCAD codeblocks/something similar?
        # TODO: Control input parameters with potentiometers on an RPi?
        # TODO: Show graphs with an animation where the line draws in from left to right, to link the x-axis with time and aid kids without graph intuition.
        # TODO: New traits: Jaw muscle mass?  Fire breath Wattage?  What about a binary choice, like eye color, that doesn't influence survival, so that we can look at genetic drift?
        # TODO: Tweak helper function clicked_buttoon_confirm() so that it doesn't run the simulation if the user inputs "e"s without proper numeric context.
    # Beyond the scope of KID Museum:
        # TODO: Enable Monte Carlo style analysis, to observe the average statistics of many runs.
        # TODO: Introduce traits that only influence reproductive odds, and not survival odds?
        # TODO: For clean code, consider making helper functions for complicated processes like reproduction.
        # TODO: For clean code, use pop() instead of emptying lists after-the fact with =.


# Zork class, including attributes and methods
class Zork:
    """A goofy animal (1200 kg winged giraffe) with some traits."""

    def __init__(self, vitals, mutation_level, parent1=None, parent2=None, leg_length=None, fur_length=None, wingspan=None, final_survivability=None):
        """Vitals is a string: either "alive", "failed", or "retired".
        parent1 and parent2 are each tuples of integers (a, b), where a is the generation of the parent, and b is that
        parent's index in the generation.
        leg_length is a float.
        fur_length is a float.
        wingspan is a float.
        boundaries values represent the minimum and maximum possible boundaries for a trait.
        spectrum values represent the difference between the minimum and maximum possible values for a trait.
        final_survivability is a float.
        """
        self.vitals = vitals
        self.mutation_level = mutation_level
        self.parent1 = parent1
        self.parent2 = parent2
        self.boundaries_leg_length = (1.2, 2.5)         # Meters
        self.spectrum_leg_length = abs(self.boundaries_leg_length[1] - self.boundaries_leg_length[0])
        self.boundaries_fur_length = (0.0064, 0.0508)   # Meters
        self.spectrum_fur_length = abs(self.boundaries_fur_length[1] - self.boundaries_fur_length[0])
        self.boundaries_wingspan = (28, 38)             # Meters
        self.spectrum_wingspan = abs(self.boundaries_wingspan[1] - self.boundaries_wingspan[0])
        self.leg_length = leg_length
        self.fur_length = fur_length
        self.wingspan = wingspan
        self.final_survivability = final_survivability

    def set_traits(self):
        """Sets traits for this particular zork.  If this is a generation 0 zork, traits are completely random.
        Else, traits are based on the traits of parents, with some random noise thrown in.
        """
        if self.parent1 is None and self.parent2 is None:     # No parents; generate from random parameters.
            self.leg_length = random.uniform(self.boundaries_leg_length[0], self.boundaries_leg_length[1])
            self.fur_length = random.uniform(self.boundaries_fur_length[0], self.boundaries_fur_length[1])
            self.wingspan = random.uniform(self.boundaries_wingspan[0], self.boundaries_wingspan[1])
        else:   # This zork has parents; generate from average of parents' paremeters ± mutation * spectrum, then limit the trait to the boundaries if that trait exceeded the boundaries.
            self.leg_length = statistics.mean([self.parent1.leg_length, self.parent2.leg_length]) + random.uniform(-self.mutation_level, self.mutation_level) * self.spectrum_leg_length
            if self.leg_length < self.boundaries_leg_length[0]:
                self.leg_length = self.boundaries_leg_length[0]
            elif self.leg_length > self.boundaries_leg_length[1]:
                self.leg_length = self.boundaries_leg_length[1]

            self.fur_length = statistics.mean([self.parent1.fur_length, self.parent2.fur_length]) + random.uniform(-self.mutation_level, self.mutation_level) * self.spectrum_fur_length
            if self.fur_length < self.boundaries_fur_length[0]:
                self.fur_length = self.boundaries_fur_length[0]
            elif self.fur_length > self.boundaries_fur_length[1]:
                self.fur_length = self.boundaries_fur_length[1]

            self.wingspan = statistics.mean([self.parent1.wingspan, self.parent2.wingspan]) + random.uniform(-self.mutation_level, self.mutation_level) * self.spectrum_wingspan
            if self.wingspan < self.boundaries_wingspan[0]:
                self.wingspan = self.boundaries_wingspan[0]
            elif self.wingspan > self.boundaries_wingspan[1]:
                self.wingspan = self.boundaries_wingspan[1]

    def grade_survivability(self):
        """Outputs a survivability rating for this particular zork.
        Each trait results in a specific survivability rating, between -3 (extremely detrimental) and +3 (extremely
        beneficial).  Less important traits have smaller ranges in survivability ratings.

        legs of middle length are preferred; short legs make it hard for the zork to reach food, while excessively long legs cause blood pressure issues.  A negative quadratic function converts length to survivability_leg_length.
        short fur is slightly preferred; zorks live in a hot environment.  A linear function converts fur length to survivability_fur_length.
        long wingspan is preferred; zorks can only fly at all if their wingspan is 32 m or greater.  Else, wings are detrimental dead weight.  A piecewise linear function converts wingspan to survivability_wingspan.


        final_survivability is the average of all other survivability ratings.
        """
        survivability_leg_length = -((6 ** 0.5 / 0.65) * (self.leg_length - 1.85)) ** 2 + 3
        survivability_fur_length = -45.045 * self.fur_length + 1.288
        if self.wingspan < 32:
            survivability_wingspan = -2
        else:
            survivability_wingspan = 0.5 * self.wingspan - 16

        self.final_survivability = statistics.mean([survivability_leg_length, survivability_fur_length, survivability_wingspan])
        return self.final_survivability


# Helper functions.
def contains_non_numeric(input_string):
    """Inputs a string.  Returns True if the string contains any characters outside the set [-.0123456789]"""
    for character in input_string:
        if not (character in "e-.0123456789"):
            return True
    return False


def clicked_button_confirm():
    # Tell the user if they've entered any invalid parameters.
    input_issue_flag = 0
    instructions.config(text="")
    if contains_non_numeric(entry_max_number_generations.get()) or float(entry_max_number_generations.get()) < 1 or float(entry_max_number_generations.get()) != int(float(entry_max_number_generations.get())):   # Check entry_max_number_generations
        instructions.config(text=instructions["text"] + "Number of generations must be a whole number.\n")
        input_issue_flag = 1
    if contains_non_numeric(entry_base_threshold_to_survive.get()) or not(-3 <= float(entry_base_threshold_to_survive.get()) <= 3):    # Check entry_base_threshold_to_survive
        instructions.config(text=instructions["text"] + "Base survival threshold must be a real number from -3 to 3.\n")
        input_issue_flag = 1
    if contains_non_numeric(entry_environment_caprice.get()) or not (0 <= float(entry_environment_caprice.get()) <= 6):  # Check entry_environment_caprice
        instructions.config(text=instructions["text"] + "Environment caprice should be a real number from 0 to 6.\n")
        input_issue_flag = 1
    if contains_non_numeric(entry_initial_population.get()) or float(entry_initial_population.get()) < 2 or float(entry_initial_population.get()) != int(float(entry_initial_population.get())):    # Check entry_initial_population
        instructions.config(text=instructions["text"] + "Initial population must be a whole number greater than 1.\n")
        input_issue_flag = 1
    if contains_non_numeric(entry_mutation_coefficient.get()) or not(0 <= float(entry_mutation_coefficient.get()) <= 1):  # Check entry_mutation_coefficient
        instructions.config(text=instructions["text"] + "Mutation intensity must be a real number from 0 to 1.\n")
        input_issue_flag = 1
    if contains_non_numeric(entry_children_per_mate.get()) or float(entry_children_per_mate.get()) < 1 or float(entry_children_per_mate.get()) != int(float(entry_children_per_mate.get())):   # Check entry_children_per_mate
        instructions.config(text=instructions["text"] + "Children per mating group must be a whole number greater than 0.\n")
        input_issue_flag = 1
    if contains_non_numeric(entry_carrying_capacity.get()) or float(entry_carrying_capacity.get()) < 2 or float(entry_carrying_capacity.get()) != int(float(entry_carrying_capacity.get())):   # Check entry_carrying_capacity
        instructions.config(text=instructions["text"] + "Carrying capacity must be a whole number greater than 1.\n")
        input_issue_flag = 1

    # If there are no issues, then proceed with the simulation!
    if input_issue_flag == 0:   # Proceed with the simulation!
        # Set these variables to global so that the rest of the script can use them afterward.
        global max_number_generations
        global base_threshold_to_survive
        global environment_caprice
        global initial_population
        global mutation_coefficient
        global children_per_mate
        global carrying_capacity

        # Get values from entry boxes and store in the appropriate variables.
        max_number_generations = int(entry_max_number_generations.get())
        base_threshold_to_survive = float(entry_base_threshold_to_survive.get())
        environment_caprice = float(entry_environment_caprice.get())
        initial_population = int(entry_initial_population.get())
        mutation_coefficient = float(entry_mutation_coefficient.get())
        children_per_mate = int(entry_children_per_mate.get())
        carrying_capacity = int(entry_carrying_capacity.get())
        panel.destroy()


# Set default parameters.
max_number_generations = 30    # Total number of generations to simulate.
base_threshold_to_survive = 1     # Minimum survivability rating that a zork needs not to fail, before accounting for population vs carrying_capacity.
environment_caprice = 1   # Not all zorks are held to the exact same standard.  Each zork's final_survivability will be compared to threshold_to_survive ± a random number between 0 and environment_caprice.
initial_population = 100  # Number of zorks in the first generation.
mutation_coefficient = 0.01  # A child's trait will equal the average of their parents' traits, plus or minus up to this percentage of the range for that trait.  0.05 is 5%.
children_per_mate = 3     # The number of children a reproducing couple will have.
carrying_capacity = 20000   # Capacity at which threshold_to_survive = 3.  Beyond this population level, threshold_to_survive > 3.

did_zorks_die_out_last_run = False  # This is a flag to tell the user if the zorks died out in the previous simulation.

# Begin loop.
while True:
    # Let the user adjust parameters via a GUI.
    panel = tkinter.Tk()
    panel.title("Select parameters")
    panel.geometry("750x450")

    instructions = tkinter.Label(panel, text="Please select parameters.\n", font=("Arial", 14))
    if did_zorks_die_out_last_run:  # If the last run failed due to extinction, edit this message to inform the user:
        instructions.config(text="There was a generation of 0 or 1 zorks!  No graph generated.")
    instructions.grid(row=0, column=0)

    label_max_number_generations = tkinter.Label(panel, text="Number of generations", font=("Arial", 14))
    label_max_number_generations.grid(row=1, column=0)

    entry_max_number_generations = tkinter.Entry(panel, width=30)
    entry_max_number_generations.insert(0, str(max_number_generations))
    entry_max_number_generations.grid(row=1, column=1)

    label_base_threshold_to_survive = tkinter.Label(panel, text="Base survival threshold (higher is harsher)", font=("Arial", 14))
    label_base_threshold_to_survive.grid(row=2, column=0)

    entry_base_threshold_to_survive = tkinter.Entry(panel, width=30)
    entry_base_threshold_to_survive.insert(0, str(base_threshold_to_survive))
    entry_base_threshold_to_survive.grid(row=2, column=1)

    label_environment_caprice = tkinter.Label(panel, text="Environment caprice (higher is more unfair)", font=("Arial", 14))
    label_environment_caprice.grid(row=3, column=0)

    entry_environment_caprice = tkinter.Entry(panel, width=30)
    entry_environment_caprice.insert(0, str(environment_caprice))
    entry_environment_caprice.grid(row=3, column=1)

    label_initial_population = tkinter.Label(panel, text="Initial population", font=("Arial", 14))
    label_initial_population.grid(row=4, column=0)

    entry_initial_population = tkinter.Entry(panel, width=30)
    entry_initial_population.insert(0, str(initial_population))
    entry_initial_population.grid(row=4, column=1)

    label_mutation_coefficient = tkinter.Label(panel, text="Mutation intensity (between 0 and 1)", font=("Arial", 14))
    label_mutation_coefficient.grid(row=5, column=0)

    entry_mutation_coefficient = tkinter.Entry(panel, width=30)
    entry_mutation_coefficient.insert(0, str(mutation_coefficient))
    entry_mutation_coefficient.grid(row=5, column=1)

    label_children_per_mate = tkinter.Label(panel, text="Children per mating group", font=("Arial", 14))
    label_children_per_mate.grid(row=6, column=0)

    entry_children_per_mate = tkinter.Entry(panel, width=30)
    entry_children_per_mate.insert(0, str(children_per_mate))
    entry_children_per_mate.grid(row=6, column=1)

    label_carrying_capacity = tkinter.Label(panel, text="Carrying capacity (maximum creatures that can coexist)", font=("Arial", 14))
    label_carrying_capacity.grid(row=7, column=0)

    entry_carrying_capacity = tkinter.Entry(panel, width=30)
    entry_carrying_capacity.insert(0, str(carrying_capacity))
    entry_carrying_capacity.grid(row=7, column=1)

    button_confirm = tkinter.Button(panel, text="RUN", font=("Arial", 16), command=clicked_button_confirm)
    button_confirm.grid(row=8, column=1)

    panel.protocol("WM_DELETE_WINDOW", exit)    # Exits the code if the panel is closed in Windows.
    panel.mainloop()


    # Set initial variables.
    all_zorks = []  # List of lists.  Each list within the list contains a generation of zorks.
    thresholds_to_survive = []  # Contains survival thresholds, one for each generation.  Survival thresholds are influenced by population and carrying capacity.

    # Main loop.
    for generation in tqdm(range(max_number_generations)):
        # Create new zorks.
        zorks_this_generation = []
        if generation == 0:     # If this generation 0:
            for specimen in range(initial_population):
                zorks_this_generation.append(Zork("alive", mutation_coefficient))
                zorks_this_generation[specimen].set_traits()
        else:   # If this isn't generation 0:
            # Retire all alive zorks from the last generation.
            for specimen in all_zorks[generation - 1]:
                if specimen.vitals == "alive":
                    specimen.vitals = "retired"

            # Reproduction.  Group surviving zorks into random pairs.  If there's a leftover zork, that zork will self-reproduce.
            # Randomly group zorks, including a group of 1 if there's an odd number of zorks in the generation.
            unassigned_reproducing_zorks = [specimen for specimen in all_zorks[generation - 1] if specimen.vitals == "retired"]  # Create a list of retired zorks from the last generation.  These zorks will be assigned to pairs in a moment, with one singleton if there's an odd number of zorks in this generation.
            reproducing_groups = []
            while len(unassigned_reproducing_zorks) != 0:
                this_pair = []
                if len(unassigned_reproducing_zorks) > 1:   # If a group of 2 can still be made from the unassigned zorks:
                    for repetition in range(2):
                        choice = random.randint(0, len(unassigned_reproducing_zorks)-1)
                        this_pair.append(unassigned_reproducing_zorks.pop(choice))
                else:   # If a pair can't still be made from the unassigned zorks:
                    this_pair.append(unassigned_reproducing_zorks.pop(0))
                reproducing_groups.append(this_pair)
            this_pair = []  # Empty this_pair, to avoid confusion later.
            # Now unassigned_reproducing_zorks is an empty list.

            # Have each couple make children_per_mate children.
            for mating_unit in reproducing_groups:  # Have each mating unit make 3 children, regardless of whether there are 2 or 1 zorks in the mating unit.
                for repetition in range(3):
                    zorks_this_generation.append(Zork("alive", mutation_coefficient, parent1=mating_unit[0], parent2=mating_unit[-1]))   # By having one parent be the first in the mating unit, and the second be the last in the mating unit, this line causes correct reproduction for both 2-zork and 1-zork mating units.
                    zorks_this_generation[-1].set_traits()

        all_zorks.append(zorks_this_generation)
        zorks_this_generation = []  # For clarity, because this list will now become outdated, empty it.

        # Grade each zork in this generation based on its traits, outputting a survivability rating.
        for specimen in all_zorks[generation]:
            specimen.grade_survivability()

        # Set threshold_to_survive based on carrying_capacity and the population of this generation of zorks.
        thresholds_to_survive.append(((3 - base_threshold_to_survive) / carrying_capacity) * len(all_zorks[generation]) + base_threshold_to_survive)

        # Cull zorks in this generation whose survivability falls below a certain threshold.
        for specimen in all_zorks[generation]:
            if specimen.final_survivability < thresholds_to_survive[generation] + random.uniform(-environment_caprice, environment_caprice):     # Judge the zork against threshold_to_survive ± a random number between 0 and environment_caprice.
                specimen.vitals = "failed"

        # If this is the last generation, retire zorks in the final generation without them reproducing.
        if generation == max_number_generations - 1:
            for specimen in all_zorks[generation]:
                if specimen.vitals == "alive":
                    specimen.vitals = "retired"


    # Gather data to plot results.  Includes try/except to handle errors if the zorks die off or there's a generation of just 1 zork.
    try:
        # Number of surviving and failed zorks in each generation
        group_survivors = []
        group_failures = []
        for generation in all_zorks:
            survivors_this_generation = 0
            failures_this_generation = 0
            for zork in generation:
                if zork.vitals == "retired":
                    survivors_this_generation = survivors_this_generation + 1
                else:   # This zork must have failed.
                    failures_this_generation = failures_this_generation + 1
            group_survivors.append(survivors_this_generation)
            group_failures.append(failures_this_generation)

        # Average survivability in each generation
        group_survivability = []
        for generation in all_zorks:
            survivabilities_this_generation = []
            for zork in generation:
                survivabilities_this_generation.append(zork.final_survivability)
            group_survivability.append(statistics.mean(survivabilities_this_generation))

        # Average traits and standard deviations within traits in each generation
        group_leg_length = []
        group_standard_deviation_leg_length = []
        for generation in all_zorks:
            leg_length_this_generation = []
            for zork in generation:
                leg_length_this_generation.append(zork.leg_length)
            group_leg_length.append(statistics.mean(leg_length_this_generation))
            group_standard_deviation_leg_length.append(statistics.stdev(leg_length_this_generation))

        group_fur_length = []
        group_standard_deviation_fur_length = []
        for generation in all_zorks:
            fur_length_this_generation = []
            for zork in generation:
                fur_length_this_generation.append(zork.fur_length)
            group_fur_length.append(statistics.mean(fur_length_this_generation))
            group_standard_deviation_fur_length.append(statistics.stdev(fur_length_this_generation))

        group_wingspan = []
        group_standard_deviation_wingspan = []
        for generation in all_zorks:
            wingspan_this_generation = []
            for zork in generation:
                wingspan_this_generation.append(zork.wingspan)
            group_wingspan.append(statistics.mean(wingspan_this_generation))
            group_standard_deviation_wingspan.append(statistics.stdev(wingspan_this_generation))

        # Plot results versus generation.
        fig, axs = plt.subplots(2, 5)
        fig.suptitle("Evolution results.  All measurements vs generation number.  Close this window to run again.\nbase survival threshold " + str(base_threshold_to_survive) + ", caprice " + str(environment_caprice) + ", initial population " + str(initial_population) + ", mutation " + str(mutation_coefficient) + ", children per mate " + str(children_per_mate) + ", carrying capacity " + str(carrying_capacity))

        axs[0, 0].plot(range(max_number_generations), group_survivors)
        axs[0, 0].set_title("Number of surviving animals")
        axs[0, 0].set(ylim=(0, None))
        axs[0, 0].set_xlabel("Generation")
        axs[0, 0].set_ylabel("Animals")
        axs[0, 0].grid()

        axs[1, 0].plot(range(max_number_generations), group_failures)
        axs[1, 0].set_title("Number of failed animals")
        axs[1, 0].set(ylim=(0, None))
        axs[1, 0].set_xlabel("Generation")
        axs[1, 0].set_ylabel("Animals")
        axs[1, 0].grid()

        axs[0, 1].plot(range(max_number_generations), group_leg_length)
        axs[0, 1].set_title("Average leg length")
        axs[0, 1].set(ylim=all_zorks[0][0].boundaries_leg_length)
        axs[0, 1].set_xlabel("Generation")
        axs[0, 1].set_ylabel("Leg length (m)")
        axs[0, 1].grid()

        axs[1, 1].plot(range(max_number_generations), group_standard_deviation_leg_length)
        axs[1, 1].set_title("Standard deviation of leg length")
        axs[1, 1].set(ylim=(0, None))
        axs[1, 1].set_xlabel("Generation")
        axs[1, 1].set_ylabel("Standard deviation (m)")
        axs[1, 1].grid()

        axs[0, 2].plot(range(max_number_generations), group_fur_length)
        axs[0, 2].set_title("Average fur length")
        axs[0, 2].set(ylim=all_zorks[0][0].boundaries_fur_length)
        axs[0, 2].set_xlabel("Generation")
        axs[0, 2].set_ylabel("Fur length (m)")
        axs[0, 2].grid()

        axs[1, 2].plot(range(max_number_generations), group_standard_deviation_fur_length)
        axs[1, 2].set_title("Standard deviation of fur length")
        axs[1, 2].set(ylim=(0, None))
        axs[1, 2].set_xlabel("Generation")
        axs[1, 2].set_ylabel("Standard deviation (m)")
        axs[1, 2].grid()

        axs[0, 3].plot(range(max_number_generations), group_wingspan)
        axs[0, 3].set_title("Average wingspan")
        axs[0, 3].set(ylim=all_zorks[0][0].boundaries_wingspan)
        axs[0, 3].set_xlabel("Generation")
        axs[0, 3].set_ylabel("Wingspan (m)")
        axs[0, 3].grid()

        axs[1, 3].plot(range(max_number_generations), group_standard_deviation_wingspan)
        axs[1, 3].set_title("Standard deviation of wingspan")
        axs[1, 3].set(ylim=(0, None))
        axs[1, 3].set_xlabel("Generation")
        axs[1, 3].set_ylabel("Standard deviation (m)")
        axs[1, 3].grid()

        axs[0, 4].plot(range(max_number_generations), group_survivability)
        axs[0, 4].set_title("Average survivability rating")
        axs[0, 4].set(ylim=(0, None))
        axs[0, 4].set_xlabel("Generation")
        axs[0, 4].set_ylabel("Survivability (scale from -3 to 3)")
        axs[0, 4].grid()

        axs[1, 4].plot(range(max_number_generations), thresholds_to_survive)
        axs[1, 4].set_title("Threshold to survive (before caprice)")
        axs[1, 4].set(ylim=(0, None))
        axs[1, 4].set_xlabel("Generation")
        axs[1, 4].set_ylabel("Survivability (scale from -3 to 3)")
        axs[1, 4].grid()

        # Show plot in fullscreen.
        manager = plt.get_current_fig_manager()
        manager.resize(1920, 1080)
        plt.show()

    except statistics.StatisticsError as err:
        did_zorks_die_out_last_run = True
