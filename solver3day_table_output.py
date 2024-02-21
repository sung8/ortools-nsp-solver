from ortools.sat.python import cp_model

def main():
    num_nurses = 4
    num_days = 3
    shifts_per_day = 2

    # nurse availability matrix
    # 1 - available, 0 - unavailable
    nurse_availability = [
        [1, 1, 0],
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 1]
    ]

    model = cp_model.CpModel()

    # decision variables
    shifts = {}
    for nurse in range(num_nurses):
        for day in range(num_days):
            for shift in range(shifts_per_day):
                shifts[(nurse, day, shift)] = model.NewBoolVar(f'nurse_{nurse}_day_{day}_shift_{shift}')

    # basic constraints
    # assign each based on availability
    for day in range(num_days):
        for shift in range(shifts_per_day):
            model.Add(sum(shifts[(nurse, day, shift)] for nurse in range(num_nurses)) == 1)

    for nurse in range(num_nurses):
        for day in range(num_days):
            for shift in range(shifts_per_day):
                if not nurse_availability[nurse][day]:
                    model.Add(shifts[(nurse, day, shift)] == 0)

    # solver
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # print output as table
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(" Day  Shift  Assigned Nurse")
        for day in range(num_days):
            for shift in range(shifts_per_day):
                assigned_nurse = None
                for nurse in range(num_nurses):
                    if solver.Value(shifts[(nurse, day, shift)]) == 1:
                        assigned_nurse = nurse + 1
                        break
                print(f"  {day + 1}    {shift + 1}         {assigned_nurse}          ")
        print()
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()
