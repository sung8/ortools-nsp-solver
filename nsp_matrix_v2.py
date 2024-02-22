from ortools.sat.python import cp_model
import pandas as pd

import random

def generate_random_nurse_availability(num_nurses, num_days, max_consecutive_shifts=2, min_availability_percentage=0.66):
    nurse_availability = []

    for _ in range(num_nurses):
        availability = [1] * num_days  # Start with all shifts available
        # Introduce randomness
        for day in range(num_days):
            if random.random() > min_availability_percentage:
                availability[day] = 0  # Nurse unavailable for this shift

        # Ensure maximum consecutive shifts
        for day in range(num_days - max_consecutive_shifts):
            if sum(availability[day:day+max_consecutive_shifts]) > max_consecutive_shifts:
                for d in range(day, day+max_consecutive_shifts):
                    availability[d] = 0

        nurse_availability.append(availability)

    return nurse_availability


def main():
    num_nurses = 4
    num_shifts = 2
    num_days = 7
    shifts_per_day = 2
    max_consecutive_shifts = 2
    min_rest_time = 1

    # generate random nurse availability matrix
    # generate_random_nurse_availability's min_availability_percentage parameter is auto-set
    #   pass in a fourth parameter to override
    nurse_availability = generate_random_nurse_availability(num_nurses, num_days, max_consecutive_shifts)

    print("Nurse Availability Matrix:")
    for row in nurse_availability:
        print(row)

    model = cp_model.CpModel()

    # decision vars
    # x_{n,d,s} = assignment var
    shifts = {}
    for nurse in range(num_nurses):
        for day in range(num_days):
            for shift in range(shifts_per_day):
                shifts[(nurse, day, shift)] = model.NewBoolVar(f'nurse_{nurse}_day_{day}_shift_{shift}')

    # constraints
    for day in range(num_days):
        for shift in range(shifts_per_day):
            model.Add(sum(shifts[(nurse, day, shift)] for nurse in range(num_nurses)) == 1)

    for nurse in range(num_nurses):
        for day in range(num_days):
            for shift in range(shifts_per_day):
                if not nurse_availability[nurse][day]:
                    model.Add(shifts[(nurse, day, shift)] == 0)

    # mx consecutive shifts = 2
    for nurse in range(num_nurses):
        for day in range(num_days - max_consecutive_shifts + 1):
            model.Add(sum(shifts[(nurse, day + i, 0)] + shifts[(nurse, day + i, 1)] for i in range(max_consecutive_shifts)) <= max_consecutive_shifts)

    # min rest time = 1 day
    for nurse in range(num_nurses):
        for day in range(num_days - 1):
            model.Add(sum(shifts[(nurse, day + i, 0)] + shifts[(nurse, day + i, 1)] for i in range(min_rest_time)) <= 1)

    # solver
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # create table for output
    output_table = []

    # collect results
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for day in range(num_days):
            day_output = []
            for shift in range(shifts_per_day):
                shift_output = []
                for nurse in range(num_nurses):
                    if solver.Value(shifts[(nurse, day, shift)]) == 1:
                        shift_output.append(f"Nurse {nurse + 1}")
                day_output.append(", ".join(shift_output))
            output_table.append(day_output)
    else:
        output_table = [["No solution found."] * shifts_per_day] * num_days

    # print result as table
    print("\nSchedule:")
    df = pd.DataFrame(output_table, index=[f"Day {day + 1}" for day in range(num_days)], columns=[f"Shift {shift + 1}" for shift in range(shifts_per_day)])
    print(df)

    # Statistics.
    print("\nStatistics")
    print(f"  - conflicts      : {solver.NumConflicts()}")
    print(f"  - branches       : {solver.NumBranches()}")
    print(f"  - wall time      : {solver.WallTime()} s")

if __name__ == "__main__":
    main()
