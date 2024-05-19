from ortools.sat.python import cp_model
model = cp_model.CpModel()
staff = ['Mark', 'Judy', 'Colm', 'Dave', 'Jane', 'Anne', 'Gavin', 'Tanya']
mapped_hours = { key: value for key, value in zip(range(9,19), range(0,10)) }
staff_time_slots = {'Mark': (9, 14), 
                        'Judy': (10, 15),
                        'Colm': (13, 15),
                        'Dave': (11, 12),
                        'Jane': (10, 13),
                        'Anne': (14, 18),
                        'Gavin': (13, 17),
                        'Tanya': (9, 15)}
    
num_days = 4
hours_per_day = 9  # From 9:00 to 18:00
# Create shift variables
shifts = {}
for day in range(num_days):
    for hour in range(hours_per_day):
        for s in range(len(staff)):
            shifts[(day, hour, s)] = model.new_bool_var(f'shift_{day}_{hour}_{staff[s]}')
for day in range(num_days):
    for hour in range(hours_per_day):
        model.add_exactly_one(shifts[(day, hour, s)] for s in range(len(staff)))

# everyone should work.
for s in range(len(staff)):
    for day in range(num_days):
        shift_sum = sum(shifts[(day, hour, s)] for hour in range(hours_per_day)) >= 1
        model.add(shift_sum)

# Each member the staff except Anne and Gavin will be one turn.
# From the turn table is evident to keep fairness between employee, it is needed someone in
# the afternoon. we can pin the afternoon turns to be fair
anne_index = staff.index('Anne')
gavin_index = staff.index('Gavin')
for staff_index in  range(len(staff)):
   if anne_index != staff_index and gavin_index != staff_index:
      for day in range(num_days):
         model.add_at_most_one(shifts[(day,hour,staff_index)] for hour in range(hours_per_day))

# i pin Anne everyday at 3 p.m and 5 p.m. This allows her to stay in different slots non consecutive and reduce the space of solutions.
# Anne is the only one that has a fixed slot. We fix manually the turn in the afternoon in fair way between Gavin and Anne.

for day in range(num_days):
    model.add(sum(shifts[(day, hour, anne_index)] for hour in range(hours_per_day)) <= 2)
    model.add(sum(shifts[(day, hour, gavin_index)] for hour in range(hours_per_day)) <= 2)
        
    if day == 0:
        model.add(shifts[(day, mapped_hours[15], anne_index)] == 1) 
        model.add(shifts[(day, mapped_hours[16], gavin_index)] == 1)
        model.add(shifts[(day, mapped_hours[17], anne_index)] == 1)
    elif day == 1:
        model.add(shifts[(day, mapped_hours[15], gavin_index)] == 1) 
        model.add(shifts[(day, mapped_hours[16], gavin_index)] == 1)
        model.add(shifts[(day, mapped_hours[17], anne_index)] == 1)
    elif day == 2:
        model.add(shifts[(day, mapped_hours[15], gavin_index)] == 1) 
        model.add(shifts[(day, mapped_hours[16], anne_index)] == 1)
        model.add(shifts[(day, mapped_hours[17], anne_index)] == 1)
    elif day == 3:
        model.add(shifts[(day, mapped_hours[15], gavin_index)] == 1) 
        model.add(shifts[(day, mapped_hours[16], gavin_index)] == 1)
        model.add(shifts[(day, mapped_hours[17], anne_index)] == 1)

# Each staff member can only work within their available times
for name in staff:
    staff_index = staff.index(name)
    for day in range(num_days):
        for hour in range(hours_per_day):
            start = staff_time_slots[name][0]
            end = staff_time_slots[name][1]
            if hour < mapped_hours[start] or hour >= mapped_hours[end]:  
                model.add(shifts[(day, hour, staff_index)] == 0)

# Solve the model
solver = cp_model.CpSolver()
solver.parameters.linearization_level = 0
solver.parameters.enumerate_all_solutions = True
class ReceptionistShiftPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, shifts, num_days, hours_per_day, staff, limit=2):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._shifts = shifts
        self._num_days = num_days
        self._hours_per_day = hours_per_day
        self._staff = staff
        self.solution_count = 0
        self._solution_limit = limit
        
    def OnSolutionCallback(self):
        self.solution_count += 1
        if self.solution_count <=self._solution_limit:
            print(f'Solution {self.solution_count}')
            for day in range(self._num_days):
                print(f'Day {day + 1}')
                for hour in range(self._hours_per_day):
                    for s in range(len(self._staff)):
                        if self.Value(self._shifts[(day, hour, s)]):
                            print(f'  Hour {hour + 9}:00 - {self._staff[s]}')


solution_printer = ReceptionistShiftPrinter(shifts, num_days, hours_per_day, staff)
solver.Solve(model, solution_printer)
print(f'Number of solutions found: {solution_printer.solution_count}')