from ortools.sat.python import cp_model
import pandas as pd

def main():
    num_nurses = 4
    num_shifts = 2
    num_days = 7
    shifts_per_day = 2
    max_consecutive_shifts = 2

    # nurse availability matrix
    # 1 - available, 0 - unavailable
    nurse_availability = [
        [1, 1, 0, 1, 0, 1, 1],
        [0, 1, 1, 0, 1, 1, 0],
        [1, 0, 1, 1, 0, 0, 1],
        [1, 1, 1, 0, 1, 0, 1]
    ]

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
    df = pd.DataFrame(output_table, index=[f"Day {day + 1}" for day in range(num_days)], columns=[f"Shift {shift + 1}" for shift in range(shifts_per_day)])
    print(df)

    # Statistics.
    print("\nStatistics")
    print(f"  - conflicts      : {solver.NumConflicts()}")
    print(f"  - branches       : {solver.NumBranches()}")
    print(f"  - wall time      : {solver.WallTime()} s")

if __name__ == "__main__":
    main()
