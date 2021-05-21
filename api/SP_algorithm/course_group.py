class Course_group:

    def __init__(self, course_name, department, enroll_possible_list):
        self.name = course_name
        self.office = department
        self.possibles = enroll_possible_list

    def get_possibles(self):
        return self.possibles

    def get_office(self):
        return self.office

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id