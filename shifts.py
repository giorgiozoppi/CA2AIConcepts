from ortools.sat.python import cp_model

def main():
    # Create the model
    
    model = cp_model.CpModel()
    # Data
    staff = ['Mark', 'Judy', 'Colm', 'Dave', 'Jane', 'Anne', 'Gavin', 'Tanya']
    mapped_hours = { key: value for key, value in zip(range(9,19), range(0,10)) }
    staff_time_slots = {'Mark': (9,15), 
                        'Judy': (10, 15),
                        'Colm': (13, 15),
                        'Dave': (11, 12),
                        'Jane': (10, 13),
                        'Anne':(14, 18), 
                        'Gavin':(13, 17),
                        'Tanya':(9, 15)}
    
    num_days = 3
    hours_per_day = 9
    
    # Create shift variables
    shifts = {}
    for day in range(num_days):
        for hour in range(hours_per_day):
            for s in range(len(staff)):
                print(f'shift_{day}_{hour}_{staff[s]}')
                shifts[(day, hour, s)] = model.new_bool_var(f'shift_{day}_{hour}_{staff[s]}')

    # Constraints
    # Each time slot must be covered by exactly one staff member
    for day in range(num_days):
        for hour in range(hours_per_day):
            model.add_exactly_one(shifts[(day, hour, s)] for s in range(len(staff)))
    
     # Staff members should not work consecutive hours
    for s in range(len(staff)):
        for day in range(num_days):
            for hour in range(hours_per_day - 1):
                model.add_implication(shifts[(day, hour, s)], shifts[(day, hour + 1, s)].Not())

    # Everyone should work.
    for s in range(len(staff)):
        for day in range(num_days):
            model.add(sum(shifts[(day, hour, s)] for hour in range(hours_per_day)) >= 1)

    
    # Each staff member can only work within their available times
    for name in staff:
        staff_index = staff.index(name)
        for day in range(num_days):
            for hour in range(hours_per_day):
                start = staff_time_slots[name][0]
                end = staff_time_slots[name][1]
                if hour < mapped_hours[start] or hour >= mapped_hours[end]:  
                    model.add(shifts[(day, hour, staff_index)] == 0)
    
    min_shifts_per_receptionist = (hours_per_day * num_days) // len(staff)
    if hours_per_day * num_days % len(staff) == 0:
        max_shifts_per_receptionist = min_shifts_per_receptionist
    else:
        max_shifts_per_receptionist = min_shifts_per_receptionist + 1
    
    # anne is the only one available for the last shift each day

    for s in range(len(staff)):
        shifts_worked = []
        for d in range(num_days):
            for h in range(hours_per_day):
                if s != staff.index('Anne'):
                    shifts_worked.append(shifts[(d,h,s)])
        if s != staff.index('Anne'):
            model.add(min_shifts_per_receptionist <= sum(shifts_worked))
            model.add(sum(shifts_worked) <= max_shifts_per_receptionist)
    
    # Solve the model
    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0
    solver.parameters.enumerate_all_solutions = True


    class ReceptionistShiftPrinter(cp_model.CpSolverSolutionCallback):
        def __init__(self, shifts, num_days, hours_per_day, staff, limit):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._shifts = shifts
            self._num_days = num_days
            self._hours_per_day = hours_per_day
            self._staff = staff
            self._solution_count = 0
            self._solution_limit = limit
        @property
        def solution_count(self):
            return self._solution_count
        def OnSolutionCallback(self):
            self._solution_count += 1
            if self._solution_count <=self._solution_limit:
                print(f'Solution {self._solution_count}')
                for day in range(self._num_days):
                    print(f'Day {day + 1}')
                    for hour in range(self._hours_per_day):
                        for s in range(len(self._staff)):
                            if self.Value(self._shifts[(day, hour, s)]):
                                print(f'  Hour {hour + 9}:00 - {self._staff[s]}')

    # Create the solution printer and solve
    solution_limit = 5000 # print up to 
    solution_printer = ReceptionistShiftPrinter(shifts, num_days, hours_per_day, staff, solution_limit)
    solver.solve(model, solution_printer)
    print(solution_printer._solution_count)
    

if __name__ == '__main__':
    main()
