"""First draft of an evolution simulator code for KID Museum.

Generates zorks (winged giraffe-like animals) with random traits.  Grades each zork's survivability based on its
traits.  Culls zorks that fall below a certain threshold.  Zorks mate in random pairs to create new zorks.

New in this version of the code, the population changes dynamically from generation to generation, and overpopulation
affects how selective the environment is.  In addition, the environment has a caprice parameter; some zorks below the
survivability threshold may live, and some above the survivability threshold may die.

Note that this new model means that better-evolved surviving zorks no longer have a higher chance to reproduce than
worse-evolved surviving zorks.  All surviving zorks will have a chance to survive.
"""

# Imports
import random
import statistics
from matplotlib import pyplot as plt
from tqdm import tqdm

# Todos
    # Within the scope of KID Museum:
        # TODO: Figure out how kids can interact with it.  Is it a black box where they get to control parameters, and thus gain intuition about evolution?
        # TODO: Draw zorks graphically or build them in TinkerCAD codeblocks/something similar?
        # TODO: Make a nice GUI to let the user input parameters.  Knobs?
        # TODO: Control input parameters with potentiometers on an RPi?
        # TODO: Show graphs with an animation where the line draws in from left to right, to link the x-axis with time and aid kids without graph intuition.
        # TODO: New traits: Jaw muscle mass?  Fire breath Wattage?  What about a binary choice, like eye color, that doesn't influence survival, so that we can look at genetic drift?
    # Beyond the scope of KID Museum:
        # TODO: Enable Monte Carlo style analysis, to observe the average statistics of many runs.
        # TODO: Let caprice affect REPRODUCTION as well as survival.  Move it to be a CLASS ATTRIBUTE of each individual zork, randomly determined for that zork.
        # TODO: For clean code, consider making helper functions for complicated processes like reproduction.
        # TODO: For clean code, use pop() instead of emptying lists after-the fact with =.
        # TODO: Graph survival threshold over time.


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


# Parameters
max_number_generations = 30    # Total number of generations to simulate.
base_threshold_to_survive = 1     # Minimum survivability rating that a zork needs not to fail, before accounting for population vs carrying_capacity.
environment_caprice = 1   # Not all zorks are held to the exact same standard.  Each zork's final_survivability will be compared to threshold_to_survive ± a random number between 0 and environment_caprice.
initial_population = 100  # Number of zorks in the first generation.
mutation_coefficient = 0.01  # A child's trait will equal the average of their parents' traits, plus or minus up to this percentage of the range for that trait.  0.05 is 5%.
children_per_mate = 3     # The number of children a reproducing couple will have.
carrying_capacity = 20000   # Capacity at which threshold_to_survive = 3.  Beyond this population level, threshold_to_survive > 3.

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


# Gather data to plot results
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
fig.suptitle("Evolution results.  All measurements vs generation number.\nbase survival threshold " + str(base_threshold_to_survive) + ", caprice " + str(environment_caprice) + ", initial population " + str(initial_population) + ", mutation " + str(mutation_coefficient) + ", children per mate " + str(children_per_mate) + ", carrying capacity " + str(carrying_capacity))

axs[0, 0].plot(range(max_number_generations), group_survivors)
axs[0, 0].set_title("Number of surviving animals")
axs[0, 0].set(ylim=(0, None))
axs[0, 0].grid()

axs[1, 0].plot(range(max_number_generations), group_failures)
axs[1, 0].set_title("Number of failed animals")
axs[1, 0].set(ylim=(0, None))
axs[1, 0].grid()

axs[0, 1].plot(range(max_number_generations), group_leg_length)
axs[0, 1].set_title("Average leg length")
axs[0, 1].set(ylim=all_zorks[0][0].boundaries_leg_length)
axs[0, 1].grid()

axs[1, 1].plot(range(max_number_generations), group_standard_deviation_leg_length)
axs[1, 1].set_title("Standard deviation of leg length")
axs[1, 1].set(ylim=(0, None))
axs[1, 1].grid()

axs[0, 2].plot(range(max_number_generations), group_fur_length)
axs[0, 2].set_title("Average fur length")
axs[0, 2].set(ylim=all_zorks[0][0].boundaries_fur_length)
axs[0, 2].grid()

axs[1, 2].plot(range(max_number_generations), group_standard_deviation_fur_length)
axs[1, 2].set_title("Standard deviation of fur length")
axs[1, 2].set(ylim=(0, None))
axs[1, 2].grid()

axs[0, 3].plot(range(max_number_generations), group_wingspan)
axs[0, 3].set_title("Average wingspan")
axs[0, 3].set(ylim=all_zorks[0][0].boundaries_wingspan)
axs[0, 3].grid()

axs[1, 3].plot(range(max_number_generations), group_standard_deviation_wingspan)
axs[1, 3].set_title("Standard deviation of wingspan")
axs[1, 3].set(ylim=(0, None))
axs[1, 3].grid()

axs[0, 4].plot(range(max_number_generations), group_survivability)
axs[0, 4].set_title("Average survivability rating")
axs[0, 4].set(ylim=(0, None))
axs[0, 4].grid()

axs[1, 4].plot(range(max_number_generations), thresholds_to_survive)
axs[1, 4].set_title("Threshold to survive (before caprice)")
axs[1, 4].set(ylim=(0, None))
axs[1, 4].grid()

plt.show()
